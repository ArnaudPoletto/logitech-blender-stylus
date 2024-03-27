import bpy
from mathutils import Vector, Matrix
from typing import List

from blender_objects.blender_object import BlenderObject


class Window:
    """
    A window in a wall.
    """

    def __init__(
        self,
        name: str,
        location: Vector,
        scale: Vector,
    ) -> None:
        """
        Initialize the window.

        Args:
            name (str): The name of the window.
            location (Vector): The relative location of the window from the location of the wall as a 2D vector.
            scale (Vector): The scale of the window as a 2D vector.

        Raises:
            ValueError: If the location is not a 2D vector.
            ValueError: If the scale is not a 2D vector.
        """
        if len(location) != 2:
            raise ValueError("The location must be a 2D vector.")

        if len(scale) != 2:
            raise ValueError("The scale must be a 2D vector.")

        self.name = name
        self.location = Vector((location.x, location.y, 0))
        self.scale = Vector((scale.x, scale.y, 1))

    def _window_is_in_bounds(self, wall: "WallBlenderObject") -> bool:
        """
        Check if the window is in bounds of the wall.

        Args:
            wall (bpy.types.Object): The wall to add the window to.

        Returns:
            bool: Whether the window is in bounds of the wall.
        """
        window_min_x = self.location.x - self.scale.x / 2
        window_max_x = self.location.x + self.scale.x / 2
        window_min_y = self.location.y - self.scale.y / 2
        window_max_y = self.location.y + self.scale.y / 2
        wall_min_x = -wall.scale.x / 2
        wall_max_x = wall.scale.x / 2
        wall_min_y = -wall.scale.y / 2
        wall_max_y = wall.scale.y / 2

        return (
            window_min_x >= wall_min_x
            and window_max_x <= wall_max_x
            and window_min_y >= wall_min_y
            and window_max_y <= wall_max_y
        )

    def apply_to_wall(
        self,
        wall: "WallBlenderObject",
        wall_object: bpy.types.Object,
        wall_object_matrix_world: Matrix,
    ) -> None:
        """
        Apply the window to the wall.

        Args:
            wall (WallBlenderObject): The wall to add the window to.
            wall_object (bpy.types.Object): The wall object to add the window to.
            wall_object_rotation_euler (bpy.types.Vector): The rotation_euler of the wall object.
            wall_object_matrix_world (bpy.types.Matrix): The matrix_world of the wall object.

        Raises:
            ValueError: If the window is not in bounds of the wall.
        """
        if not self._window_is_in_bounds(wall):
            raise ValueError("The window is not in bounds of the wall.")

        # Add cube of window shape into the wall
        bpy.ops.mesh.primitive_cube_add(size=1)
        window_object = bpy.context.view_layer.objects.active
        window_object.name = self.name
        window_object.rotation_euler = wall.rotation
        window_object.location = wall_object_matrix_world @ self.location # Relative to the wall
        window_object.scale = self.scale
        bpy.context.view_layer.update()
        
        # Apply boolean modifier to the wall
        boolean_modifier = wall_object.modifiers.new(name=f"{self.name}BoolDiff", type="BOOLEAN")
        boolean_modifier.object = window_object
        boolean_modifier.operation = "DIFFERENCE"
        
        # Apply modifiers to the wall
        bpy.ops.object.select_all(action='DESELECT')
        wall_object.select_set(True)
        bpy.context.view_layer.objects.active = wall_object
        bpy.ops.object.convert(target='MESH')
        
        # Delete window object
        bpy.ops.object.select_all(action='DESELECT')
        window_object.select_set(True)
        bpy.ops.object.delete()
        
class WallBlenderObject(BlenderObject):
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

    def add_window(
        self, window_name: str, window_location: Vector, window_scale: Vector
    ) -> None:
        """
        Add a window to the wall.

        Args:
            window_name (str): The name of the window.
            window_location (Vector): The relative location of the window from the location of the wall as a 2D vector.
            window_scale (Vector): The scale of the window as a 2D vector.
        """
        window = Window(window_name, window_location, window_scale)
        self.windows.append(window)

    def apply_to_collection(self, collection: bpy.types.Collection) -> None:
        bpy.context.view_layer.update()
        bpy.ops.object.mode_set(mode='OBJECT')
        
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
            window.apply_to_wall(self, wall_object, wall_object_matrix_world)
        