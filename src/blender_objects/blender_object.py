# This file contains the blender object class, which is the base class for all blender objects.

import bpy
from typing import List
from abc import abstractmethod
from mathutils import Vector, Euler


class BlenderObject:
    """
    A Blender object.
    """

    def __init__(
        self,
        name: str,
        location: Vector = Vector((0, 0, 0)),
        rotation: Euler = Euler((0, 0, 0)),
        scale: Vector = Vector((1, 1, 1)),
    ) -> None:
        """
        Initialize the Blender object.

        Args:
            name (str): The name of the Blender object.
            location (Vector): The location of the Blender object in the world as a 3D vector. Defaults to the origin.
            rotation (Vector): The rotation of the Blender object in the world as a 3D vector. Defaults to no rotation.
            scale (Vector): The scale of the Blender object as a 3D vector. Defaults to no scaling.

        Raises:
            ValueError: If the location is not a 3D vector.
            ValueError: If the rotation is not a 3D vector.
            ValueError: If the scale is not a 3D vector.
            ValueError: If the scale values are not positive.
        """
        if len(location) != 3:
            raise ValueError("❌ The location must be a 3D vector.")
        if len(rotation) != 3:
            raise ValueError("❌ The rotation must be a 3D vector.")
        if len(scale) != 3:
            raise ValueError("❌ The scale must be a 3D vector.")
        if any(value <= 0 for value in scale):
            raise ValueError("❌ The scale values must be positive.")

        self.name = name
        self.location = location
        self.rotation = rotation
        self.scale = scale
        self.relative_blender_objects: List[BlenderObject] = []

    def add_relative_blender_object(
        self, relative_blender_object: "BlenderObject"
    ) -> None:
        """
        Add a relative Blender object to the Blender Object.

        Args:
            relative_blender_object (BlenderObject): The relative Blender object to add to the Blender Object.
        """
        self.relative_blender_objects.append(relative_blender_object)

    @abstractmethod
    def apply_to_collection(self, collection: bpy.types.Collection) -> None:
        """
        Apply the Blender object to the collection.

        Args:
            collection (bpy.types.Collection): The collection to add the Blender object to.
        """
        raise NotImplementedError(
            "❌ The apply_to_collection method must be implemented in the subclass."
        )
