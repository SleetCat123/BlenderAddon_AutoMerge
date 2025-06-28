"""
オペレーター責務: 全選択オブジェクト（アクティブ以外）とその再帰的子オブジェクトをJoin Geometry
- アクティブオブジェクト以外の全選択オブジェクトを取得
- get_top_level_objectsで真のルートオブジェクトのみを特定（重複処理回避）
- 各ルートオブジェクトの再帰的子オブジェクトをfunc_object_utilsで取得
- 全てをアクティブオブジェクトにGeometry NodesでJoin Geometry
"""

import bpy
from .. import consts
from ..funcs.utils import func_object_utils
from .join_geometry_base import JoinGeometryBase


class OBJECT_OT_automerge_join_geometry_recursive(bpy.types.Operator, JoinGeometryBase):
    """Join all selected objects and their recursive children to active object using Geometry Nodes"""
    bl_idname = "object.automerge_join_geometry_recursive"
    bl_label = "Join Geometry Recursive"
    bl_description = "Join all selected objects and their recursive children to active object using Geometry Nodes Join Geometry"
    bl_options = {'REGISTER', 'UNDO'}





    @classmethod
    def poll(cls, context):
        """実行可能条件: アクティブオブジェクトが存在し、複数のオブジェクトが選択されている"""
        return (
            context.active_object 
            and context.active_object.type == 'MESH'
            and len(context.selected_objects) > 1
        )



    def execute(self, context):
        """オペレーターのメイン処理"""
        # 共通基盤クラスを初期化
        JoinGeometryBase.__init__(self, consts.JOIN_GEOMETRY_NODE_GROUP_NAME_RECURSIVE, consts.JOIN_GEOMETRY_MODIFIER_NAME_RECURSIVE)
        
        active_obj = context.active_object
        
        # アクティブオブジェクト以外の全選択オブジェクトを取得
        selected_objects = [obj for obj in context.selected_objects if obj != active_obj]
        
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected other than active object")
            return {'CANCELLED'}
        
        print(f"Join Geometry Recursive: Selected objects (excluding active) = {len(selected_objects)}")
        for obj in selected_objects:
            print(f"  - {obj.name}")
        
        # get_top_level_objectsで真のルートオブジェクトのみを特定（重複処理回避）
        root_objects = func_object_utils.get_top_level_objects(selected_objects)
        
        print(f"Join Geometry Recursive: Root objects (duplicates avoided) = {len(root_objects)}")
        for obj in root_objects:
            print(f"  - {obj.name}")
        
        # 効率化ログ出力
        efficiency_gain = len(selected_objects) - len(root_objects)
        if efficiency_gain > 0:
            print(f"Join Geometry Recursive: Avoided {efficiency_gain} redundant recursive processing")
        
        # 各ルートオブジェクトとその再帰的子オブジェクトを取得（1回ずつのみ実行）
        all_target_objects = []
        
        for root_obj in root_objects:
            # 各ルートオブジェクトとその再帰的子オブジェクトを取得
            recursive_objects = func_object_utils.get_children_recursive(
                targets=[root_obj], 
                contains_self=True
            )
            
            print(f"Join Geometry Recursive: {root_obj.name} has {len(recursive_objects)} objects including children:")
            for obj in recursive_objects:
                print(f"    - {obj.name}")
                
            all_target_objects.extend(recursive_objects)
        
        print(f"Join Geometry Recursive: Total target objects = {len(all_target_objects)}")
        for obj in sorted(all_target_objects, key=lambda x: x.name):
            print(f"  - {obj.name}")
        
        # 共通基盤クラスのメソッドを使用してJoin Geometry実行
        result, message = self.execute_join_geometry(
            active_obj, 
            all_target_objects, 
            "Join Geometry Recursive"
        )
        
        if result == {'FINISHED'}:
            self.report({'INFO'}, message)
        else:
            self.report({'ERROR'}, message)
        
        return result


# 翻訳辞書
translations_dict = {
    "ja_JP": {
        # オペレーター説明
        ("*", "Join all selected objects and their recursive children to active object using Geometry Nodes"): "選択中の全オブジェクトとその再帰的子オブジェクトをアクティブオブジェクトにGeometry NodesでJoinします",
        

        
        # エラー・警告メッセージ
        ("*", "No objects selected other than active object"): "アクティブオブジェクト以外のオブジェクトが選択されていません",
    },
}


def register():
    """アドオンの登録処理"""
    bpy.utils.register_class(OBJECT_OT_automerge_join_geometry_recursive)
    bpy.app.translations.register(__name__, translations_dict)


def unregister():
    """アドオンの登録解除処理"""
    bpy.utils.unregister_class(OBJECT_OT_automerge_join_geometry_recursive)
    bpy.app.translations.unregister(__name__) 