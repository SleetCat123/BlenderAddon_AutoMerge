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

from . import func_object_utils, func_apply_modifier_and_merge_selections


def merge_children_recursive(operator, context, apply_modifiers_with_shapekeys: bool, ignore_armature=True):
    obj = func_object_utils.get_active_object()
    # obj.hide_set(False)
    if obj.hide_get():
        return True

    children = func_object_utils.get_children_objects(obj)
    for child in children:
        # print("call:"+child.name)
        func_object_utils.set_active_object(child)
        b = merge_children_recursive(operator=operator,
                                     context=context,
                                     apply_modifiers_with_shapekeys=apply_modifiers_with_shapekeys,
                                     ignore_armature=ignore_armature)
        if not b:
            # 処理に失敗したら中断
            print("!!! Failed - merge_children_recursive A")
            return False
    # EMPTYをメッシュに変換した場合など、オブジェクトが消えていることがあるため再取得
    children = func_object_utils.get_children_objects(obj)

    func_object_utils.deselect_all_objects()
    func_object_utils.select_objects(children, True)
    func_object_utils.select_object(obj, True)
    func_object_utils.set_active_object(obj)
    print("merge:" + obj.name)
    b = func_apply_modifier_and_merge_selections.apply_modifier_and_merge_selections(operator, context, apply_modifiers_with_shapekeys, ignore_armature)
    if not b:
        print("!!! Failed - merge_children_recursive B")
    return b

