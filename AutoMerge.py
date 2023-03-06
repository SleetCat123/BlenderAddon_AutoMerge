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
import os
from bpy.props import (StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty, CollectionProperty)
from bpy_extras.io_utils import ExportHelper, path_reference_mode

PARENTS_GROUP_NAME = "MergeGroup"  # マージ先となるオブジェクトが属するグループの名前
APPLY_AS_SHAPEKEY_NAME = "%AS%"  # モディファイア名が%AS%で始まっているならApply as shapekey
FORCE_APPLY_MODIFIER_PREFIX = "%A%"  # モディファイア名が"%A%"で始まっているならArmatureなどの対象外モディファイアでも強制的に適用


### region Func ###
def select_object(obj, value=True):
    # try:
    obj.select_set(value)
    # except ReferenceError:
    #     print("removed")


def select_objects(objects, value=True):
    for obj in objects:
        select_object(obj, value)


def get_active_object():
    return bpy.context.view_layer.objects.active


def set_active_object(obj):
    # try:
    bpy.context.view_layer.objects.active = obj
    # except ReferenceError:
    #    print("removed")


def deselect_all_objects():
    targets = bpy.context.selected_objects
    for obj in targets:
        select_object(obj, False)
    # bpy.context.view_layer.objects.active = None


def get_addon_prefs():
    return bpy.context.preferences.addons[__package__].preferences


### endregion ###

### region Translation ###
translations_dict = {
    "en_US": {
        ("*", "box_warning_slow_method_1"): "Warning: ",
        ("*", "box_warning_slow_method_2"): "If using the settings below,",
        ("*", "box_warning_slow_method_3"): "some functions may take a while in this add-on.",
        ("*", "box_warning_read_pref_1"): "You can change a setting below",
        ("*", "box_warning_read_pref_2"): " in this add-on preference.",
        ("*", "box_warning_read_pref_3"): "",
    },
    "ja_JP": {
        ("*", "box_warning_slow_method_1"): "注意：",
        ("*", "box_warning_slow_method_2"): "以下の項目を有効にすると",
        ("*", "box_warning_slow_method_3"): "処理に時間がかかる場合があります。",
        ("*", "box_warning_read_pref_1"): "以下の項目は",
        ("*", "box_warning_read_pref_2"): "Preference画面から設定できます。",
        ("*", "box_warning_read_pref_3"): "（アドオン同梱の画像参照）",
    },
}


### endregion ###

### region Func ###
def get_children(obj):
    allobjects = bpy.data.objects
    return [child for child in allobjects if child.parent == obj]


def find_collection(name):
    return next((c for c in bpy.context.scene.collection.children if name in c.name), None)


def find_layer_collection(name):
    return next((c for c in bpy.context.view_layer.layer_collection.children if name in c.name), None)


def merge_children_recursive(self,
                             context,
                             obj,
                             enable_apply_modifiers_with_shapekeys,
                             apply_parentobj_modifier=True,
                             ignore_armature=True,
                             ):
    # obj.hide_set(False)
    if obj.hide_get() == True:
        return True

    children = get_children(obj)
    for child in children:
        # print("call:"+child.name)
        b = merge_children_recursive(self, context, child, enable_apply_modifiers_with_shapekeys,
                                     apply_parentobj_modifier, ignore_armature)
        if b == False:
            # 処理に失敗したら中断
            print("!!! Failed - merge_children_recursive A")
            return False

    deselect_all_objects()
    select_objects(children, True)
    select_object(obj, True)
    set_active_object(obj)
    print("merge:" + obj.name)
    b = apply_modifier_and_merge_selections(self, context, enable_apply_modifiers_with_shapekeys,
                                            apply_parentobj_modifier, ignore_armature)
    if b == False:
        print("!!! Failed - merge_children_recursive B")
    return b != False


def duplicate_selected_objects():
    dup_source = bpy.context.selected_objects
    # 対象オブジェクトを複製
    bpy.ops.object.duplicate()
    dup_result = bpy.context.selected_objects

    return (dup_source, dup_result)


def apply_modifiers(self, obj, enable_apply_modifiers_with_shapekeys):
    # オブジェクトのモディファイアを適用
    if obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) != 0:
        # オブジェクトにシェイプキーがあったら
        succeed_import = False
        if enable_apply_modifiers_with_shapekeys == True:
            try:
                # ShapeKeysUtil連携
                # ShapeKeysUtilが導入されていたらシェイプキーつきオブジェクトでもモディファイア適用
                from ShapeKeysUtil import apply_modifiers_with_shapekeys_for_automerge_addon
                succeed_import = True
                b = apply_modifiers_with_shapekeys_for_automerge_addon(self, obj)
                if b == False:
                    return False
            except ImportError:
                t = "!!! Failed to load ShapeKeysUtil !!! - on apply modifier"
                print(t)
                self.report({'ERROR'}, t)
        if enable_apply_modifiers_with_shapekeys == False or succeed_import == False:
            # オブジェクトにシェイプキーが存在するなら適用せずモディファイアを削除
            obj.modifiers.clear()
            self.report({'INFO'}, "[" + obj.name + "] has shape key. apply modifier was skipped.")
    else:
        for modifier in obj.modifiers:
            if modifier.show_render == False:
                # モディファイアがレンダリング対象ではない（モディファイア一覧のカメラアイコンが押されていない）なら無視
                continue
            if modifier.name.startswith(APPLY_AS_SHAPEKEY_NAME):
                # モディファイア名が%AS%で始まっているならApply as shapekey
                try:
                    # 名前の文字列から%AS%を削除する
                    modifier.name = modifier.name[len(APPLY_AS_SHAPEKEY_NAME):len(modifier.name)]
                    # Apply As Shape
                    bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=False, modifier=modifier.name)
                    # シェイプキーが追加された影響で通常のApply Modifierが動作しなくなるので関数をリスタート
                    return apply_modifiers(self, obj, enable_apply_modifiers_with_shapekeys)
                except RuntimeError:
                    # 無効なModifier（対象オブジェクトが指定されていないなどの状態）は適用しない
                    print("!!! Apply as shapekey failed !!!: [{0}]".format(modifier.name))
                    bpy.ops.object.modifier_remove(modifier=modifier.name)
                else:
                    try:
                        print("Apply as shapekey: [{0}]".format(modifier.name))
                    except UnicodeDecodeError:
                        print("Apply as shapekey")
            elif modifier.name.startswith(FORCE_APPLY_MODIFIER_PREFIX) or modifier.type != 'ARMATURE':
                # モディファイアが処理対象モディファイアなら
                # または、モディファイアの名前欄が%A%で始まっているなら
                try:
                    bpy.ops.object.modifier_apply(modifier=modifier.name)
                except RuntimeError:
                    # 無効なModifier（対象オブジェクトが指定されていないなどの状態）は適用しない
                    print("!!! Apply failed !!!: [{0}]".format(modifier.name))
                    bpy.ops.object.modifier_remove(modifier=modifier.name)
                else:
                    try:
                        # なんかここだけUnicodeEncodeErrorが出たり出なかったりする。なんで……？
                        print("Apply: [{0}]".format(modifier.name))
                    except UnicodeDecodeError:
                        print("Apply")


def apply_modifier_and_merge_selections(self, context, enable_apply_modifiers_with_shapekeys,
                                        apply_parentobj_modifier=False, ignore_armature=False):
    modeTemp = None
    if bpy.context.object is not None:
        # 開始時のモードを記憶しオブジェクトモードに
        modeTemp = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='OBJECT')

    merged = get_active_object()
    targets = bpy.context.selected_objects

    if apply_parentobj_modifier == False:
        targets.remove(merged)

    # リンクされたオブジェクトのモディファイアは適用できないので予めリンクを解除しておく
    bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, animation=False)

    for obj in targets:
        if obj.type == "MESH":
            # オブジェクトの種類がメッシュなら
            deselect_all_objects()
            select_object(merged, True)
            set_active_object(obj)
            b = apply_modifiers(self, obj, enable_apply_modifiers_with_shapekeys)
            if b == False:
                return False

        # else:
        #    # オブジェクトの種類がメッシュ以外ならそのオブジェクトを削除
        #    deselect_all_objects()
        #    set_active_object(obj)
        #    bpy.ops.object.delete()

    # オブジェクトを結合
    deselect_all_objects()
    select_object(merged, True)
    set_active_object(merged)
    if targets and 1 < len(targets):
        targets.sort(key=lambda x: x.name)
        print("------ Merge ------\n" + '\n'.join([obj.name for obj in targets]) + "\n-------------------")
        for obj in targets:
            if merged == obj: continue
            select_object(obj, True)
            if obj.data.use_auto_smooth:
                # 子オブジェクトのuse_auto_smoothがtrueならAutoSmoothを有効化
                merged.data.use_auto_smooth = True
                merged.data.auto_smooth_angle = math.pi

        bpy.ops.object.join()

    if modeTemp is not None:
        # 開始時のモードを復元
        bpy.ops.object.mode_set(mode=modeTemp)
    return True


def deselect_collection(collection):
    if collection is None:
        return
    print("Deselect Collection: " + collection.name)
    active = get_active_object()
    targets = bpy.context.selected_objects
    # 処理targetsから除外するオブジェクトの選択を外す
    # 対象コレクションに属するオブジェクトと選択中オブジェクトの積集合
    assigned_objs = list(set(collection.objects) & set(targets))
    for obj in assigned_objs:
        deselect_all_objects()
        select_object(obj, True)
        set_active_object(obj)
        if bpy.context.object.mode != 'OBJECT':
            # Armatureをアクティブにしたとき勝手にPoseモードになる場合があるためここで確実にObjectモードにする
            bpy.ops.object.mode_set(mode='OBJECT')
        # オブジェクトの子も除外対象に含める
        bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')
        children = bpy.context.selected_objects;
        for child in children:
            if child in targets:
                targets.remove(child)
            if child == active:
                active = None
            print("Deselect: " + child.name)
    deselect_all_objects()
    select_objects(targets, True)
    if active is not None:
        set_active_object(active)


def apply_modifier_and_merge_children_grouped(self, context, ignore_collection, enable_apply_modifiers_with_shapekeys,
                                              duplicate, apply_parentobj_modifier=False, ignore_armature=False):
    # 処理から除外するオブジェクトの選択を外す
    deselect_collection(ignore_collection)

    print(
        "xxxxxx Targets xxxxxx\n" + '\n'.join([obj.name for obj in bpy.context.selected_objects]) + "\nxxxxxxxxxxxxxxx")

    # コレクションを取得
    collection = find_collection(PARENTS_GROUP_NAME)
    if not collection:
        # コレクションがなかったら処理中断
        return
    if not collection.name in bpy.context.scene.collection.children.keys():
        # コレクションをLinkする。
        # Unlink状態のコレクションでもPythonからは参照できてしまう場合があるようなので、確実にLink状態になるようにしておく
        bpy.context.scene.collection.children.link(collection)

    modeTemp = None
    if bpy.context.object is not None:
        # 開始時のモードを記憶しオブジェクトモードに
        modeTemp = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='OBJECT')

    dup_source_parents = []
    dup_result_parents = []

    targets = bpy.context.selected_objects

    # ------------------
    # 結合処理
    merge_targets = set(collection.objects) & set(targets)
    # merge_targets=targets

    results = targets

    # 多重マージに対応
    is_parent_list = [False] * len(merge_targets)
    roots = set()  # 要素が重複することがないようにsetを使用する
    i = -1
    for obj in merge_targets:
        i += 1
        if is_parent_list[i] == True:
            # 既にルートではないことが確定しているオブジェクトは処理スキップ
            continue
        merge_root_parent = obj
        parent = obj
        # マージ対象のルートを取得
        while True:
            parent = parent.parent
            print(parent)
            if parent is None:
                print("root:" + merge_root_parent.name)
                roots.add(merge_root_parent)
                break
            if parent in merge_targets:
                print("parent:" + parent.name)
                merge_root_parent = parent
                is_parent_list[i] = True
    for merge_root_parent in roots:
        deselect_all_objects()
        select_object(merge_root_parent, True)
        set_active_object(merge_root_parent)
        bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')

        # マージ対象オブジェクトをresultsから消しておく（あとで親オブジェクトだけ再追加する）
        results = list(set(results) - set(bpy.context.selected_objects))

        # 処理から除外するオブジェクトの選択を外す
        deselect_collection(ignore_collection)

        if duplicate == True:
            dup_source_parents.append(merge_root_parent)
            # 対象オブジェクトを複製
            duplicate_selected_objects()
            print("dup:" + merge_root_parent.name)
        active = get_active_object()

        # 子を再帰的にマージ
        b = merge_children_recursive(self, context, active, enable_apply_modifiers_with_shapekeys,
                                     apply_parentobj_modifier=True, ignore_armature=True)
        if b == False:
            # 処理に失敗したら中断
            return False

        dup_result_parents.append(get_active_object())
    results.extend(dup_result_parents)
    # ------------------

    # 選択を復元
    deselect_all_objects()
    select_objects(results, True)

    if modeTemp is not None:
        # 開始時のモードを復元
        bpy.ops.object.mode_set(mode=modeTemp)

    # layer_col.exclude = True

    return (dup_source_parents, dup_result_parents)


# 選択オブジェクトを指定名のグループに入れたり外したり
def assign_object_group(group_name, assign=True):
    collection = find_collection(group_name)
    if not collection:
        if assign == True:
            # コレクションが存在しなければ新規作成
            collection = bpy.data.collections.new(name=group_name)
            bpy.context.scene.collection.children.link(collection)
        else:
            # コレクションが存在せず、割り当てがfalseなら何もせず終了
            return

    # if not collection.name in bpy.context.scene.collection.children.keys():
    # コレクションをLinkする。
    # Unlink状態のコレクションでもPythonからは参照できてしまう場合があるようなので、確実にLink状態になるようにしておく
    # bpy.context.scene.collection.children.link(collection)

    active = get_active_object()
    targets = bpy.context.selected_objects
    for obj in targets:
        if assign == True:
            set_active_object(obj)
            if not obj.name in collection.objects:
                # コレクションに追加
                collection.objects.link(obj)
        else:
            if obj.name in collection.objects:
                # コレクションから外す
                collection.objects.unlink(obj)

    if collection.objects == False:
        # コレクションが空なら削除する
        bpy.context.scene.collection.children.unlink(collection)

    # アクティブオブジェクトを元に戻す
    set_active_object(active)


def hide_collection(context, group_name, hide=True):
    layer_col = find_layer_collection(group_name)
    if layer_col:
        layer_col.hide_viewport = hide


### endregion ###

### region ShapeKeysUtil連携 ###
def shapekey_util_is_found():
    try:
        from ShapeKeysUtil import apply_modifiers_with_shapekeys
        return True
    except ImportError:
        t = "!!! Failed to load ShapeKeysUtil !!! - on shapekey_util_is_found"
        print(t)
        # self.report({'ERROR'}, t)
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
    bl_idname = __package__

    enable_apply_modifiers_with_shapekeys: BoolProperty(name="Apply Modifier with Shape Keys", default=True)

    def draw(self, context):
        layout = self.layout

        # ShapekeysUtil
        box = layout.box()
        if shapekey_util_is_found() == True:
            box.label(text='AutoMerge - ShapeKey Utils')
            box_warning_slow_method(box)
            box.prop(self, "enable_apply_modifiers_with_shapekeys")


### Object Operator ###
class OBJECT_OT_specials_merge_children_grouped(bpy.types.Operator):
    bl_idname = "object.apply_modifier_and_merge_children_grouped"
    bl_label = "Merge Grouped Children"
    bl_description = "選択中のオブジェクトのうち、\nオブジェクトグループ“MergeGroup”に属するものに対し、それぞれ子階層以下にあるオブジェクトをマージします"
    bl_options = {'REGISTER', 'UNDO'}

    duplicate: BoolProperty(name="Duplicate", default=False)
    apply_parentobj_modifier: bpy.props.BoolProperty(name="Apply Parent Object Modifiers", default=True)
    ignore_armature: bpy.props.BoolProperty(name="Ignore Armature", default=True)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "duplicate")
        layout.prop(self, "apply_parentobj_modifier")
        layout.prop(self, "ignore_armature")
        if shapekey_util_is_found() == True:
            layout.separator()
            box = layout.box()
            shapekey_util_label(box)
            box_warning_slow_method(box)
            box_warning_read_pref(box)
            col = box.column()
            col.enabled = False
            addon_prefs = get_addon_prefs()
            col.prop(addon_prefs, "enable_apply_modifiers_with_shapekeys")

    def execute(self, context):
        addon_prefs = get_addon_prefs()
        b = apply_modifier_and_merge_children_grouped(
            self, context, None, addon_prefs.enable_apply_modifiers_with_shapekeys,
            duplicate=self.duplicate, apply_parentobj_modifier=self.apply_parentobj_modifier,
            ignore_armature=self.ignore_armature)
        if b == False:
            return {'CANCELLED'}
        else:
            return {'FINISHED'}


class OBJECT_OT_specials_merge_children(bpy.types.Operator):
    bl_idname = "object.apply_modifier_and_merge_children"
    bl_label = "Merge Children"
    bl_description = "最後に選択したオブジェクトに対し、\nその子階層以下にあるオブジェクトをマージします"
    bl_options = {'REGISTER', 'UNDO'}

    duplicate: BoolProperty(name="Duplicate", default=False)
    apply_parentobj_modifier: bpy.props.BoolProperty(name="Apply Parent Object Modifiers", default=True)
    ignore_armature: bpy.props.BoolProperty(name="Ignore Armature", default=True)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "duplicate")
        layout.prop(self, "apply_parentobj_modifier")
        layout.prop(self, "ignore_armature")
        if shapekey_util_is_found() == True:
            layout.separator()
            box = layout.box()
            shapekey_util_label(box)
            box_warning_slow_method(box)
            box_warning_read_pref(box)
            col = box.column()
            col.enabled = False
            addon_prefs = get_addon_prefs()
            col.prop(addon_prefs, "enable_apply_modifiers_with_shapekeys")

    def execute(self, context):
        print("apply_modifier_and_merge_children")

        # rootを取得
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

        # 結合処理
        addon_prefs = get_addon_prefs()
        for obj in root_objects:
            if self.duplicate == True:
                # 対象オブジェクトを複製
                duplicate_selected_objects()

            b = merge_children_recursive(self, context, obj, addon_prefs.enable_apply_modifiers_with_shapekeys,
                                         self.apply_parentobj_modifier, self.ignore_armature)
            if b == False:
                return {'CANCELLED'}

        select_objects(root_objects, True)
        return {'FINISHED'}


class OBJECT_OT_specials_merge_selections(bpy.types.Operator):
    bl_idname = "object.apply_modifier_and_merge_selections"
    bl_label = "Merge Selections"
    bl_description = "最後に選択したオブジェクトに対し、\n選択中の他オブジェクトをマージします"
    bl_options = {'REGISTER', 'UNDO'}

    duplicate: bpy.props.BoolProperty(name="Duplicate", default=False)
    apply_parentobj_modifier: bpy.props.BoolProperty(name="Apply Parent Object Modifiers", default=True)
    ignore_armature: bpy.props.BoolProperty(name="Ignore Armature", default=True)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "duplicate")
        layout.prop(self, "apply_parentobj_modifier")
        layout.prop(self, "ignore_armature")
        if shapekey_util_is_found() == True:
            layout.separator()
            box = layout.box()
            shapekey_util_label(box)
            box_warning_slow_method(box)
            box_warning_read_pref(box)
            col = box.column()
            col.enabled = False
            addon_prefs = get_addon_prefs()
            col.prop(addon_prefs, "enable_apply_modifiers_with_shapekeys")

    def execute(self, context):
        if self.duplicate == True:
            # 対象オブジェクトを複製
            duplicate_selected_objects()

        addon_prefs = get_addon_prefs()
        b = apply_modifier_and_merge_selections(self, context, addon_prefs.enable_apply_modifiers_with_shapekeys,
                                                self.apply_parentobj_modifier, self.ignore_armature)
        if b == True:
            return {'FINISHED'}
        else:
            return {'CANCELLED'}


# 選択オブジェクトをMergeGroupグループに入れたり外したりするクラス
class OBJECT_OT_specials_assign_merge_group(bpy.types.Operator):
    bl_idname = "object.assign_merge_group"
    bl_label = "Assign Merge Group"
    bl_description = "選択中のオブジェクトを\nオブジェクトグループ“" + PARENTS_GROUP_NAME + "”に入れたり外したりします"
    bl_options = {'REGISTER', 'UNDO'}

    assign: bpy.props.BoolProperty(name="Assign", default=True)

    def execute(self, context):
        assign_object_group(group_name=PARENTS_GROUP_NAME, assign=self.assign)
        # exclude_collection(context=context, group_name=PARENTS_GROUP_NAME, exclude=True)
        hide_collection(context=context, group_name=PARENTS_GROUP_NAME, hide=True)
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

    bpy.app.translations.register(__package__, translations_dict)

    bpy.types.VIEW3D_MT_object_context_menu.append(INFO_MT_object_specials_auto_merge_menu)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.app.translations.unregister(__package__)

    bpy.types.VIEW3D_MT_object_context_menu.remove(INFO_MT_object_specials_auto_merge_menu)
