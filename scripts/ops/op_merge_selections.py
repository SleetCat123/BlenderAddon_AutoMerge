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

import traceback
import bpy
from bpy.props import BoolProperty
from .. import consts
from ..link import func_link_with_ShapeKeysUtil
from ..funcs import func_apply_modifier_and_merge_selections, func_warning_slow_method
from ..funcs.utils import func_package_utils


class OBJECT_OT_specials_merge_selections(bpy.types.Operator):
    bl_idname = "object.automerge_apply_modifier_and_merge_selections"
    bl_label = "Merge Selections"
    bl_description = "Merge selected objects into the active object"
    bl_options = {'REGISTER', 'UNDO'}

    remove_non_render_mod: BoolProperty(
        name="Remove Non-Render Modifiers",
        default=True,
        description="A non-render modifier will be removed."
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "remove_non_render_mod")
        if func_link_with_ShapeKeysUtil.shapekey_util_is_found():
            layout.separator()
            box = layout.box()
            func_warning_slow_method.shapekey_util_label(box)
            func_warning_slow_method.box_warning_slow_method(box)
            func_warning_slow_method.box_warning_read_pref(box)
            col = box.column()
            col.enabled = False
            addon_prefs = func_package_utils.get_addon_prefs()
            col.prop(addon_prefs, "apply_modifiers_with_shapekeys")

    def execute(self, context):
        try:
            addon_prefs = func_package_utils.get_addon_prefs()
            func_apply_modifier_and_merge_selections.apply_modifier_and_merge_selections(
                operator=self,
                use_shapekeys_util=addon_prefs.apply_modifiers_with_shapekeys,
                remove_non_render_mod=self.remove_non_render_mod
            )
            return {'FINISHED'}
        except Exception as e:
            bpy.ops.ed.undo_push(message = "Restore point")
            bpy.ops.ed.undo()
            bpy.ops.ed.undo_push(message = "Restore point")
            traceback.print_exc()
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}


translations_dict = {
    "ja_JP": {
        ("*", "Merge selected objects into the active object"): "最後に選択したオブジェクトに対し、\n他の選択中オブジェクトをマージします",
        ("*", "Remove Non-Render Modifiers"): "レンダリング無効モディファイアを削除",
        ("*", "A non-render modifier will be removed."): "レンダリング対象外のモディファイアを削除します",
    },
}


def register():
    bpy.utils.register_class(OBJECT_OT_specials_merge_selections)
    bpy.app.translations.register(__name__, translations_dict)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_specials_merge_selections)
    bpy.app.translations.unregister(__name__)
