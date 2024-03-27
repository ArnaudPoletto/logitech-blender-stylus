import bpy
from typing import List
from mathutils import Vector

from blender_objects.window import Window
from blender_objects.blender_object import BlenderObject

class Wall(BlenderObject):
    """
    A wall in a scene.
    """

    def __init__(
        self,
        name: str,
        location: Vector,
        rotation: Vector,
        scale: Vector,
        centered: bool,
    ) -> None:
        """
        Initialize the wall.

        Args:
            name (str): The fixed origin point of the wall, either one of the corners or the center depending on the centered flag.
            location (Vector): The location of the wall as a 3D vector.
            rotation (Vector): The rotation of the wall as a 3D vector.
            scale (Vector): The scale of the wall as a 2D vector.
            centered (bool): Whether the rectangle is centered at the origin.

        Raises:
            ValueError: If the location is not a 3D vector.
            ValueError: If the rotation is not a 3D vector.
            ValueError: If the scale is not a 2D vector.
        """
        if len(location) != 3:
            raise ValueError("The location must be a 3D vector.")

        if len(rotation) != 3:
            raise ValueError("The rotation must be a 3D vector.")

        if len(scale) != 2:
            raise ValueError("The scale must be a 2D vector.")

        # Change location to the center of the wall if centered
        if not centered:
            location -= Vector((scale.x / 2, scale.y / 2, 0))

        super().__init__(
            name=name,
            location=location,
        )

        self.rotation = rotation
        self.scale = Vector((scale.x, scale.y, 1))

        self.windows: List[Window] = []

    def _window_is_in_bounds(self, window) -> bool:
        """
        Check if the window is in bounds of the wall.

        Args:
            wall (bpy.types.Object): The wall to add the window to.

        Returns:
            bool: Whether the window is in bounds of the wall.
        """
        window_min_x = window.location.x - window.scale.x / 2
        window_max_x = window.location.x + window.scale.x / 2
        window_min_y = window.location.y - window.scale.y / 2
        window_max_y = window.location.y + window.scale.y / 2
        wall_min_x = -self.scale.x / 2
        wall_max_x = self.scale.x / 2
        wall_min_y = -self.scale.y / 2
        wall_max_y = self.scale.y / 2

        return (
            window_min_x >= wall_min_x
            and window_max_x <= wall_max_x
            and window_min_y >= wall_min_y
            and window_max_y <= wall_max_y
        )
    
    def _window_do_not_overlap(self, window) -> bool:
        """
        Check if the window does not overlap with existing windows.

        Args:
            wall (bpy.types.Object): The wall to add the window to.

        Returns:
            bool: Whether the window does not overlap with existing windows.
        """
        window_min_x = window.location.x - window.scale.x / 2
        window_max_x = window.location.x + window.scale.x / 2
        window_min_y = window.location.y - window.scale.y / 2
        window_max_y = window.location.y + window.scale.y / 2
        for other in self.windows:
            other_min_x = other.location.x - other.scale.x / 2
            other_max_x = other.location.x + other.scale.x / 2
            other_min_y = other.location.y - other.scale.y / 2
            other_max_y = other.location.y + other.scale.y / 2

            if (
                window_min_x <= other_max_x
                and window_max_x >= other_min_x
                and window_min_y <= other_max_y
                and window_max_y >= other_min_y
            ):
                return False
            
        return True

    def add_window(self, window: Window) -> None:
        """
        Add a window to the wall.

        Args:
            window (Window): The window to add to the wall.

        Raises:
            ValueError: If the window is not in bounds of the wall.
            ValueError: If the window overlaps with existing windows.
        """
        if not self._window_is_in_bounds(window):
            raise ValueError("The window is not in bounds of the wall.")
        if not self._window_do_not_overlap(window):
            raise ValueError("The window overlaps with existing windows.")
        
        self.windows.append(window)

    def apply_to_collection(self, collection: bpy.types.Collection) -> None:
        # Add wall
        bpy.ops.mesh.primitive_plane_add(size=1)
        wall_object = bpy.context.view_layer.objects.active
        wall_object.name = self.name
        wall_object.rotation_euler = self.rotation
        wall_object.location = self.location
        bpy.context.view_layer.update()  # Update to commit location and rotation changes
        wall_object_matrix_world = (
            wall_object.matrix_world.copy()
        )  # Store the matrix_world of the wall object before scaling
        wall_object.dimensions = self.scale
        bpy.context.view_layer.update()  # Update to commit scaling changes

        # Add windows
        for window in self.windows:
            window.apply_to_collection(collection, wall_object, wall_object_matrix_world)
