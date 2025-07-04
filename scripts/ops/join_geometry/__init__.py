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

"""
Join Geometry 機能パッケージ
Geometry Nodesを使用したオブジェクト結合機能群
"""

from . import (
    join_geometry_base,
    op_join_geometry,
    op_join_geometry_recursive,
    op_join_geometry_to_new,
    op_join_geometry_recursive_to_new,
    op_update_join_geometry,
)

def register():
    """Join Geometry機能群の登録"""
    op_join_geometry.register()
    op_join_geometry_recursive.register()
    op_join_geometry_to_new.register()
    op_join_geometry_recursive_to_new.register()
    op_update_join_geometry.register()

def unregister():
    """Join Geometry機能群の登録解除"""
    op_update_join_geometry.unregister()
    op_join_geometry_recursive_to_new.unregister()
    op_join_geometry_to_new.unregister()
    op_join_geometry_recursive.unregister()
    op_join_geometry.unregister()