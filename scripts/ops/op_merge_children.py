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
from .. import consts
from ..link import link_with_ShapeKeysUtil
from ..funcs import func_merge_children_recursive, func_merge_children_main
from ..funcs.utils import func_ui_utils, func_package_utils


class OBJECT_OT_specials_merge_children(bpy.types.Operator):
    bl_idname = "object.automerge_apply_modifier_and_merge_children"
    bl_label = "Merge Children"
    bl_description = bpy.app.translations.pgettext(bl_idname + consts.DESC)
    bl_options = {'REGISTER', 'UNDO'}

    ignore_dont_merge_to_parent_group: BoolProperty(
        name="Ignore " + consts.DONT_MERGE_TO_PARENT_GROUP_NAME + " Property",
        default=True,
    )

    use_variants_merge: BoolProperty(
        name="Use Variants",
        default=True,
        description=bpy.app.translations.pgettext(consts.KEY_USE_VARIANTS)
    )

    remove_non_render_mod: BoolProperty(
        name="Remove Non-Render Modifiers",
        default=True,
        description=bpy.app.translations.pgettext(consts.KEY_REMOVE_NON_RENDER_MOD)
    )

    reparent_if_object_hidden: BoolProperty(
        name="Reparent If Object Hidden",
        default=True,
    )

    only_grouped: BoolProperty(
        name="Only Grouped",
        default=False,
    )
    root_is_selected: BoolProperty(
        name="Root is Selected",
        default=False,
    )

    restore_selection: BoolProperty(
        name="Restore Selection",
        default=False,
    )

    @classmethod
    def poll(cls, context):
        return bpy.context.selected_objects

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "use_variants_merge")
        layout.prop(self, "reparent_if_object_hidden")
        layout.prop(self, "remove_non_render_mod")
        layout.prop(self, "ignore_dont_merge_to_parent_group")
        layout.prop(self, "restore_selection")

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
        try:
            addon_prefs = func_package_utils.get_addon_prefs()
            settings_1 = func_merge_children_recursive.Settings()
            settings_1.use_shapekeys_util = addon_prefs.apply_modifiers_with_shapekeys
            settings_1.remove_non_render_mod = self.remove_non_render_mod
            settings_1.ignore_dont_merge_to_parent_group = self.ignore_dont_merge_to_parent_group
            settings_1.reparent_if_object_hidden = self.reparent_if_object_hidden
            settings_2 = func_merge_children_main.Settings()
            settings_2.use_variants_merge = self.use_variants_merge
            settings_2.only_grouped = self.only_grouped
            settings_2.root_is_selected = self.root_is_selected
            settings_2.restore_selection = self.restore_selection
            func_merge_children_main.merge_children_main(
                operator=self,
                settings_1=settings_1,
                settings_2=settings_2
            )
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
