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
from . import func_package_utils


def select_object(obj, value=True):
    obj.select_set(value)


def select_objects(objects, value=True):
    for obj in objects:
        select_object(obj, value)


def get_active_object():
    return bpy.context.view_layer.objects.active


def set_active_object(obj):
    # try:
    bpy.context.view_layer.objects.active = obj
    # except ReferenceError:
    #    print("removed")


def get_children_objects(obj, only_current_view_layer: bool = True):
    all_objects = bpy.data.objects
    if only_current_view_layer:
        current_layer_objects = bpy.context.window.view_layer.objects
        return [child for child in all_objects if
                child.parent == obj and child in current_layer_objects]
    else:
        return [child for child in all_objects if child.parent == obj]


def select_children_recursive(targets=None):
    def recursive(t):
        select_object(t, True)
        children = get_children_objects(t)
        for child in children:
            recursive(child)

    if targets is None:
        targets = bpy.context.selected_objects
    for obj in targets:
        recursive(obj)


def deselect_all_objects():
    targets = bpy.context.selected_objects
    for obj in targets:
        select_object(obj, False)
    # bpy.context.view_layer.objects.active = None


def get_addon_prefs():
    return bpy.context.preferences.addons[func_package_utils.get_package_root()].preferences

