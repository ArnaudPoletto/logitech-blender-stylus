import bpy
import math
from mathutils import Vector

from utils.axis import Axis
from blender_objects.window_decorator import WindowDecorator

class Blinds(WindowDecorator):
    """
    A blind window decorator of a window.
    """

    def __init__(
        self,
        name: str,
        n_blinds: int,
        angle: float,
        vertical: bool,
    ) -> None:
        """
        Initialize the blind window decorator.

        Args:
            name (str): The name of the window decorator.
            n_blinds (int): The number of blinds.
            angle (float): The angle of the blinds.
            vertical (bool): True if the blinds are vertical, False if the blinds are horizontal.

        Raises:
            ValueError: If the number of blinds is less than 1.
            ValueError: If the angle of the blinds is not between 0 and pi.
        """
        if n_blinds < 1:
            raise ValueError("The number of blinds must be greater than 0.")
        
        if angle < 0 or angle > math.pi:
            raise ValueError("The angle of the blinds must be between 0 and pi.")

        super().__init__(
            name=name,
            location=Vector((0, 0, 0)), # The location of the blinds is always relative to the window.
        )

        self.n_blinds = n_blinds
        self.angle = angle
        self.vertical = vertical

    def apply_to_collection(
        self,
        collection: bpy.types.Collection,
        window_object: bpy.types.Object,
    ) -> None:
        """
        Apply the blinds to the window.
        
        Args:
            collection (bpy.types.Collection): The collection to which the blinds are applied.
            window_object (bpy.types.Object): The window object to which the blinds are applied.
        """
        # Add blinds to the wall
        axis = Axis.Y_AXIS if self.vertical else Axis.X_AXIS
        for i in range(self.n_blinds):
            bpy.ops.mesh.primitive_plane_add(size=1)
            blind_object = bpy.context.view_layer.objects.active
            blind_object.name = f"{window_object.name}{self.name}{i}"
            blind_object.rotation_euler = window_object.rotation_euler
            local_location = Vector((0, 0, 0))
            location_offset = 0.5 - (2 * i + 1) / (2 * self.n_blinds)
            local_location[axis.index()] = location_offset
            blind_object.location = window_object.matrix_world @ local_location
            blind_object.scale = Vector((window_object.scale.x, window_object.scale.y, 1))
            blind_object.scale[axis.index()] /= self.n_blinds
            bpy.context.view_layer.update()

            # Rotate blind to the desired angle
            rotation_axis = Axis.X_AXIS if axis == Axis.Y_AXIS else Axis.Y_AXIS
            blind_object.rotation_euler.rotate_axis(rotation_axis.value, self.angle)
            bpy.context.view_layer.update()

            # Add blind to collection
            collection.objects.link(blind_object)
            bpy.context.view_layer.update()
