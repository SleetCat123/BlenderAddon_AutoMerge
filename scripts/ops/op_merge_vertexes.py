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
import bmesh
from bpy.props import BoolProperty
from .. import consts
from ..funcs import func_merge_vertexes


class OBJECT_OT_mizore_merge_vertexes(bpy.types.Operator):
    bl_idname = "object.automerge_merge_vertexes"
    bl_label = "Merge Vertexes"
    bl_description = bpy.app.translations.pgettext(bl_idname + consts.DESC)
    bl_options = {'REGISTER', 'UNDO'}

    threshold: bpy.props.FloatProperty(
        name="Threshold",
        default=0.0001,
        min=0.0,
        max=1.0,
        precision=6,
    )
    remove_merged_group: BoolProperty(
        name="Remove Merged Group",
        default=True,
    )

    def execute(self, context):
        selected = bpy.context.selected_objects
        func_merge_vertexes.merge_vertexes(
            objects=selected,
            threshold=self.threshold,
            remove_merged_group=self.remove_merged_group,
        )
        return {'FINISHED'}


def register():
    bpy.utils.register_class(OBJECT_OT_mizore_merge_vertexes)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_mizore_merge_vertexes)
