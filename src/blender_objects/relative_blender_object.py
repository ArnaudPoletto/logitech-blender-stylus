import bpy
from typing import List, Tuple
from mathutils import Vector, Euler
from abc import abstractmethod

from blender_objects.blender_object import BlenderObject


class RelativeBlenderObject(BlenderObject):
    """
    A relative Blender object.
    """

    def __init__(
        self,
        name: str,
        relative_location: Vector = Vector((0, 0, 0)),
        relative_rotation: Euler = Euler((0, 0, 0)),
        scale: Vector = Vector((1, 1, 1)),
    ) -> None:
        """
        Initialize the relative Blender object.

        Args:
            name (str): The name of the Blender object.
            relative_location (Vector): The relative location of the relative Blender object from the location of the Blender object as a 3D vector. Defaults to no relative location.
            relative_rotation (Vector): The relative rotation of the relative Blender object from the rotation of the Blender object as a 3D vector. Defaults to no relative rotation.
            scale (Vector): The scale of the Blender object as a 3D vector. Defaults to no scaling.
        """
        super().__init__(
            name=name,
            location=relative_location,
            rotation=relative_rotation,
            scale=scale,
        )
        
        self.name = name
        self.scale = scale
        self.relative_blender_objects: List[RelativeBlenderObject] = []

    @abstractmethod
    def get_bounds(
        self,
    ) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
        """
        Get the bounds of the Blender object from its relative location.

        Returns:
            Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]: The bounds of the Blender object where the first tuple
            represents the signed distance from the relative location to the minimum and maximum x values, the second tuple is the same but
            for y values, and the third tuple is the same but for z values.
        """
        raise NotImplementedError(
            "The get_object_bounds method must be implemented in the subclass."
        )