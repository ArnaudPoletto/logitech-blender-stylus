import random
import numpy as np
from typing import List, Tuple
from tqdm import tqdm

from utils.config import RESOLUTION_DIGITS
from input_data_generation.module_generator import ModuleGenerator
from input_data_generation.module_generator_type import ModuleGeneratorType


class RandomTableModuleGenerator(ModuleGenerator):
    """
    A random table generator, linked to an input data generator to generate table data.
    """

    def __init__(
        self,
        weight: float,
        priority: int,
        name: str,
        id: str,
        room_id: str,
        n_tables: int,
        xy_scale_range: Tuple[float, float],
        z_scale_range: Tuple[float, float],
        top_thickness_range: Tuple[float, float],
        leg_thickness_range: Tuple[float, float],
        padding: float,
    ) -> None:
        """
        Initialize the random table generator.

        Args:
            weight (float): The weight of the module, used to determine the probability of the module being selected.
            priority (int): The priority of the module, used to determine the order of the module being selected.
            name (str): The prefix of the tables name.
            id (str): The prefix of the tables id.
            room_id (str): The id of the room.
            n_tables (int): The number of tables to generate.
            xy_scale_range (Tuple[float, float]): The range of xy scale values for the tables.
            z_scale_range (Tuple[float, float]): The range of z scale values for the tables.
            top_thickness_range (Tuple[float, float]): The range of top thickness values for the tables.
            leg_thickness_range (Tuple[float, float]): The range of leg thickness values for the tables.
            padding (float): The padding between the tables.
        """
        super(RandomTableModuleGenerator, self).__init__(
            weight=weight,
            priority=priority,
            type=ModuleGeneratorType.ROOM_FLOOR,
            name=name,
            id=id,
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
        wall_scale: Tuple[int, int],
        existing_objects: List[Tuple[int, int, int, int]],
    ) -> Tuple[dict, List[Tuple[int, int, int, int]]]:
        """
        Generate the random tables.
        
        Args:
            wall_scale (Tuple[int, int]): The scale of the wall.
            existing_objects (List[Tuple[int, int, int, int]]): The existing objects in the room.

        Returns:
            dict: The tables data.
            List[Tuple[int, int, int, int]]: The updated existing objects.
        """
        width, length = wall_scale
        resolution = 10**RESOLUTION_DIGITS
        padding_resolution = int(self.padding * resolution)

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
                    return tables_data, existing_objects
                x, y = positions[random.randint(0, positions.shape[0] - 1)]
            else: # Special case to speed up the process when a lot of space is available
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
            
        return tables_data, existing_objects
