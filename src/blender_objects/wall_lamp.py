# This file contains the wall lamp class.

import bpy
from typing import Tuple
from mathutils import Vector

from blender_objects.relative_blender_object import RelativeBlenderObject


class WallLamp(RelativeBlenderObject):
    """
    A Wall Lamp.
    """

    def __init__(
        self,
        name: str,
        relative_location: Vector,
        scale: Vector,
        emission_strength: float,
    ) -> None:
        """
        Initialize the wall lamp.

        Args:
            name (str): The name of the wall lamp.
            relative_location (Vector): The relative location of the wall lamp from the location of the wall as a 2D vector.
            scale (Vector): The scale of the wall lamp as a 2D vector.
            emission_strength (float): The emission strength of the wall lamp.

        Raises:
            ValueError: If the location is not a 2D vector.
            ValueError: If the scale is not a 2D vector.
            ValueError: If the scale values are not positive.
            ValueError: If the strength of the wall lamp is less than or equal to 0.
        """
        if len(scale) != 2:
            raise ValueError("❌ The scale must be a 2D vector.")
        if any(value <= 0 for value in scale):
            raise ValueError("❌ The scale values must be positive.")
        if emission_strength <= 0:
            raise ValueError(
                "❌ The emission strength of the wall lamp must be greater than 0."
            )

        relative_location = Vector((relative_location.x, relative_location.y, 0))
        scale = Vector((scale.x, scale.y, 0.1))
        super(WallLamp, self).__init__(
            name=name, relative_location=relative_location, scale=scale
        )

        self.emission_strength = emission_strength

    def get_bounds(
        self,
    ) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
        """
        Get the bounds of the wall lamp.
        
        Returns:
            Tuple[float, float]: The bounds of the wall lamp in the x-direction.
            Tuple[float, float]: The bounds of the wall lamp in the y-direction.
            Tuple[float, float]: The bounds of the wall lamp in the z-direction.
        """
        min_x = -self.scale.x / 2
        max_x = self.scale.x / 2
        min_y = -self.scale.y / 2
        max_y = self.scale.y / 2

        return (min_x, max_x), (min_y, max_y), (0.0, 0.0)

    def apply_to_collection(
        self,
        collection: bpy.types.Collection,
        blender_object: bpy.types.Object,
    ) -> None:
        """
        Apply the wall lamp to a Blender object.
        
        Args:
            collection (bpy.types.Collection): The collection to add the wall lamp to.
            blender_object (bpy.types.Object): The Blender object to decorate.
        """
        bpy.ops.object.mode_set(mode="OBJECT")

        # Create the wall lamp object
        bpy.ops.mesh.primitive_cube_add(size=1)
        wall_lamp_object = bpy.context.view_layer.objects.active
        wall_lamp_object.name = self.name
        wall_lamp_object.rotation_euler = blender_object.rotation_euler
        scaled_relative_location = Vector(
            (
                self.location.x / blender_object.scale.x,
                self.location.y / blender_object.scale.y,
                self.location.z / blender_object.scale.z,
            )
        )
        wall_lamp_object.location = (
            blender_object.matrix_world @ scaled_relative_location
        )
        wall_lamp_object.scale = self.scale
        bpy.context.view_layer.update()

        # Set wall lamp material and emission
        wall_lamp_material = bpy.data.materials.new(name=f"{self.name}Material")
        wall_lamp_material.use_nodes = True
        wall_lamp_material.node_tree.nodes.clear()
        wall_lamp_material_output = wall_lamp_material.node_tree.nodes.new(
            "ShaderNodeOutputMaterial"
        )
        wall_lamp_emission = wall_lamp_material.node_tree.nodes.new(
            "ShaderNodeEmission"
        )
        wall_lamp_emission.inputs["Strength"].default_value = self.emission_strength
        wall_lamp_material.node_tree.links.new(
            wall_lamp_material_output.inputs["Surface"],
            wall_lamp_emission.outputs["Emission"],
        )
        wall_lamp_object.data.materials.append(wall_lamp_material)

        # Link the wall lamp object to the collection
        collection.objects.link(wall_lamp_object)
        bpy.context.view_layer.update()
