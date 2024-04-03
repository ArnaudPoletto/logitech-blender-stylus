import bpy
from mathutils import Vector, Matrix

from blender_objects.window_decorator import WindowDecorator
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
            ValueError: If the scale values are not positive.
        """
        if len(relative_location) != 2:
            raise ValueError("The location must be a 2D vector.")

        if len(scale) != 2:
            raise ValueError("The scale must be a 2D vector.")
        
        if any(value <= 0 for value in scale):
            raise ValueError("The scale values must be positive.")
        
        relative_location = Vector((relative_location.x, relative_location.y, 0))
        scale = Vector((scale.x, scale.y, 1))
        super(Window, self).__init__(
            name=name,
            relative_location=relative_location,
            scale=scale,
        )

    def apply_to_collection(
        self,
        collection: bpy.types.Collection,
        wall_object: bpy.types.Object,
    ) -> None:
        """
        Apply the window to the wall.

        Args:
            collection (bpy.types.Collection): The collection to add the window to.
            wall_object (bpy.types.Object): The wall object to add the window to.
            wall_object_matrix_world (bpy.types.Matrix): The matrix_world of the wall object.
        """
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Add cube of window shape into the wall
        bpy.ops.mesh.primitive_cube_add(size=1)
        window_object = bpy.context.view_layer.objects.active
        window_object.name = f"{wall_object.name}{self.name}"
        window_object.rotation_euler = wall_object.rotation_euler
        window_object.location = (
            wall_object.matrix_world @ self.relative_location
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
        for relative_blender_object in self.relative_blender_objects:
            relative_blender_object.apply_to_collection(collection, window_object)

        # Delete window object
        bpy.ops.object.select_all(action="DESELECT")
        window_object.select_set(True)
        bpy.ops.object.delete()
        bpy.context.view_layer.update()
