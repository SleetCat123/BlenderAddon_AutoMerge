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


bl_info = {
    "name": "AutoMerge",
    "author": "@sleetcat123(Twitter)",
    "version": (2,2,0),
    "blender": (2, 80, 0),
    "location": "",
    "description": "Merge Objects.",
    "category": "Objects"
}


def reload():
    import importlib
    for file in files:
        importlib.reload(file)


try:
    is_loaded
    reload()
except NameError:
    from .scripts import (
        addon_preferences,
        consts,
        link_with_MizoresCustomExporter,
        link_with_ShapeKeysUtil,
        menu_object_context,
        translations,
    )

    from .scripts.funcs import (
        func_apply_modifier_and_merge_children_grouped,
        func_apply_modifier_and_merge_selections,
        func_apply_modifiers,
        func_merge_children_recursive,
    )
    from .scripts.funcs.utils import (
        func_collection_utils,
        func_object_utils,
        func_package_utils,
        func_ui_utils,
    )

    from .scripts.ops import (
        op_assign_merge_group,
        op_merge_children,
        op_merge_children_grouped,
        op_merge_selections,
    )

files = [
    addon_preferences,
    consts,
    func_apply_modifier_and_merge_children_grouped,
    func_apply_modifier_and_merge_selections,
    func_apply_modifiers,
    func_collection_utils,
    func_merge_children_recursive,
    func_object_utils,
    func_package_utils,
    func_ui_utils,
    link_with_MizoresCustomExporter,
    link_with_ShapeKeysUtil,
    menu_object_context,
    op_assign_merge_group,
    op_merge_children,
    op_merge_children_grouped,
    op_merge_selections,
    translations,
]

is_loaded = False


def register():
    global is_loaded
    if is_loaded:
        reload()
    for file in files:
        func = getattr(file, "register", None)
        if callable(func):
            func()
    is_loaded = True


def unregister():
    for file in files:
        func = getattr(file, "unregister", None)
        if callable(func):
            func()


if __name__ == "__main__":
    register()
