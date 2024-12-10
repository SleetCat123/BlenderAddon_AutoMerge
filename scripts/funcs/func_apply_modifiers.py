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
from .utils import func_object_utils


def apply_modifiers(operator, use_shapekeys_util: bool, remove_non_render_mod: bool):
    obj = func_object_utils.get_active_object()
    print(f"Start Apply Modifiers: {obj.name}")
    # オブジェクトのモディファイアを適用
    if use_shapekeys_util:
        print(f"{obj.name} has shapekey ({len(obj.data.shape_keys.key_blocks)})")
        # オブジェクトにシェイプキーがあったら
        try:
            # ShapeKeysUtil連携
            # ShapeKeysUtilが導入されていたらシェイプキーつきオブジェクトでもモディファイア適用
            print("func_apply_modifiers -> shapekeys_util_apply_mod_with_shapekeys_automerge")
            bpy.ops.object.shapekeys_util_apply_mod_with_shapekeys_automerge()
        except AttributeError:
            obj.modifiers.clear()
            t = "!!! Failed to load ShapeKeysUtil !!! - on apply modifier"
            print(t)
            operator.report({'ERROR'}, t)
    else:
        if obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) != 0:
            # シェイプキーがある場合はモディファイアを適用せずにスキップ
            obj.modifiers.clear()
            operator.report({'INFO'}, "[" + obj.name + "] has shape key. apply modifier was skipped.")
            return True
        
        for modifier in obj.modifiers:
            if modifier.name.startswith(consts.FORCE_KEEP_MODIFIER_PREFIX):
                # モディファイア名がFORCE_KEEP_MODIFIER_PREFIXで始まっているなら無視
                print(f"Force Keep: [{modifier.name}]")
                continue
            if not modifier.show_render:
                # モディファイアがレンダリング対象ではない（モディファイア一覧のカメラアイコンが押されていない）なら無視
                if remove_non_render_mod:
                    print(f"Remove Non Render: [{modifier.name}]")
                    bpy.ops.object.modifier_remove(modifier=modifier.name)
                continue
            if modifier.name.startswith(consts.FORCE_APPLY_MODIFIER_PREFIX) or modifier.type != 'ARMATURE':
                # モディファイアが処理対象モディファイアなら
                # または、モディファイアの名前欄が%A%で始まっているなら
                try:
                    bpy.ops.object.modifier_apply(modifier=modifier.name)
                    try:
                        # なんかここだけUnicodeEncodeErrorが出たり出なかったりするので対策
                        print(f"Apply: [{modifier.name}]")
                    except UnicodeDecodeError:
                        print("Apply: ?")
                except RuntimeError:
                    # 無効なModifier（対象オブジェクトが指定されていないなどの状態）は適用しない
                    print(f"!!! Apply failed !!!: [{modifier.name}]")
                    bpy.ops.object.modifier_remove(modifier=modifier.name)
    return True

