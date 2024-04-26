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
from . import func_merge_vertexes
from .utils import func_object_utils, func_collection_utils, func_custom_props_utils


def merge_children_recursive(operator, context, apply_modifiers_with_shapekeys: bool, remove_non_render_mod: bool):
    print("")
    print("merge_children_recursive")
    obj = func_object_utils.get_active_object()
    # obj.hide_set(False)
    if obj.hide_get():
        return True

    merge_target_collection = func_collection_utils.find_collection(consts.PARENTS_GROUP_NAME)
    dont_merge_collection = func_collection_utils.find_collection(consts.DONT_MERGE_TO_PARENT_GROUP_NAME)
    dont_merge_objects = set(func_custom_props_utils.get_objects_prop_is_true(consts.DONT_MERGE_TO_PARENT_GROUP_NAME))
    if dont_merge_collection:
        dont_merge_objects = dont_merge_objects | set(dont_merge_collection.objects)

    children = func_object_utils.get_children_objects(obj)
    for child in children:
        # print("call:"+child.name)
        func_object_utils.set_active_object(child)
        b = merge_children_recursive(operator=operator,
                                     context=context,
                                     apply_modifiers_with_shapekeys=apply_modifiers_with_shapekeys,
                                     remove_non_render_mod=remove_non_render_mod)
        if not b:
            # 処理に失敗したら中断
            print("!!! Failed - merge_children_recursive A")
            return False
    # EMPTYをメッシュに変換した場合など、オブジェクトが消えていることがあるため再取得
    children = func_object_utils.get_children_objects(obj)

    target_children = []
    variants = []
    for child in children:
        if child in dont_merge_objects:
            print(f"ignore: {child}")
        else:
            target_children.append(child)
            if child.name.startswith(consts.MULTIPLE_VARIANTS_PREFIX):
                variants.append(child)
    b = True
    results = []
    if variants and len(variants) > 1:
        print("variants: " + str(variants))
        for i, variant in enumerate(variants):
            print("variant: " + variant.name)
            func_object_utils.deselect_all_objects()
            func_object_utils.select_objects(target_children, True)
            func_object_utils.select_objects(variants, False)
            func_object_utils.select_object(variant, True)
            func_object_utils.select_object(obj, True)
            func_object_utils.set_active_object(obj)
            dup_targets = func_object_utils.duplicate_object()
            dup_obj = func_object_utils.get_active_object()
            dup_obj.name = variant.name[len(consts.MULTIPLE_VARIANTS_PREFIX):]
            dup_targets.remove(dup_obj)
            print("! merge to:" + dup_obj.name)
            print("children: " + str(dup_targets))
            print(str(bpy.context.selected_objects))
            b = apply_modifier_and_merge_selections(
                operator=operator,
                context=context,
                apply_modifiers_with_shapekeys=apply_modifiers_with_shapekeys,
                remove_non_render_mod=remove_non_render_mod
            )
            func_merge_vertexes.merge_vertexes(
                objects=[dup_obj],
                threshold=0.0001,
                remove_merged_group=False,
            )
            results.extend(func_object_utils.get_children_objects(dup_obj))
            results.append(dup_obj)
            if not b:
                print("!!! Failed - merge_children_recursive B  " + variant.name)
                break
        # オリジナルを削除
        func_object_utils.remove_object(obj)
        func_object_utils.remove_objects(target_children)
    else:
        func_object_utils.deselect_all_objects()
        func_object_utils.select_objects(target_children, True)
        func_object_utils.select_object(obj, True)
        func_object_utils.set_active_object(obj)
        print("! merge to:" + obj.name)
        print("children: " + str(children))
        print(str(bpy.context.selected_objects))
        b = apply_modifier_and_merge_selections(
            operator=operator,
            context=context,
            apply_modifiers_with_shapekeys=apply_modifiers_with_shapekeys,
            remove_non_render_mod=remove_non_render_mod
        )
        if not b:
            print("!!! Failed - merge_children_recursive B")

        func_merge_vertexes.merge_vertexes(
            objects=[obj],
            threshold=0.0001,
            remove_merged_group=False,
        )
        results.extend(func_object_utils.get_children_objects(obj))

    func_object_utils.select_objects(results, True)
    print("result: " + str(results))
    print("")
    return b

