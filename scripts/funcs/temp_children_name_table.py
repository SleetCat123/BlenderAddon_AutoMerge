import bpy
from .utils import func_object_utils


def update_table():
    global children_name_table
    children_name_table = func_object_utils.get_children_name_table()

def clear_table():
    global children_name_table
    children_name_table = {}

def get(key: str):
    global children_name_table
    return children_name_table[key]

def set_parent(obj: bpy.types.Object, parent: bpy.types.Object):
    global children_name_table
    prev_parent = obj.parent
    if prev_parent == parent:
        return
    if prev_parent:
        children_name_table[prev_parent.name].remove(obj.name)
    children_name_table[parent.name].append(obj.name)
    func_object_utils.set_parent(obj, parent)