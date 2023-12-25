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


PARENTS_GROUP_NAME = "MergeGroup"  # マージ先となるオブジェクトが属するグループの名前
DONT_MERGE_TO_PARENT_GROUP_NAME = "DontMergeToParent"  # このグループに属するオブジェクトが他オブジェクトにマージされることはない（Merge Selectionの場合はマージされる）
APPLY_AS_SHAPEKEY_NAME = "%AS%"  # モディファイア名が%AS%で始まっているならApply as shapekey
FORCE_APPLY_MODIFIER_PREFIX = "%A%"  # モディファイア名が"%A%"で始まっているならArmatureなどの対象外モディファイアでも強制的に適用
FORCE_KEEP_MODIFIER_PREFIX = "%KEEP%"  # モディファイア名が"%KEEP%"で始まっているならモディファイアを適用せずに処理を続行する
JOIN_AS_SHAPEKEY_PREFIX = "%SHAPE%"  # オブジェクト名が"%SHAPE%"で始まっているならそのオブジェクトをJoin as shapeで結合する
MERGE_VERTEX_GROUP_PREFIX = "%M%"  # 頂点グループ名が"%M%"で始まっているならマージ対象の頂点グループとみなす

DESC = ".desc"
KEY_REMOVE_NON_RENDER_MOD = "automerge_remove_non_render_modifiers"
KEY_DUPLICATE = "duplicate"


def register():
    bpy.types.WindowManager.mizore_automerge_collection_name = PARENTS_GROUP_NAME
    bpy.types.WindowManager.mizore_automerge_dont_merge_to_parent_collection_name = DONT_MERGE_TO_PARENT_GROUP_NAME


def unregister():
    del bpy.types.WindowManager.mizore_automerge_collection_name
    del bpy.types.WindowManager.mizore_automerge_dont_merge_to_parent_collection_name
