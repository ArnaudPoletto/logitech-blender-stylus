import bpy

from backgrounds.background_object import BackgroundObject

class Window(BackgroundObject):
    def __init__(
        self,
        name: str
    ):
        pass
    
    def add_to_scene(self, scene: bpy.types.Scene) -> None:
        pass