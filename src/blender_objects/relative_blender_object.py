import bpy
from typing import List, Tuple
from mathutils import Vector, Euler
from abc import abstractmethod


class RelativeBlenderObject:
    """
    A Blender object.
    """

    def __init__(
        self,
        name: str,
        relative_location: Vector = Vector((0, 0, 0)),
        relative_rotation: Euler = Euler((0, 0, 0)),
        scale: Vector = Vector((1, 1, 1)),
    ) -> None:
        """
        Initialize the Blender object.

        Args:
            name (str): The name of the Blender object.
            relative_location (Vector): The relative location of the relative Blender object from the location of the Blender object as a 3D vector. Defaults to the origin.
            relative_rotation (Vector): The relative rotation of the relative Blender object from the rotation of the Blender object as a 3D vector. Defaults to no rotation.
            scale (Vector): The scale of the Blender object as a 3D vector. Defaults to no scaling.

        Raises:
            ValueError: If the relative location is not a 3D vector.
            ValueError: If the relative rotation is not a 3D vector.
            ValueError: If the scale is not a 3D vector.
            ValueError: If the scale values are not positive.
        """

        if len(relative_location) != 3:
            raise ValueError("The relative location must be a 3D vector.")

        if len(relative_rotation) != 3:
            raise ValueError("The relative rotation must be a 3D vector.")

        if len(scale) != 3:
            raise ValueError("The scale must be a 3D vector.")

        if any(value <= 0 for value in scale):
            raise ValueError("The scale values must be positive.")

        self.name = name
        self.relative_location = relative_location
        self.relative_rotation = relative_rotation
        self.scale = scale
        self.relative_blender_objects: List[RelativeBlenderObject] = []

    def add_relative_blender_object(
        self, relative_blender_object: "RelativeBlenderObject"
    ) -> None:
        """
        Add a relative Blender object to the Blender Object.

        Args:
            relative_blender_object (RelativeBlenderObject): The relative Blender object to add to the Blender Object.
        """
        self.relative_blender_objects.append(relative_blender_object)

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

    @abstractmethod
    def apply_to_collection(
        self, collection: bpy.types.Collection, blender_object: bpy.types.Object
    ) -> None:
        """
        Apply the Blender object to the collection.

        Args:
            collection (bpy.types.Collection): The collection to add the Blender object to.
            blender_object (bpy.types.Object): The Blender object to add the relative Blender object to.
        """
        raise NotImplementedError(
            "The apply_to_collection method must be implemented in the subclass."
        )
