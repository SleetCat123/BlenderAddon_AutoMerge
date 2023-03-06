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
from . import AutoMerge
from bpy.props import PointerProperty


# MizoresCustomExporter連携用
class OBJECT_OT_merge_children_grouped_for_exporter_addon(bpy.types.Operator):
    bl_idname = "object.apply_modifier_and_merge_grouped_exporter_addon"
    bl_label = "[Internal] Merge Grouped Children For MizoresCustomExporter Addon"
    bl_options = {'REGISTER', 'UNDO'}

    enable_apply_modifiers_with_shapekeys: bpy.props.BoolProperty(name="Ignore Armature", default=True)

    def execute(self, context):
        ignore_collection = bpy.types.WindowManager.mizore_automerge_temp_ignore_collection
        print("IGNORE!!!!!!!!!!!!" + str(ignore_collection))
        b = AutoMerge.apply_modifier_and_merge_children_grouped(
            self,
            context,
            ignore_collection=ignore_collection,
            enable_apply_modifiers_with_shapekeys=self.enable_apply_modifiers_with_shapekeys,
            duplicate=False,
            apply_parentobj_modifier=True,
            ignore_armature=True
        )
        if b:
            return {'FINISHED'}
        else:
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(OBJECT_OT_merge_children_grouped_for_exporter_addon)
    bpy.types.WindowManager.mizore_automerge_temp_ignore_collection = PointerProperty(
        type=bpy.types.Collection,
        name='Ignore Collection'
    )


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_merge_children_grouped_for_exporter_addon)
    del bpy.types.WindowManager.mizore_automerge_temp_ignore_collection

