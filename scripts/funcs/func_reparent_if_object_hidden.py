import bpy
from . import temp_children_name_table
from .utils import func_object_utils


def reparent_if_object_hidden(target: bpy.types.Object):
    print(f"reparent_if_object_hidden: {target.name}")
    # 再帰的に子オブジェクトを処理
    children = temp_children_name_table.get(target.name).copy()
    if func_object_utils.is_hidden(target):
        print(f"IsHidden: {target.name}")
        # オブジェクトが非表示の場合は親を変更
        parent = target.parent
        if parent:
            for child_name in children:
                child = bpy.data.objects[child_name]
                print(f"Reparent: {child.name} ({child.parent} -> {parent.name})")
                temp_children_name_table.set_parent(child, parent)

    for child_name in children:
        child = bpy.data.objects[child_name]
        reparent_if_object_hidden(child)
    
