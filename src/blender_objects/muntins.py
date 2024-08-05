import bpy
from mathutils import Vector

from utils.axis import Axis
from blender_objects.window_decorator import WindowDecorator


class Muntins(WindowDecorator):
    """
    A muntins window decorator of a window.
    """

    def __init__(
        self,
        name: str,
        size: float,
        n_muntins_width: int,
        n_muntins_height: int,
    ) -> None:
        """
        Initialize the muntins window decorator.

        Args:
            name (str): The name of the window decorator.
            size (float): The size of the muntins.
            n_muntins_width (int): The number of muntins in the width of the window.
            n_muntins_height (int): The number of muntins in the height of the window.

        Raises:
            ValueError: If the size of the muntins is less than or equal to 0.
            ValueError: If the number of muntins in the width is less than 1.
            ValueError: If the number of muntins in the height is less than 1.
        """
        if size <= 0:
            raise ValueError("❌ The size of the muntins must be greater than 0.")
        if n_muntins_width < 1:
            raise ValueError(
                "❌ The number of muntins in the width must be greater than 0."
            )
        if n_muntins_height < 1:
            raise ValueError(
                "❌ The number of muntins in the height must be greater than 0."
            )

        super(Muntins, self).__init__(name=name)

        self.size = size
        self.n_muntins_width = n_muntins_width
        self.n_muntins_height = n_muntins_height

    def _apply_muntins(
        self,
        collection: bpy.types.Collection,
        blender_object: bpy.types.Object,
        axis: Axis,
        n_muntins: int,
    ) -> None:
        """
        Apply the muntins to the window along the specified axis.

        Args:
            collection (bpy.types.Collection): The collection to which the muntins are applied.
            blender_object (bpy.types.Object): The Blender object to which the muntins are applied.
            axis (Axis): The axis along which the muntins are applied.
            n_muntins (int): The number of muntins to apply.

        Raises:
            ValueError: If the total width of the muntins is greater than the width of the window.
        """
        axis_name = "width" if axis == Axis.X_AXIS else "height"
        if n_muntins * self.size > blender_object.scale[axis.index()]:
            raise ValueError(
                f"❌ The total {axis_name} of the muntins is greater than the {axis_name} of the window."
            )

        for i in range(n_muntins):
            bpy.ops.mesh.primitive_plane_add(size=1)
            muntin_object = bpy.context.view_layer.objects.active
            muntin_object.name = (
                f"{blender_object.name}{self.name}{i}{axis_name.capitalize()}"
            )
            muntin_object.rotation_euler = blender_object.rotation_euler
            local_location = Vector((0, 0, 0))
            location_offset = (i + 1) * (
                blender_object.scale[axis.index()] - n_muntins * self.size
            ) / (n_muntins + 1) + (2 * i + 1) * self.size / 2
            location_offset /= blender_object.scale[axis.index()]
            location_offset -= 0.5
            local_location[axis.index()] = location_offset
            muntin_object.location = blender_object.matrix_world @ local_location
            muntin_object.scale = Vector((0, 0, 1))
            muntin_object.scale[axis.index()] = self.size
            muntin_object.scale[(axis.index() + 1) % 2] = blender_object.scale[
                (axis.index() + 1) % 2
            ]
            bpy.context.view_layer.update()

            # Add muntin to collection
            collection.objects.link(muntin_object)
            bpy.context.view_layer.update()

    def apply_to_collection(
        self,
        collection: bpy.types.Collection,
        blender_object: bpy.types.Object,
    ) -> None:
        bpy.ops.object.mode_set(mode="OBJECT")

        self._apply_muntins(
            collection, blender_object, Axis.X_AXIS, self.n_muntins_width
        )
        self._apply_muntins(
            collection, blender_object, Axis.Y_AXIS, self.n_muntins_height
        )
        bpy.context.view_layer.update()
