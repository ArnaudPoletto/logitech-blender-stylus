import bpy
from typing import List

from blender_objects.blender_object import BlenderObject


class BlenderCollection:
    """
    A Blender collection.
    """

    def __init__(
        self,
        name: str,
        parent_collection: bpy.types.Collection = bpy.context.scene.collection,
    ) -> None:
        """
        Initialize the Blender collection.

        Args:
            name (str): The name of the Blender collection.
            parent_collection (bpy.types.Collection): The parent collection to add the collection to. Defaults to the scene collection.

        Raises:
            Exception: If the collection already exists in the scene.
        """
        if name in bpy.data.collections:
            raise Exception(
                f"Collection with name '{name}' already exists in the scene."
            )

        # Create the collection
        self.collection = bpy.data.collections.new(name)
        parent_collection.children.link(self.collection)

        self.name = name
        self.objects: List[BlenderObject] = []
        self.is_added_to_collection = False

    def add_object(self, blender_object: BlenderObject) -> None:
        """
        Add an object to the collection.

        Args:
            blender_object (BlenderObject): The Blender object to add to the collection.

        Raises:
            Exception: If the collection has already been added to the scene.
        """
        if self.is_added_to_collection:
            raise Exception(
                "Cannot add Blender object to collection after it has been added to the scene."
            )

        self.objects.append(blender_object)

    def add_all_objects(self, blender_objects: List[BlenderObject]) -> None:
        """
        Add multiple Blender objects to the collection.

        Args:
            blender_objects (List[BlenderObject]): The objects to add to the collection.

        Raises:
            Exception: If the collection has already been added to the scene.
        """
        if self.is_added_to_collection:
            raise Exception(
                "Cannot add objects to collection after it has been added to the scene."
            )

        for obj in blender_objects:
            self.add_object(obj)

    def apply(self) -> None:
        """
        Apply the collection to the scene.

        Args:
            collection (bpy.types.Collection): The collection to add to the scene.

        Raises:
            Exception: If the collection has already been added to the scene.
        """
        if self.is_added_to_collection:
            raise Exception(
                "Cannot add collection to scene after it has already been added."
            )

        for obj in self.objects:
            obj.apply_to_collection(self.collection)
        bpy.context.view_layer.update()

        self.is_added_to_collection = True
