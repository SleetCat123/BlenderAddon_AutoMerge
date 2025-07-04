"""
共通基盤クラス責務: Geometry NodesのJoin Geometry処理の共通機能を提供
- Geometry Nodesモディファイアの取得/作成
- ノードグループの作成と管理
- オブジェクトソケットの設定
- モディファイアへのオブジェクト割り当て
- UI更新処理
"""

import bpy
import traceback
from bpy.props import StringProperty
from mathutils import Vector
from ... import consts


class JoinGeometryBase:
    """Geometry Nodes Join処理の共通基盤クラス"""
    
    def __init__(self, node_group_name: str = None, modifier_name: str = None):
        """共通基盤クラスの初期化"""
        self.node_group_name = node_group_name or consts.JOIN_GEOMETRY_NODE_GROUP_NAME
        self.modifier_name = modifier_name or consts.JOIN_GEOMETRY_MODIFIER_NAME
    
    def get_or_create_geometry_modifier(self, obj):
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

    def create_new_node_group(self):
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

    def setup_object_sockets(self, node_group, target_objects, transform_space='RELATIVE'):
        """対象オブジェクト用のソケットとノードを設定"""
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
        
        # 各対象オブジェクトに対してソケットとノードを動的作成
        y_offset = -200
        for i, obj in enumerate(target_objects):
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
            obj_info_node.transform_space = 'ABSOLUTE' if transform_space == 'ABSOLUTE' else 'RELATIVE'
            
            # 絶対位置モードの場合、Transform Geometryノードを追加してオフセット調整
            if transform_space == 'ABSOLUTE':
                # Transform Geometryノード作成
                transform_node = nodes.new("GeometryNodeTransform")
                transform_node.location = (-50, y_offset)
                transform_node.name = f"Transform_{obj.name}"
                
                # オフセット値を取得・設定
                offset = self.get_or_store_object_offset(obj)
                transform_node.inputs["Translation"].default_value = (-offset.x, -offset.y, -offset.z)
                
                # 接続: Object Info -> Transform -> Join Geometry
                if input_node:
                    links.new(input_node.outputs[socket_name], obj_info_node.inputs["Object"])
                links.new(obj_info_node.outputs["Geometry"], transform_node.inputs["Geometry"])
                links.new(transform_node.outputs["Geometry"], join_node.inputs["Geometry"])
            else:
                # 相対位置モード（従来通り）
                if input_node:
                    links.new(input_node.outputs[socket_name], obj_info_node.inputs["Object"])
                links.new(obj_info_node.outputs["Geometry"], join_node.inputs["Geometry"])
            
            
            # 次のノードの位置を調整
            y_offset -= 150

        # レイアウト調整
        if output_node:
            output_node.location = (200 + len(target_objects) * 50, 0)

    def assign_objects_to_modifier(self, modifier, target_objects):
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
        for i, obj in enumerate(target_objects):
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
        self.update_ui()

    def update_ui(self):
        """UI更新処理"""
        try:
            bpy.context.view_layer.update()
            depsgraph = bpy.context.evaluated_depsgraph_get()
            depsgraph.update()
        except:
            pass

    def execute_join_geometry(self, active_obj, target_objects, log_message: str = "Join Geometry", transform_space='RELATIVE'):
        """Join Geometry処理の実行（共通メイン処理）"""
        try:
            # アクティブオブジェクトがMESHタイプかどうか確認
            if not active_obj or active_obj.type != 'MESH':
                return {'CANCELLED'}, "Active object is not a mesh object"
            
            # 対象オブジェクトのフィルタリング（MESHタイプのみ）
            valid_objects = [obj for obj in target_objects if obj != active_obj and obj.type == 'MESH']
            
            if not valid_objects:
                return {'CANCELLED'}, "No valid mesh objects to join"

            print(f"{log_message}: {active_obj.name} + {len(valid_objects)} objects")

            # Geometry Nodesモディファイアの取得または作成
            modifier = self.get_or_create_geometry_modifier(active_obj)
            
            # ノードグループの新規作成（Socket_Nカウンター問題回避のため）
            node_group = self.create_new_node_group()
            modifier.node_group = node_group

            # オブジェクトソケットの設定（座標システム指定）
            self.setup_object_sockets(node_group, valid_objects, transform_space)
            
            # モディファイアにオブジェクトを設定
            self.assign_objects_to_modifier(modifier, valid_objects)

            # Join対象オブジェクトからArmatureモディファイアをコピー
            self.copy_armature_modifiers(valid_objects, active_obj)

            # アクティブオブジェクトのみを選択状態に変更
            bpy.ops.object.select_all(action='DESELECT')
            active_obj.select_set(True)
            bpy.context.view_layer.objects.active = active_obj

            success_message = f"{log_message} completed: {len(valid_objects)} objects joined"
            print(success_message)
            return {'FINISHED'}, success_message

        except Exception as e:
            # エラー時のアンドゥ処理
            bpy.ops.ed.undo_push(message="Restore point")
            bpy.ops.ed.undo()
            bpy.ops.ed.undo_push(message="Restore point")
            traceback.print_exc()
            error_message = f"{log_message} Error: {str(e)}"
            print(error_message)
            return {'CANCELLED'}, error_message

    def copy_armature_modifiers(self, source_objects, target_obj):
        """ソースオブジェクトからターゲットオブジェクトにArmatureモディファイアをコピー（重複回避）"""
        # ターゲットオブジェクトが持つ既存のArmatureを収集
        existing_armatures = set()
        for modifier in target_obj.modifiers:
            if modifier.type == 'ARMATURE' and modifier.object:
                existing_armatures.add(modifier.object)
        
        # ソースオブジェクトからArmatureモディファイアを検索
        copied_count = 0
        for source_obj in source_objects:
            if source_obj.type != 'MESH':
                continue
                
            for modifier in source_obj.modifiers:
                if modifier.type != 'ARMATURE' or not modifier.object:
                    continue
                
                # 既に同じArmatureを対象とするモディファイアがある場合はスキップ
                if modifier.object in existing_armatures:
                    print(f"Armatureモディファイア '{modifier.name}' (Armature: {modifier.object.name}) は既に存在するためスキップ")
                    continue
                
                # Armatureモディファイアをコピー
                try:
                    new_modifier = target_obj.modifiers.new(modifier.name, 'ARMATURE')
                    new_modifier.object = modifier.object
                    new_modifier.use_vertex_groups = modifier.use_vertex_groups
                    new_modifier.use_bone_envelopes = modifier.use_bone_envelopes
                    new_modifier.use_deform_preserve_volume = modifier.use_deform_preserve_volume
                    
                    # バージョン互換性のためのプロパティコピー
                    if hasattr(modifier, 'invert_vertex_group'):
                        new_modifier.invert_vertex_group = modifier.invert_vertex_group
                    if hasattr(modifier, 'vertex_group'):
                        new_modifier.vertex_group = modifier.vertex_group
                    
                    existing_armatures.add(modifier.object)
                    copied_count += 1
                    print(f"Armatureモディファイア '{modifier.name}' を {source_obj.name} から {target_obj.name} にコピーしました")
                    
                except Exception as e:
                    print(f"Armatureモディファイア '{modifier.name}' のコピーに失敗: {str(e)}")
        
        if copied_count > 0:
            print(f"合計 {copied_count} 個のArmatureモディファイアをコピーしました")
        else:
            print("コピー対象のArmatureモディファイアはありませんでした")

    def get_modifier_target_objects(self, modifier):
        """モディファイアから設定されているオブジェクトを取得"""
        target_objects = []
        
        if not modifier or not modifier.node_group:
            return target_objects
        
        # Socket_Nからオブジェクトを取得
        for test_index in range(0, 20):  # 最大20個のソケットをチェック
            test_socket = f"Socket_{test_index}"
            try:
                if test_socket in modifier and modifier[test_socket]:
                    obj = modifier[test_socket]
                    if obj and obj.type == 'MESH':
                        target_objects.append(obj)
            except:
                pass
        
        return target_objects

    def get_or_store_object_offset(self, obj):
        """オブジェクトのワールド座標オフセットを取得または保存"""
        offset_key_x = f"automerge_offset_x"
        offset_key_y = f"automerge_offset_y"
        offset_key_z = f"automerge_offset_z"
        
        # 既存のオフセット情報を確認
        if (offset_key_x in obj and offset_key_y in obj and offset_key_z in obj):
            # 既存のオフセットを返す
            return Vector((
                obj[offset_key_x],
                obj[offset_key_y], 
                obj[offset_key_z]
            ))
        else:
            # 新規オフセットを現在のワールド座標で保存
            world_location = obj.matrix_world.translation
            obj[offset_key_x] = world_location.x
            obj[offset_key_y] = world_location.y
            obj[offset_key_z] = world_location.z
            
            print(f"新規オフセット保存: {obj.name} -> ({world_location.x:.3f}, {world_location.y:.3f}, {world_location.z:.3f})")
            return world_location.copy()
    
    def update_object_offset(self, obj):
        """オブジェクトのワールド座標オフセットを現在の位置で更新"""
        world_location = obj.matrix_world.translation
        obj[f"automerge_offset_x"] = world_location.x
        obj[f"automerge_offset_y"] = world_location.y
        obj[f"automerge_offset_z"] = world_location.z
        
        print(f"オフセット更新: {obj.name} -> ({world_location.x:.3f}, {world_location.y:.3f}, {world_location.z:.3f})")
    
    def detect_transform_space(self, modifier):
        """モディファイアから現在の座標システムを検出"""
        if not modifier.node_group:
            return 'RELATIVE'
        
        # Transform Geometryノードの存在確認
        for node in modifier.node_group.nodes:
            if node.type == 'TRANSFORM_GEOMETRY':
                return 'ABSOLUTE'
        
        return 'RELATIVE'