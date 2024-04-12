import cv2
import bpy
import random
import numpy as np
from typing import Tuple
from scipy.interpolate import interp1d

# TODO: add documentation 
class BackgroundImageGenerator:
    def __init__(
            self,
            width: int,
            height: int,
            n_patches_range: Tuple[int, int],
            n_patch_corners_range: Tuple[int, int],
            patch_size_range: Tuple[int, int],
            n_lines_range: Tuple[int, int],
            line_size_range: Tuple[int, int],
            n_line_points_range: Tuple[int, int],
            line_thickness_range: Tuple[int, int],
    ) -> None:
        if width <= 0:
            raise ValueError("Width must be greater than 0")
        if height <= 0:
            raise ValueError("Height must be greater than 0")
        if n_patches_range[0] <= 0:
            raise ValueError("Number of patches must be greater than 0")
        if n_patches_range[1] < n_patches_range[0]:
            raise ValueError("Upper bound of number of patches must be greater than lower bound")
        if n_patch_corners_range[0] <= 0:
            raise ValueError("Number of patch corners must be greater than 0")
        if n_patch_corners_range[1] < n_patch_corners_range[0]:
            raise ValueError("Upper bound of number of patch corners must be greater than lower bound")
        if patch_size_range[0] <= 0:
            raise ValueError("Minimum patch size must be greater than 0")
        if patch_size_range[1] > min(width, height):
            raise ValueError("Minimum patch size must be less than width and height")
        if patch_size_range[1] < patch_size_range[0]:
            raise ValueError("Upper bound of minimum patch size must be greater than lower bound")
        if n_lines_range[0] <= 0:
            raise ValueError("Number of lines must be greater than 0")
        if n_lines_range[1] < n_lines_range[0]:
            raise ValueError("Upper bound of number of lines must be greater than lower bound")
        if line_size_range[0] <= 0:
            raise ValueError("Minimum line size must be greater than 0")
        if line_size_range[1] > min(width, height):
            raise ValueError("Minimum line size must be less than width and height")
        if n_line_points_range[0] <= 0:
            raise ValueError("Number of line points must be greater than 0")
        if n_line_points_range[1] < n_line_points_range[0]:
            raise ValueError("Upper bound of number of line points must be greater than lower bound")
        if line_thickness_range[0] <= 0:
            raise ValueError("Minimum line thickness must be greater than 0")
        if line_thickness_range[1] < line_thickness_range[0]:
            raise ValueError("Upper bound of minimum line thickness must be greater than lower bound")
        
        self.width = width
        self.height = height
        self.n_patches_range = n_patches_range
        self.n_patch_corners_range = n_patch_corners_range
        self.patch_size_range = patch_size_range
        self.n_lines_range = n_lines_range
        self.line_size_range = line_size_range
        self.n_line_points_range = n_line_points_range
        self.line_thickness_range = line_thickness_range

    def _get_background_image(self) -> np.array:
        background_image = np.ones((self.height, self.width, 4), dtype=np.float32)
            
        # Add random polygons as patches
        n_random_patches = random.randint(*self.n_patches_range)
        for _ in range(n_random_patches):
            n_corners = random.randint(*self.n_patch_corners_range)
            patch_width = random.randint(*self.patch_size_range)
            patch_height = random.randint(*self.patch_size_range)
            x = random.randint(0, self.width - patch_width)
            y = random.randint(0, self.height - patch_height)
            xs = np.random.randint(x, x + patch_width, n_corners)
            ys = np.random.randint(y, y + patch_height, n_corners)
            
            # Get points in clockwise order
            points = np.column_stack((xs, ys)).astype(int)
            centroid = np.mean(points, axis=0)
            points = sorted(points, key=lambda point: np.arctan2(point[1] - centroid[1], point[0] - centroid[0]), reverse=True)
            points = np.array(points)
            
            color = random.random()
            cv2.fillPoly(background_image, [points], color=(color, color, color, 1.0))
            
        # Add random curves resembling tree branches
        n_lines = random.randint(*self.n_lines_range)
        for _ in range(n_lines):
            line_width = random.randint(*self.line_size_range)
            line_height = random.randint(*self.line_size_range)
            n_line_points = random.randint(*self.n_line_points_range)
            line_thickness = random.randint(*self.line_thickness_range)
        
            x = random.randint(0, self.width - line_width)
            y = random.randint(0, self.height - line_height)
            xs = np.random.randint(x, x + line_width, n_line_points)
            ys = np.random.randint(y, y + line_height, n_line_points)
            points = np.column_stack((xs, ys)).astype(int)
            color = random.random()
            cv2.polylines(background_image, [points], isClosed=False, color=(color, color, color, 1.0), thickness=line_thickness)
            
        return background_image
    
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
        image = bpy.data.images.new("BackgroundImage", width=self.width, height=self.height)
        image.pixels = background_image.flatten()
        image_node.image = image
                
