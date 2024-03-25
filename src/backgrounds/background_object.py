import bpy

class BackgroundObject():
    """
    An object that can be added to a background.
    """
    def __init__(self, name: str) -> None:
        """
        Initialize the background object.
        
        Args:
            name (str): The name of the object.
        """
        self.name = name
    
    def add_to_scene(self, scene: bpy.types.Scene) -> None:
        """
        Add the object to the scene.
        
        Args:
            scene (bpy.types.Scene): The scene to add the object to.
        """
        raise NotImplementedError("The add_to_scene method must be implemented.")