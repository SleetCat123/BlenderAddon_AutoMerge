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
from ..variants import variants_prop
from ..funcs import func_merge_children_recursive
from ..funcs.utils import func_object_utils, func_custom_props_utils


class Settings:
    use_variants_merge: bool
    only_grouped: bool
    root_is_selected: bool
    restore_selection: bool
    reparent_if_object_hidden: bool

    def __init__(self):
        self.use_variants_merge = False
        self.only_grouped = False
        self.root_is_selected = False
        self.restore_selection = False
        self.reparent_if_object_hidden = True


def merge_children_main(operator, settings_1: func_merge_children_recursive.Settings, settings_2: Settings):
    print("start merge_children_main")

    print(f"use_shapekeys_util: {settings_1.use_shapekeys_util}")
    print(f"remove_non_render_mod: {settings_1.remove_non_render_mod}")
    print(f"ignore_dont_merge_to_parent_group: {settings_1.ignore_dont_merge_to_parent_group}")

    print(f"use_variants_merge: {settings_2.use_variants_merge}")
    print(f"only_grouped: {settings_2.only_grouped}")
    print(f"root_is_selected: {settings_2.root_is_selected}")
    print(f"restore_selection: {settings_2.restore_selection}")
    print(f"reparent_if_object_hidden: {settings_2.reparent_if_object_hidden}")

    if settings_2.restore_selection:
        selected_objects_names = [obj.name for obj in bpy.context.selected_objects]
    else:
        selected_objects_names = []

    # rootを取得
    if settings_2.only_grouped:
        root_objects = func_custom_props_utils.get_prop_root_objects(
            prop_name=consts.PARENTS_GROUP_NAME,
            targets=bpy.context.selected_objects
        )
        if settings_2.root_is_selected:
            root_objects = list(set(root_objects) & set(bpy.context.selected_objects))
    else:
        root_objects = func_object_utils.get_selected_root_objects()
    root_objects_names = []
    for root in root_objects:
        if func_object_utils.is_hidden(root):
            continue
        variant_names = variants_prop.get_all_variant_names_in_children(root)
        if settings_2.use_variants_merge and variant_names:
            variants_count = len(variant_names)
            print(f"{root.name} has {variants_count} variants")
            # variantの数だけオブジェクトと子階層を複製して結合
            for i, variant_name in enumerate(variant_names):
                print(f"variant: {variant_name}")
                settings_1.variants_name = variant_name
                if i == variants_count - 1:
                    # 最後の要素は元のオブジェクトを使用
                    root.name = root.name + "_" + variant_name
                    root_objects_names.append(root.name)
                    func_merge_children_recursive.merge_children_recursive(
                        operator=operator,
                        settings=settings_1,
                        target=root
                    )
                else:
                    # ルートと子階層を複製
                    children = func_object_utils.get_children_recursive(root)
                    func_object_utils.duplicate_objects(children)
                    root_copy = func_object_utils.get_active_object()
                    root_copy.name = root.name + "_" + variant_name
                    root_objects_names.append(root_copy.name)
                    func_merge_children_recursive.merge_children_recursive(
                        operator=operator,
                        settings=settings_1,
                        target=root_copy
                    )
        else:
            root_objects_names.append(root.name)
            func_merge_children_recursive.merge_children_recursive(
                operator=operator,
                settings=settings_1,
                target=root
            )
    for root_name in root_objects_names:
        root = bpy.data.objects.get(root_name)
        func_object_utils.select_children_recursive(root)
    if settings_2.restore_selection:
        for name in selected_objects_names:
            if name in bpy.data.objects:
                bpy.data.objects[name].select_set(True)
    print("end merge_children_main")
