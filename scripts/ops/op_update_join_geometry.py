"""
オペレーター責務: Join Geometry Recursiveノードの対象オブジェクト状態を最新に更新
- 全選択オブジェクトのJoin Geometry Recursiveモディファイアを検索（再帰版のみが対象）
- モディファイアに設定されている全オブジェクトからget_top_level_objectsで真のルートオブジェクトを特定
- 各ルートオブジェクトとその再帰的子オブジェクトで再度Join Geometry実行（重複処理回避）
"""

import bpy
from bpy.props import BoolProperty, EnumProperty
from .. import consts
from ..funcs.utils import func_object_utils
from .join_geometry_base import JoinGeometryBase


class OBJECT_OT_automerge_update_join_geometry(bpy.types.Operator, JoinGeometryBase):
    """Update Join Geometry nodes with current state of target objects"""
    bl_idname = "object.automerge_update_join_geometry"
    bl_label = "Update Join Geometry"
    bl_description = "Update Join Geometry nodes to reflect current state of target objects and their children"
    bl_options = {'REGISTER', 'UNDO'}

    update_offsets: BoolProperty(
        name="Update Offsets",
        description="Update stored world coordinates to current object positions",
        default=False
    )
    
    change_transform_mode: EnumProperty(
        name="Transform System Change",
        description="Change existing coordinate system",
        items=[
            ('KEEP', "Keep Current", "Maintain current coordinate system"),
            ('TO_RELATIVE', "To Relative", "Change to relative coordinate system"),
            ('TO_ABSOLUTE', "To Absolute", "Change to absolute coordinate system")
        ],
        default='KEEP'
    )





    @classmethod
    def poll(cls, context):
        """実行可能条件: 選択オブジェクトの中にMESHタイプのオブジェクトが存在する"""
        return any(obj.type == 'MESH' for obj in context.selected_objects)



    def execute(self, context):
        """オペレーターのメイン処理"""
        # 共通基盤クラスを初期化
        JoinGeometryBase.__init__(self, consts.JOIN_GEOMETRY_NODE_GROUP_NAME_RECURSIVE, consts.JOIN_GEOMETRY_MODIFIER_NAME_RECURSIVE)
        
        # 全選択オブジェクトのJoin Geometry Recursiveモディファイアを検索（再帰版のみが対象）
        target_modifier = None
        target_obj = None
        
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue
                
            for modifier in obj.modifiers:
                if modifier.type == 'NODES':
                    # モディファイア名またはノードグループ名で判定（再帰版のみ）
                    is_modifier_match = (modifier.name.startswith(consts.JOIN_GEOMETRY_MODIFIER_NAME_RECURSIVE))
                    is_nodegroup_match = (modifier.node_group and 
                                        modifier.node_group.name.startswith(consts.JOIN_GEOMETRY_NODE_GROUP_NAME_RECURSIVE))
                    
                    if is_modifier_match or is_nodegroup_match:
                        target_modifier = modifier
                        target_obj = obj
                        break
            
            # 最初に見つかったモディファイアで処理を行う
            if target_modifier:
                break
        
        if not target_modifier:
            self.report({'WARNING'}, "No Join Geometry Recursive modifier found in selected objects")
            return {'CANCELLED'}
        
        print(f"Update Join Geometry: Found modifier = {target_modifier.name} on object = {target_obj.name}")
        
        # モディファイアから設定されているオブジェクトを取得
        current_target_objects = self.get_modifier_target_objects(target_modifier)
        
        if not current_target_objects:
            self.report({'WARNING'}, "No target objects found in Join Geometry modifier")
            return {'CANCELLED'}
        
        print(f"Update Join Geometry: Current target objects = {len(current_target_objects)}")
        for obj in current_target_objects:
            print(f"  - {obj.name}")
        
        # get_top_level_objectsで真のルートオブジェクトのみを特定（重複処理回避）
        root_objects = func_object_utils.get_top_level_objects(current_target_objects)
        
        if not root_objects:
            # フォールバック: 現在の対象オブジェクト全てをルートとして使用
            root_objects = current_target_objects
            print("Update Join Geometry: No clear hierarchy found, using all current objects as roots")
        
        print(f"Update Join Geometry: Root objects (duplicates avoided) = {len(root_objects)}")
        for obj in root_objects:
            print(f"  - {obj.name}")
        
        # 効率化ログ出力
        efficiency_gain = len(current_target_objects) - len(root_objects)
        if efficiency_gain > 0:
            print(f"Update Join Geometry: Avoided {efficiency_gain} redundant recursive processing")
        
        # 各ルートオブジェクトとその再帰的子オブジェクトを取得（1回ずつのみ実行）
        all_target_objects = []
        
        for root_obj in root_objects:
            # 各ルートオブジェクトとその再帰的子オブジェクトを取得
            recursive_objects = func_object_utils.get_children_recursive(
                targets=[root_obj], 
                contains_self=True
            )
            
            print(f"Update Join Geometry: {root_obj.name} has {len(recursive_objects)} objects including children:")
            for obj in recursive_objects:
                print(f"    - {obj.name}")
                
            all_target_objects.extend(recursive_objects)
        
        print(f"Update Join Geometry: Total target objects = {len(all_target_objects)}")
        for obj in sorted(all_target_objects, key=lambda x: x.name):
            print(f"  - {obj.name}")
        
        # 現在の座標システムを検出
        current_transform_space = self.detect_transform_space(target_modifier)
        print(f"Update Join Geometry: Current transform space = {current_transform_space}")
        
        # 座標システム変更の処理
        if self.change_transform_mode == 'TO_RELATIVE':
            new_transform_space = 'RELATIVE'
            print("Update Join Geometry: Changing to RELATIVE transform space")
        elif self.change_transform_mode == 'TO_ABSOLUTE':
            new_transform_space = 'ABSOLUTE'
            print("Update Join Geometry: Changing to ABSOLUTE transform space")
        else:  # 'KEEP'
            new_transform_space = current_transform_space
            print(f"Update Join Geometry: Keeping current transform space ({current_transform_space})")
        
        # オフセット更新処理（絶対位置モード時のみ）
        if new_transform_space == 'ABSOLUTE' and self.update_offsets:
            print("Update Join Geometry: Updating object offsets to current positions")
            for obj in all_target_objects:
                self.update_object_offset(obj)
        
        # 現在の設定と新しい設定の比較
        current_objects_set = set(current_target_objects)
        new_objects_set = set(all_target_objects)
        
        added_objects = new_objects_set - current_objects_set
        removed_objects = current_objects_set - new_objects_set
        
        if added_objects:
            print(f"Update Join Geometry: Added {len(added_objects)} new objects:")
            for obj in sorted(added_objects, key=lambda x: x.name):
                print(f"  + {obj.name}")
        
        if removed_objects:
            print(f"Update Join Geometry: Removed {len(removed_objects)} objects:")
            for obj in sorted(removed_objects, key=lambda x: x.name):
                print(f"  - {obj.name}")
        
        if not added_objects and not removed_objects:
            print("Update Join Geometry: No changes detected in object hierarchy")
        
        # 共通基盤クラスのメソッドを使用してJoin Geometry更新実行（座標システム指定）
        result, message = self.execute_join_geometry(
            target_obj, 
            all_target_objects, 
            "Update Join Geometry",
            new_transform_space
        )
        
        if result == {'FINISHED'}:
            # より詳細な成功メッセージ
            change_info = ""
            if added_objects or removed_objects:
                change_info = f" (Added: {len(added_objects)}, Removed: {len(removed_objects)})"
            
            # 座標システム情報を追加
            mode_text = "（絶対位置）" if new_transform_space == 'ABSOLUTE' else "（相対位置）"
            
            # オフセット更新情報を追加
            offset_info = ""
            if new_transform_space == 'ABSOLUTE':
                if self.update_offsets:
                    offset_info = "（位置更新）"
                else:
                    offset_info = "（位置保持）"
            
            detailed_message = f"{message}{change_info}{mode_text}{offset_info}"
            self.report({'INFO'}, detailed_message)
        else:
            self.report({'ERROR'}, message)
        
        return result
    
    def draw(self, context):
        """プロパティパネル表示用"""
        layout = self.layout
        
        layout.prop(self, "change_transform_mode")
        
        # 座標システム変更時の詳細設定
        if self.change_transform_mode != 'KEEP':
            box = layout.box()
            box.label(text="座標システム変更:")
            if self.change_transform_mode == 'TO_ABSOLUTE':
                box.prop(self, "update_offsets")
                if self.update_offsets:
                    box.label(text="現在の位置を新しい基準位置として設定します")
        else:
            # 現状維持時はオフセット更新のみ表示
            layout.prop(self, "update_offsets")
            if self.update_offsets:
                box = layout.box()
                box.label(text="絶対位置モードの場合のみ有効")


# 翻訳辞書
translations_dict = {
    "ja_JP": {
        # オペレーター説明
        ("*", "Update Join Geometry nodes to reflect current state of target objects and their children"): "Join Geometryノードを対象オブジェクトとその子オブジェクトの現在の状態に更新します",
        

        
        # プロパティの翻訳
        ("*", "Update Offsets"): "オフセット更新",
        ("*", "Update stored world coordinates to current object positions"): "保存されたワールド座標を現在のオブジェクト位置に更新",
        ("*", "Transform System Change"): "座標システム変更",
        ("*", "Change existing coordinate system"): "既存の座標システムを変更",
        ("*", "Keep Current"): "現状維持",
        ("*", "Maintain current coordinate system"): "現在の座標システムを維持",
        ("*", "To Relative"): "相対位置に変更",
        ("*", "Change to relative coordinate system"): "相対位置システムに変更",
        ("*", "To Absolute"): "絶対位置に変更",
        ("*", "Change to absolute coordinate system"): "絶対位置システムに変更",
        
        # エラー・警告メッセージ
        ("*", "No Join Geometry Recursive modifier found in selected objects"): "選択オブジェクトにJoin Geometry Recursiveモディファイアが見つかりません",
        ("*", "No target objects found in Join Geometry modifier"): "Join Geometryモディファイアに対象オブジェクトが設定されていません",
    },
}


def register():
    """アドオンの登録処理"""
    bpy.utils.register_class(OBJECT_OT_automerge_update_join_geometry)
    bpy.app.translations.register(__name__, translations_dict)


def unregister():
    """アドオンの登録解除処理"""
    bpy.utils.unregister_class(OBJECT_OT_automerge_update_join_geometry)
    bpy.app.translations.unregister(__name__) 