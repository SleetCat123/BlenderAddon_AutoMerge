"""
オペレーター責務: 選択中のオブジェクトをGeometry NodesのJoin Geometryで結合
- アクティブオブジェクトに専用のGeometry Nodesモディファイアを追加/再利用
- 選択している全オブジェクトをJoin Geometryするノードグラフを構築
- アクティブオブジェクトのみを選択状態にする
- Blender 2.92以降との広いバージョン互換性を提供
"""

import bpy
import traceback
from bpy.props import StringProperty
from .. import consts
from ..funcs.utils import func_package_utils


class OBJECT_OT_automerge_join_geometry_nodes(bpy.types.Operator):
    """Join selected objects to active object using Geometry Nodes Join Geometry"""
    bl_idname = "object.automerge_join_geometry_nodes"
    bl_label = "Join Geometry Nodes"
    bl_description = "Join all selected objects to active object using Geometry Nodes Join Geometry"
    bl_options = {'REGISTER', 'UNDO'}

    node_group_name: StringProperty(
        name="Node Group Name",
        default=consts.JOIN_GEOMETRY_NODE_GROUP_NAME,
        description="Name of the Geometry Nodes node group"
    )

    modifier_name: StringProperty(
        name="Modifier Name", 
        default=consts.JOIN_GEOMETRY_MODIFIER_NAME,
        description="Name of the modifier to create"
    )

    @classmethod
    def poll(cls, context):
        """実行可能条件: アクティブオブジェクトが存在し、複数のオブジェクトが選択されている"""
        return (
            context.active_object 
            and context.active_object.type == 'MESH'
            and len(context.selected_objects) > 1
        )

    def draw(self, context):
        """オペレーターのUI描画"""
        layout = self.layout
        layout.prop(self, "node_group_name")
        layout.prop(self, "modifier_name")

    def execute(self, context):
        """オペレーターのメイン処理"""
        try:
            active_obj = context.active_object
            
            # アクティブオブジェクトがMESHタイプかどうか確認
            if not active_obj or active_obj.type != 'MESH':
                self.report({'ERROR'}, "Active object is not a mesh object")
                return {'CANCELLED'}
            
            selected_objects = [obj for obj in context.selected_objects if obj != active_obj and obj.type == 'MESH']
            
            if not selected_objects:
                self.report({'WARNING'}, "No valid mesh objects selected other than active object")
                return {'CANCELLED'}

            print(f"Join Geometry: {active_obj.name} + {len(selected_objects)} objects")

            # Geometry Nodesモディファイアの取得または作成
            modifier = self._get_or_create_geometry_modifier(active_obj)
            
            # ノードグループの新規作成（Socket_Nカウンター問題回避のため）
            node_group = self._create_new_node_group()
            modifier.node_group = node_group

            # オブジェクトソケットの設定
            self._setup_object_sockets(node_group, selected_objects)
            
            # モディファイアにオブジェクトを設定
            self._assign_objects_to_modifier(modifier, selected_objects)

            # アクティブオブジェクトのみを選択状態に変更
            bpy.ops.object.select_all(action='DESELECT')
            active_obj.select_set(True)
            context.view_layer.objects.active = active_obj

            print(f"Join Geometry completed: {len(selected_objects)} objects joined")
            self.report({'INFO'}, f"Join Geometry completed: {len(selected_objects)} objects joined")
            return {'FINISHED'}

        except Exception as e:
            # エラー時のアンドゥ処理
            bpy.ops.ed.undo_push(message="Restore point")
            bpy.ops.ed.undo()
            bpy.ops.ed.undo_push(message="Restore point")
            traceback.print_exc()
            print(f"Join Geometry Error: {str(e)}")
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

    def _get_or_create_geometry_modifier(self, obj):
        """アクティブオブジェクトにGeometry Nodesモディファイアを取得または作成"""
        # 既存のモディファイアを検索（モディファイア名またはノードグループ名で判定）
        for modifier in obj.modifiers:
            if modifier.type == 'NODES':
                # モディファイア名での判定（アドオン専用名）
                is_modifier_match = (modifier.name == self.modifier_name or 
                                   modifier.name.startswith(consts.JOIN_GEOMETRY_MODIFIER_NAME))
                
                # ノードグループ名での判定（アドオン専用名）
                is_nodegroup_match = (modifier.node_group and 
                                    modifier.node_group.name == self.node_group_name)
                
                # どちらか片方が条件を満たしたら再利用
                if is_modifier_match or is_nodegroup_match:
                    return modifier
        
        # 新規モディファイア作成
        modifier = obj.modifiers.new(self.modifier_name, 'NODES')
        return modifier

    def _create_new_node_group(self):
        """新規ノードグループを作成（Socket_Nカウンター問題回避のため既存削除）"""
        # 既存のノードグループを検索して削除（Socket_Nカウンターリセットのため）
        existing_groups = []
        for node_group in bpy.data.node_groups:
            if (node_group.name == self.node_group_name or 
                node_group.name.startswith(self.node_group_name)):
                existing_groups.append(node_group)
        
        for node_group in existing_groups:
            try:
                bpy.data.node_groups.remove(node_group)
            except:
                pass
        
        # 新規作成
        node_group = bpy.data.node_groups.new(self.node_group_name, 'GeometryNodeTree')
        self._create_node_graph(node_group)
        return node_group

    def _create_node_graph(self, node_group):
        """Join Geometryのノードグラフを作成"""
        nodes = node_group.nodes
        links = node_group.links
        
        # 既存ノードをクリア
        nodes.clear()

        # Group Input/Output作成
        input_node = nodes.new("NodeGroupInput")
        input_node.location = (-400, 0)
        output_node = nodes.new("NodeGroupOutput")
        output_node.location = (400, 0)

        # Geometry ソケットの作成（バージョン互換性対応）
        try:
            # Blender 3.4以降のinterface API
            if hasattr(node_group, 'interface') and hasattr(node_group.interface, 'new_socket'):
                node_group.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
                node_group.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
            else:
                # 古いバージョン用のフォールバック
                node_group.inputs.new('NodeSocketGeometry', "Geometry")
                node_group.outputs.new('NodeSocketGeometry', "Geometry")
        except:
            # 最後の手段として古い方法を試す
            try:
                node_group.inputs.new('NodeSocketGeometry', "Geometry")
                node_group.outputs.new('NodeSocketGeometry', "Geometry")
            except:
                print("Error: Failed to create basic geometry sockets")

        # Join Geometryノード作成
        join_node = nodes.new("GeometryNodeJoinGeometry")
        join_node.location = (0, 0)

        # 基本接続: Input Geometry -> Join Geometry -> Output
        links.new(input_node.outputs["Geometry"], join_node.inputs["Geometry"])
        links.new(join_node.outputs["Geometry"], output_node.inputs["Geometry"])

    def _setup_object_sockets(self, node_group, selected_objects):
        """選択オブジェクト用のソケットとノードを設定"""
        nodes = node_group.nodes
        links = node_group.links
        
        join_node = None
        for node in nodes:
            if node.type == 'JOIN_GEOMETRY':
                join_node = node
                break
                
        if not join_node:
            return

        # Group InputとGroup Outputノードを取得
        input_node = None
        output_node = None
        for node in nodes:
            if node.type == 'GROUP_INPUT':
                input_node = node
            elif node.type == 'GROUP_OUTPUT':
                output_node = node
        
        # 各選択オブジェクトに対してソケットとノードを動的作成
        y_offset = -200
        for i, obj in enumerate(selected_objects):
            socket_name = f"Object_{i+1}_{obj.name}"
            
            # オブジェクトソケット作成（バージョン互換性対応）
            try:
                # Blender 3.4以降のinterface API
                if hasattr(node_group, 'interface') and hasattr(node_group.interface, 'new_socket'):
                    obj_socket = node_group.interface.new_socket(socket_name, in_out='INPUT', socket_type='NodeSocketObject')
                else:
                    # 古いバージョン用のフォールバック
                    obj_socket = node_group.inputs.new('NodeSocketObject', socket_name)
            except:
                try:
                    obj_socket = node_group.inputs.new('NodeSocketObject', socket_name)
                except:
                    continue
            
            # Object Infoノード作成
            obj_info_node = nodes.new("GeometryNodeObjectInfo")
            obj_info_node.location = (-200, y_offset)
            obj_info_node.name = f"ObjectInfo_{obj.name}"
            obj_info_node.transform_space = 'RELATIVE'  # 相対変換空間に設定
            
            # 接続
            if input_node:
                links.new(input_node.outputs[socket_name], obj_info_node.inputs["Object"])
            links.new(obj_info_node.outputs["Geometry"], join_node.inputs["Geometry"])
            
            # 次のノードの位置を調整
            y_offset -= 150

        # レイアウト調整
        if output_node:
            output_node.location = (200 + len(selected_objects) * 50, 0)

    def _assign_objects_to_modifier(self, modifier, selected_objects):
        """モディファイアの各オブジェクトソケットに実際のオブジェクトを設定"""
        if not modifier.node_group:
            return
        
        # オブジェクトソケットの名前とインデックスのマッピングを作成
        socket_mapping = {}
        node_group = modifier.node_group
        
        try:
            # Blender 3.4以降のinterface API
            if hasattr(node_group, 'interface') and hasattr(node_group.interface, 'items_tree'):
                for idx, socket in enumerate(node_group.interface.items_tree):
                    if socket.in_out == 'INPUT':
                        socket_mapping[socket.name] = idx
            # より古いバージョン用のフォールバック
            elif hasattr(node_group, 'inputs'):
                for idx, socket in enumerate(node_group.inputs):
                    socket_mapping[socket.name] = idx
        except:
            return
        
        # 各オブジェクトをSocket_Nに設定
        for i, obj in enumerate(selected_objects):
            expected_socket_name = f"Object_{i+1}_{obj.name}"
            
            if expected_socket_name in socket_mapping:
                # インターフェースソケットのインデックスに対応するSocket_Nに設定
                socket_index = socket_mapping[expected_socket_name]
                socket_n_name = f"Socket_{socket_index}"
                
                try:
                    modifier[socket_n_name] = obj
                except:
                    pass
        
        # UI更新
        try:
            bpy.context.view_layer.update()
            depsgraph = bpy.context.evaluated_depsgraph_get()
            depsgraph.update()
        except:
            pass


# 翻訳辞書
translations_dict = {
    "ja_JP": {
        # オペレーター説明
        ("*", "Join all selected objects to active object using Geometry Nodes Join Geometry"): "選択中の全オブジェクトをアクティブオブジェクトにGeometry NodesでJoin Geometryします",
        
        # プロパティ名
        ("*", "Node Group Name"): "ノードグループ名",
        ("*", "Modifier Name"): "モディファイア名",
        
        # プロパティ説明
        ("*", "Name of the Geometry Nodes node group"): "Geometry Nodesのノードグループ名",
        ("*", "Name of the modifier to create"): "作成するモディファイア名",
        
        # エラー・警告メッセージ
        ("*", "Active object is not a mesh object"): "アクティブオブジェクトがメッシュオブジェクトではありません",
        ("*", "No valid mesh objects selected other than active object"): "アクティブオブジェクト以外の有効なメッシュオブジェクトが選択されていません",
    },
}


def register():
    """アドオンの登録処理"""
    bpy.utils.register_class(OBJECT_OT_automerge_join_geometry_nodes)
    bpy.app.translations.register(__name__, translations_dict)


def unregister():
    """アドオンの登録解除処理"""
    bpy.utils.unregister_class(OBJECT_OT_automerge_join_geometry_nodes)
    bpy.app.translations.unregister(__name__) 