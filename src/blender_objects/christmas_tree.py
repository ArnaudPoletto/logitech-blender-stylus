import bpy
import math
import random
from typing import Tuple
from mathutils import Vector

from blender_objects.relative_blender_object import RelativeBlenderObject


class ChristmasTree(RelativeBlenderObject):
    """
    A Christmas tree.
    """

    def __init__(
        self,
        name: str,
        relative_location: Vector,
        height: float,
        radius: float,
        n_leds: int,
        led_radius_range: Tuple[float, float],
        emission_range: Tuple[float, float],
        flicker_probability: float,
    ) -> None:
        """
        Initialize the Christmas tree.

        Args:
            name (str): The name of the Christmas tree.
            relative_location (Vector): The relative location of the Christmas tree from the location of the Blender object as a 2D vector.
            height (float): The height of the Christmas tree.
            radius (float): The radius of the Christmas tree.
            n_leds (int): The number of LEDs on the Christmas tree.
            led_radius_range (Tuple[float, float]): The range of the radius of the LEDs.
            emission_range (Tuple[float, float]): The range of the emission of the LEDs.
            flicker_probability (float): The probability of each LEDs flickering at each frame.

        Raises:
            ValueError: If the height of the Christmas tree is less than or equal to 0.
            ValueError: If the radius of the Christmas tree is less than or equal to 0.
            ValueError: If the number of LEDs is less than 1.
            ValueError: If the minimum radius of the LEDs is less than 0.
            ValueError: If the maximum radius of the LEDs is less than the minimum radius.
            ValueError: If the minimum emission of the LEDs is less than 0.
            ValueError: If the maximum emission of the LEDs is less than the minimum emission.
        """
        if height <= 0:
            raise ValueError("The height of the Christmas tree must be greater than 0.")
        if radius <= 0:
            raise ValueError("The radius of the Christmas tree must be greater than 0.")
        if n_leds <= 0:
            raise ValueError("The number of LEDs must be greater than 0.")
        if led_radius_range[0] <= 0:
            raise ValueError("The minimum radius of the LEDs must be greater than 0.")
        if led_radius_range[1] < led_radius_range[0]:
            raise ValueError(
                "The maximum radius of the LEDs must be greater than the minimum radius."
            )
        if emission_range[0] < 0:
            raise ValueError("The minimum emission of the LEDs must be greater than 0.")
        if emission_range[1] < emission_range[0]:
            raise ValueError(
                "The maximum emission of the LEDs must be greater than the minimum emission."
            )
        if flicker_probability < 0 or flicker_probability > 1:
            raise ValueError("The flicker probability must be between 0 and 1.")

        # Define relative location at center of the base and object relative location at the center of the object
        self.object_relative_location = Vector(
            (relative_location.x, relative_location.y, 0)
        )
        relative_location = Vector(
            (relative_location.x, relative_location.y, height / 2)
        )
        super(ChristmasTree, self).__init__(
            name=name, relative_location=relative_location
        )

        self.height = height
        self.radius = radius
        self.n_leds = n_leds
        self.led_radius_range = led_radius_range
        self.emission_range = emission_range
        self.flicker_probability = flicker_probability

    def get_bounds(
        self,
    ) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
        min_x = -self.radius
        max_x = self.radius
        min_y = -self.radius
        max_y = self.radius

        return (min_x, max_x), (min_y, max_y), (0, 0)

    def apply_to_collection(
        self, collection: bpy.types.Collection, blender_object: bpy.types.Object
    ) -> None:
        bpy.ops.object.mode_set(mode="OBJECT")

        # Add Christmas tree to the collection, a cone with a cylinder as the base
        scaled_relative_location = Vector(
            (
                self.location.x / blender_object.scale.x,
                self.location.y / blender_object.scale.y,
                self.location.z / blender_object.scale.z,
            )
        )
        location = blender_object.matrix_world @ scaled_relative_location
        bpy.ops.mesh.primitive_cone_add(
            vertices=128,
            radius1=self.radius,
            radius2=0,
            depth=self.height,
            location=location,
        )
        christmas_tree_object = bpy.context.object
        christmas_tree_object.name = self.name
        collection.objects.link(christmas_tree_object)
        bpy.context.view_layer.update()

        # Add LEDs to the Christmas tree uniformly distributed on the cone surface
        led_objects = []
        for i in range(self.n_leds):
            theta = random.uniform(0, 1) * 2 * math.pi
            a = random.uniform(0, 1)
            radius = self.radius * math.sqrt(a)
            x = radius * math.cos(theta)
            y = radius * math.sin(theta)
            z = (
                -self.height * math.sqrt(((x * x) + (y * y))) / self.radius
                + self.height
            )

            # Add object
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=random.uniform(*self.led_radius_range),
            )
            led_object = bpy.context.object
            led_object.name = f"{self.name}LED{i}"

            # Set location
            led_location = Vector(
                (
                    location.x + x,
                    location.y + y,
                    self.object_relative_location.z + z,
                )
            )
            scaled_led_location = Vector(
                (
                    led_location.x / blender_object.scale.x,
                    led_location.y / blender_object.scale.y,
                    led_location.z / blender_object.scale.z,
                )
            )
            led_location = blender_object.matrix_world @ scaled_led_location
            led_object.location = led_location

            # Set LED material and emission
            led_material = bpy.data.materials.new(name=f"{self.name}LED{i}Material")
            led_material.use_nodes = True
            led_material.node_tree.nodes.clear()
            led_material_output = led_material.node_tree.nodes.new(
                "ShaderNodeOutputMaterial"
            )
            led_emission = led_material.node_tree.nodes.new("ShaderNodeEmission")
            emission_strength = random.uniform(*self.emission_range)
            led_emission.inputs["Strength"].default_value = emission_strength
            led_material.node_tree.links.new(
                led_material_output.inputs["Surface"],
                led_emission.outputs["Emission"],
            )
            led_object.data.materials.append(led_material)

            # Set flicker probability starting state
            if random.random() < self.flicker_probability:
                led_object.hide_render = True

            led_objects.append(led_object)

            # Add LED to the collection
            collection.objects.link(led_object)
            bpy.context.view_layer.update()

        # Set flicker animation
        start_frame = bpy.context.scene.frame_start
        end_frame = bpy.context.scene.frame_end
        for frame in range(start_frame, end_frame + 1):
            for led_object in led_objects:
                if random.random() < self.flicker_probability:
                    led_object.hide_render = not led_object.hide_render
                led_object.keyframe_insert(data_path="hide_render", frame=frame)
