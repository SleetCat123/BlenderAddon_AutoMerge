import bpy
from . import variants_prop


# パネルの定義
class OBJECT_PT_AutoMergeVariantsPanel(bpy.types.Panel):
    bl_label = "AutoMerge - Variants List"
    bl_idname = "OBJECT_PT_AutoMergeVariantsPanel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        prop = variants_prop.get_variants_list(obj)

        row = layout.row()
        row.template_list("UI_UL_list", "variants_list", prop, "variants_list", prop, "active_variant_index")

        col = row.column(align=True)
        col.operator("object.automerge_add_variant", icon='ADD', text="")
        col.operator("object.automerge_remove_variant", icon='REMOVE', text="")
        col.separator()
        col.menu("OBJECT_MT_AutoMerge_VariantsListMenu", icon='DOWNARROW_HLT', text="")


class OBJECT_MT_AutoMerge_VariantsListMenu(bpy.types.Menu):
    bl_label = "Variants List Menu"
    bl_idname = "OBJECT_MT_AutoMerge_VariantsListMenu"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.automerge_clear_variants", text="Clear All Variants")


# 文字列を追加するオペレーター
class OBJECT_OT_AutoMerge_AddVariant(bpy.types.Operator):
    bl_idname = "object.automerge_add_variant"
    bl_label = "Add Variant"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        prop = variants_prop.get_variants_list(obj)
        new_variant = prop.variants_list.add()
        basename = "New Variant"
        # 重複しない名前を生成
        name = basename
        i = 1
        while name in prop.variants_list:
            # 末尾に.001, .002, ...を追加
            name = basename + ".{:03d}".format(i)
            i += 1
        new_variant.name = name
        return {'FINISHED'}


# 文字列を削除するオペレーター
class OBJECT_OT_AutoMerge_RemoveVariant(bpy.types.Operator):
    bl_idname = "object.automerge_remove_variant"
    bl_label = "Remove Variant"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        prop = variants_prop.get_variants_list(obj)
        if prop.variants_list:
            prop.variants_list.remove(prop.active_variant_index)
            prop.active_variant_index = max(0, prop.active_variant_index - 1)
        return {'FINISHED'}


# すべての文字列をクリアするオペレーター
class OBJECT_OT_AutoMerge_ClearVariants(bpy.types.Operator):
    bl_idname = "object.automerge_clear_variants"
    bl_label = "Clear All Variants"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        prop = variants_prop.get_variants_list(obj)
        prop.variants_list.clear()
        prop.active_variant_index = 0
        return {'FINISHED'}


def register():
    bpy.utils.register_class(OBJECT_PT_AutoMergeVariantsPanel)
    bpy.utils.register_class(OBJECT_MT_AutoMerge_VariantsListMenu)
    bpy.utils.register_class(OBJECT_OT_AutoMerge_AddVariant)
    bpy.utils.register_class(OBJECT_OT_AutoMerge_RemoveVariant)
    bpy.utils.register_class(OBJECT_OT_AutoMerge_ClearVariants)


def unregister():
    bpy.utils.unregister_class(OBJECT_PT_AutoMergeVariantsPanel)
    bpy.utils.unregister_class(OBJECT_MT_AutoMerge_VariantsListMenu)
    bpy.utils.unregister_class(OBJECT_OT_AutoMerge_AddVariant)
    bpy.utils.unregister_class(OBJECT_OT_AutoMerge_RemoveVariant)
    bpy.utils.unregister_class(OBJECT_OT_AutoMerge_ClearVariants)
