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
from .. import consts
from ..funcs.utils import func_collection_utils, func_custom_props_utils


class OBJECT_OT_mizore_add_vertex_group(bpy.types.Operator):
    bl_idname = "object.auto_merge_add_vertex_group"
    bl_label = "Add Vertex Group"
    bl_description = bpy.app.translations.pgettext(bl_idname + consts.DESC)
    bl_options = {'REGISTER', 'UNDO'}

    group_name: bpy.props.StringProperty(
        name="Group Name",
        default="",
    )

    def execute(self, context):
        obj = bpy.context.active_object
        obj.vertex_groups.new(name=self.group_name)
        self.report({'INFO'}, f"Added Vertex Group: {self.group_name}")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(OBJECT_OT_mizore_add_vertex_group)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_mizore_add_vertex_group)
