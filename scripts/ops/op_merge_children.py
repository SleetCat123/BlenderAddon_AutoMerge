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
import traceback
from bpy.props import BoolProperty
from .. import consts
from ..link import func_link_with_ShapeKeysUtil
from ..funcs import func_merge_children_recursive, func_merge_children_main
from ..funcs import func_warning_slow_method
from ..funcs.utils import func_package_utils


class OBJECT_OT_specials_merge_children(bpy.types.Operator):
    bl_idname = "object.automerge_apply_modifier_and_merge_children"
    bl_label = "Merge Children"
    bl_description = "Merge child objects into parent objects"
    bl_options = {'REGISTER', 'UNDO'}

    ignore_dont_merge_to_parent_group: BoolProperty(
        name=f"Ignore \"{consts.DONT_MERGE_TO_PARENT_GROUP_NAME}\"",
        default=True,
        description=f"Ignore objects assigned the property \"{consts.DONT_MERGE_TO_PARENT_GROUP_NAME}\""
    )

    use_variants_merge: BoolProperty(
        name="Use Variant Merge",
        default=True,
        description="Use variants merge"
    )

    remove_non_render_mod: BoolProperty(
        name="Remove Non-Render Modifiers",
        default=True,
        description="A non-render modifier will be removed."
    )

    reparent_if_object_hidden: BoolProperty(
        name="Reparent If Object Hidden",
        default=True,
        description="Reparent if the parent object is hidden"
    )

    only_grouped: BoolProperty(
        name=f"Only Grouped {consts.PARENTS_GROUP_NAME}",
        default=False,
        description=f"Only merge objects assigned the property \"{consts.PARENTS_GROUP_NAME}\""
    )

    root_is_selected: BoolProperty(
        name="Selected Only",
        default=False,
        description="Only merge objects selected"
    )

    restore_selection: BoolProperty(
        name="Restore Selection",
        default=False,
        description="Restore the selection after merging"
    )


    @classmethod
    def poll(cls, context):
        return bpy.context.selected_objects

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "use_variants_merge")
        layout.prop(self, "reparent_if_object_hidden")
        layout.prop(self, "remove_non_render_mod")
        layout.prop(self, "ignore_dont_merge_to_parent_group")
        layout.prop(self, "restore_selection")

        layout.separator()
        layout.prop(self, "only_grouped")
        row = layout.row()
        row.enabled = self.only_grouped
        row.prop(self, "root_is_selected")

        if func_link_with_ShapeKeysUtil.shapekey_util_is_found():
            layout.separator()
            box = layout.box()
            func_warning_slow_method.shapekey_util_label(box)
            func_warning_slow_method.box_warning_slow_method(box)
            func_warning_slow_method.box_warning_read_pref(box)
            col = box.column()
            col.enabled = False
            addon_prefs = func_package_utils.get_addon_prefs()
            col.prop(addon_prefs, "apply_modifiers_with_shapekeys")

    def execute(self, context):
        try:
            addon_prefs = func_package_utils.get_addon_prefs()
            settings_1 = func_merge_children_recursive.Settings()
            settings_1.use_shapekeys_util = addon_prefs.apply_modifiers_with_shapekeys
            settings_1.remove_non_render_mod = self.remove_non_render_mod
            settings_1.ignore_dont_merge_to_parent_group = self.ignore_dont_merge_to_parent_group
            settings_1.reparent_if_object_hidden = self.reparent_if_object_hidden
            settings_2 = func_merge_children_main.Settings()
            settings_2.use_variants_merge = self.use_variants_merge
            settings_2.only_grouped = self.only_grouped
            settings_2.root_is_selected = self.root_is_selected
            settings_2.restore_selection = self.restore_selection
            func_merge_children_main.merge_children_main(
                operator=self,
                settings_1=settings_1,
                settings_2=settings_2
            )
            return {'FINISHED'}
        except Exception as e:
            bpy.ops.ed.undo_push(message = "Restore point")
            bpy.ops.ed.undo()
            bpy.ops.ed.undo_push(message = "Restore point")
            traceback.print_exc()
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}


translations_dict = {
    "ja_JP": {
        ("*", "Merge child objects into parent objects"): "オブジェクトの子オブジェクトをマージします",
        ("*", f"Ignore \"{consts.DONT_MERGE_TO_PARENT_GROUP_NAME}\""): f"「{consts.DONT_MERGE_TO_PARENT_GROUP_NAME}」を無視",
        ("*", f"Ignore objects assigned the property \"{consts.DONT_MERGE_TO_PARENT_GROUP_NAME}\""): f"「{consts.DONT_MERGE_TO_PARENT_GROUP_NAME}」を無視",
        ("*", "Use Variant Merge"): "バリアントマージを使用",
        ("*", "Use variants merge"): "バリアントマージを使用",
        ("*", "Remove Non-Render Modifiers"): "レンダリング無効モディファイアを削除",
        ("*", "A non-render modifier will be removed."): "レンダリング対象外のモディファイアを削除します",
        ("*", "Reparent If Object Hidden"): "親子関係の再設定",
        ("*", "Reparent if the parent object is hidden"): "親オブジェクトが非表示の場合、オブジェクトの親を変更します",
        ("*", f"Only Grouped {consts.PARENTS_GROUP_NAME}"): f"{consts.PARENTS_GROUP_NAME}が有効なオブジェクトのみ",
        ("*", f"Only merge objects assigned the property \"{consts.PARENTS_GROUP_NAME}\""): f"「{consts.PARENTS_GROUP_NAME}」が有効なオブジェクトだけをマージ処理の対象とします",
        ("*", "Selected Only"): "選択中のみ",
        ("*", "Only merge objects selected"): "選択中のオブジェクトのみをマージ処理の対象とします",
        ("*", "Restore Selection"): "選択を復元",
        ("*", "Restore the selection after merging"): "処理の終了後にオブジェクトの選択状態を復元します",
    },
}

def register():
    bpy.utils.register_class(OBJECT_OT_specials_merge_children)
    bpy.app.translations.register(__name__, translations_dict)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_specials_merge_children)
    bpy.app.translations.unregister(__name__)