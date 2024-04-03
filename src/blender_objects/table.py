import bpy
from mathutils import Vector

from blender_objects.blender_object import BlenderObject

# TODO: add to room
class Table(BlenderObject):
    """
    A Table.
    """

    def __init__(
        self,
        name: str,
        location: Vector,
        width: float,
        height: float,
        depth: float,
        top_thickness: float,
        leg_thickness: float,
    ) -> None:
        """
        Initialize the table.
        
        Args:
            name (str): The name of the table.
            location (Vector): The location of the table.
            width (float): The width of the table.
            height (float): The height of the table.
            depth (float): The depth of the table.
            top_thickness (float): The thickness of the table top.
            leg_thickness (float): The thickness of the table legs.
            
        Raises:
            ValueError: If the width is not a positive number.
            ValueError: If the height is not a positive number.
            ValueError: If the depth is not a positive number.
            ValueError: If the top thickness is not a positive number or is greater than the height.
            ValueError: If the leg thickness is not a positive number or is greater than half the width or depth.
        """
        super(Table, self).__init__(name=name, location=location)
        
        if width <= 0:
            raise ValueError("The width must be a positive number.")
        
        if height <= 0:
            raise ValueError("The height must be a positive number.")
        
        if depth <= 0:
            raise ValueError("The depth must be a positive number.")
        
        if top_thickness <= 0 or top_thickness >= height:
            raise ValueError("The top thickness must be a positive number and less than the height.")
        
        if leg_thickness <= 0 or leg_thickness >= width / 2 or leg_thickness >= depth / 2:
            raise ValueError("The leg thickness must be a positive number and less than half the width or depth.")
        
        self.width = width
        self.height = height
        self.depth = depth
        self.top_thickness = top_thickness
        self.leg_thickness = leg_thickness
        
    # TODO: factorize code
    def apply_to_collection(self, collection: bpy.types.Collection) -> None:
        bpy.ops.object.mode_set(mode="OBJECT")
        
        # Add top
        top_location = Vector((
            self.location.x,
            self.location.y,
            self.location.z + self.height - self.top_thickness / 2
            
        ))
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=top_location
        )
        top_table_object = bpy.context.object
        top_table_object.name = self.name
        top_table_object.scale = (self.width, self.depth, self.top_thickness)
        collection.objects.link(top_table_object)
        bpy.context.view_layer.update()
        
        # Add legs
        leg_locations = [
            Vector((
                self.location.x - self.width / 2 + self.leg_thickness / 2,
                self.location.y - self.depth / 2 + self.leg_thickness / 2,
                self.location.z + self.height / 2 - self.top_thickness / 2
            )),
            Vector((
                self.location.x - self.width / 2 + self.leg_thickness / 2,
                self.location.y + self.depth / 2 - self.leg_thickness / 2,
                self.location.z + self.height / 2 - self.top_thickness / 2
            )),
            Vector((
                self.location.x + self.width / 2 - self.leg_thickness / 2,
                self.location.y - self.depth / 2 + self.leg_thickness / 2,
                self.location.z + self.height / 2 - self.top_thickness / 2
            )),
            Vector((
                self.location.x + self.width / 2 - self.leg_thickness / 2,
                self.location.y + self.depth / 2 - self.leg_thickness / 2,
                self.location.z + self.height / 2 - self.top_thickness / 2
            ))
        ]
        for i, leg_location in enumerate(leg_locations):
            bpy.ops.mesh.primitive_cube_add(
                size=1,
                location=leg_location
            )
            leg_object = bpy.context.object
            leg_object.name = f"{self.name}Leg{i}"
            leg_object.scale = (self.leg_thickness, self.leg_thickness, self.height - self.top_thickness)
            collection.objects.link(leg_object)
            bpy.context.view_layer.update()