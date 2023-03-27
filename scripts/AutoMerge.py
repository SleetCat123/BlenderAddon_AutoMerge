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
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty, CollectionProperty
from . import consts, func_package_utils, func_object_utils, func_collection_utils
from . import func_apply_modifiers, func_apply_modifier_and_merge_children_grouped


### region Func ###


def merge_children_recursive(operator,
                             context,
                             apply_modifiers_with_shapekeys: bool,
                             ignore_armature=True,
                             ):
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
    b = apply_modifier_and_merge_selections(operator, context, apply_modifiers_with_shapekeys, ignore_armature)
    if not b:
        print("!!! Failed - merge_children_recursive B")
    return b


def apply_modifier_and_merge_selections(operator, context, apply_modifiers_with_shapekeys: bool, ignore_armature=False):
    mode_temp = None
    if bpy.context.object is not None:
        # 開始時のモードを記憶しオブジェクトモードに
        mode_temp = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='OBJECT')

    merged = func_object_utils.get_active_object()
    func_object_utils.select_object(merged, True)
    targets = bpy.context.selected_objects

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
        for obj in instance_parent:
            obj.data = bpy.data.meshes.new('new_mesh')
            if obj.modifiers:
                obj.modifiers.clear()
        for obj in instance_sources:
            print(f"remove: {obj}")
            bpy.data.objects.remove(obj)
    targets = bpy.context.selected_objects

    # リンクされたオブジェクトのモディファイアは適用できないので予めリンクを解除しておく
    bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, animation=False)

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
    return True


### endregion ###

### region ShapeKeysUtil連携 ###
def shapekey_util_is_found():
    try:
        return hasattr(bpy.types, bpy.ops.object.shapekeys_util_apply_mod_with_shapekeys_automerge.idname())
    except AttributeError:
        return False


def shapekey_util_label(layout):
    layout.label(text='ShapeKey Utils')


def box_warning_slow_method(layout):
    box = layout.box()
    box.label(text=bpy.app.translations.pgettext("box_warning_slow_method_1"))
    box.label(text=bpy.app.translations.pgettext("box_warning_slow_method_2"))
    box.label(text=bpy.app.translations.pgettext("box_warning_slow_method_3"))


def box_warning_read_pref(layout):
    box = layout.box()
    box.label(text=bpy.app.translations.pgettext("box_warning_read_pref_1"))
    box.label(text=bpy.app.translations.pgettext("box_warning_read_pref_2"))
    box.label(text=bpy.app.translations.pgettext("box_warning_read_pref_3"))


### endregion ###

### AddonPreferences ###
class addon_preferences(bpy.types.AddonPreferences):
    bl_idname = func_package_utils.get_package_root()

    apply_modifiers_with_shapekeys: BoolProperty(name="Apply Modifier with Shape Keys", default=True)

    def draw(self, context):
        layout = self.layout

        # ShapekeysUtil
        box = layout.box()
        if shapekey_util_is_found():
            box.label(text='AutoMerge - ShapeKey Utils')
            box_warning_slow_method(box)
            box.prop(self, "apply_modifiers_with_shapekeys")


### Object Operator ###
class OBJECT_OT_specials_merge_children_grouped(bpy.types.Operator):
    bl_idname = "object.apply_modifier_and_merge_children_grouped"
    bl_label = "Merge Grouped Children"
    bl_description = "選択中のオブジェクトのうち、\nオブジェクトグループ“MergeGroup”に属するものに対し、それぞれ子階層以下にあるオブジェクトをマージします"
    bl_options = {'REGISTER', 'UNDO'}

    duplicate: BoolProperty(name="Duplicate", default=False)
    ignore_armature: bpy.props.BoolProperty(name="Ignore Armature", default=True)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "duplicate")
        layout.prop(self, "ignore_armature")
        if shapekey_util_is_found():
            layout.separator()
            box = layout.box()
            shapekey_util_label(box)
            box_warning_slow_method(box)
            box_warning_read_pref(box)
            col = box.column()
            col.enabled = False
            addon_prefs = func_object_utils.get_addon_prefs()
            col.prop(addon_prefs, "apply_modifiers_with_shapekeys")

    def execute(self, context):
        addon_prefs = func_object_utils.get_addon_prefs()
        b = func_apply_modifier_and_merge_children_grouped.apply_modifier_and_merge_children_grouped(
            self, context, None, addon_prefs.apply_modifiers_with_shapekeys,
            duplicate=self.duplicate,
            ignore_armature=self.ignore_armature)
        if b:
            return {'FINISHED'}
        else:
            return {'CANCELLED'}


def get_selected_root_objects():
    selected_objects = bpy.context.selected_objects
    not_root = []
    root_objects = []
    for obj in selected_objects:
        if obj in not_root:
            continue
        parent = obj
        while True:
            parent = parent.parent
            print(parent)
            if parent is None:
                # 親以上のオブジェクトに選択中オブジェクトが存在しなければ、そのオブジェクトはrootとなる
                root_objects.append(obj)
                break
            if parent in selected_objects:
                not_root.append(parent)
                break
    return root_objects


class OBJECT_OT_specials_merge_children(bpy.types.Operator):
    bl_idname = "object.apply_modifier_and_merge_children"
    bl_label = "Merge Children"
    bl_description = "最後に選択したオブジェクトに対し、\nその子階層以下にあるオブジェクトをマージします"
    bl_options = {'REGISTER', 'UNDO'}

    duplicate: BoolProperty(name="Duplicate", default=False)
    ignore_armature: bpy.props.BoolProperty(name="Ignore Armature", default=True)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "duplicate")
        layout.prop(self, "ignore_armature")
        if shapekey_util_is_found():
            layout.separator()
            box = layout.box()
            shapekey_util_label(box)
            box_warning_slow_method(box)
            box_warning_read_pref(box)
            col = box.column()
            col.enabled = False
            addon_prefs = func_object_utils.get_addon_prefs()
            col.prop(addon_prefs, "apply_modifiers_with_shapekeys")

    def execute(self, context):
        print("apply_modifier_and_merge_children")

        # rootを取得
        root_objects = get_selected_root_objects()

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

            b = merge_children_recursive(operator=self,
                                         context=context,
                                         apply_modifiers_with_shapekeys=addon_prefs.apply_modifiers_with_shapekeys,
                                         ignore_armature=self.ignore_armature)
            result.append(func_object_utils.get_active_object())
            if not b:
                return {'CANCELLED'}

        func_object_utils.select_objects(result, True)
        print("finished")
        return {'FINISHED'}


class OBJECT_OT_specials_merge_selections(bpy.types.Operator):
    bl_idname = "object.apply_modifier_and_merge_selections"
    bl_label = "Merge Selections"
    bl_description = "最後に選択したオブジェクトに対し、\n選択中の他オブジェクトをマージします"
    bl_options = {'REGISTER', 'UNDO'}

    duplicate: bpy.props.BoolProperty(name="Duplicate", default=False)
    ignore_armature: bpy.props.BoolProperty(name="Ignore Armature", default=True)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "duplicate")
        layout.prop(self, "ignore_armature")
        if shapekey_util_is_found():
            layout.separator()
            box = layout.box()
            shapekey_util_label(box)
            box_warning_slow_method(box)
            box_warning_read_pref(box)
            col = box.column()
            col.enabled = False
            addon_prefs = func_object_utils.get_addon_prefs()
            col.prop(addon_prefs, "apply_modifiers_with_shapekeys")

    def execute(self, context):
        if self.duplicate:
            # 対象オブジェクトを複製
            bpy.ops.object.duplicate()

        addon_prefs = func_object_utils.get_addon_prefs()
        b = apply_modifier_and_merge_selections(self, context, addon_prefs.apply_modifiers_with_shapekeys,
                                                self.ignore_armature)
        if b:
            return {'FINISHED'}
        else:
            return {'CANCELLED'}


# 選択オブジェクトをMergeGroupグループに入れたり外したりするクラス
class OBJECT_OT_specials_assign_merge_group(bpy.types.Operator):
    bl_idname = "object.assign_merge_group"
    bl_label = "Assign Merge Group"
    bl_description = "選択中のオブジェクトを\nオブジェクトグループ“" + consts.PARENTS_GROUP_NAME + "”に入れたり外したりします"
    bl_options = {'REGISTER', 'UNDO'}

    assign: bpy.props.BoolProperty(name="Assign", default=True)

    def execute(self, context):
        func_collection_utils.assign_object_group(group_name=consts.PARENTS_GROUP_NAME, assign=self.assign)
        # exclude_collection(context=context, group_name=PARENTS_GROUP_NAME, exclude=True)
        func_collection_utils.hide_collection(context=context, group_name=consts.PARENTS_GROUP_NAME, hide=True)
        return {'FINISHED'}


### Init Menu ###
# Special → Auto Merge Objects を登録する
def INFO_MT_object_specials_auto_merge_menu(self, context):
    self.layout.menu(VIEW3D_MT_object_specials_auto_merge.bl_idname)


# Special → Auto Merge にコマンドを登録するクラス
class VIEW3D_MT_object_specials_auto_merge(bpy.types.Menu):
    bl_label = "Auto Merge"
    bl_idname = "VIEW3D_MT_object_specials_auto_merge"

    def draw(self, context):
        self.layout.operator(OBJECT_OT_specials_merge_children.bl_idname)
        self.layout.operator(OBJECT_OT_specials_merge_children_grouped.bl_idname)
        self.layout.operator(OBJECT_OT_specials_merge_selections.bl_idname)
        self.layout.separator()
        self.layout.operator(OBJECT_OT_specials_assign_merge_group.bl_idname)


### Init ###
classes = [
    VIEW3D_MT_object_specials_auto_merge,

    OBJECT_OT_specials_merge_children_grouped,
    OBJECT_OT_specials_merge_children,
    OBJECT_OT_specials_merge_selections,

    OBJECT_OT_specials_assign_merge_group,

    addon_preferences,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.app.translations.register(func_package_utils.get_package_root(), translations_dict)

    bpy.types.VIEW3D_MT_object_context_menu.append(INFO_MT_object_specials_auto_merge_menu)
    bpy.types.WindowManager.mizore_automerge_collection_name = bpy.props.StringProperty(consts.PARENTS_GROUP_NAME)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.app.translations.unregister(func_package_utils.get_package_root())

    bpy.types.VIEW3D_MT_object_context_menu.remove(INFO_MT_object_specials_auto_merge_menu)
    del bpy.types.WindowManager.mizore_automerge_collection_name
