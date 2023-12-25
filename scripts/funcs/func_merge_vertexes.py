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
from .. import consts
from ..funcs.utils import func_object_utils


def merge_vertexes(objects, threshold: float = 0.0001, remove_merged_group: bool = True):
    temp_active_obj = func_object_utils.get_active_object()
    for obj in objects:
        if obj.type != 'MESH':
            continue
        # 対象となる頂点グループの一覧を取得
        target_groups = []
        for group in obj.vertex_groups:
            if group.name.startswith(consts.MERGE_VERTEX_GROUP_PREFIX):
                target_groups.append(group)
        if not target_groups:
            continue
        func_object_utils.set_active_object(obj)
        temp_mode = obj.mode
        bpy.ops.object.mode_set(mode='EDIT')
        verts = obj.data.vertices
        # 頂点グループごとに処理
        for group in target_groups:
            print("Merge Vertexes: [" + obj.name + "] - [" + group.name + "]")
            # 頂点の選択を解除
            for vert in verts:
                if vert.select:
                    vert.select = False
            # 頂点グループの値が1.0の頂点を選択
            for vert in verts:
                for vgroup in vert.groups:
                    if vgroup.group == group.index and vgroup.weight == 1.0:
                        vert.select = True
                        break
            bpy.ops.mesh.remove_doubles(threshold=threshold)
            if remove_merged_group:
                # 頂点グループを削除
                obj.vertex_groups.remove(group)
        bpy.ops.object.mode_set(mode=temp_mode)
    func_object_utils.set_active_object(temp_active_obj)