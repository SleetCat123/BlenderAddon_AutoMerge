from typing import Any
import bpy
from bpy.types import AnyType, Context, UILayout
from ..funcs.utils import func_custom_props_utils


PREFIX_LIST = (
    ("None", "None", "None"),
    ("%AS%", "%AS%", "Apply as shapekey"),
    ("%A%", "%A%", "Force Apply Modifier"),
    ("%KEEP%", "%KEEP%", "Force Keep Modifier"),
)


class MIZORE_UL_Select_Mod_Prefix_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index, flt_flag):
        split = layout.split(factor=0.4)
        split.label(text=item.name, translate=False)
        split = split.split(factor=1)
        row = split.row(align=True)
        row.alignment = 'RIGHT'
        for prefix in PREFIX_LIST:
            prefix_name = prefix[0]
            current_row = row.row()
            if prefix_name != "None" and item.name.startswith(prefix_name):
            # すでにprefixが付いているならボタンをdisableにする
                current_row.enabled = False
            op = current_row.operator(OBJECT_OT_mizore_utilspanel_select_mod_prefix.bl_idname, text=prefix_name)
            op.modifier_name = item.name
            op.prefix_name = prefix_name

    def filter_items(self, context, data, property):
        items = getattr(data, property)
        filtered = [self.bitflag_filter_item] * len(items)
        ordered = []
        return filtered, ordered



class OBJECT_OT_mizore_utilspanel_select_mod_prefix(bpy.types.Operator):
    bl_idname = "object.mizore_utilspanel_select_mod_prefix"
    bl_label = "Select Modifier Prefix"
    bl_description = "Select Modifier Prefix"
    bl_options = {'REGISTER', 'UNDO'}

    modifier_name: bpy.props.StringProperty(name="Modifier Name", default="")
    prefix_name: bpy.props.EnumProperty(
        items=PREFIX_LIST,
        name="Prefix Name",
        default=None
    )

    def execute(self, context):
        target = bpy.context.object
        if self.modifier_name not in target.modifiers:
            self.report({'ERROR'}, "Modifier not found")
            return {'CANCELLED'}
        mod = target.modifiers[self.modifier_name]
        for prefix in PREFIX_LIST:
            # prefixが付いているなら削除
            prefix_name = prefix[0]
            if prefix_name != "None" and mod.name.startswith(prefix_name):
                mod.name = mod.name[len(prefix_name):]
        if self.prefix_name != "None":
            # prefixを追加
            mod.name = self.prefix_name + mod.name

        return {'FINISHED'}


class OBJECT_PT_mizores_utilspanel_select_mod_prefix_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Mizore"
    bl_label = "Modifier Prefix"

    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object
        wm = bpy.context.window_manager

        if not obj:
            layout.label(text="No object selected.")
            return
        
        layout.label(text="Target: " + obj.name)
        if not obj.modifiers:
            layout.label(text="No modifiers found.")
            return
        layout.label(text="Select Modifier Prefix.", translate=True)
        layout.label(text="Prefix is used in ShapekeysUtil and AutoMerge addon.", translate=True)

        # template_listでモディファイアのリストを表示
        layout.template_list("MIZORE_UL_Select_Mod_Prefix_List", "mizore_select_mod_prefix_list", obj, "modifiers", wm, "mizore_utilspanel_select_mod_prefix_index", rows=5)
        

translations_dict = {
    "ja_JP": {
        ("*", "No modifiers found."): "モディファイアが見つかりません。",
        ("*", "No object selected."): "選択中のオブジェクトがありません。",
        ("*", "Select Modifier Prefix."): "モディファイアのprefixを選択します。",
        ("*", "Prefix is used in ShapekeysUtil and AutoMerge addon."): "prefixはShapekeysUtilとAutoMergeアドオンで使用されます。",
    },
}


classes = [
    MIZORE_UL_Select_Mod_Prefix_List,
    OBJECT_OT_mizore_utilspanel_select_mod_prefix,
    OBJECT_PT_mizores_utilspanel_select_mod_prefix_panel
]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.WindowManager.mizore_utilspanel_select_mod_prefix_index = bpy.props.IntProperty(
        name="Index",
        default=0
    )
    bpy.app.translations.register(__name__, translations_dict)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    del bpy.types.WindowManager.mizore_utilspanel_select_mod_prefix_index
    bpy.app.translations.unregister(__name__)
