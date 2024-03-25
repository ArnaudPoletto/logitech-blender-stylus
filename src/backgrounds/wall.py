import bpy
from typing import Tuple
from mathutils import Vector

from backgrounds.window import Window
from backgrounds.background_object import BackgroundObject

class Wall(BackgroundObject):
    def __init__(
        self, 
        name: str,
        p: Vector,
        width: float,
        height: float,
        normal: Vector,
    ) -> None:
        """
        Initialize the wall.
        
        Args:
            name (str): The name of the wall.
            p (Vector): The bottom left corner of the wall.
            width (float): The width of the wall.
            height (float): The height of the wall.
            
        Raises:
            ValueError: If the corners do not form a valid wall.
        """
        super(Wall, self).__init__(name)
        
        # Get the wall information
        self.p = p
        self.width = width
        self.height = height
        
        # Get the corners of the wall
        self.bl = p
        self.tl = (p[0], p[1], p[2] + height)
        self.tr = (p[0] + width, p[1], p[2] + height)
        self.br = (p[0] + width, p[1], p[2])
                
        self.windows = []
        
    def add_window(self, center, width, height) -> None:
        """
        Add a window to the wall.
        
        Args:
            center (Tuple[float, float, float]): The center of the window.
            width (float): The width of the window.
            height (float): The height of the window.
            
        Raises:
            ValueError: If the window is not within the wall.
        """
        pass
        
    
    def add_to_scene(self, scene: bpy.types.Scene) -> None:
        # Add wall to scene
        # Get mesh information
        vertices = [self.bl, self.tl, self.tr, self.br]
        edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
        faces = [(0, 1, 2, 3)]
        
        # Create the mesh
        mesh = bpy.data.meshes.new(name=f"{self.name}Mesh")
        mesh.from_pydata(vertices, edges, faces)
        mesh.update()
        
        # Link the object to the scene
        obj = bpy.data.objects.new(self.name, mesh)
        scene.collection.objects.link(obj)
        
        # Add windows to scene
        for window in self.windows:
            window.add_to_scene(scene)