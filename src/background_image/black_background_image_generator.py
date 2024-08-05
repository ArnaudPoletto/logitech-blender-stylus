# This file contains the black background image generator class.

import numpy as np

from background_image.background_image_generator import BackgroundImageGenerator


class BlackBackgroundImageGenerator(BackgroundImageGenerator):
    """
    A black background image generator.
    """
    def __init__(
        self,
        width: int,
        height: int,
    ) -> None:
        """
        Initialize the black background image generator.
        
        Args:
            width (int): The width of the background image.
            height (int): The height of the background image.
        """
        super(BlackBackgroundImageGenerator, self).__init__(width=width, height=height)

        self.width = width
        self.height = height

    def get_background_image(self) -> np.ndarray:
        """
        Get the background image.
        
        Returns:
            np.ndarray: The background image.
        """
        background_image = np.zeros((self.height, self.width, 4), dtype=np.float32)

        return background_image