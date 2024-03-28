import bpy
import math
from mathutils import Vector

from utils.axis import Axis
from blender_objects.window_decorator import WindowDecorator

class Shades(WindowDecorator):
    """
    A shades window decorator of a window.
    """

    def __init__(
        self,
        name: str,
        shade_ratio: float,
        transmission: float,
    ) -> None:
        """
        Initialize the shades window decorator.

        Args:
            name (str): The name of the window decorator.
            shade_ratio (float): The ratio of the window that is shaded.
            transmission (float): The material transmission of the shades, to make them transparent.

        Raises:
            ValueError: If the shade ratio is not between 0 and 1.
            ValueError: If the transmission is not between 0 and 1.
        """
        if shade_ratio < 0 or shade_ratio > 1:
            raise ValueError("The shade ratio must be between 0 and 1.")
        if transmission < 0 or transmission > 1:
            raise ValueError("The transmission must be between 0 and 1.")

        super().__init__(
            name=name,
            location=Vector((0, 0, 0)), # The location of the blinds is always relative to the window.
        )

        self.shade_ratio = shade_ratio
        self.transmission = transmission

    def apply_to_collection(
        self,
        collection: bpy.types.Collection,
        window_object: bpy.types.Object,
    ) -> None:
        """
        Apply the shades to the window.
        
        Args:
            collection (bpy.types.Collection): The collection to which the shades are applied.
            window_object (bpy.types.Object): The window object to which the shades are applied.
        """
        # Add shade to the wall
        bpy.ops.mesh.primitive_plane_add(size=1)
        shape_object = bpy.context.view_layer.objects.active
        shape_object.name = f"{window_object.name}{self.name}"
        shape_object.rotation_euler = window_object.rotation_euler
        location_offset = 0.5 - self.shade_ratio / 2
        shape_object.location = window_object.matrix_world @ Vector(
            (0, location_offset, 0)
        )
        shape_object.scale = Vector((window_object.scale.x, window_object.scale.y * self.shade_ratio, 1))
        
        # Change material of shade to make it transparent
        if "Shade" not in bpy.data.materials:
            bpy.data.materials.new(name="Shade")
            material = bpy.data.materials["Shade"]
            material.use_nodes = True
            material.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = self.transmission
        shape_object.data.materials.append(bpy.data.materials["Shade"])
        
            
        # Add shade to collection
        collection.objects.link(shape_object)
        bpy.context.view_layer.update()
