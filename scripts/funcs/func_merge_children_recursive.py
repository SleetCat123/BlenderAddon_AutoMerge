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
from .. variants import variants_prop
from .utils import func_object_utils, func_custom_props_utils


class Settings:
    use_shapekeys_util: bool
    remove_non_render_mod: bool
    ignore_dont_merge_to_parent_group: bool # DONT_MERGE_TO_PARENT_GROUP_NAMEに属するオブジェクトを無視する
    variants_name: str

    def __init__(self):
        self.use_shapekeys_util = True
        self.remove_non_render_mod = True
        self.ignore_dont_merge_to_parent_group = True
        self.variants_name = ""


def merge_children_recursive(operator, settings: Settings, target: bpy.types.Object):
    func_object_utils.deselect_all_objects()
    children = func_object_utils.get_children_objects(target)
    merge_children = []
    for child in children:
        name = child.name
        if settings.variants_name:
            # Variants
            prop = variants_prop.get_variants_list(child)
            if prop and prop.variants_list:
                # 要素がある場合のみ判定
                if settings.variants_name not in prop.variants_list:
                    # Variants名が一致しない場合はオブジェクトを削除
                    func_object_utils.remove_object(child)
                    continue

        merge_children_recursive(
            operator=operator,
            settings=settings,
            target=child
        )
        # 再帰処理後に子オブジェクトが変化している可能性があるため再取得
        child_obj = bpy.data.objects[name]
        if settings.ignore_dont_merge_to_parent_group and func_custom_props_utils.prop_is_true(child_obj, consts.DONT_MERGE_TO_PARENT_GROUP_NAME):
            print(f"Don't merge: {child_obj}")
        else:
            merge_children.append(child_obj)

    if func_object_utils.is_hidden(target):
        # オブジェクトが非表示の場合はマージしない
        return
    
    print("")
    print(f"merge_children_recursive: {target}")
    if settings.variants_name:
        print(f"variants_name: {settings.variants_name}")
    func_object_utils.deselect_all_objects()
    func_object_utils.set_active_object(target)
    func_object_utils.select_objects(merge_children, True)
    # オブジェクトをマージする
    apply_modifier_and_merge_selections(
        operator=operator,
        use_shapekeys_util=settings.use_shapekeys_util,
        remove_non_render_mod=settings.remove_non_render_mod
    )
    