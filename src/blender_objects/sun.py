# This file contains the sun class.

import bpy
from mathutils import Euler

from blender_objects.blender_object import BlenderObject


class Sun(BlenderObject):
    """
    A Sun.
    """

    def __init__(
        self,
        name: str,
        rotation: Euler,
        energy: float,
    ) -> None:
        """
        Initialize the sun.

        Args:
            name (str): The name of the sun.
            rotation (Euler): The rotation of the sun.
            energy (float): The energy of the sun.

        Raises:
            ValueError: If the energy of the sun is less than or equal to 0.
        """
        if energy <= 0:
            raise ValueError("❌ The energy of the sun must be greater than 0.")

        super(Sun, self).__init__(
            name=name,
            rotation=rotation,
        )

        self.energy = energy

    def apply_to_collection(self, collection: bpy.types.Collection) -> None:
        """
        Apply the sun to a Blender collection.
        
        Args:
            collection (bpy.types.Collection): The collection to add the sun to.
        """
        bpy.ops.object.mode_set(mode="OBJECT")

        # Define objects and properties
        bpy.ops.object.light_add(type="SUN")
        sun_object = bpy.context.object
        sun_object.name = self.name
        sun_object.location = self.location
        sun_object.rotation_euler = self.rotation
        sun_object.data.energy = self.energy

        # Add object to collection
        collection.objects.link(sun_object)
        bpy.context.view_layer.update()
