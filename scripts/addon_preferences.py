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
from .funcs import func_warning_slow_method
from .funcs.utils import func_package_utils
from .link import func_link_with_ShapeKeysUtil


class addon_preferences(bpy.types.AddonPreferences):
    bl_idname = func_package_utils.get_package_root()

    apply_modifiers_with_shapekeys: BoolProperty(name="Apply Modifier with Shape Keys", default=True)

    def draw(self, context):
        layout = self.layout

        # ShapekeysUtil
        box = layout.box()
        if func_link_with_ShapeKeysUtil.shapekey_util_is_found():
            box.label(text='AutoMerge - ShapeKey Utils')
            func_warning_slow_method.box_warning_slow_method(box)
            box.prop(self, "apply_modifiers_with_shapekeys")


def register():
    bpy.utils.register_class(addon_preferences)


def unregister():
    bpy.utils.unregister_class(addon_preferences)

