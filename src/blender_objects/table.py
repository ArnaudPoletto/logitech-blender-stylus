import bpy
from typing import Tuple
from mathutils import Vector

from blender_objects.relative_blender_object import RelativeBlenderObject


class Table(RelativeBlenderObject):
    """
    A Table.
    """

    def __init__(
        self,
        name: str,
        relative_location: Vector,
        scale: Vector,
        top_thickness: float,
        leg_thickness: float,
    ) -> None:
        """
        Initialize the table.

        Args:
            name (str): The name of the table.
            relative_location (Vector): The relative location of the table from the location of the Blender object as a 2D vector.
            scale (Vector): The scale of the table as a 3D vector.
            top_thickness (float): The thickness of the table top.
            leg_thickness (float): The thickness of the table legs.

        Raises:
            ValueError: If the scale is not a 3D vector.
            ValueError: If the scale values are not positive.
            ValueError: If the top thickness is not a positive number or is greater than the height.
            ValueError: If the leg thickness is not a positive number or is greater than half the width or depth.
        """
        if len(scale) != 3:
            raise ValueError("The scale must be a 3D vector.")

        if any(value <= 0 for value in scale):
            raise ValueError("The scale values must be positive.")

        if top_thickness <= 0 or top_thickness >= scale.z:
            raise ValueError(
                "The top thickness must be a positive number and less than the height."
            )

        if (
            leg_thickness <= 0
            or leg_thickness >= scale.x / 2
            or leg_thickness >= scale.y / 2
        ):
            raise ValueError(
                "The leg thickness must be a positive number and less than half the width or depth."
            )

        relative_location = Vector((relative_location.x, relative_location.y, 0))
        super(Table, self).__init__(name=name, relative_location=relative_location)

        self.scale = scale
        self.top_thickness = top_thickness
        self.leg_thickness = leg_thickness

    def get_bounds(
        self,
    ) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
        min_x = -self.scale.x / 2
        max_x = self.scale.x / 2
        min_y = -self.scale.y / 2
        max_y = self.scale.y / 2

        return (min_x, max_x), (min_y, max_y), (0, 0)

    # TODO: factorize code
    def apply_to_collection(
        self, 
        collection: bpy.types.Collection,
        blender_object: bpy.types.Object
    ) -> None:
        bpy.ops.object.mode_set(mode="OBJECT")

        # Add top
        scaled_relative_location = Vector((
            self.relative_location.x / blender_object.scale.x,
            self.relative_location.y / blender_object.scale.y,
            self.relative_location.z / blender_object.scale.z,
        ))
        location = blender_object.matrix_world @ scaled_relative_location
        top_location = Vector(
            (
                location.x,
                location.y,
                location.z + self.scale.z - self.top_thickness / 2,
            )
        )
        bpy.ops.mesh.primitive_cube_add(size=1, location=top_location)
        top_table_object = bpy.context.object
        top_table_object.name = self.name
        top_table_object.scale = (self.scale.x, self.scale.y, self.top_thickness)
        collection.objects.link(top_table_object)
        bpy.context.view_layer.update()

        # Add legs
        leg_locations = [
            Vector(
                (
                    location.x - self.scale.x / 2 + self.leg_thickness / 2,
                    location.y - self.scale.y / 2 + self.leg_thickness / 2,
                    location.z + self.scale.z / 2 - self.top_thickness / 2,
                )
            ),
            Vector(
                (
                    location.x - self.scale.x / 2 + self.leg_thickness / 2,
                    location.y + self.scale.y / 2 - self.leg_thickness / 2,
                    location.z + self.scale.z / 2 - self.top_thickness / 2,
                )
            ),
            Vector(
                (
                    location.x + self.scale.x / 2 - self.leg_thickness / 2,
                    location.y - self.scale.y / 2 + self.leg_thickness / 2,
                    location.z + self.scale.z / 2 - self.top_thickness / 2,
                )
            ),
            Vector(
                (
                    location.x + self.scale.x / 2 - self.leg_thickness / 2,
                    location.y + self.scale.y / 2 - self.leg_thickness / 2,
                    location.z + self.scale.z / 2 - self.top_thickness / 2,
                )
            ),
        ]
        for i, leg_location in enumerate(leg_locations):
            bpy.ops.mesh.primitive_cube_add(size=1, location=leg_location)
            leg_object = bpy.context.object
            leg_object.name = f"{self.name}Leg{i}"
            leg_object.scale = (
                self.leg_thickness,
                self.leg_thickness,
                self.scale.z - self.top_thickness,
            )
            collection.objects.link(leg_object)
            bpy.context.view_layer.update()
