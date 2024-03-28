import bpy
import math
import random
from mathutils import Vector

from blender_objects.blender_object import BlenderObject

class ChristmasTree(BlenderObject):
    """
    A Christmas tree.
    """
    
    def __init__(
        self,
        name: str,
        location: Vector,
        height: float,
        radius: float,
        n_leds: int,
    ) -> None:
        """
        Initialize the Christmas tree.
        
        Args:
            name (str): The name of the Christmas tree.
            location (Vector): The location of the Christmas tree from the base.
            height (float): The height of the Christmas tree.
            radius (float): The radius of the Christmas tree.
            n_leds (int): The number of LEDs on the Christmas tree.
        """
        if height <= 0:
            raise ValueError("The height of the Christmas tree must be greater than 0.")
        
        if radius <= 0:
            raise ValueError("The radius of the Christmas tree must be greater than 0.")
        
        if n_leds < 1:
            raise ValueError("The number of LEDs must be greater than 0.")
        
        # Change location to the base of the Christmas tree
        location.z += height / 2
        
        super(ChristmasTree, self).__init__(name=name, location=location)
        
        self.height = height
        self.radius = radius
        self.n_leds = n_leds
        
    def apply_to_collection(self, collection: bpy.types.Collection) -> None:
        """
        Apply the Christmas tree to the collection.
        
        Args:
            collection (bpy.types.Collection): The collection to add the Christmas tree to.
        """
        # Add Christmas tree to the collection, a cone with a cylinder as the base
        bpy.ops.mesh.primitive_cone_add(
            vertices=128,
            radius1=self.radius,
            radius2=0,
            depth=self.height,
            location=self.location,
        )
        christmas_tree_object = bpy.context.object
        christmas_tree_object.name = self.name
        
        # set transparent tecture
        christmas_tree_object
        
        # Add LEDs to the Christmas tree
        for i in range(self.n_leds):
            x = random.uniform(-self.radius, self.radius)
            y_bound = math.sin(math.acos(x / self.radius)) * self.radius
            y = random.uniform(-y_bound, y_bound)
            z = -self.height * math.sqrt(((x * x) + (y * y))) / self.radius + self.height + 1e-1
            led_location = Vector((
                self.location.x + x,
                self.location.y + y,
                self.location.z + z - self.height / 2,
            ))
            bpy.ops.object.light_add(
                type='POINT',
                radius=0.1,
                location=led_location,
            )
            led_object = bpy.context.object
            led_object.name = f"{self.name}LED{i}"
            led_object.data.energy = 10
            led_object.data.color = (1, 1, 1)
        