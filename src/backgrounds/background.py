import bpy
from typing import List

from backgrounds.background_object import BackgroundObject


class Background:
    """
    A background in a scene.
    """

    def __init__(self) -> None:
        """
        Initialize the background.
        """
        self.objects: List[BackgroundObject] = []
        self.is_added_to_scene = False

    def add_object(self, obj: BackgroundObject) -> None:
        """
        Add an object to the background.

        Args:
            obj (BackgroundObject): The object to add to the background.

        Raises:
            Exception: If the background has already been added to a scene.
        """
        if self.is_added_to_scene:
            raise Exception(
                "Cannot add object to background after it has been added to a scene."
            )

        self.objects.append(obj)

    def add_all_objects(self, objs: List[BackgroundObject]) -> None:
        """
        Add multiple objects to the background.

        Args:
            objs (List[BackgroundObject]): The objects to add to the background.

        Raises:
            Exception: If the background has already been added to a scene.
        """
        if self.is_added_to_scene:
            raise Exception(
                "Cannot add objects to background after it has been added to a scene."
            )

        for obj in objs:
            self.add_object(obj)

    def add_to_scene(self, scene: bpy.types.Scene) -> None:
        """
        Add a background to the scene.

        Args:
            scene (bpy.types.Scene): The scene to add the background to.

        Raises:
            Exception: If the background has already been added to a scene.
        """
        if self.is_added_to_scene:
            raise Exception(
                "Cannot add background to scene after it has already been added."
            )

        for obj in self.objects:
            obj.add_to_scene(scene)

        self.is_added_to_scene = True
