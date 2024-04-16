import cv2
import bpy
import random
import numpy as np
from typing import Tuple
from abc import abstractmethod


# TODO: add documentation
class BackgroundImageGenerator:
    def __init__(
        self,
        width: int,
        height: int,
    ) -> None:
        if width <= 0:
            raise ValueError("Width must be greater than 0")
        if height <= 0:
            raise ValueError("Height must be greater than 0")

        self.width = width
        self.height = height

    @abstractmethod
    def _get_background_image(self) -> np.array:
        raise NotImplementedError("The _get_background_image method must be implemented.")

    def apply_to_scene(self) -> None:
        tree = bpy.context.scene.node_tree

        # Find scale node
        scale_node = tree.nodes.get("Scale")
        if scale_node is None:
            raise ValueError("Scale node not found")

        # Delete existing image node
        for node in tree.nodes:
            if node.type == "IMAGE":
                tree.nodes.remove(node)

        # Create new image node
        image_node = tree.nodes.new("CompositorNodeImage")
        image_node.location = (100, 700)
        tree.links.new(image_node.outputs[0], scale_node.inputs[0])

        # Get and set image
        background_image = self._get_background_image()
        image = bpy.data.images.new(
            "BackgroundImage", width=self.width, height=self.height
        )
        image.pixels = background_image.flatten()
        image_node.image = image
