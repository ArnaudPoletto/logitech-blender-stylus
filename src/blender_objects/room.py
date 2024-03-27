import bpy
import math
from mathutils import Vector

from blender_objects.blender_object import BlenderObject
from blender_objects.wall import Wall

class Room(BlenderObject):
    """
    A room in a scene.
    """

    def _define_walls(self, width: float, height: float, depth: float) -> None:
        """
        Define the walls of the room.

        Args:
            width (float): The width of the room.
            height (float): The length of the room.
            depth (float): The height of the room.
        """
        # Right wall
        right_wall_location = self.location + Vector((0, -width / 2, 0))
        wall = Wall(
            name=f"{self.name}RightWall",
            location=right_wall_location,
            rotation=Vector((math.pi / 2, math.pi / 2, 0)),
            scale=Vector((height, depth)),
            centered=True,
        )
        self.right_wall = wall

        # Left wall
        left_wall_location = self.location + Vector((0, width / 2, 0))
        wall = Wall(
            name=f"{self.name}LeftWall",
            location=left_wall_location,
            rotation=Vector((math.pi / 2, math.pi / 2, 0)),
            scale=Vector((height, depth)),
            centered=True,
        )
        self.left_wall = wall

        # Front wall
        front_wall_location = self.location + Vector((depth / 2, 0, 0))
        wall = Wall(
            name=f"{self.name}FrontWall",
            location=front_wall_location,
            rotation=Vector((0, math.pi / 2, 0)),
            scale=Vector((height, width)),
            centered=True,
        )
        self.front_wall = wall

        # Back wall
        back_wall_location = self.location + Vector((-depth / 2, 0, 0))
        wall = Wall(
            name=f"{self.name}BackWall",
            location=back_wall_location,
            rotation=Vector((0, math.pi / 2, 0)),
            scale=Vector((height, width)),
            centered=True,
        )
        self.back_wall = wall

        # Ceiling
        ceiling_location = self.location + Vector((0, 0, height / 2))
        wall = Wall(
            name=f"{self.name}Ceiling",
            location=ceiling_location,
            rotation=Vector((0, 0, 0)),
            scale=Vector((depth, width)),
            centered=True,
        )
        self.ceiling = wall

        # Floor
        floor_location = self.location + Vector((0, 0, -height / 2))
        wall = Wall(
            name=f"{self.name}Floor",
            location=floor_location,
            rotation=Vector((0, 0, 0)),
            scale=Vector((depth, width)),
            centered=True,
        )
        self.floor = wall
    
    def __init__(
            self,
            name: str,
            location: Vector,
            width: float,
            height: float,
            depth: float,
            ):
        """
        Initialize the room.

        Args:
            name (str): The name of the room.
            location (Vector): The location of the room as a 3D vector.
            width (float): The width of the room.
            height (float): The height of the room.
            depth (float): The depth of the room.

        Raises:
            ValueError: If the width is not a positive number.
            ValueError: If the height is not a positive number.
            ValueError: If the depth is not a positive number.
        """
        if width <= 0:
            raise ValueError("The width must be a positive number.")
        
        if height <= 0:
            raise ValueError("The height must be a positive number.")
        
        if depth <= 0:
            raise ValueError("The depth must be a positive number.")

        super().__init__(
            name=name,
            location=location,
        )

        self._define_walls(width, height, depth)

    def apply_to_collection(self, collection: bpy.types.Collection) -> None:
        self.right_wall.apply_to_collection(collection)
        self.left_wall.apply_to_collection(collection)
        self.front_wall.apply_to_collection(collection)
        self.back_wall.apply_to_collection(collection)
        self.ceiling.apply_to_collection(collection)
        self.floor.apply_to_collection(collection)