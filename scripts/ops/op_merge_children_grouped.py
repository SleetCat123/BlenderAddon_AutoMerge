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
from bpy.props import BoolProperty
from .. import consts, link_with_ShapeKeysUtil
from ..funcs import func_apply_modifier_and_merge_children_grouped
from ..funcs.utils import func_ui_utils, func_package_utils


class OBJECT_OT_specials_merge_children_grouped(bpy.types.Operator):
    bl_idname = "object.automerge_apply_modifier_and_merge_children_grouped"
    bl_label = "Merge Grouped Children"
    bl_description = bpy.app.translations.pgettext(bl_idname + consts.DESC)
    bl_options = {'REGISTER', 'UNDO'}

    duplicate: BoolProperty(
        name="Duplicate",
        default=False,
        description=bpy.app.translations.pgettext(consts.KEY_DUPLICATE)
    )
    remove_non_render_mod: BoolProperty(
        name="Remove Non-Render Modifiers",
        default=True,
        description=bpy.app.translations.pgettext(consts.KEY_REMOVE_NON_RENDER_MOD)
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "duplicate")
        layout.prop(self, "remove_non_render_mod")
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
        b = func_apply_modifier_and_merge_children_grouped.apply_modifier_and_merge_children_grouped(
            self=self, 
            context=context,
            ignore_collection=None,
            ignore_prop_name=None,
            apply_modifiers_with_shapekeys= addon_prefs.apply_modifiers_with_shapekeys,
            duplicate=self.duplicate,
            remove_non_render_mod=self.remove_non_render_mod,
        )
        if b:
            return {'FINISHED'}
        else:
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(OBJECT_OT_specials_merge_children_grouped)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_specials_merge_children_grouped)
