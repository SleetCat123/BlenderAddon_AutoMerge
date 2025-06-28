"""
オペレーター責務: 選択中のオブジェクトをGeometry NodesのJoin Geometryで結合
- アクティブオブジェクトに専用のGeometry Nodesモディファイアを追加/再利用
- 選択している全オブジェクトをJoin Geometryするノードグラフを構築
- アクティブオブジェクトのみを選択状態にする
"""

import bpy
import traceback
from bpy.props import BoolProperty, StringProperty
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

    clear_existing_objects: BoolProperty(
        name="Clear Existing Objects",
        default=True,
        description="Clear existing Join Geometry object sockets before setting new objects"
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
        layout.separator()
        layout.prop(self, "clear_existing_objects")

    def execute(self, context):
        """オペレーターのメイン処理"""
        try:
            active_obj = context.active_object
            
            # アクティブオブジェクトがMESHタイプかどうか確認
            if not active_obj or active_obj.type != 'MESH':
                error_msg = f"Active object is not a mesh object (Type: {active_obj.type if active_obj else 'None'})"
                print(f"Join Geometry Error: {error_msg}")
                self.report({'ERROR'}, "Active object is not a mesh object")
                return {'CANCELLED'}
            
            selected_objects = [obj for obj in context.selected_objects if obj != active_obj and obj.type == 'MESH']
            
            if not selected_objects:
                self.report({'WARNING'}, "No valid mesh objects selected other than active object")
                return {'CANCELLED'}

            # ログ出力: 処理開始
            print(f"Join Geometry started: Active={active_obj.name}, Target objects={len(selected_objects)}")

            # Geometry Nodesモディファイアの取得または作成
            modifier = self._get_or_create_geometry_modifier(active_obj)
            
            # ノードグループの取得または作成
            node_group = self._get_or_create_node_group()
            modifier.node_group = node_group

            # オブジェクトソケットの設定
            self._setup_object_sockets(node_group, selected_objects)

            # アクティブオブジェクトのみを選択状態に変更
            bpy.ops.object.select_all(action='DESELECT')
            active_obj.select_set(True)
            context.view_layer.objects.active = active_obj

            # ログ出力: 処理完了
            print(f"Join Geometry completed: Modifier={modifier.name}, Node Group={node_group.name}")
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
        # 既存のモディファイアを検索（ノードグループ名で判定）
        for modifier in obj.modifiers:
            if (modifier.type == 'NODES' 
                and modifier.node_group 
                and modifier.node_group.name == self.node_group_name):
                print(f"Reusing existing Geometry Nodes modifier: {modifier.name}")
                return modifier
        
        # 新規モディファイア作成
        modifier = obj.modifiers.new(self.modifier_name, 'NODES')
        print(f"Created new Geometry Nodes modifier: {modifier.name}")
        return modifier

    def _get_or_create_node_group(self):
        """ノードグループを取得または作成"""
        # 既存のノードグループを検索
        if self.node_group_name in bpy.data.node_groups:
            node_group = bpy.data.node_groups[self.node_group_name]
            print(f"Reusing existing node group: {node_group.name}")
            return node_group

        # 新規ノードグループ作成
        node_group = bpy.data.node_groups.new(self.node_group_name, 'GeometryNodeTree')
        self._create_node_graph(node_group)
        print(f"Created new node group: {node_group.name}")
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

        # Geometry ソケットの作成
        node_group.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
        node_group.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

        # Join Geometryノード作成
        join_node = nodes.new("GeometryNodeJoinGeometry")
        join_node.location = (0, 0)

        # 基本接続: Input Geometry -> Join Geometry -> Output
        links.new(input_node.outputs["Geometry"], join_node.inputs["Geometry"])
        links.new(join_node.outputs["Geometry"], output_node.inputs["Geometry"])

        print("Created basic node graph")

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
            print("Join Geometry node not found")
            return

        # 既存のオブジェクトソケットをクリア（オプション）
        if self.clear_existing_objects:
            self._clear_existing_object_sockets(node_group, join_node)

        # 各選択オブジェクト用のソケットとノードを作成
        input_node = None
        output_node = None
        for node in nodes:
            if node.type == 'GROUP_INPUT':
                input_node = node
            elif node.type == 'GROUP_OUTPUT':
                output_node = node
        
        y_offset = -200
        for i, obj in enumerate(selected_objects):
            socket_name = f"Object_{i+1}_{obj.name}"
            
            # オブジェクトソケット作成
            obj_socket = node_group.interface.new_socket(socket_name, in_out='INPUT', socket_type='NodeSocketObject')
            
            # Object Infoノード作成
            obj_info_node = nodes.new("GeometryNodeObjectInfo")
            obj_info_node.location = (-200, y_offset)
            obj_info_node.name = f"ObjectInfo_{obj.name}"
            obj_info_node.transform_space = 'ORIGINAL'
            
            # 接続
            if input_node:
                links.new(input_node.outputs[socket_name], obj_info_node.inputs["Object"])
            links.new(obj_info_node.outputs["Geometry"], join_node.inputs["Geometry"])
            
            y_offset -= 150
            print(f"Created object socket: {socket_name}")

        # レイアウト調整
        if output_node:
            output_node.location = (200 + len(selected_objects) * 50, 0)

    def _clear_existing_object_sockets(self, node_group, join_node):
        """既存のオブジェクト関連ソケットとノードをクリア"""
        # ObjectInfoノードを削除
        nodes_to_remove = []
        for node in node_group.nodes:
            if node.type == 'OBJECT_INFO' and node.name.startswith("ObjectInfo_"):
                nodes_to_remove.append(node)
        
        for node in nodes_to_remove:
            node_group.nodes.remove(node)
            print(f"Removed existing ObjectInfo node: {node.name}")

        # オブジェクトソケットを削除（Geometry以外）
        sockets_to_remove = []
        for socket in node_group.interface.items_tree:
            if (socket.in_out == 'INPUT' 
                and socket.socket_type == 'NodeSocketObject' 
                and socket.name.startswith("Object_")):
                sockets_to_remove.append(socket)
        
        for socket in sockets_to_remove:
            node_group.interface.remove(socket)
            print(f"Removed existing object socket: {socket.name}")


# 翻訳辞書
translations_dict = {
    "ja_JP": {
        # オペレーター説明
        ("*", "Join all selected objects to active object using Geometry Nodes Join Geometry"): "選択中の全オブジェクトをアクティブオブジェクトにGeometry NodesでJoin Geometryします",
        
        # プロパティ名
        ("*", "Node Group Name"): "ノードグループ名",
        ("*", "Modifier Name"): "モディファイア名",
        ("*", "Clear Existing Objects"): "既存オブジェクトをクリア",
        
        # プロパティ説明
        ("*", "Name of the Geometry Nodes node group"): "Geometry Nodesのノードグループ名",
        ("*", "Name of the modifier to create"): "作成するモディファイア名",
        ("*", "Clear existing Join Geometry object sockets before setting new objects"): "既存のJoinGeometryオブジェクトソケットをクリアしてから新しいオブジェクトを設定",
        
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