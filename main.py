import bpy
import os
import sys
from threading import Thread

FILEPATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, FILEPATH)

from geometry_utils import *
import spatial
import constraint_solver
from world import World
from hci_manager import HCIManager

COLOR_MODS = ['black', 'red', 'blue', 'brown', 'green', 'yellow']
"""list[str]: Possible color modifiers."""

RELATIONS = ['on', 'to the left of', 'to the right of', 'in front of', 'behind', 'above', 'below', 'over', 'under', 'near', 'touching', 'at', 'between']
"""list[str]: Possible spatial relations."""

TYPES_IDS = {
	'chair':  'props.item.furniture.chair',
	'rocking chair':  'props.item.furniture.rocking chair',
	'table':  'props.item.furniture.table',    
	'bed':     'props.item.furniture.bed',
	'sofa':  'props.item.furniture.sofa',
	'bookshelf':  'props.item.furniture.bookshelf',
	'desk':  'props.item.furniture.desk',
	'book': 'props.item.portable.book',
	'laptop': 'props.item.portable.laptop',
	'pencil': 'props.item.portable.pencil',
	'pencil holder': 'props.item.portable.pencil holder',
	'note': 'props.item.portable.note',
	'rose': 'props.item.portable.rose',
	'vase': 'props.item.portable.vase',
	'cardbox': 'props.item.portable.cardbox',
	'box': 'props.item.portable.box',
	'ceiling light': 'props.item.stationary.ceiling light',
	'lamp': 'props.item.portable.lamp',
	'apple': 'props.item.food.apple',
	'banana': 'props.item.food.banana',
	'plate': 'props.item.portable.plate',
	'bowl': 'props.item.portable.bowl',
	'trash bin': 'props.item.portable.trash can',
	'trash can': 'props.item.portable.trash can',
	'tv': 'props.item.appliances.tv',
	'poster': 'props.item.stationary.poster',
	'picture': 'props.item.stationary.picture',
	'fridge' : 'props.item.appliances.fridge',
	'ceiling fan': 'props.item.stationary.ceiling fan',
	'block': 'props.item.block',
	'floor': 'world.plane.floor',
	'ceiling': 'world.plane.ceiling',
	'wall': 'world.plane.wall',
	'beach umbrella': 'props.items.outdoor.beach_umbrella',
	'umbrella': 'props.items.indoor.portable.umbrella',
	'big tree': 'props.indoor.plants.big_tree',
	'small tree': 'props.indoor.plants.small tree',
	'footrest': 'props.indoor.items.portable.footrest',
	'aquarium': 'props.indoor.items.stationary.aquarium',
	'fish': 'props.mobile.animate.fish',
	'human': 'props.mobile.animate.human',
	'cat': 'props.mobile.animate.cat'
}
"""dict[str, str]: Mapping of room world object IDs to objects."""


def main():
	"""Entry point."""
	my_areas = bpy.context.workspace.screens[0].areas
	my_shading = 'MATERIAL'  # 'WIREFRAME' 'SOLID' 'MATERIAL' 'RENDERED'
	
	for area in my_areas:
		for space in area.spaces:
			if space.type == 'VIEW_3D':
				space.shading.type = my_shading
			 
	world = World(bpy.context.scene)
	spatial.entities = world.entities
	spatial.world = world
	constraint_solver.world = world
  
	hci_manager = HCIManager(world)
	hci_thread = Thread(target = hci_manager.start)
	hci_thread.daemon = True
	hci_thread.start()

if __name__ == "__main__":
	main()