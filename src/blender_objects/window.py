import bpy
import math
from enum import Enum
from typing import List, Tuple
from mathutils import Vector, Matrix

from utils.axis import Axis
from blender_objects.wall_decorator import WallDecorator
from blender_objects.window_decorator import WindowDecorator

# TODO: Add material to the window decorators / windows

class Window(WallDecorator):
    """
    A window in a wall.
    """

    def __init__(
        self,
        name: str,
        location: Vector,
        scale: Vector,
    ) -> None:
        """
        Initialize the window.

        Args:
            name (str): The name of the window.
            location (Vector): The relative location of the window from the location of the wall as a 2D vector.
            scale (Vector): The scale of the window as a 2D vector.

        Raises:
            ValueError: If the location is not a 2D vector.
            ValueError: If the scale is not a 2D vector.
        """
        if len(location) != 2:
            raise ValueError("The location must be a 2D vector.")

        if len(scale) != 2:
            raise ValueError("The scale must be a 2D vector.")

        location = Vector((location.x, location.y, 0))
        super().__init__(
            name=name,
            location=location,
        )

        self.scale = Vector((scale.x, scale.y, 1))
        self.decorators = []

    def add_decorator(self, decorator: WindowDecorator) -> None:
        """
        Add a decorator to the window.

        Args:
            decorator (WindowDecorator): The decorator to add.

        Raises:
            ValueError: If the decorator is already added.
        """
        self.decorators.append(decorator)

    def apply_to_collection(
        self,
        collection: bpy.types.Collection,
        wall_object: bpy.types.Object,
        wall_object_matrix_world: Matrix,
    ) -> None:
        """
        Apply the window to the wall.

        Args:
            collection (bpy.types.Collection): The collection to add the window to.
            wall_object (bpy.types.Object): The wall object to add the window to.
            wall_object_matrix_world (bpy.types.Matrix): The matrix_world of the wall object.
        """
        # Add cube of window shape into the wall
        bpy.ops.mesh.primitive_cube_add(size=1)
        window_object = bpy.context.view_layer.objects.active
        window_object.name = f"{wall_object.name}{self.name}"
        window_object.rotation_euler = wall_object.rotation_euler
        window_object.location = (
            wall_object_matrix_world @ self.location
        )  # Location relative to the wall
        window_object.scale = self.scale
        bpy.context.view_layer.update()

        # Apply boolean modifier to the wall
        boolean_modifier = wall_object.modifiers.new(
            name=f"{self.name}BoolDiff", type="BOOLEAN"
        )
        boolean_modifier.object = window_object
        boolean_modifier.operation = "DIFFERENCE"

        # Apply modifiers to the wall
        bpy.ops.object.select_all(action="DESELECT")
        wall_object.select_set(True)
        bpy.context.view_layer.objects.active = wall_object
        bpy.ops.object.convert(target="MESH")

        # Add window decorators
        for decorator in self.decorators:
            decorator.apply_to_collection(collection, window_object)

        # Delete window object
        bpy.ops.object.select_all(action="DESELECT")
        window_object.select_set(True)
        bpy.ops.object.delete()
