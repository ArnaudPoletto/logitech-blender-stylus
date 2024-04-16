import cv2
import bpy
import random
import numpy as np
from typing import Tuple

from background_image.background_image_generator import BackgroundImageGenerator


# TODO: add documentation
class BlackBackgroundImageGenerator(BackgroundImageGenerator):
    def __init__(
        self,
        width: int,
        height: int,
    ) -> None:
        super(BlackBackgroundImageGenerator, self).__init__(width=width, height=height)

        self.width = width
        self.height = height

    def _get_background_image(self) -> np.array:
        background_image = np.zeros((self.height, self.width, 4), dtype=np.float32)

        return background_image