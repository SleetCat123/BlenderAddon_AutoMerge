"""
オペレーター責務: 選択中のオブジェクトをGeometry NodesのJoin Geometryで結合
- アクティブオブジェクトに専用のGeometry Nodesモディファイアを追加/再利用
- 選択している全オブジェクトをJoin Geometryするノードグラフを構築
- アクティブオブジェクトのみを選択状態にする
- Blender 2.92以降との広いバージョン互換性を提供
"""

import bpy
from bpy.props import EnumProperty
from ... import consts
from .join_geometry_base import JoinGeometryBase


class OBJECT_OT_automerge_join_geometry_nodes(bpy.types.Operator, JoinGeometryBase):
    """Join selected objects to active object using Geometry Nodes Join Geometry"""
    bl_idname = "object.automerge_join_geometry_nodes"
    bl_label = "Join Geometry Nodes"
    bl_description = "Join all selected objects to active object using Geometry Nodes Join Geometry"
    bl_options = {'REGISTER', 'UNDO'}

    transform_space_mode: EnumProperty(
        name="Transform Space",
        description="Choose coordinate system for object positioning",
        items=[
            ('RELATIVE', "Relative", "Objects follow their current positions (dynamic)"),
            ('ABSOLUTE', "Absolute", "Objects locked to creation-time positions (static)")
        ],
        default='RELATIVE'
    )





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
        JoinGeometryBase.__init__(self, consts.JOIN_GEOMETRY_NODE_GROUP_NAME, consts.JOIN_GEOMETRY_MODIFIER_NAME)
        
        active_obj = context.active_object
        selected_objects = [obj for obj in context.selected_objects if obj != active_obj and obj.type == 'MESH']
        
        # 座標システムの設定
        transform_space = 'ABSOLUTE' if self.transform_space_mode == 'ABSOLUTE' else 'RELATIVE'
        
        # 共通基盤クラスのメソッドを使用（座標システム指定）
        result, message = self.execute_join_geometry(active_obj, selected_objects, "Join Geometry", transform_space)
        
        if result == {'FINISHED'}:
            # 座標システム情報をメッセージに追加
            mode_text = "（絶対位置）" if transform_space == 'ABSOLUTE' else "（相対位置）"
            detailed_message = f"{message}{mode_text}"
            self.report({'INFO'}, detailed_message)
        else:
            self.report({'ERROR'}, message)
        
        return result
    
    def draw(self, context):
        """プロパティパネル表示用"""
        layout = self.layout
        
        layout.prop(self, "transform_space_mode")
        
        # 絶対位置モード時の説明
        if self.transform_space_mode == 'ABSOLUTE':
            box = layout.box()
            box.label(text="絶対位置モード:")
            box.label(text="オブジェクトを移動しても結合位置は固定されます")


# 翻訳辞書
translations_dict = {
    "ja_JP": {
        # オペレーター説明
        ("*", "Join all selected objects to active object using Geometry Nodes Join Geometry"): "選択中の全オブジェクトをアクティブオブジェクトにGeometry NodesでJoin Geometryします",
        

        
        # プロパティの翻訳
        ("*", "Transform Space"): "座標システム",
        ("*", "Choose coordinate system for object positioning"): "オブジェクトの位置制御方法を選択",
        ("*", "Relative"): "相対位置",
        ("*", "Objects follow their current positions (dynamic)"): "オブジェクトの移動に結合結果が追従（動的）",
        ("*", "Absolute"): "絶対位置",
        ("*", "Objects locked to creation-time positions (static)"): "作成時の位置に固定（静的）",
        
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