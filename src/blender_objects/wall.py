import bpy
import numpy as np
from mathutils import Vector, Euler

from blender_objects.blender_object import BlenderObject
from blender_objects.relative_blender_object import RelativeBlenderObject


class Wall(BlenderObject):
    """
    A wall in a scene.
    """

    def __init__(
        self,
        name: str,
        location: Vector,
        rotation: Euler,
        scale: Vector,
    ) -> None:
        """
        Initialize the wall.

        Args:
            name (str): The name of the wall.
            location (Vector): The location of the wall in the world as a 3D vector.
            rotation (Euler): The rotation of the wall in the world as a 3D vector.
            scale (Vector): The scale of the wall as a 2D vector.

        Raises:
            ValueError: If the scale is not a 2D vector.
        """
        if len(scale) != 2:
            raise ValueError("❌ The scale must be a 2D vector.")

        scale = Vector((scale.x, scale.y, 1))
        super(Wall, self).__init__(
            name=name,
            location=location,
            rotation=rotation,
            scale=scale,
        )

    def _relative_blender_object_is_in_bounds(
        self, relative_blender_object: RelativeBlenderObject
    ) -> bool:
        """
        Check if the relative Blender object is in bounds of the wall.

        Args:
            relative_blender_object (RelativeBlenderObject): The relative Blender object to add to the wall.

        Returns:
            bool: Whether the relative Blender object is in bounds of the wall.
        """
        (min_x, max_x), (min_y, max_y), _ = relative_blender_object.get_bounds()
        relative_blender_object_min_x = (
            relative_blender_object.location.x + min_x
        )
        relative_blender_object_max_x = (
            relative_blender_object.location.x + max_x
        )
        relative_blender_object_min_y = (
            relative_blender_object.location.y + min_y
        )
        relative_blender_object_max_y = (
            relative_blender_object.location.y + max_y
        )
        wall_min_x = -self.scale.x / 2
        wall_max_x = self.scale.x / 2
        wall_min_y = -self.scale.y / 2
        wall_max_y = self.scale.y / 2

        return (
            relative_blender_object_min_x >= wall_min_x
            and relative_blender_object_max_x <= wall_max_x
            and relative_blender_object_min_y >= wall_min_y
            and relative_blender_object_max_y <= wall_max_y
        )

    def _relative_blender_object_does_not_intersect(
        self, relative_blender_object: RelativeBlenderObject
    ) -> bool:
        """
        Check if the relative Blender object does not interset existing decorators.

        Args:
            relative_blender_object (RelativeBlenderObject): The relative Blender object to add to the wall.

        Returns:
            bool: Whether the decorator does not intersect existing decorators.
        """
        (min_x, max_x), (min_y, max_y), _ = relative_blender_object.get_bounds()
        relative_blender_object_min_x = (
            relative_blender_object.location.x + min_x
        )
        relative_blender_object_max_x = (
            relative_blender_object.location.x + max_x
        )
        relative_blender_object_min_y = (
            relative_blender_object.location.y + min_y
        )
        relative_blender_object_max_y = (
            relative_blender_object.location.y + max_y
        )
        for other in self.relative_blender_objects:
            (other_min_x, other_max_x), (other_min_y, other_max_y), _ = (
                other.get_bounds()
            )
            other_min_x = other.location.x + other_min_x
            other_max_x = other.location.x + other_max_x
            other_min_y = other.location.y + other_min_y
            other_max_y = other.location.y + other_max_y

            if (
                relative_blender_object_min_x <= other_max_x
                and relative_blender_object_max_x >= other_min_x
                and relative_blender_object_min_y <= other_max_y
                and relative_blender_object_max_y >= other_min_y
            ):
                return False

        return True

    def add_relative_blender_object(
        self, relative_blender_object: RelativeBlenderObject
    ) -> None:
        if not self._relative_blender_object_is_in_bounds(relative_blender_object):
            raise ValueError(
               f"❌ Relative Blender object {relative_blender_object.name} is not in bounds of the wall."
            )

        if not self._relative_blender_object_does_not_intersect(
            relative_blender_object
        ):
            raise ValueError(
                f"❌ Relative Blender object {relative_blender_object.name} intersects with existing decorators."
            )

        super(Wall, self).add_relative_blender_object(relative_blender_object)

    def apply_to_collection(
        self,
        collection: bpy.types.Collection,
    ) -> None:
        # Add wall
        bpy.ops.mesh.primitive_plane_add(size=1)
        wall_object = bpy.context.view_layer.objects.active
        wall_object.name = self.name
        wall_object.rotation_euler = self.rotation
        wall_object.location = self.location
        wall_object.scale = self.scale
        bpy.context.view_layer.update()

        # Add relative Blender objects
        for relative_blender_object in self.relative_blender_objects:
            relative_blender_object.apply_to_collection(collection, wall_object)

        # Link wall to collection
        collection.objects.link(wall_object)
        bpy.context.view_layer.update()
