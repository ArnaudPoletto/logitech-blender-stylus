import random
from typing import Tuple

from utils.seed import set_seed
from config.config import RESOLUTION_DIGITS, MAX_PRIORITY
from input_data_generation.module_generator import ModuleGenerator
from input_data_generation.module_generator_type import ModuleGeneratorType


class RandomRoomModuleGenerator(ModuleGenerator):
    """
    A random room module generator, linked to an input data generator to generate room data.
    """

    def __init__(
        self,
        name: str,
        id: str,
        xy_scale_range: Tuple[float, float],
        z_scale_range: Tuple[float, float],
    ) -> None:
        """
        Initialize the random room module generator.

        Args:
            weight (float): The weight of the module, used to determine the probability of the module being selected.
            name (str): The name of the room.
            id (str): The id of the room.
            xy_scale_range (Tuple[float, float]): The range of xy scale values for the room.
            z_scale_range (Tuple[float, float]): The range of z scale values for the room.

        Raises:
            ValueError: If the minimum xy scale is less than 0.
            ValueError: If the maximum xy scale is less than the minimum xy scale.
            ValueError: If the minimum z scale is less than 0.
            ValueError: If the maximum z scale is less than the minimum z scale.
            ValueError: If the resolution digits is less than 0.
        """
        if xy_scale_range[0] < 0:
            raise ValueError("The minimum xy scale must be greater than or equal to 0.")
        if xy_scale_range[1] < xy_scale_range[0]:
            raise ValueError(
                "The maximum xy scale must be greater than or equal to the minimum xy scale."
            )
        if z_scale_range[0] < 0:
            raise ValueError("The minimum z scale must be greater than or equal to 0.")
        if z_scale_range[1] < z_scale_range[0]:
            raise ValueError(
                "The maximum z scale must be greater than or equal to the minimum z scale."
            )

        super(RandomRoomModuleGenerator, self).__init__(
            type=ModuleGeneratorType.GLOBAL,
            name=name,
            id=id,
            priority=MAX_PRIORITY,
        )

        self.xy_scale_range = xy_scale_range
        self.z_scale_range = z_scale_range

    def generate(
        self,
        wall_scales_per_wall: dict = None,
        existing_objects_per_wall: dict = None,
    ) -> Tuple[dict, dict]:
        set_seed()
        
        # Get random room parameters
        scale_x = int(round(random.uniform(*self.xy_scale_range), RESOLUTION_DIGITS))
        scale_y = int(round(random.uniform(*self.xy_scale_range), RESOLUTION_DIGITS))
        scale_z = int(round(random.uniform(*self.z_scale_range), RESOLUTION_DIGITS))

        # Define data
        room_data = {
            "blender_objects": {
                self.id: {
                    "type": "Room",
                    "args": {
                        "name": self.name,
                        "location": {
                            "x": 0,
                            "y": 0,
                            "z": 0,
                        },
                        "scale": {"x": scale_x, "y": scale_y, "z": scale_z},
                    },
                }
            }
        }

        # Get wall scales
        floor_scale = (scale_y, scale_x)
        ceiling_scale = (scale_y, scale_x)
        front_wall_scale = (scale_x, scale_z)
        back_wall_scale = (scale_x, scale_z)
        left_wall_scale = (scale_y, scale_z)
        right_wall_scale = (scale_y, scale_z)
        wall_scales_per_wall = {
            ModuleGeneratorType.FLOOR: floor_scale,
            ModuleGeneratorType.CEILING: ceiling_scale,
            ModuleGeneratorType.FRONT_WALL: front_wall_scale,
            ModuleGeneratorType.BACK_WALL: back_wall_scale,
            ModuleGeneratorType.LEFT_WALL: left_wall_scale,
            ModuleGeneratorType.RIGHT_WALL: right_wall_scale,
        }

        return room_data, wall_scales_per_wall
