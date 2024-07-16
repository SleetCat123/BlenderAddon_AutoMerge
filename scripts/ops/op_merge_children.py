# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import traceback
from bpy.props import BoolProperty
from .. import consts, link_with_ShapeKeysUtil
from ..variants import variants_prop
from ..funcs import func_merge_children_recursive
from ..funcs.utils import func_object_utils, func_ui_utils, func_package_utils, func_custom_props_utils


class OBJECT_OT_specials_merge_children(bpy.types.Operator):
    bl_idname = "object.automerge_apply_modifier_and_merge_children"
    bl_label = "Merge Children"
    bl_description = bpy.app.translations.pgettext(bl_idname + consts.DESC)
    bl_options = {'REGISTER', 'UNDO'}

    ignore_dont_merge_to_parent_group: BoolProperty(
        name="Ignore DONT_MERGE_TO_PARENT_GROUP",
        default=True,
    )

    use_variants: BoolProperty(
        name="Use Variants",
        default=True,
        description=bpy.app.translations.pgettext(consts.KEY_USE_VARIANTS)
    )

    remove_non_render_mod: BoolProperty(
        name="Remove Non-Render Modifiers",
        default=True,
        description=bpy.app.translations.pgettext(consts.KEY_REMOVE_NON_RENDER_MOD)
    )

    only_grouped: BoolProperty(
        name="Only Grouped",
        default=False,
    )
    root_is_selected: BoolProperty(
        name="Root is Selected",
        default=False,
    )

    @classmethod
    def poll(cls, context):
        return bpy.context.selected_objects

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "use_variants")
        layout.prop(self, "remove_non_render_mod")

        layout.separator()
        layout.prop(self, "only_grouped")
        row = layout.row()
        row.enabled = self.only_grouped
        row.prop(self, "root_is_selected")

        if link_with_ShapeKeysUtil.shapekey_util_is_found():
            layout.separator()
            box = layout.box()
            func_ui_utils.shapekey_util_label(box)
            func_ui_utils.box_warning_slow_method(box)
            func_ui_utils.box_warning_read_pref(box)
            col = box.column()
            col.enabled = False
            addon_prefs = func_package_utils.get_addon_prefs()
            col.prop(addon_prefs, "apply_modifiers_with_shapekeys")

    def execute(self, context):
        addon_prefs = func_package_utils.get_addon_prefs()
        settings = func_merge_children_recursive.Settings()
        settings.apply_modifiers_with_shapekeys = addon_prefs.apply_modifiers_with_shapekeys
        settings.remove_non_render_mod = self.remove_non_render_mod
        settings.ignore_dont_merge_to_parent_group = self.ignore_dont_merge_to_parent_group
        print(OBJECT_OT_specials_merge_children.bl_idname)
        print(f"apply_modifiers_with_shapekeys: {settings.apply_modifiers_with_shapekeys}")
        print(f"remove_non_render_mod: {settings.remove_non_render_mod}")
        print(f"ignore_dont_merge_to_parent_group: {settings.ignore_dont_merge_to_parent_group}")
        print(f"use_variants: {self.use_variants}")
        print(f"only_grouped: {self.only_grouped}")
        try:
            # rootを取得
            if self.only_grouped:
                root_objects = func_custom_props_utils.get_prop_root_objects(
                    prop_name=consts.PARENTS_GROUP_NAME,
                    targets=bpy.context.selected_objects
                )
                if self.root_is_selected:
                    root_objects = list(set(root_objects) & set(bpy.context.selected_objects))
            else:
                root_objects = func_object_utils.get_selected_root_objects()
            root_objects_names = []
            for root in root_objects:
                variant_names = variants_prop.get_all_variant_names_in_children(root)
                if self.use_variants and variant_names:
                    variants_count = len(variant_names)
                    print(f"{root.name} has {variants_count} variants")
                    # variantの数だけオブジェクトと子階層を複製して結合
                    for i, variant_name in enumerate(variant_names):
                        print(f"variant: {variant_name}")
                        settings.variants_name = variant_name
                        if i == variants_count - 1:
                            # 最後の要素は元のオブジェクトを使用
                            root.name = root.name + "_" + variant_name
                            root_objects_names.append(root.name)
                            func_object_utils.set_active_object(root)
                            func_merge_children_recursive.merge_children_recursive(
                                operator=self,
                                settings=settings
                            )
                        else:
                            # ルートと子階層を複製
                            children = func_object_utils.get_children_recursive(root)
                            func_object_utils.duplicate_objects(children)
                            root_copy = func_object_utils.get_active_object()
                            root_copy.name = root.name + "_" + variant_name
                            root_objects_names.append(root_copy.name)
                            func_merge_children_recursive.merge_children_recursive(
                                operator=self,
                                settings=settings
                            )
                else:
                    root_objects_names.append(root.name)
                    func_object_utils.set_active_object(root)
                    func_merge_children_recursive.merge_children_recursive(
                        operator=self,
                        settings=settings
                    )
            for root_name in root_objects_names:
                root = bpy.data.objects.get(root_name)
                func_object_utils.select_children_recursive(root)
            return {'FINISHED'}
        except Exception as e:
            bpy.ops.ed.undo_push(message = "Restore point")
            bpy.ops.ed.undo()
            bpy.ops.ed.undo_push(message = "Restore point")
            traceback.print_exc()
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(OBJECT_OT_specials_merge_children)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_specials_merge_children)
