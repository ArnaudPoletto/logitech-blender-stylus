import bpy
from mathutils import Vector
from abc import abstractmethod


class BlenderObject:
    """
    A Blender object.
    """

    def __init__(self, name: str, location: Vector) -> None:
        """
        Initialize the Blender object.

        Args:
            name (str): The name of the Blender object.
            location (Vector): The location of the Blender object.

        Raises:
            ValueError: If the location is not a 3D vector.
            ValueError: If a mesh with the same name already exists.
        """
        if len(location) != 3:
            raise ValueError("The location must be a 3D vector.")
        
        mesh_name = f"{name}Mesh"
        if bpy.data.meshes.get(mesh_name) is not None:
            raise ValueError(f"A mesh with the name {mesh_name} already exists.")

        self.name = name
        self.mesh_name = mesh_name
        self.location = location

    @abstractmethod
    def apply_to_collection(self, collection: bpy.types.Collection) -> None:
        """
        Apply the Blender object to the collection.

        Args:
            collection (bpy.types.Collection): The collection to add the Blender object to.
        """
        raise NotImplementedError("The apply_to_collection method must be implemented.")
