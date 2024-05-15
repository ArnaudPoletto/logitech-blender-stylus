import cv2
import random
import numpy as np
from typing import Tuple

from background_image.background_image_generator import BackgroundImageGenerator


# TODO: add documentation
class RandomBackgroundImageGenerator(BackgroundImageGenerator):
    """
    A random background image generator.
    """
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
        smooth_gaussian_kernel_size: int,
        n_blur_steps: int,
        max_blur: int,
        color_range: Tuple[float, float],
    ) -> None:
        """
        Initialize the random background image generator.
        
        Args:
            width (int): The width of the background image.
            height (int): The height of the background image.
            n_patches_range (Tuple[int, int]): The range of the number of patches.
            n_patch_corners_range (Tuple[int, int]): The range of the number of patch corners.
            patch_size_range (Tuple[int, int]): The range of the patch size.
            n_lines_range (Tuple[int, int]): The range of the number of lines.
            line_size_range (Tuple[int, int]): The range of the line size.
            n_line_points_range (Tuple[int, int]): The range of the number of line points.
            line_thickness_range (Tuple[int, int]): The range of the line thickness.
            smooth_gaussian_kernel_size (int): The size of the smooth Gaussian kernel.
            n_blur_steps (int): The number of blur steps.
            max_blur (int): The maximum blur.
            color_range (Tuple[float, float]): The range of the color.
        
        Raises:
            ValueError: If the number of patches is less than or equal to 0.
            ValueError: If the upper bound of the number of patches is less than the lower bound.
            ValueError: If the number of patch corners is less than or equal to 0.
            ValueError: If the upper bound of the number of patch corners is less than the lower bound.
            ValueError: If the minimum patch size is less than or equal to 0.
            ValueError: If the maximum patch size is greater than the width and height.
            ValueError: If the upper bound of the minimum patch size is less than the lower bound.
            ValueError: If the number of lines is less than or equal to 0.
            ValueError: If the upper bound of the number of lines is less than the lower bound.
            ValueError: If the minimum line size is less than or equal to 0.
            ValueError: If the minimum line size is greater than the width and height.
            ValueError: If the number of line points is less than or equal to 0.
            ValueError: If the upper bound of the number of line points is less than the lower bound.
            ValueError: If the minimum line thickness is less than or equal to 0.
            ValueError: If the upper bound of the minimum line thickness is less than the lower bound.
            ValueError: If the smooth Gaussian kernel size is less than or equal to 0.
            ValueError: If the smooth Gaussian kernel size is even.
            ValueError: If the number of blur steps is less than or equal to 0.
            ValueError: If the maximum blur is less than or equal to 0.
            ValueError: If the minimum color is less than 0.
            ValueError: If the maximum color is greater than 1.
            ValueError: If the maximum color is less than the minimum color.
        """
        if n_patches_range[0] <= 0:
            raise ValueError("Number of patches must be greater than 0")
        if n_patches_range[1] < n_patches_range[0]:
            raise ValueError(
                "Upper bound of number of patches must be greater than lower bound"
            )
        if n_patch_corners_range[0] <= 0:
            raise ValueError("Number of patch corners must be greater than 0")
        if n_patch_corners_range[1] < n_patch_corners_range[0]:
            raise ValueError(
                "Upper bound of number of patch corners must be greater than lower bound"
            )
        if patch_size_range[0] <= 0:
            raise ValueError("Minimum patch size must be greater than 0")
        if patch_size_range[1] > min(width, height):
            raise ValueError("Maximum patch size must be less than width and height")
        if patch_size_range[1] < patch_size_range[0]:
            raise ValueError(
                "Upper bound of minimum patch size must be greater than lower bound"
            )
        if n_lines_range[0] <= 0:
            raise ValueError("Number of lines must be greater than 0")
        if n_lines_range[1] < n_lines_range[0]:
            raise ValueError(
                "Upper bound of number of lines must be greater than lower bound"
            )
        if line_size_range[0] <= 0:
            raise ValueError("Minimum line size must be greater than 0")
        if line_size_range[1] > min(width, height):
            raise ValueError("Minimum line size must be less than width and height")
        if n_line_points_range[0] <= 0:
            raise ValueError("Number of line points must be greater than 0")
        if n_line_points_range[1] < n_line_points_range[0]:
            raise ValueError(
                "Upper bound of number of line points must be greater than lower bound"
            )
        if line_thickness_range[0] <= 0:
            raise ValueError("Minimum line thickness must be greater than 0")
        if line_thickness_range[1] < line_thickness_range[0]:
            raise ValueError(
                "Upper bound of minimum line thickness must be greater than lower bound"
            )
        if smooth_gaussian_kernel_size <= 0:
            raise ValueError("Smooth Gaussian kernel size must be greater than 0")
        if smooth_gaussian_kernel_size % 2 == 0:
            raise ValueError("Smooth Gaussian kernel size must be odd")
        if n_blur_steps <= 0:
            raise ValueError("Number of blur steps must be greater than 0")
        if max_blur <= 0:
            raise ValueError("Maximum blur must be greater than 0")
        if color_range[0] < 0:
            raise ValueError("Minimum color must be greater than 0")
        if color_range[1] > 1:
            raise ValueError("Maximum color must be less than or equal to 1")
        if color_range[1] < color_range[0]:
            raise ValueError("Maximum color must be greater than minimum color")

        super(RandomBackgroundImageGenerator, self).__init__(width=width, height=height)

        self.width = width
        self.height = height
        self.n_patches_range = n_patches_range
        self.n_patch_corners_range = n_patch_corners_range
        self.patch_size_range = patch_size_range
        self.n_lines_range = n_lines_range
        self.line_size_range = line_size_range
        self.n_line_points_range = n_line_points_range
        self.line_thickness_range = line_thickness_range
        self.smooth_gaussian_kernel_size = smooth_gaussian_kernel_size
        self.n_blur_steps = n_blur_steps
        self.max_blur = max_blur
        self.color_range = color_range

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
            points = sorted(
                points,
                key=lambda point: np.arctan2(
                    point[1] - centroid[1], point[0] - centroid[0]
                ),
                reverse=True,
            )
            points = np.array(points)

            color = random.uniform(*self.color_range)
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
            color = random.uniform(*self.color_range)
            cv2.polylines(
                background_image,
                [points],
                isClosed=False,
                color=(color, color, color, 1.0),
                thickness=line_thickness,
            )

        # Blur image randomly
        kernel = (self.smooth_gaussian_kernel_size, self.smooth_gaussian_kernel_size)
        smooth_map = cv2.GaussianBlur(
            np.random.rand(self.height, self.width), kernel, 0
        )
        smooth_map = (smooth_map - np.min(smooth_map)) / (
            np.max(smooth_map) - np.min(smooth_map)
        )
        for i in range(self.n_blur_steps):
            blur_step = i + 1
            blur_strength = int(
                (self.n_blur_steps - blur_step + 1) / self.n_blur_steps * self.max_blur
            )
            mask = smooth_map < (blur_step / self.n_blur_steps)
            blurred_image = cv2.blur(background_image, (blur_strength, blur_strength))
            background_image = np.where(
                mask[..., np.newaxis], blurred_image, background_image
            )

        return background_image