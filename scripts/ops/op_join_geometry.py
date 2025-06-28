"""
オペレーター責務: 選択中のオブジェクトをGeometry NodesのJoin Geometryで結合
- アクティブオブジェクトに専用のGeometry Nodesモディファイアを追加/再利用
- 選択している全オブジェクトをJoin Geometryするノードグラフを構築
- アクティブオブジェクトのみを選択状態にする
- Blender 2.92以降との広いバージョン互換性を提供
"""

import bpy
from bpy.props import StringProperty
from .. import consts
from .join_geometry_base import JoinGeometryBase


class OBJECT_OT_automerge_join_geometry_nodes(bpy.types.Operator, JoinGeometryBase):
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
        # 共通基盤クラスを初期化
        JoinGeometryBase.__init__(self, self.node_group_name, self.modifier_name)
        
        active_obj = context.active_object
        selected_objects = [obj for obj in context.selected_objects if obj != active_obj and obj.type == 'MESH']
        
        # 共通基盤クラスのメソッドを使用
        result, message = self.execute_join_geometry(active_obj, selected_objects, "Join Geometry")
        
        if result == {'FINISHED'}:
            self.report({'INFO'}, message)
        else:
            self.report({'ERROR'}, message)
        
        return result


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