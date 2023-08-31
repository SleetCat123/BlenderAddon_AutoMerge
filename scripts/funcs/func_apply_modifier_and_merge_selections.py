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
import math
from .. import consts
from . import func_apply_modifiers
from .utils import func_object_utils


def apply_modifier_and_merge_selections(operator, context, apply_modifiers_with_shapekeys: bool, ignore_armature=False):
    mode_temp = None
    if bpy.context.object is not None:
        # 開始時のモードを記憶しオブジェクトモードに
        mode_temp = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='OBJECT')

    merged = func_object_utils.get_active_object()
    func_object_utils.select_object(merged, True)
    targets = bpy.context.selected_objects

    # リンクされたオブジェクトのモディファイアは適用できないので予めリンクを解除しておく
    bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, animation=False)

    for i, obj in enumerate(targets):
        if obj.type == 'CURVE' or obj.type == 'SURFACE' or obj.type == 'META' or obj.type == 'FONT':
            func_object_utils.deselect_all_objects()

            children = func_object_utils.get_children_objects(obj)
            func_object_utils.select_objects(children, True)
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
            func_object_utils.select_objects(children, False)

            func_object_utils.select_object(obj, True)
            func_object_utils.set_active_object(obj)

            matrix = obj.matrix_world.inverted()
            bpy.ops.object.convert(target='MESH')
            print("Converted: " + str(obj.type))

            func_object_utils.select_objects(children, True)
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
            # # Meshに変換した際、子オブジェクトの位置がずれるので修正をかける
            # children = get_children(obj)
            # for c in children:
            #     c.matrix_parent_inverse = matrix
        elif obj.type == 'EMPTY':
            func_object_utils.deselect_all_objects()
            func_object_utils.select_object(obj, True)
            func_object_utils.set_active_object(obj)

            bpy.ops.object.add(type='MESH')
            new_obj = bpy.context.object
            new_obj.matrix_world = obj.matrix_world.copy()
            new_obj.name = obj.name
            new_obj.data.name = obj.name
            new_obj.parent = obj.parent

            children = func_object_utils.get_children_objects(obj)
            func_object_utils.select_objects(children, True)
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
            # for c in children:
            #     c.parent = new_obj
            #     c.matrix_parent_inverse = new_obj.matrix_world.inverted()

            if merged == obj:
                merged = new_obj
            targets[i] = new_obj
            bpy.data.objects.remove(obj)

    func_object_utils.deselect_all_objects()
    func_object_utils.select_objects(targets, True)

    # 子オブジェクトをインスタンス化している場合
    instance_parent = []
    instance_sources = set()
    for obj in targets:
        if obj.instance_type and obj.instance_type != 'NONE':
            print(f"{obj.name} instance_type is {obj.instance_type}")
            children_recursive = func_object_utils.get_children_recursive([obj])
            children_recursive.remove(obj)
            instance_parent.append(obj)
            print(children_recursive)
            instance_sources = instance_sources | set(children_recursive)
            print(instance_sources)
    if instance_sources:
        print(f"instance_sources: \n{instance_sources}")
        bpy.ops.object.duplicates_make_real(use_base_parent=True, use_hierarchy=True)
        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False,
                                        animation=False)
        for obj in instance_parent:
            obj.data = bpy.data.meshes.new('new_mesh')
            if obj.modifiers:
                obj.modifiers.clear()
        for obj in instance_sources:
            print(f"remove: {obj}")
            bpy.data.objects.remove(obj)
    targets = bpy.context.selected_objects

    for obj in targets:
        if obj.type != 'MESH':
            continue
        func_object_utils.deselect_all_objects()
        func_object_utils.select_object(obj, True)
        func_object_utils.set_active_object(obj)
        # オブジェクトの種類がメッシュならモディファイアを適用
        b = func_apply_modifiers.apply_modifiers(operator=operator,
                                                 apply_modifiers_with_shapekeys=apply_modifiers_with_shapekeys)
        if not b:
            return False

    # オブジェクトを結合
    func_object_utils.deselect_all_objects()
    func_object_utils.select_object(merged, True)
    func_object_utils.set_active_object(merged)
    print(f"target: {merged}")
    if targets and len(targets) > 1:
        targets.sort(key=lambda x: x.name)
        print("------ Merge ------\n" + '\n'.join([f"{obj.name}   {obj}" for obj in targets]) + "\n-------------------")
        join_as_shape_meshes = []
        is_join_needed = False
        for obj in targets:
            if merged == obj:
                continue
            if obj.type != 'MESH':
                print(f"{obj} is not mesh")
                continue
            if obj.name.startswith(consts.JOIN_AS_SHAPEKEY_PREFIX):
                join_as_shape_meshes.append(obj)
                print(f"join as shape: {obj}")
                continue
            func_object_utils.select_object(obj, True)
            is_join_needed = True
            if obj.data.use_auto_smooth:
                # 子オブジェクトのuse_auto_smoothがtrueなら親のAutoSmoothを有効化
                merged.data.use_auto_smooth = True
                merged.data.auto_smooth_angle = math.pi
        if is_join_needed:
            bpy.ops.object.join()

        # JOIN_AS_SHAPEKEY_PREFIXで始まる名前のオブジェクトをJoin as shapeで結合する
        if join_as_shape_meshes:
            func_object_utils.select_objects(join_as_shape_meshes)
            bpy.ops.object.join_shapes()
            for obj in join_as_shape_meshes:
                # シェイプキー名からprefixを削除
                key_blocks = merged.data.shape_keys.key_blocks
                if obj.name in key_blocks:
                    new_name = obj.name[len(consts.JOIN_AS_SHAPEKEY_PREFIX):]
                    merged.data.shape_keys.key_blocks[obj.name].name = new_name
                    print(f"shapekey renamed: {obj.name} -> {new_name}")
                else:
                    print(f"!!! failed to rename shapekey: {obj.name}")
            func_object_utils.remove_objects(join_as_shape_meshes)

    if mode_temp is not None:
        # 開始時のモードを復元
        bpy.ops.object.mode_set(mode=mode_temp)
    print("completed")
    return True

