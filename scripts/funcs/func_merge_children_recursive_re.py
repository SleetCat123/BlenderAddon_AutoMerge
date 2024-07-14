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
from .func_apply_modifier_and_merge_selections import apply_modifier_and_merge_selections
from .utils import func_object_utils, func_custom_props_utils


class Settings:
    apply_modifiers_with_shapekeys: bool
    remove_non_render_mod: bool
    ignore_dont_merge_to_parent_group: bool # DONT_MERGE_TO_PARENT_GROUP_NAMEに属するオブジェクトを無視する

    def __init__(self):
        self.apply_modifiers_with_shapekeys = True
        self.remove_non_render_mod = True
        self.ignore_dont_merge_to_parent_group = True


def merge_children_recursive(operator, settings: Settings):
    target = func_object_utils.get_active_object()
    func_object_utils.deselect_all_objects()
    children = func_object_utils.get_children_objects(target)
    merge_children = []
    for child in children:
        func_object_utils.set_active_object(child)
        name = child.name
        merge_children_recursive(
            operator=operator,
            settings=settings
        )
        # 再帰処理後に子オブジェクトが変化している可能性があるため再取得
        child_obj = bpy.data.objects[name]
        if settings.ignore_dont_merge_to_parent_group and func_custom_props_utils.prop_is_true(child_obj, consts.DONT_MERGE_TO_PARENT_GROUP_NAME):
            print(f"Don't merge: {child_obj}")
        else:
            merge_children.append(child_obj)

    print("")
    print(f"merge_children_recursive: {target}")
    func_object_utils.deselect_all_objects()
    func_object_utils.set_active_object(target)
    func_object_utils.select_objects(merge_children, True)
    # オブジェクトをマージする
    apply_modifier_and_merge_selections(
        operator=operator,
        context=None,
        apply_modifiers_with_shapekeys=settings.apply_modifiers_with_shapekeys,
        remove_non_render_mod=settings.remove_non_render_mod
    )
    