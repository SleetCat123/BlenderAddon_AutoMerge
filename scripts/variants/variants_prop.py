import bpy
from ..funcs.utils import func_object_utils

class PROP_automerge_variants_list(bpy.types.PropertyGroup):
    variants_list: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    active_variant_index: bpy.props.IntProperty()

def get_variants_list(obj: bpy.types.Object):
    return obj.automerge_variants_list

def get_all_variant_names_in_children(obj: bpy.types.Object):
    print("get_all_variant_names_in_children")
    names = set()
    children = func_object_utils.get_children_recursive(obj)
    for child in children:
        prop = get_variants_list(child)
        if prop and prop.variants_list:
            print(f"{child.name}: {prop.variants_list.keys()}")
            names.update(prop.variants_list.keys())
    print(f"result: {names}")
    return names

def register():
    bpy.utils.register_class(PROP_automerge_variants_list)
    bpy.types.Object.automerge_variants_list = bpy.props.PointerProperty(type=PROP_automerge_variants_list)

def unregister():
    bpy.utils.unregister_class(PROP_automerge_variants_list)
    del bpy.types.Object.automerge_variants_list
