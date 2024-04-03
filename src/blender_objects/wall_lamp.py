import bpy
from mathutils import Vector, Matrix

from blender_objects.blender_object import BlenderObject

# TODO: add to room
class WallLamp(BlenderObject):
    """
    A Wall Lamp.
    """

    def __init__(
        self,
        name: str,
        location: Vector,
        scale: Vector
    ) -> None:
        """
        Initialize the wall lamp.

        Args:
            name (str): The name of the wall lamp.
            location (Vector): The  relative location of the wall lamp from the location of the wall as a 2D vector.
            scale (Vector): The scale of the wall lamp as a 2D vector.
            
        Raises:
            ValueError: If the location is not a 2D vector.
            ValueError: If the scale is not a 2D vector.
            ValueErrir: If the scale values are not positive.
        """
        
        if len(location) != 2:
            raise ValueError("The location must be a 2D vector.")
        
        if len(scale) != 2:
            raise ValueError("The scale must be a 2D vector.")
        
        if any(value <= 0 for value in scale):
            raise ValueError("The scale values must be positive.")
        
        location = Vector((location.x, location.y, 0))
        super(WallLamp, self).__init__(name=name, location=location)
        
        self.scale = Vector((scale.x, scale.y, 1))
        
    def apply_to_collection(
        self,
        collection: bpy.types.Collection,
        wall_object: bpy.types.Object,
        wall_object_matrix_world: Matrix,
    ) -> None:
        bpy.ops.object.mode_set(mode="OBJECT")

        bpy.ops.mesh.primitive_cube_add(size=1)
        wall_lamp_object = bpy.context.view_layer.objects.active
        wall_lamp_object.name = self.name
        wall_lamp_object.rotation_euler = wall_object.rotation_euler
        wall_lamp_object.location = wall_object_matrix_world @ self.location
        wall_lamp_object.scale = Vector((self.width, self.height, self.depth))
        collection.objects.link(wall_lamp_object)
        bpy.context.view_layer.update()
