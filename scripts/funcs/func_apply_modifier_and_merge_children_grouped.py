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
from .utils import func_object_utils, func_collection_utils, func_custom_props_utils
from . import func_merge_children_recursive


def apply_modifier_and_merge_children_grouped(self,
                                              context,
                                              ignore_collection,
                                              ignore_prop_name,
                                              apply_modifiers_with_shapekeys: bool,
                                              duplicate: bool,
                                              remove_non_render_mod: bool):
    # 処理から除外するオブジェクトの選択を外す
    func_collection_utils.deselect_collection(ignore_collection)
    if ignore_prop_name:
        func_custom_props_utils.select_if_prop_is_true(prop_name=ignore_prop_name, select=False)

    print(
        "xxxxxx Targets xxxxxx\n" + '\n'.join([obj.name for obj in bpy.context.selected_objects]) + "\nxxxxxxxxxxxxxxx")

    # コレクションを取得
    collection = func_collection_utils.find_collection(consts.PARENTS_GROUP_NAME)
    if collection and collection.name not in bpy.context.scene.collection.children.keys():
        # コレクションをLinkする。
        # Unlink状態のコレクションでもPythonからは参照できてしまう場合があるようなので、確実にLink状態になるようにしておく
        bpy.context.scene.collection.children.link(collection)

    mode_temp = None
    if bpy.context.object is not None:
        # 開始時のモードを記憶しオブジェクトモードに
        mode_temp = bpy.context.object.mode
        if mode_temp != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

    dup_source_parents = []
    dup_result_parents = []

    targets = bpy.context.selected_objects

    # ------------------
    # 結合処理
    merge_group_objects = set()
    if collection:
        merge_group_objects = set(collection.objects)
    prop_true_objects =  set(func_custom_props_utils.get_objects_prop_is_true(consts.PARENTS_GROUP_NAME, targets=targets))
    merge_group_objects = merge_group_objects | prop_true_objects

    merge_targets = merge_group_objects & set(targets)
    # merge_targets=targets

    results = targets

    # 多重マージに対応
    is_parent_list = [False] * len(merge_targets)
    roots = set()  # 要素が重複することがないようにsetを使用する
    i = -1
    for obj in merge_targets:
        i += 1
        if is_parent_list[i]:
            # 既にルートではないことが確定しているオブジェクトは処理スキップ
            continue
        merge_root_parent = obj
        parent = obj
        # マージ対象のルートを取得
        while True:
            parent = parent.parent
            print(parent)
            if parent is None:
                print("root:" + merge_root_parent.name)
                roots.add(merge_root_parent)
                break
            if parent in merge_targets:
                print("parent:" + parent.name)
                merge_root_parent = parent
                is_parent_list[i] = True
    for merge_root_parent in roots:
        func_object_utils.deselect_all_objects()
        func_object_utils.select_object(merge_root_parent, True)
        func_object_utils.set_active_object(merge_root_parent)
        func_object_utils.select_children_recursive()

        # マージ対象オブジェクトをresultsから消しておく
        results = list(set(results) - set(bpy.context.selected_objects))

        # 処理から除外するオブジェクトの選択を外す
        func_collection_utils.deselect_collection(ignore_collection)

        if duplicate:
            dup_source_parents.append(merge_root_parent)
            # 対象オブジェクトを複製
            func_object_utils.duplicate_object()
            print("dup:" + merge_root_parent.name)

        # 子を再帰的にマージ
        b = func_merge_children_recursive.merge_children_recursive(
            operator=self,
            context=context,
            apply_modifiers_with_shapekeys=apply_modifiers_with_shapekeys,
            remove_non_render_mod=remove_non_render_mod,
            )
        if not b:
            # 処理に失敗したら中断
            print(f"!!! merge_children_recursive was failed")
            return False

        dup_result_parents.extend(bpy.context.selected_objects)
    results.extend(dup_result_parents)
    # ------------------

    # 選択を復元
    func_object_utils.deselect_all_objects()
    func_object_utils.select_objects(results, True)

    if mode_temp is not None:
        # 開始時のモードを復元
        if mode_temp != 'OBJECT':
            bpy.ops.object.mode_set(mode=mode_temp)

    # layer_col.exclude = True

    return dup_source_parents, dup_result_parents
