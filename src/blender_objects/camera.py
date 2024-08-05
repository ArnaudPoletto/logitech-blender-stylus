# This file contains the camera class.

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
        type: str,  # TODO: as enum and multiple camera types
        focal_length: float,
        fov: float = None,
    ) -> None:
        """
        Initialize the camera.

        Args:
            name (str): The name of the Camera.
            location (Vector): The location of the Camera in the world as a 3D vector. Defaults to the origin.
            rotation (Vector): The rotation of the Camera in the world as a 3D vector. Defaults to no rotation.
            type (str): The type of the camera.
            focal_length (float): The focal length of the camera.
            fov (float): The field of view of the camera. Defaults to None.

        Raises:
            ValueError: If the camera type is not 'PERSP', 'ORTHO', or 'PANO'.
            ValueError: If the focal length is less than or equal to 0.
            ValueError: If the field of view is less than or equal to 0 or greater than 2 * pi.
        """
        if type not in ["PERSP", "ORTHO", "PANO"]:
            raise ValueError("❌ The camera type must be 'PERSP', 'ORTHO', or 'PANO'.")
        if focal_length <= 0:
            raise ValueError("❌ The focal length must be greater than 0.")
        if fov <= 0 or fov > 2 * math.pi:
            raise ValueError("❌ The field of view must be between 0 and 2 * pi.")

        super(Camera, self).__init__(
            name=name,
            location=location,
            rotation=rotation,
        )

        self.type = type
        self.focal_length = focal_length
        self.fov = fov

    def apply_to_collection(self, collection: bpy.types.Collection) -> None:
        """
        Apply the camera to a Blender collection.

        Args:
            collection (bpy.types.Collection): The collection to add the camera to.
        """
        bpy.ops.object.mode_set(mode="OBJECT")

        # Define the camera
        camera = bpy.data.cameras.new(self.name)
        camera_object = bpy.data.objects.new(self.name, camera)
        # replace collection by scene
        bpy.context.scene.collection.objects.link(
            camera_object
        )  # Add the camera to the scene, not the given collection
        camera_object.data.type = self.type

        # Panoramic camera
        if self.type == "PANO":
            camera_object.data.panorama_type = "FISHEYE_EQUISOLID"
            if self.fov is None:
                raise ValueError(
                    "The field of view must be provided for a panoramic camera."
                )
            camera_object.data.fisheye_fov = self.fov
            camera_object.data.fisheye_lens = self.focal_length
        if self.type == "PERSP":
            camera_object.data.lens = self.focal_length

        camera_object.location = self.location
        camera_object.rotation_euler = self.rotation

        bpy.context.view_layer.update()
