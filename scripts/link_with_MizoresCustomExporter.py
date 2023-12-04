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
from .funcs import func_apply_modifier_and_merge_children_grouped
from bpy.props import StringProperty, BoolProperty


# MizoresCustomExporter連携用
class OBJECT_OT_merge_children_grouped_for_exporter_addon(bpy.types.Operator):
    bl_idname = "object.apply_modifier_and_merge_grouped_exporter_addon"
    bl_label = "[Internal] Merge Grouped Children For MizoresCustomExporter Addon"
    bl_options = {'REGISTER', 'UNDO'}

    enable_apply_modifiers_with_shapekeys: BoolProperty(default=True)
    ignore_collection_name = StringProperty(
        name='Ignore Collection'
    )
    ignore_prop_name = StringProperty(
        name='Ignore Property'
    )

    def execute(self, context):
        ignore_collection = None
        if self.ignore_collection_name in bpy.data.collections:
            ignore_collection = bpy.data.collections[self.ignore_collection_name]
        b = func_apply_modifier_and_merge_children_grouped.apply_modifier_and_merge_children_grouped(
            self,
            context,
            ignore_collection=ignore_collection,
            ignore_prop_name=self.ignore_prop_name,
            apply_modifiers_with_shapekeys=self.enable_apply_modifiers_with_shapekeys,
            duplicate=False,
            remove_non_render_mod=True
        )
        if b:
            return {'FINISHED'}
        else:
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(OBJECT_OT_merge_children_grouped_for_exporter_addon)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_merge_children_grouped_for_exporter_addon)

