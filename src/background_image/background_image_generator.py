# This file contains the background image generator class, which is a base class for all background image generators.

import bpy
import numpy as np
from abc import abstractmethod


class BackgroundImageGenerator:
    """
    A background image generator.
    """
    def __init__(
        self,
        width: int,
        height: int,
    ) -> None:
        """
        Initialize the background image generator.
        
        Args:
            width (int): The width of the background image.
            height (int): The height of the background image.
            
        Raises:
            ValueError: If the width is less than or equal to 0.
            ValueError: If the height is less than or equal to 0.
        """
        if width <= 0:
            raise ValueError("❌ Width must be greater than 0")
        if height <= 0:
            raise ValueError("❌ Height must be greater than 0")

        self.width = width
        self.height = height
        self.image_node = None

    @abstractmethod
    def get_background_image(self) -> np.ndarray:
        """
        Get the background image.
        
        Returns:
            np.ndarray: The background image.
        """
        raise NotImplementedError("❌ The get_background_image method must be implemented.")

    def apply_to_scene(self) -> None:
        """
        Apply the background image to the scene.
        
        Raises:
            ValueError: If the scale node is not found.
        """
        tree = bpy.context.scene.node_tree

        # Find scale node
        scale_node = tree.nodes.get("Scale")
        if scale_node is None:
            raise ValueError("❌ Scale node not found")

        # Create new image node if it does not exist
        if self.image_node is None:
            image_node = tree.nodes.new("CompositorNodeImage")
            image_node.location = (100, 700)
            background_image = self.get_background_image()
            image = bpy.data.images.new(
                "BackgroundImage", width=self.width, height=self.height
            )
            image.pixels = background_image.flatten()
            image_node.image = image
            self.image_node = image_node

        tree.links.new(self.image_node.outputs[0], scale_node.inputs[0])