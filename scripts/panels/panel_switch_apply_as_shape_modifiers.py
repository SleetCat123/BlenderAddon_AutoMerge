from typing import Any
import bpy
from bpy.types import AnyType, Context, UILayout
from ..funcs.utils import func_custom_props_utils


APPLY_AS_SHAPEKEY_PREFIX = "%AS%"


class MIZORE_UL_AS_Modifiers_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index, flt_flag):
        label = item.name[len(APPLY_AS_SHAPEKEY_PREFIX):]
        op = layout.operator(OBJECT_OT_mizore_utilspanel_switch_a_a_s_modifiers.bl_idname, text=label, translate=False)
        op.target_mode = 'ALL'
        op.modifier_name = item.name

    def filter_items(self, context, data, property):
        items = getattr(data, property)
        filtered = [self.bitflag_filter_item] * len(items)
        for i, item in enumerate(items):
            if not item.name.startswith(APPLY_AS_SHAPEKEY_PREFIX):
                filtered[i] &= ~self.bitflag_filter_item
        ordered = []
        return filtered, ordered



class OBJECT_OT_mizore_utilspanel_switch_a_a_s_modifiers(bpy.types.Operator):
    bl_idname = "object.mizore_utilspanel_switch_a_a_s_modifiers"
    bl_label = "Switch Apply As Shape Modifiers"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    target_mode: bpy.props.EnumProperty(
        items=[
            ("SELECTED", "Selected", ""),
            ("ALL", "All", ""),
        ],
        name="Target Mode",
        default="SELECTED"
    )
    modifier_name: bpy.props.StringProperty(name="Modifier Name", default=APPLY_AS_SHAPEKEY_PREFIX)

    def execute(self, context):
        if self.modifier_name and not self.modifier_name.startswith(APPLY_AS_SHAPEKEY_PREFIX):
            self.report({'ERROR'}, f"Modifier name must start with '{APPLY_AS_SHAPEKEY_PREFIX}'")
            return {'CANCELLED'}
        if self.target_mode == "SELECTED":
            targets = bpy.context.selected_objects
        else:
            targets = bpy.data.objects
        for obj in targets:
            if obj.type != "MESH":
                continue
            for mod in obj.modifiers:
                if mod.name.startswith(APPLY_AS_SHAPEKEY_PREFIX):
                    if mod.name == self.modifier_name:
                        mod.show_viewport = True
                    else:
                        mod.show_viewport = False
        return {'FINISHED'}


# class OBJECT_PT_mizores_utilspanel_group_panel(bpy.types.Panel):
class OBJECT_PT_mizores_utilspanel_switch_a_a_s_modifiers_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Mizore"
    bl_label = "Switch " + APPLY_AS_SHAPEKEY_PREFIX + " Modifiers"

    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object
        wm = bpy.context.window_manager

        if not obj:
            layout.label(text="No object selected.")
            return
        
        layout.label(text="Switch Visibility of Apply As Shape Modifiers")
        
        op = layout.operator(OBJECT_OT_mizore_utilspanel_switch_a_a_s_modifiers.bl_idname, text="None")
        op.target_mode = 'ALL'
        op.modifier_name = ""

        # template_listでモディファイアのリストを表示
        layout.template_list("MIZORE_UL_AS_Modifiers_List", "mizore_AS_modlist", obj, "modifiers", wm, "mizore_utilspanel_switch_a_a_s_modifiers_index", rows=5)
        


classes = [
    MIZORE_UL_AS_Modifiers_List,
    OBJECT_OT_mizore_utilspanel_switch_a_a_s_modifiers,
    OBJECT_PT_mizores_utilspanel_switch_a_a_s_modifiers_panel,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.WindowManager.mizore_utilspanel_switch_a_a_s_modifiers_index = bpy.props.IntProperty(
        name="Index",
        default=0
    )


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    del bpy.types.WindowManager.mizore_utilspanel_switch_a_a_s_modifiers_index
