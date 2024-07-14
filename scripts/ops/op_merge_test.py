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
from ..funcs import func_merge_children_recursive_re
from ..funcs.utils import func_ui_utils, func_package_utils, func_object_utils
import traceback


class OBJECT_OT_automerge_merge_test(bpy.types.Operator):
    bl_idname = "object.automerge_merge_test"
    bl_label = "Merge Test"
    bl_description = bpy.app.translations.pgettext(bl_idname + consts.DESC)
    bl_options = {'REGISTER', 'UNDO'}

    remove_non_render_mod: BoolProperty(
        name="Remove Non-Render Modifiers",
        default=True,
        description=bpy.app.translations.pgettext(consts.KEY_REMOVE_NON_RENDER_MOD)
    )

    @classmethod
    def poll(cls, context):
        active_object = func_object_utils.get_active_object()
        return active_object

    def execute(self, context):
        settings = func_merge_children_recursive_re.Settings()
        settings.remove_non_render_mod = self.remove_non_render_mod
        try:
            func_merge_children_recursive_re.merge_children_recursive(
                operator=self,
                settings=settings
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
    bpy.utils.register_class(OBJECT_OT_automerge_merge_test)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_automerge_merge_test)
