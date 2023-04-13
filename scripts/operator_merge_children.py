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
from . import consts, func_object_utils, func_ui_utils, func_merge_children_recursive, link_with_ShapeKeysUtil


class OBJECT_OT_specials_merge_children(bpy.types.Operator):
    bl_idname = "object.automerge_apply_modifier_and_merge_children"
    bl_label = "Merge Children"
    bl_description = bpy.app.translations.pgettext(bl_idname + consts.DESC)
    bl_options = {'REGISTER', 'UNDO'}

    duplicate: BoolProperty(name="Duplicate", default=False,
                            description=bpy.app.translations.pgettext(consts.KEY_DUPLICATE))
    ignore_armature: BoolProperty(name="Ignore Armature", default=True,
                                  description=bpy.app.translations.pgettext(consts.KEY_IGNORE_ARMATURE))

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "duplicate")
        layout.prop(self, "ignore_armature")
        if link_with_ShapeKeysUtil.shapekey_util_is_found():
            layout.separator()
            box = layout.box()
            func_ui_utils.shapekey_util_label(box)
            func_ui_utils.box_warning_slow_method(box)
            func_ui_utils.box_warning_read_pref(box)
            col = box.column()
            col.enabled = False
            addon_prefs = func_object_utils.get_addon_prefs()
            col.prop(addon_prefs, "apply_modifiers_with_shapekeys")

    def execute(self, context):
        print("apply_modifier_and_merge_children")

        # rootを取得
        root_objects = func_object_utils.get_selected_root_objects()

        # 結合処理
        addon_prefs = func_object_utils.get_addon_prefs()
        result = []
        for obj in root_objects:
            func_object_utils.deselect_all_objects()
            func_object_utils.set_active_object(obj)
            if self.duplicate:
                # 対象オブジェクトを複製
                children_recursive = func_object_utils.get_children_recursive([obj])
                func_object_utils.select_objects(children_recursive, True)
                bpy.ops.object.duplicate()

            b = func_merge_children_recursive.merge_children_recursive(
                operator=self,
                context=context,
                apply_modifiers_with_shapekeys=addon_prefs.apply_modifiers_with_shapekeys,
                ignore_armature=self.ignore_armature)
            result.append(func_object_utils.get_active_object())
            if not b:
                return {'CANCELLED'}

        func_object_utils.select_objects(result, True)
        print("finished")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(OBJECT_OT_specials_merge_children)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_specials_merge_children)
