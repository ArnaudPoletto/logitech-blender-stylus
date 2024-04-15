import random
import numpy as np
from tqdm import tqdm
from typing import Tuple

from utils.config import MIN_PRIORITY
from utils.seed import set_seed
from utils.config import RESOLUTION_DIGITS
from input_data_generation.module_generator import ModuleGenerator
from input_data_generation.module_generator_type import ModuleGeneratorType

class RandomWallLampModuleGenerator(ModuleGenerator):
    """
    A random wall lamp generator, linked to an input data generator to generate random wall lamp data.
    """
    
    def __init__(
        self,
        name: str,
        id: str,
        room_id: str,
        n_wall_lamps: int,
        xy_scale_range: Tuple[float, float],
        emission_strength_range: Tuple[float, float],
        padding: float,
        weight: float = 1.0,
        priority: int = MIN_PRIORITY,
        ) -> None:
        """
        Initialize the random wall lamp generator.
        
        Args:
            name (str): The prefix of the wall lamps name.
            id (str): The prefix of the wall lamps id.
            room_id (str): The id of the room.
            n_wall_lamps (int): The number of wall lamps to generate, -1 for unlimited.
            xy_scale_range (Tuple[float, float]): The range of xy scale values for the wall lamps.
            emission_strength_range (Tuple[float, float]): The range of emission strength values for the wall lamps.
            padding (float): The padding between the wall lamps.
            weight (float): The weight of the module, used to determine the probability of the module being selected. Defaults to 1.0.
            priority (int): The priority of the module, used to determine the order of the module being selected. Defaults to the minimum priority.
            
        Raises:
            ValueError: If the number of wall lamps is less than -1.
            ValueError: If the minimum xy scale is less than 0.
            ValueError: If the maximum xy scale is less than the minimum xy scale.
            ValueError: If the minimum z scale is less than 0.
            ValueError: If the maximum z scale is less than the minimum z scale.
            ValueError: If the minimum emission strength is less than 0.
            ValueError: If the maximum emission strength is less than the minimum emission strength.
            ValueError: If the padding is less than 0.
        """
        if n_wall_lamps < -1:
            raise ValueError(
                "The number of wall lamps must be greater than or equal to -1."
            )
        if xy_scale_range[0] < 0:
            raise ValueError("The minimum xy scale must be greater than or equal to 0.")
        if xy_scale_range[1] < xy_scale_range[0]:
            raise ValueError(
                "The maximum xy scale must be greater than or equal to the minimum xy scale."
            )
        if emission_strength_range[0] < 0:
            raise ValueError("The minimum emission strength must be greater than or equal to 0.")
        if emission_strength_range[1] < emission_strength_range[0]:
            raise ValueError(
                "The maximum emission strength must be greater than or equal to the minimum emission strength."
            )
        if padding < 0:
            raise ValueError("The padding must be greater than or equal to 0.")
            
        super(RandomWallLampModuleGenerator, self).__init__(
            type=ModuleGeneratorType.CEILING,
            name=name,
            id=id,
            weight=weight,
            priority=priority,
        )
        
        self.room_id = room_id
        self.n_wall_lamps = n_wall_lamps
        self.xy_scale_range = xy_scale_range
        self.emission_strength_range = emission_strength_range
        self.padding = padding
        
    def generate(
        self,
        wall_scales_per_wall: dict = None,
        existing_objects_per_wall: dict = None,
    ) -> Tuple[dict, dict]:
        set_seed()
        
        wall_scale = wall_scales_per_wall[self.type]
        existing_objects = existing_objects_per_wall[self.type]
        
        width, length = wall_scale
        resolution = 10**RESOLUTION_DIGITS
        padding_resolution = int(self.padding * resolution)
        
        # Generate wall lamps one by one
        wall_lamps_data = {"blender_objects": {}}
        n_placed_wall_lamps = 0
        bar = tqdm(total=self.n_wall_lamps, desc=f"Generating {self.name}", leave=False)
        while self.n_wall_lamps == -1 or n_placed_wall_lamps < self.n_wall_lamps:
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
                        wall_lamps_data,
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
            wall_lamps_data["blender_objects"][f"{self.id}_{n_placed_wall_lamps}"] = {
                "type": "WallLamp",
                "args": {
                    "name": f"{self.name}{n_placed_wall_lamps}",
                    "relative_location": {
                        "x": x / resolution - width / 2,
                        "y": y / resolution - length / 2,
                    },
                    "scale": {
                        "x": 2 * w / resolution,
                        "y": 2 * l / resolution,
                    },
                    "emission_strength": random.uniform(*self.emission_strength_range),
                },
                "parents": [f"{self.room_id}.ceiling"],
            }

            n_placed_wall_lamps += 1
            bar.update(1)

        # Update existing objects on the used wall
        existing_objects_per_wall[self.type] = existing_objects

        return wall_lamps_data, existing_objects_per_wall