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
from ..ops import (
    op_merge_children,
    op_merge_selections,
)
from ..assign_prop_panel import op_assign_prop
from .. import consts


def INFO_MT_object_specials_auto_merge_menu(self, context):
    self.layout.menu(VIEW3D_MT_object_specials_auto_merge.bl_idname)


class VIEW3D_MT_object_specials_auto_merge(bpy.types.Menu):
    bl_label = "Auto Merge"
    bl_idname = "VIEW3D_MT_object_specials_auto_merge"

    def draw(self, context):
        op = self.layout.operator(op_merge_children.OBJECT_OT_specials_merge_children.bl_idname)
        op.only_grouped = False

        op = self.layout.operator(op_merge_children.OBJECT_OT_specials_merge_children.bl_idname, text="Merge Grouped Children")
        op.only_grouped = True
        op.root_is_selected = False

        # op = self.layout.operator(op_merge_children.OBJECT_OT_specials_merge_children.bl_idname, text="Merge Grouped Children (Root is Selected)")
        # op.only_grouped = True
        # op.root_is_selected = True

        self.layout.operator(op_merge_selections.OBJECT_OT_specials_merge_selections.bl_idname)
        self.layout.separator()
        label_base = bpy.app.translations.pgettext(op_assign_prop.OBJECT_OT_mizore_assign_prop.bl_idname + ".label")

        op = self.layout.operator(op_assign_prop.OBJECT_OT_mizore_assign_prop.bl_idname, text=label_base.format(consts.PARENTS_GROUP_NAME))
        op.name = consts.PARENTS_GROUP_NAME

        op = self.layout.operator(op_assign_prop.OBJECT_OT_mizore_assign_prop.bl_idname, text=label_base.format(consts.DONT_MERGE_TO_PARENT_GROUP_NAME))
        op.name = consts.DONT_MERGE_TO_PARENT_GROUP_NAME


def register():
    bpy.utils.register_class(VIEW3D_MT_object_specials_auto_merge)
    bpy.types.VIEW3D_MT_object_context_menu.append(INFO_MT_object_specials_auto_merge_menu)


def unregister():
    bpy.utils.unregister_class(VIEW3D_MT_object_specials_auto_merge)
    bpy.types.VIEW3D_MT_object_context_menu.remove(INFO_MT_object_specials_auto_merge_menu)
