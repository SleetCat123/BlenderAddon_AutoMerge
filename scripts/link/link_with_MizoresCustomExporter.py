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
from ..funcs import func_merge_children_main, func_merge_children_recursive


# MizoresCustomExporter連携用
class OBJECT_OT_merge_children_grouped_for_exporter_addon(bpy.types.Operator):
    bl_idname = "object.apply_modifier_and_merge_grouped_exporter_addon"
    bl_label = "[Internal] Merge Grouped Children For MizoresCustomExporter Addon"
    bl_options = {'REGISTER', 'UNDO'}

    use_shapekeys_util: BoolProperty(default=True)
    remove_non_render_mod: BoolProperty(default=True)
    use_variants_merge: BoolProperty(default=True)

    def execute(self, context):
        settings_1 = func_merge_children_recursive.Settings()
        settings_1.use_shapekeys_util = self.use_shapekeys_util
        settings_1.remove_non_render_mod = self.remove_non_render_mod
        settings_1.ignore_dont_merge_to_parent_group = True
        settings_2 = func_merge_children_main.Settings()
        settings_2.use_variants_merge = self.use_variants_merge
        settings_2.only_grouped = True
        settings_2.root_is_selected = False
        settings_2.restore_selection = True
        settings_2.reparent_if_object_hidden = True
        func_merge_children_main.merge_children_main(
            operator=self,
            settings_1=settings_1,
            settings_2=settings_2
        )
        return {'FINISHED'}


def register():
    bpy.utils.register_class(OBJECT_OT_merge_children_grouped_for_exporter_addon)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_merge_children_grouped_for_exporter_addon)
