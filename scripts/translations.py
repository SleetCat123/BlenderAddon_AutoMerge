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
from . import consts, func_package_utils
from .consts import DESC
from .operator_merge_selections import OBJECT_OT_specials_merge_selections as merge_selections
from .operator_merge_children import OBJECT_OT_specials_merge_children as merge_children
from .operator_merge_children_grouped import OBJECT_OT_specials_merge_children_grouped as merge_children_grouped
from .operator_assign_merge_group import OBJECT_OT_specials_assign_merge_group as assing_merge_group


translations_dict = {
    "en_US": {
        ("*", "box_warning_slow_method_1"): "Warning: ",
        ("*", "box_warning_slow_method_2"): "If using the settings below,",
        ("*", "box_warning_slow_method_3"): "some functions may take a while in this add-on.",
        ("*", "box_warning_read_pref_1"): "You can change a setting below",
        ("*", "box_warning_read_pref_2"): " in this add-on preference.",
        ("*", "box_warning_read_pref_3"): "",

        ("*", merge_selections.bl_idname + DESC): "Merge selected objects into the active object",

        ("*", merge_children.bl_idname + DESC): "Merge child objects into parent objects",

        ("*", merge_children_grouped.bl_idname + DESC):
            f"Merge child objects of selected objects assigned to the \"{consts.PARENTS_GROUP_NAME}\" collection",

        ("*", consts.KEY_IGNORE_ARMATURE): "Keep Armature modifier",
        ("*", consts.KEY_DUPLICATE): "Processing on duplicated objects",
    },
    "ja_JP": {
        ("*", "box_warning_slow_method_1"): "注意：",
        ("*", "box_warning_slow_method_2"): "以下の項目を有効にすると",
        ("*", "box_warning_slow_method_3"): "処理に時間がかかる場合があります。",
        ("*", "box_warning_read_pref_1"): "以下の項目は",
        ("*", "box_warning_read_pref_2"): "Preference画面から設定できます。",
        ("*", "box_warning_read_pref_3"): "（アドオン同梱の画像参照）",

        ("*", merge_selections.bl_idname + DESC): "最後に選択したオブジェクトに対し、\n他の選択中オブジェクトをマージします",

        ("*", merge_children.bl_idname + DESC): "オブジェクトの子オブジェクトをマージします",

        ("*", merge_children_grouped.bl_idname + DESC):
            "選択中のオブジェクトのうち、\n"
            f"\"{consts.PARENTS_GROUP_NAME}\"コレクションに属するものに対し、それぞれ子階層以下にあるオブジェクトをマージします",

        ("*", assing_merge_group.bl_idname + DESC):
            "選択中のオブジェクトを\nオブジェクトグループ“" + consts.PARENTS_GROUP_NAME + "”に入れたり外したりします",
        ("*", assing_merge_group.bl_idname + "assign"):
            "選択中のオブジェクトを\nオブジェクトグループ“" + consts.PARENTS_GROUP_NAME + "”に追加",

        ("*", consts.KEY_IGNORE_ARMATURE): "アーマチュアモディファイアを残す",
        ("*", consts.KEY_DUPLICATE): "オブジェクトを複製して処理を行う",
    },
}


def register():
    bpy.app.translations.register(func_package_utils.get_package_root(), translations_dict)


def unregister():
    bpy.app.translations.unregister(func_package_utils.get_package_root())
