import bpy
from typing import Tuple
from mathutils import Vector

from blender_objects.relative_blender_object import RelativeBlenderObject

class Window(RelativeBlenderObject):
    """
    A window in a wall.
    """

    def __init__(
        self,
        name: str,
        relative_location: Vector,
        scale: Vector,
    ) -> None:
        """
        Initialize the window.

        Args:
            name (str): The name of the window.
            relative_location (Vector): The relative location of the window from the location of the wall as a 2D vector.
            scale (Vector): The scale of the window as a 2D vector.

        Raises:
            ValueError: If the location is not a 2D vector.
            ValueError: If the scale is not a 2D vector.
        """
        if len(relative_location) != 2:
            raise ValueError("❌ The location must be a 2D vector.")
        if len(scale) != 2:
            raise ValueError("❌ The scale must be a 2D vector.")
        
        relative_location = Vector((relative_location.x, relative_location.y, 0))
        scale = Vector((scale.x, scale.y, 1))
        super(Window, self).__init__(
            name=name,
            relative_location=relative_location,
            scale=scale,
        )
        
    def get_bounds(
        self,
    ) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
        min_x = -self.scale.x / 2
        max_x = self.scale.x / 2
        min_y = -self.scale.y / 2
        max_y = self.scale.y / 2
        
        return (min_x, max_x), (min_y, max_y), (0, 0)

    def apply_to_collection(
        self,
        collection: bpy.types.Collection,
        blender_object: bpy.types.Object,
    ) -> None:
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Add cube of window shape into the wall
        bpy.ops.mesh.primitive_cube_add(size=1)
        window_object = bpy.context.view_layer.objects.active
        window_object.name = f"{blender_object.name}{self.name}"
        window_object.rotation_euler = blender_object.rotation_euler
        scaled_relative_location = Vector((
            self.location.x / blender_object.scale.x,
            self.location.y / blender_object.scale.y,
            0,
        ))
        window_object.location = (
            blender_object.matrix_world @ scaled_relative_location
        )  # Location relative to the wall
        window_object.scale = self.scale
        bpy.context.view_layer.update()

        # Apply boolean modifier to the wall
        boolean_modifier = blender_object.modifiers.new(
            name=f"{self.name}BoolDiff", type="BOOLEAN"
        )
        boolean_modifier.object = window_object
        boolean_modifier.operation = "DIFFERENCE"

        # Apply modifiers to the wall
        bpy.ops.object.select_all(action="DESELECT")
        blender_object.select_set(True)
        bpy.context.view_layer.objects.active = blender_object
        bpy.ops.object.convert(target="MESH")

        # Add window decorators
        for relative_blender_object in self.relative_blender_objects:
            relative_blender_object.apply_to_collection(collection, window_object)

        # Delete window object
        bpy.ops.object.select_all(action="DESELECT")
        window_object.select_set(True)
        bpy.ops.object.delete()
        bpy.context.view_layer.update()
