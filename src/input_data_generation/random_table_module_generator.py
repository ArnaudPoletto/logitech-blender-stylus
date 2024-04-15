import random
import numpy as np
from typing import List, Tuple
from tqdm import tqdm

from utils.seed import set_seed
from utils.config import RESOLUTION_DIGITS, MIN_PRIORITY
from input_data_generation.module_generator import ModuleGenerator
from input_data_generation.module_generator_type import ModuleGeneratorType


class RandomTableModuleGenerator(ModuleGenerator):
    """
    A random table generator, linked to an input data generator to generate table data.
    """

    def __init__(
        self,
        name: str,
        id: str,
        room_id: str,
        n_tables: int,
        xy_scale_range: Tuple[float, float],
        z_scale_range: Tuple[float, float],
        top_thickness_range: Tuple[float, float],
        leg_thickness_range: Tuple[float, float],
        padding: float,
        weight: float = 1.0,
        priority: int = MIN_PRIORITY,
    ) -> None:
        """
        Initialize the random table generator.

        Args:
            name (str): The prefix of the tables name.
            id (str): The prefix of the tables id.
            room_id (str): The id of the room.
            n_tables (int): The number of tables to generate, -1 for unlimited.
            xy_scale_range (Tuple[float, float]): The range of xy scale values for the tables.
            z_scale_range (Tuple[float, float]): The range of z scale values for the tables.
            top_thickness_range (Tuple[float, float]): The range of top thickness values for the tables.
            leg_thickness_range (Tuple[float, float]): The range of leg thickness values for the tables.
            padding (float): The padding between the tables.
            weight (float): The weight of the module, used to determine the probability of the module being selected. Defaults to 1.0.
            priority (int): The priority of the module, used to determine the order of the module being selected. Defaults to the minimum priority.

        Raises:
            ValueError: If the number of tables is less than -1.
            ValueError: If the minimum xy scale is less than 0.
            ValueError: If the maximum xy scale is less than the minimum xy scale.
            ValueError: If the minimum z scale is less than 0.
            ValueError: If the maximum z scale is less than the minimum z scale.
            ValueError: If the minimum top thickness is less than 0.
            ValueError: If the maximum top thickness is less than the minimum top thickness.
            ValueError: If the minimum leg thickness is less than 0.
            ValueError: If the maximum leg thickness is less than the minimum leg thickness.
            ValueError: If the padding is less than 0.
        """
        if n_tables < -1:
            raise ValueError(
                "The number of tables must be greater than or equal to -1."
            )
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
        if top_thickness_range[0] < 0:
            raise ValueError(
                "The minimum top thickness must be greater than or equal to 0."
            )
        if top_thickness_range[1] < top_thickness_range[0]:
            raise ValueError(
                "The maximum top thickness must be greater than or equal to the minimum top thickness."
            )
        if leg_thickness_range[0] < 0:
            raise ValueError(
                "The minimum leg thickness must be greater than or equal to 0."
            )
        if leg_thickness_range[1] < leg_thickness_range[0]:
            raise ValueError(
                "The maximum leg thickness must be greater than or equal to the minimum leg thickness."
            )
        if padding < 0:
            raise ValueError("The padding must be greater than or equal to 0.")

        super(RandomTableModuleGenerator, self).__init__(
            type=ModuleGeneratorType.FLOOR,
            name=name,
            id=id,
            weight=weight,
            priority=priority,
        )

        self.room_id = room_id
        self.n_tables = n_tables
        self.xy_scale_range = xy_scale_range
        self.z_scale_range = z_scale_range
        self.top_thickness_range = top_thickness_range
        self.leg_thickness_range = leg_thickness_range
        self.padding = padding

    def generate(
        self,
        wall_scales_per_wall: dict = None,
        existing_objects_per_wall: dict = None,
    ) -> Tuple[dict, List[Tuple[int, int, int, int]]]:
        set_seed()
        
        wall_scale = wall_scales_per_wall[self.type]
        existing_objects = existing_objects_per_wall[self.type]

        width, length = wall_scale
        resolution = 10**RESOLUTION_DIGITS
        padding_resolution = int(self.padding * resolution)

        # Generate tables one by one
        tables_data = {"blender_objects": {}}
        n_placed_tables = 0
        bar = tqdm(total=self.n_tables, desc=f"Generating {self.name}", leave=False)
        while self.n_tables == -1 or n_placed_tables < self.n_tables:
            # Get random table dimensions
            w = int(random.uniform(*self.xy_scale_range) * resolution)
            l = int(random.uniform(*self.xy_scale_range) * resolution)

            # Get the binary map of possible positions for the table
            position_map = np.ones((width * resolution, length * resolution))
            # Add wall bounds
            position_map[: w + padding_resolution, :] = 0
            position_map[-w - padding_resolution :, :] = 0
            position_map[:, : l + padding_resolution] = 0
            position_map[:, -l - padding_resolution :] = 0
            # Add existing_objects bounds
            for existing_object in existing_objects:
                tx, ty, tw, tl = existing_object
                min_x = max(0, tx - tw - w - padding_resolution)
                max_x = min(width * resolution, tx + tw + w + padding_resolution)
                min_y = max(0, ty - tl - l - padding_resolution)
                max_y = min(length * resolution, ty + tl + l + padding_resolution)
                position_map[min_x:max_x, min_y:max_y] = 0

            # Get random position for the table
            if np.sum(position_map) / position_map.size < 0.1:
                positions = np.argwhere(position_map == 1)
                if positions.size == 0:
                    return (
                        tables_data,
                        existing_objects,
                    )  # If there is no more space, stop the process
                x, y = positions[random.randint(0, positions.shape[0] - 1)]
            else:  # Special case to speed up the process when a lot of space is available
                is_valid_position = False
                while not is_valid_position:
                    x = random.randint(0, width * resolution - 1)
                    y = random.randint(0, length * resolution - 1)
                    if position_map[x, y] == 1:
                        is_valid_position = True

            # Add the table to the room and set the data
            table = (x, y, w, l)
            existing_objects.append(table)
            tables_data["blender_objects"][f"{self.id}_{n_placed_tables}"] = {
                "type": "Table",
                "args": {
                    "name": f"{self.name}{n_placed_tables}",
                    "relative_location": {
                        "x": x / resolution - width / 2,
                        "y": y / resolution - length / 2,
                    },
                    "scale": {
                        "x": 2 * w / resolution,
                        "y": 2 * l / resolution,
                        "z": random.uniform(*self.z_scale_range),
                    },
                    "top_thickness": random.uniform(*self.top_thickness_range),
                    "leg_thickness": random.uniform(*self.leg_thickness_range),
                },
                "parents": [f"{self.room_id}.floor"],
            }

            n_placed_tables += 1
            bar.update(1)

        # Update existing objects on the used wall
        existing_objects_per_wall[self.type] = existing_objects

        return tables_data, existing_objects_per_wall
