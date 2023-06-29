import bpy
from bpy.props import StringProperty, PointerProperty, EnumProperty, BoolProperty
from . import consts, func_object_utils, func_collection_utils


class OBJECT_PT_mizores_automerge_list_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Mizore"
    bl_label = "Objects"
    bl_options = {"DEFAULT_CLOSED"}

    @staticmethod
    def draw_recursive(obj, layout, indent: int,
                       merge: bool = False,
                       dont_export: bool = False,
                       always_export: bool = False):
        split = layout.split(align=True, factor=0.8)
        if indent <= 0:
            indent = 1
        split_indent = split.split(align=True, factor=0.05 * indent)
        if obj.select_get():
            split_indent.label(text="-")
        else:
            split_indent.label(text="")
        split_indent.label(text=obj.name, icon='OUTLINER_OB_' + obj.type)

        row = split.row(align=True)

        collection = func_collection_utils.find_collection('DontExport')
        if collection and obj.name in collection.objects:
            dont_export = True

        collection = func_collection_utils.find_collection('AlwaysExport')
        if collection and obj.name in collection.objects:
            always_export = True

        if merge:
            row.label(icon='EMPTY_SINGLE_ARROW')

        is_merge_root = False
        collection = func_collection_utils.find_collection(consts.PARENTS_GROUP_NAME)
        if collection and obj.name in collection.objects:
            is_merge_root = True
            merge = True

        if is_merge_root:
            row.label(icon='OUTLINER')
        if dont_export:
            row.label(icon='PANEL_CLOSE')
        if always_export:
            row.label(icon='CHECKMARK')


        children = func_object_utils.get_children_objects(obj)
        for child in children:
            OBJECT_PT_mizores_automerge_list_panel.draw_recursive(child, layout, indent=indent + 1,
                                                                  merge=merge,
                                                                  dont_export=dont_export,
                                                                  always_export=always_export
                                                                  )

    def draw(self, context):
        print("draw panel_object_list")
        layout = self.layout

        roots = [v for v in bpy.context.window.view_layer.objects if v.parent is None]
        for obj in roots:
            OBJECT_PT_mizores_automerge_list_panel.draw_recursive(obj, layout, indent=0)


classes = [
    OBJECT_PT_mizores_automerge_list_panel,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
