"""
オペレーター責務: 選択中のオブジェクトとその再帰的子オブジェクトを新規空メッシュオブジェクトにJoin Geometryで結合
- 新規の空メッシュオブジェクトを作成
- 既存のJoin Geometry Recursiveオペレータを呼び出してGeometry Nodes結合を実行
- 元のオブジェクトは非破壊的に維持
"""

import bpy
from bpy.props import StringProperty


class OBJECT_OT_automerge_join_geometry_recursive_to_new(bpy.types.Operator):
    """Join all selected objects and their recursive children to new empty mesh object using Geometry Nodes"""
    bl_idname = "object.automerge_join_geometry_recursive_to_new"
    bl_label = "Join Geometry Recursive to New"
    bl_description = "Join all selected objects and their recursive children to new empty mesh object using Geometry Nodes Join Geometry"
    bl_options = {'REGISTER', 'UNDO'}

    new_object_name: StringProperty(
        name="New Object Name",
        default="JoinedGeometry_Recursive",
        description="Name of the new mesh object to create"
    )

    @classmethod
    def poll(cls, context):
        """実行可能条件: 1つ以上のMESHオブジェクトが選択されている"""
        return any(obj.type == 'MESH' for obj in context.selected_objects)

    def draw(self, context):
        """オペレーターのUI描画"""
        layout = self.layout
        layout.prop(self, "new_object_name")

    def execute(self, context):
        """オペレーターのメイン処理"""
        # 選択中のMESHオブジェクトを取得
        selected_mesh_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_mesh_objects:
            self.report({'WARNING'}, "No mesh objects selected")
            return {'CANCELLED'}

        print(f"Join Geometry Recursive to New: Selected mesh objects = {len(selected_mesh_objects)}")
        for obj in selected_mesh_objects:
            print(f"  - {obj.name}")

        # 新規空メッシュオブジェクトを作成
        mesh = bpy.data.meshes.new(self.new_object_name)
        new_obj = bpy.data.objects.new(self.new_object_name, mesh)
        
        # シーンに追加
        context.collection.objects.link(new_obj)
        
        print(f"Join Geometry Recursive to New: Created new object = {new_obj.name}")

        # 元のオブジェクトと新規オブジェクトを選択
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected_mesh_objects:
            obj.select_set(True)
        new_obj.select_set(True)
        
        # 新規オブジェクトをアクティブに設定
        context.view_layer.objects.active = new_obj

        # 既存のJoin Geometry Recursiveオペレータを呼び出し
        try:
            result = bpy.ops.object.automerge_join_geometry_recursive()
            if result == {'FINISHED'}:
                success_message = f"Join Geometry Recursive completed - New object: {new_obj.name}"
                self.report({'INFO'}, success_message)
                print(f"Join Geometry Recursive to New: Successfully created {new_obj.name} with recursive join of {len(selected_mesh_objects)} selected objects")
                return {'FINISHED'}
            else:
                # エラー時は作成したオブジェクトを削除
                try:
                    bpy.data.objects.remove(new_obj, do_unlink=True)
                    bpy.data.meshes.remove(mesh, do_unlink=True)
                except:
                    pass
                self.report({'ERROR'}, "Failed to execute Join Geometry Recursive")
                return {'CANCELLED'}
        except Exception as e:
            # エラー時は作成したオブジェクトを削除
            try:
                bpy.data.objects.remove(new_obj, do_unlink=True)
                bpy.data.meshes.remove(mesh, do_unlink=True)
            except:
                pass
            self.report({'ERROR'}, f"Error calling Join Geometry Recursive: {str(e)}")
            return {'CANCELLED'}


# 翻訳辞書
translations_dict = {
    "ja_JP": {
        # オペレーター説明
        ("*", "Join all selected objects and their recursive children to new empty mesh object using Geometry Nodes"): "選択中の全オブジェクトとその再帰的子オブジェクトを新規空メッシュオブジェクトにGeometry NodesでJoin Geometryします",
        
        # プロパティ名
        ("*", "New Object Name"): "新規オブジェクト名",
        
        # プロパティ説明
        ("*", "Name of the new mesh object to create"): "作成する新規メッシュオブジェクト名",
        
        # エラー・警告メッセージ
        ("*", "No mesh objects selected"): "メッシュオブジェクトが選択されていません",
    },
}


def register():
    """アドオンの登録処理"""
    bpy.utils.register_class(OBJECT_OT_automerge_join_geometry_recursive_to_new)
    bpy.app.translations.register(__name__, translations_dict)


def unregister():
    """アドオンの登録解除処理"""
    bpy.utils.unregister_class(OBJECT_OT_automerge_join_geometry_recursive_to_new)
    bpy.app.translations.unregister(__name__) 