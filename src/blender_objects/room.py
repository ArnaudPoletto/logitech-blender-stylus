import bpy
import math
from mathutils import Vector, Euler

from blender_objects.blender_object import BlenderObject
from blender_objects.wall import Wall


class Room(BlenderObject):
    """
    A room in a scene.
    """

    def _define_walls(self, scale: Vector) -> None:
        """
        Define the room.

        Args:
            scale (Vector): The scale of the room as a 3D vector.
        """
        attributes = [
            "right_wall",
            "left_wall",
            "front_wall",
            "back_wall",
            "ceiling",
            "floor",
        ]
        names = ["RightWall", "LeftWall", "FrontWall", "BackWall", "Ceiling", "Floor"]
        locations = [
            Vector((0, -scale.x / 2, 0)),
            Vector((0, scale.x / 2, 0)),
            Vector((scale.y / 2, 0, 0)),
            Vector((-scale.y / 2, 0, 0)),
            Vector((0, 0, scale.z / 2)),
            Vector((0, 0, -scale.z / 2)),
        ]
        rotations = [
            Euler((math.pi / 2, 0, 0)),
            Euler((math.pi / 2, 0, 0)),
            Euler((math.pi / 2, 0, math.pi / 2)),
            Euler((math.pi / 2, 0, math.pi / 2)),
            Euler((0, 0, 0)),
            Euler((0, 0, 0)),
        ]
        scales = [
            Vector((scale.y, scale.z)),
            Vector((scale.y, scale.z)),
            Vector((scale.x, scale.z)),
            Vector((scale.x, scale.z)),
            Vector((scale.y, scale.x)),
            Vector((scale.y, scale.x)),
        ]

        for attribute, name, location, rotation, scale in zip(
            attributes, names, locations, rotations, scales
        ):
            wall = Wall(
                name=f"{self.name}{name}",
                location=location,
                rotation=rotation,
                scale=scale,
            )
            setattr(self, attribute, wall)
            self.add_relative_blender_object(getattr(self, attribute))

    def __init__(
        self,
        name: str,
        location: Vector,
        scale: Vector,
    ):
        """
        Initialize the room.

        Args:
            name (str): The name of the room.
            location (Vector): The location of the room in the world as a 3D vector.
            scale (Vector): The scale of the room as a 3D vector.
        """
        super(Room, self).__init__(
            name=name,
            location=location,
            scale=scale,
        )

        self._define_walls(scale)
        
    def apply_to_collection(self, collection: bpy.types.Collection) -> None:
        """
        Apply the Blender object to the collection.

        Args:
            collection (bpy.types.Collection): The collection to add the Blender object to.
        """
        # Walls are not relative blender objects as they are the main tangible objects in the room.
        for wall in [
            self.right_wall,
            self.left_wall,
            self.front_wall,
            self.back_wall,
            self.ceiling,
            self.floor,
        ]:
            wall.apply_to_collection(collection)