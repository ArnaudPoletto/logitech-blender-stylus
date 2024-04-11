import bpy
import math
from mathutils import Vector, Euler

from blender_objects.blender_object import BlenderObject


class Camera(BlenderObject):
    """
    A camera.
    """
    def __init__(
        self,
        name: str,
        location: Vector,
        rotation: Euler,
        ) -> None:
        """
        Initialize the camera.
        
        Args:
            name (str): The name of the Camera.
            location (Vector): The location of the Camera in the world as a 3D vector. Defaults to the origin.
            rotation (Vector): The rotation of the Camera in the world as a 3D vector. Defaults to no rotation.
        """
        super(Camera, self).__init__(
            name=name,
            location=location,
            rotation=rotation,
            scale=Vector((1, 1, 1)),
        )
        
    def apply_to_collection(self, collection: bpy.types.Collection) -> None:
        bpy.ops.object.mode_set(mode="OBJECT")
        
        # Define the camera
        camera = bpy.data.cameras.new(self.name)
        camera_object = bpy.data.objects.new(self.name, camera)
        collection.objects.link(camera_object)
        camera_object.data.type = 'PANO'
        camera_object.data.panorama_type = 'FISHEYE_EQUISOLID'
        camera_object.location = self.location
        camera_object.rotation_euler = self.rotation
        camera_object.data.fisheye_lens = 15.0 # TODO: remove hardcoding
        camera_object.data.fisheye_fov = math.pi # TODO: remove hardcoding
        
        bpy.context.view_layer.update()
