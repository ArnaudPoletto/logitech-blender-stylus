# This file contains the random christmas tree module generator class.

import random
import numpy as np
from typing import Tuple, Dict, Any

from utils.seed import set_seed
from config.config import RESOLUTION_DIGITS, MIN_PRIORITY
from input_data_generation.module_generator import ModuleGenerator
from input_data_generation.module_generator_type import ModuleGeneratorType


class RandomChristmasTreeModuleGenerator(ModuleGenerator):
    """
    A random christmas tree generator, linked to an input data generator to generate christmas tree data.
    """

    def __init__(
        self,
        name: str,
        id: str,
        room_id: str,
        height_range: Tuple[float, float],
        radius_range: Tuple[float, float],
        n_leds_range: Tuple[int, int],
        led_radius_range: Tuple[float, float],
        emission_range: Tuple[float, float],
        flicker_probability_range: Tuple[float, float],
        padding: float,
        weight: float = 1.0,
        priority: int = MIN_PRIORITY,
    ) -> None:
        """
        Initialize the random christmas tree generator.

        Args:
            name (str): The name of the module.
            id (str): The id of the module.
            room_id (str): The id of the room.
            height_range (Tuple[float, float]): The range of the height of the christmas tree.
            radius_range (Tuple[float, float]): The range of the radius of the christmas tree.
            n_leds_range (Tuple[int, int]): The range of the number of leds of the christmas tree.
            led_radius_range (Tuple[float, float]): The range of the radius of the leds of the christmas tree.
            emission_range (Tuple[float, float]): The range of the emission of the leds of the christmas tree.
            flicker_probability_range (Tuple[float, float]): The range of the flicker probability of the leds of the christmas tree.
            padding (float): The padding around the christmas tree.
            weight (float): The weight of the module, used to determine the probability of the module being selected. Defaults to 1.0.
            priority (int): The priority of the module, used to determine the order of the module being selected. Defaults to the minimum priority.

        Raises:
            ValueError: If the height is less than or equal to 0.
            ValueError: If the maximum height is less than the minimum height.
            ValueError: If the radius is less than or equal to 0.
            ValueError: If the maximum radius is less than the minimum radius.
            ValueError: If the number of leds is less than or equal to 0.
            ValueError: If the maximum number of leds is less than the minimum number of leds.
            ValueError: If the radius of the leds is less than or equal to 0.
            ValueError: If the maximum radius of the leds is less than the minimum radius of the leds.
            ValueError: If the emission of the leds is less than 0.
            ValueError: If the maximum emission of the leds is less than the minimum emission of the leds.
            ValueError: If the flicker probability of the leds is less than 0.
            ValueError: If the maximum flicker probability of the leds is greater than 1.
            ValueError: If the maximum flicker probability of the leds is less than the minimum flicker probability.
            ValueError: If the padding is less than 0.
        """
        if height_range[0] <= 0:
            raise ValueError(
                "❌ The minimum height of the christmas tree must be greater than 0."
            )
        if height_range[1] < height_range[0]:
            raise ValueError(
                "❌ The maximum height of the christmas tree must be greater than the minimum height."
            )
        if radius_range[0] <= 0:
            raise ValueError(
                "❌ The minimum radius of the christmas tree must be greater than 0."
            )
        if radius_range[1] < radius_range[0]:
            raise ValueError(
                "❌ The maximum radius of the christmas tree must be greater than the minimum radius."
            )
        if n_leds_range[0] <= 0:
            raise ValueError(
                "❌ The minimum number of leds of the christmas tree must be greater than 0."
            )
        if n_leds_range[1] < n_leds_range[0]:
            raise ValueError(
                "❌ The maximum number of leds of the christmas tree must be greater than the minimum number of leds."
            )
        if led_radius_range[0] <= 0:
            raise ValueError(
                "❌ The minimum radius of the leds of the christmas tree must be greater than 0."
            )
        if led_radius_range[1] < led_radius_range[0]:
            raise ValueError(
                "❌ The maximum radius of the leds of the christmas tree must be greater than the minimum radius of the leds."
            )
        if emission_range[0] < 0:
            raise ValueError(
                "❌ The minimum emission of the leds of the christmas tree must be greater than or equal to 0."
            )
        if emission_range[1] < emission_range[0]:
            raise ValueError(
                "❌ The maximum emission of the leds of the christmas tree must be greater than the minimum emission of the leds."
            )
        if flicker_probability_range[0] < 0:
            raise ValueError(
                "❌ The minimum flicker probability of the leds of the christmas tree must be greater than or equal to 0."
            )
        if flicker_probability_range[1] > 1:
            raise ValueError(
                "❌ The maximum flicker probability of the leds of the christmas tree must be less than or equal to 1."
            )
        if flicker_probability_range[1] < flicker_probability_range[0]:
            raise ValueError(
                "❌ The maximum flicker probability of the leds of the christmas tree must be greater than the minimum flicker probability."
            )
        if padding < 0:
            raise ValueError(
                "❌ The padding around the christmas tree must be greater than or equal to 0."
            )

        super(RandomChristmasTreeModuleGenerator, self).__init__(
            type=ModuleGeneratorType.FLOOR,
            name=name,
            id=id,
            weight=weight,
            priority=priority,
        )

        self.room_id = room_id
        self.height_range = height_range
        self.radius_range = radius_range
        self.n_leds_range = n_leds_range
        self.led_radius_range = led_radius_range
        self.emission_range = emission_range
        self.flicker_probability_range = flicker_probability_range
        self.padding = padding

    def generate(
        self,
        wall_scales_per_wall: Dict[str, Any] | None = None,
        existing_objects_per_wall: Dict[str, Any] | None = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Generate the christmas tree module.

        Args:
            wall_scales_per_wall (Dict[str, Any] | None): The scale of each wall.
            existing_objects_per_wall (Dict[str, Any] | None): The existing objects for each wall.

        Raises:
            ValueError: If the existing objects per wall is not provided.

        Returns:
            Tuple[Dict[str, Any], Dict[str, Any]]: The christmas tree data and the updated existing objects per wall.
        """
        if existing_objects_per_wall is None:
            raise ValueError("❌ The existing objects per wall must be provided.")
        set_seed()

        wall_scale = wall_scales_per_wall[self.type]
        existing_objects = existing_objects_per_wall[self.type]

        width, length = wall_scale
        resolution = 10**RESOLUTION_DIGITS
        padding_resolution = int(self.padding * resolution)

        # Get random christmas tree parameters
        radius = int(random.uniform(*self.radius_range) * resolution)
        height = int(random.uniform(*self.height_range) * resolution)
        n_leds = random.randint(*self.n_leds_range)
        flicker_probability = random.uniform(*self.flicker_probability_range)

        # Get the binary map of possible positions for the christmas tree
        position_map = np.ones((width * resolution, length * resolution))
        # Add wall bounds
        position_map[: radius + padding_resolution, :] = 0
        position_map[-radius - padding_resolution :, :] = 0
        position_map[:, : radius + padding_resolution] = 0
        position_map[:, -radius - padding_resolution :] = 0
        # Add existing_objects bounds
        for existing_object in existing_objects:
            tx, ty, tw, tl = existing_object
            min_x = max(0, tx - tw - radius - padding_resolution)
            max_x = min(width * resolution, tx + tw + radius + padding_resolution)
            min_y = max(0, ty - tl - radius - padding_resolution)
            max_y = min(length * resolution, ty + tl + radius + padding_resolution)
            position_map[min_x:max_x, min_y:max_y] = 0

        # Get random position for the christmas tree
        if np.sum(position_map) / position_map.size < 0.1:
            positions = np.argwhere(position_map == 1)
            if positions.size == 0:
                return {}, existing_objects_per_wall
            x, y = positions[random.randint(0, positions.shape[0] - 1)]
        else:  # Special case to speed up the process when a lot of space is available
            is_valid_position = False
            while not is_valid_position:
                x = random.randint(0, width * resolution - 1)
                y = random.randint(0, length * resolution - 1)
                if position_map[x, y] == 1:
                    is_valid_position = True

        # Add the christmas tree to the room and set the data
        christmas_tree = (x, y, radius, radius)
        existing_objects.append(christmas_tree)
        christmas_tree_data = {
            "blender_objects": {
                self.id: {
                    "type": "ChristmasTree",
                    "args": {
                        "name": self.name,
                        "relative_location": {
                            "x": x / resolution - width / 2,
                            "y": y / resolution - length / 2,
                        },
                        "height": height / resolution,
                        "radius": radius / resolution,
                        "n_leds": n_leds,
                        "led_radius_range": self.led_radius_range,
                        "emission_range": self.emission_range,
                        "flicker_probability": flicker_probability,
                    },
                    "parents": [f"{self.room_id}.floor"],
                }
            }
        }

        # Update existing objects on the used wall
        existing_objects_per_wall[self.type] = existing_objects

        return christmas_tree_data, existing_objects_per_wall
