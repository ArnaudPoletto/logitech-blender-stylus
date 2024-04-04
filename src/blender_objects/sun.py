import bpy
from mathutils import Vector, Euler

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
            raise ValueError("The energy of the sun must be greater than 0.")
        
        location = Vector((0, 0, 0))
        super(Sun, self).__init__(
            name=name, 
            location=location,
            rotation=rotation,
            )

        self.energy = energy

    def apply_to_collection(self, collection: bpy.types.Collection) -> None:
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
