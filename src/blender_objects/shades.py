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

        super(Shades, self).__init__(name=name)

        self.shade_ratio = shade_ratio
        self.transmission = transmission

    def apply_to_collection(
        self,
        collection: bpy.types.Collection,
        blender_object: bpy.types.Object,
    ) -> None:
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Add shade to the wall
        bpy.ops.mesh.primitive_plane_add(size=1)
        shape_object = bpy.context.view_layer.objects.active
        shape_object.name = f"{blender_object.name}{self.name}"
        shape_object.rotation_euler = blender_object.rotation_euler
        location_offset = 0.5 - self.shade_ratio / 2
        shape_object.location = blender_object.matrix_world @ Vector(
            (0, location_offset, 0)
        )
        shape_object.scale = Vector((blender_object.scale.x, blender_object.scale.y * self.shade_ratio, 1))
        
        # Change material of shade to make it transparent
        material_name = f"Shade{self.transmission}"
        if material_name not in bpy.data.materials:
            bpy.data.materials.new(name=material_name)
            material = bpy.data.materials[material_name]
            material.use_nodes = True
            material.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = self.transmission
        shape_object.data.materials.append(bpy.data.materials[material_name])
        
            
        # Add shade to collection
        collection.objects.link(shape_object)
        bpy.context.view_layer.update()
