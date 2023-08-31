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
from ..funcs.utils import func_collection_utils


# 選択オブジェクトをMergeGroupグループに入れたり外したりするクラス
class OBJECT_OT_specials_assign_merge_group(bpy.types.Operator):
    bl_idname = "object.automerge_assign_merge_group"
    bl_label = "Assign Merge Group"
    bl_description = bpy.app.translations.pgettext(bl_idname + consts.DESC)
    bl_options = {'REGISTER', 'UNDO'}

    assign: bpy.props.BoolProperty(name="Assign", default=True)

    def execute(self, context):
        func_collection_utils.assign_object_group(group_name=consts.PARENTS_GROUP_NAME, assign=self.assign)
        # exclude_collection(context=context, group_name=PARENTS_GROUP_NAME, exclude=True)
        func_collection_utils.hide_collection(context=context, group_name=consts.PARENTS_GROUP_NAME, hide=True)
        return {'FINISHED'}


class OBJECT_OT_specials_assign_dont_merge_to_parent_group(bpy.types.Operator):
    bl_idname = "object.automerge_assign_dont_merge_to_parent_group"
    bl_label = "Assign Don't Merge To Parent Group"
    bl_description = bpy.app.translations.pgettext(bl_idname + consts.DESC)
    bl_options = {'REGISTER', 'UNDO'}

    assign: bpy.props.BoolProperty(name="Assign", default=True)

    def execute(self, context):
        func_collection_utils.assign_object_group(group_name=consts.DONT_MERGE_TO_PARENT_GROUP_NAME, assign=self.assign)
        func_collection_utils.hide_collection(context=context, group_name=consts.DONT_MERGE_TO_PARENT_GROUP_NAME, hide=True)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(OBJECT_OT_specials_assign_merge_group)
    bpy.utils.register_class(OBJECT_OT_specials_assign_dont_merge_to_parent_group)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_specials_assign_merge_group)
    bpy.utils.unregister_class(OBJECT_OT_specials_assign_dont_merge_to_parent_group)
