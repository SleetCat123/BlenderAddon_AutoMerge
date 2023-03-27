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
from . import (
    operator_merge_children,
    operator_merge_children_grouped,
    operator_merge_selections,
    operator_assign_merge_group,
)


def INFO_MT_object_specials_auto_merge_menu(self, context):
    self.layout.menu(VIEW3D_MT_object_specials_auto_merge.bl_idname)


class VIEW3D_MT_object_specials_auto_merge(bpy.types.Menu):
    bl_label = "Auto Merge"
    bl_idname = "VIEW3D_MT_object_specials_auto_merge"

    def draw(self, context):
        self.layout.operator(operator_merge_children.OBJECT_OT_specials_merge_children.bl_idname)
        self.layout.operator(operator_merge_children_grouped.OBJECT_OT_specials_merge_children_grouped.bl_idname)
        self.layout.operator(operator_merge_selections.OBJECT_OT_specials_merge_selections.bl_idname)
        self.layout.separator()
        self.layout.operator(operator_assign_merge_group.OBJECT_OT_specials_assign_merge_group.bl_idname)


def register():
    bpy.utils.register_class(VIEW3D_MT_object_specials_auto_merge)
    bpy.types.VIEW3D_MT_object_context_menu.append(INFO_MT_object_specials_auto_merge_menu)


def unregister():
    bpy.utils.unregister_class(VIEW3D_MT_object_specials_auto_merge)
    bpy.types.VIEW3D_MT_object_context_menu.remove(INFO_MT_object_specials_auto_merge_menu)
