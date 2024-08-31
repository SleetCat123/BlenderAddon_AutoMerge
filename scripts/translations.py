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
from . import consts

translations_dict = {
    "en_US": {
        ("*", "error_join_as_shape_verts_count_difference"): "Join As Shape (" + consts.JOIN_AS_SHAPEKEY_PREFIX + "): Could not execute the process because the number of vertices is different.\n{obj_1} (verts: {obj_verts_1}), {obj_2} (verts: {obj_verts_2})",

        ("*", "mizore_error_apply_as_shapekey_invalid_modifier"): "Apply As Shape: Could not execute the process because the modifier type is not supported or the modifier settings are invalid.\nObject: {obj_name}\nModifier: {modifier_name}({modifier_type})"
    },
    "ja_JP": {
        ("*", "error_join_as_shape_verts_count_difference"):
            "Join As Shape (" + consts.JOIN_AS_SHAPEKEY_PREFIX + "): 頂点数が異なっているため、処理を実行できませんでした。\n{obj_1} (頂点数: {obj_verts_1}), {obj_2} (頂点数: {obj_verts_2})",

        ("*", "mizore_error_apply_as_shapekey_invalid_modifier"): "Apply As Shape: モディファイアの種類が非対応またはモディファイアの設定内容に問題があるため、処理を実行できませんでした。\nオブジェクト: {obj_name}\nモディファイア: {modifier_name}({modifier_type})"
    },
}


def register():
    bpy.app.translations.register(__name__, translations_dict)


def unregister():
    bpy.app.translations.unregister(__name__)