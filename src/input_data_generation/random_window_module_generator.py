import random
import numpy as np
from typing import List, Tuple
from tqdm import tqdm

from utils.seed import set_seed
from blender_objects.shades import Shades
from utils.config import RESOLUTION_DIGITS
from blender_objects.window_decorator import WindowDecorator
from input_data_generation.module_generator import ModuleGenerator
from input_data_generation.module_generator_type import ModuleGeneratorType


class RandomWindowModuleGenerator(ModuleGenerator):
    """
    A random window generator, linked to an input data generator to generate window data.
    """

    # TODO: define default values and setters
    # TODO: refactor checks to a separate method for bounds checking
    def __init__(
        self,
        weight: float,
        priority: int,
        wall_type: ModuleGeneratorType,
        name: str,
        id: str,
        room_id: str,
        n_windows: int,
        xy_scale_range: Tuple[float, float],
        shades_probability: float,
        shade_ratio_range: Tuple[float, float],
        shade_transmission_range: Tuple[float, float],
        blinds_probability: float,
        n_blinds_range: Tuple[int, int],
        blind_angle_range: Tuple[float, float],
        blind_vertical: bool,
        muntins_probability: float,
        muntin_size_range: Tuple[float, float],
        n_muntins_width_range: Tuple[float, float],
        n_muntins_height_range: Tuple[float, float],
        padding: float,
    ) -> None:
        """
        Initialize the random window generator.

        Args:
            weight (float): The weight of the module, used to determine the probability of the module being selected.
            priority (int): The priority of the module, used to determine the order of the module being selected.
            wall_type (ModuleGeneratorType): The type of the wall.
            name (str): The prefix of the windows name.
            id (str): The prefix of the windows id.
            room_id (str): The id of the room.
            n_windows (int): The number of windows to generate, -1 for unlimited.
            xy_scale_range (Tuple[float, float]): The range of xy scale values for the windows.
            decorators (List[WindowDecorator]): The decorators to apply to the windows. If multiple decorators are provided, they will be applied randomly.
            shades_probability (float): The probability of adding shades to the windows.
            shade_ratio_range (Tuple[float, float]): The range of shade ratio values for the shades.
            shade_transmission_range (Tuple[float, float]): The range of transmission values for the shades.
            blinds_probability (float): The probability of adding blinds to the windows.
            n_blinds_range (Tuple[int, int]): The range of number of blinds to add to the windows.
            blind_angle_range (Tuple[float, float]): The range of angle values for the blinds.
            blind_vertical (bool): Whether the blinds can be vertical or only horizontal.
            muntins_probability (float): The probability of adding muntins to the windows.
            muntin_size_range (Tuple[float, float]): The range of muntin size values for the muntins.
            n_muntins_width_range (Tuple[float, float]): The range of number of muntins width values for the muntins.
            n_muntins_height_range (Tuple[float, float]): The range of number of muntins height values for the muntins.
            padding (float): The padding between the windows.

        Raises:
            ValueError: If the wall type is not a vertical wall type.
            ValueError: If the number of windows is less than -1.
            ValueError: If the minimum xy scale is less than 0.
            ValueError: If the maximum xy scale is less than the minimum xy scale.
            ValueError: If the shades probability is less than 0 or greater than 1.
            ValueError: If the minimum shade ratio is less than 0.
            ValueError: If the maximum shade ratio is greater than 1.
            ValueError: If the maximum shade ratio is less than the minimum shade ratio.
            ValueError: If the minimum transmission is less than 0.
            ValueError: If the maximum transmission is greater than 1.
            ValueError: If the maximum transmission is less than the minimum transmission.
            ValueError: If the minimum blinds probability is less than 0 or greater than 1.
            ValueError: If the minimum number of blinds is less than 0.
            ValueError: If the maximum number of blinds is less than the minimum number of blinds.
            ValueError: If the minimum blind angle is less than 0.
            ValueError: If the maximum blind angle is greater than pi.
            ValueError: If the maximum blind angle is less than the minimum blind angle.
            ValueError: If the minimum muntins probability is less than 0 or greater than 1.
            ValueError: If the minimum muntin size is less than 0.
            ValueError: If the minimum number of muntins width is less than 1.
            ValueError: If the maximum number of muntins width is less than the minimum number of muntins width.
            ValueError: If the minimum number of muntins height is less than 1.
            ValueError: If the maximum number of muntins height is less than the minimum number of muntins height.
            ValueError: if the blinds and muntins probabilities sum to more than 1.
            ValueError: If the padding is less than 0.
        """
        if wall_type not in ModuleGeneratorType.get_vertical_wall_types():
            raise ValueError("The wall type must be a vertical wall type.")
        if n_windows < -1:
            raise ValueError(
                "The number of windows must be greater than or equal to -1."
            )
        if xy_scale_range[0] < 0:
            raise ValueError("The minimum xy scale must be greater than or equal to 0.")
        if xy_scale_range[1] < xy_scale_range[0]:
            raise ValueError(
                "The maximum xy scale must be greater than or equal to the minimum xy scale."
            )
        if shades_probability < 0 or shades_probability > 1:
            raise ValueError("The shades probability must be between 0 and 1.")
        if shade_ratio_range[0] < 0:
            raise ValueError(
                "The minimum shade ratio must be greater than or equal to 0."
            )
        if shade_ratio_range[1] > 1:
            raise ValueError("The maximum shade ratio must be less than or equal to 1.")
        if shade_ratio_range[1] < shade_ratio_range[0]:
            raise ValueError(
                "The maximum shade ratio must be greater than or equal to the minimum shade ratio."
            )
        if shade_transmission_range[0] < 0:
            raise ValueError(
                "The minimum shade transmission must be greater than or equal to 0."
            )
        if shade_transmission_range[1] > 1:
            raise ValueError(
                "The maximum shade transmission must be less than or equal to 1."
            )
        if shade_transmission_range[1] < shade_transmission_range[0]:
            raise ValueError(
                "The maximum shade transmission must be greater than or equal to the minimum shade transmission."
            )
        if blinds_probability < 0 or blinds_probability > 1:
            raise ValueError("The blinds probability must be between 0 and 1.")
        if n_blinds_range[0] < 0:
            raise ValueError(
                "The minimum number of blinds must be greater than or equal to 0."
            )
        if n_blinds_range[1] < n_blinds_range[0]:
            raise ValueError(
                "The maximum number of blinds must be greater than or equal to the minimum number of blinds."
            )
        if blind_angle_range[0] < 0:
            raise ValueError(
                "The minimum blind angle must be greater than or equal to 0."
            )
        if blind_angle_range[1] > np.pi:
            raise ValueError(
                "The maximum blind angle must be less than or equal to pi."
            )
        if blind_angle_range[1] < blind_angle_range[0]:
            raise ValueError(
                "The maximum blind angle must be greater than or equal to the minimum blind angle."
            )
        if muntins_probability < 0 or muntins_probability > 1:
            raise ValueError("The muntins probability must be between 0 and 1.")
        if muntin_size_range[0] < 0:
            raise ValueError(
                "The minimum muntin size must be greater than or equal to 0."
            )
        if n_muntins_width_range[0] < 1:
            raise ValueError(
                "The minimum number of muntins width must be greater than or equal to 1."
            )
        if n_muntins_width_range[1] < n_muntins_width_range[0]:
            raise ValueError(
                "The maximum number of muntins width must be greater than or equal to the minimum number of muntins width."
            )
        if n_muntins_height_range[0] < 1:
            raise ValueError(
                "The minimum number of muntins height must be greater than or equal to 1."
            )
        if n_muntins_height_range[1] < n_muntins_height_range[0]:
            raise ValueError(
                "The maximum number of muntins height must be greater than or equal to the minimum number of muntins height."
            )
        if blinds_probability + muntins_probability > 1:
            raise ValueError(
                "The sum of the blinds and muntins probabilities must be less than or equal to 1."
            )
        if padding < 0:
            raise ValueError("The padding must be greater than or equal to 0.")

        super(RandomWindowModuleGenerator, self).__init__(
            weight=weight,
            priority=priority,
            type=wall_type,
            name=name,
            id=id,
        )

        self.room_id = room_id
        self.n_windows = n_windows
        self.xy_scale_range = xy_scale_range
        self.shades_probability = shades_probability
        self.shade_ratio_range = shade_ratio_range
        self.shade_transmission_range = shade_transmission_range
        self.blinds_probability = blinds_probability
        self.n_blinds_range = n_blinds_range
        self.blind_angle_range = blind_angle_range
        self.blind_vertical = blind_vertical
        self.muntins_probability = muntins_probability
        self.muntin_size_range = muntin_size_range
        self.n_muntins_width_range = n_muntins_width_range
        self.n_muntins_height_range = n_muntins_height_range
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
        windows_data = {"blender_objects": {}}
        n_placed_windows = 0
        bar = tqdm(total=self.n_windows, desc=f"Generating {self.name}", leave=False)
        while self.n_windows == -1 or n_placed_windows < self.n_windows:
            # Get random window dimensions
            w = int(random.uniform(*self.xy_scale_range) * resolution)
            l = int(random.uniform(*self.xy_scale_range) * resolution)

            # Get the binary map of possible positions for the window
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

            # Get random position for the window
            if np.sum(position_map) / position_map.size < 0.1:
                positions = np.argwhere(position_map == 1)
                if positions.size == 0:
                    break
                x, y = positions[random.randint(0, positions.shape[0] - 1)]
            else:  # Special case to speed up the process when a lot of space is available
                is_valid_position = False
                while not is_valid_position:
                    x = random.randint(0, width * resolution - 1)
                    y = random.randint(0, length * resolution - 1)
                    if position_map[x, y] == 1:
                        is_valid_position = True

            # Add the window to the room and set the data
            window = (x, y, w, l)
            existing_objects.append(window)
            window_id = f"{self.id}_{n_placed_windows}"
            windows_data["blender_objects"][window_id] = {
                "type": "Window",
                "args": {
                    "name": f"{self.name}{n_placed_windows}",
                    "relative_location": {
                        "x": x / resolution - width / 2,
                        "y": y / resolution - length / 2,
                    },
                    "scale": {
                        "x": 2 * w / resolution,
                        "y": 2 * l / resolution,
                    },
                },
                "parents": [f"{self.room_id}.{self.type.value}"],
            }

            # Add decorators to the windows
            shades_p = random.uniform(0, 1)
            if shades_p < self.shades_probability:
                shade_ratio = random.uniform(*self.shade_ratio_range)
                transmission = random.uniform(*self.shade_transmission_range)
                windows_data["blender_objects"][f"{window_id}_shades"] = {
                    "type": "Shades",
                    "args": {
                        "name": f"{self.name}Shades",
                        "shade_ratio": shade_ratio,
                        "transmission": transmission,
                    },
                    "parents": [f"{window_id}"],
                }

            n_placed_windows += 1
            bar.update(1)
            decorator_p = random.uniform(0, 1)
            if decorator_p < self.blinds_probability:
                n_blinds = random.randint(*self.n_blinds_range)
                angle = random.uniform(*self.blind_angle_range)
                vertical = random.choice([True, False]) if self.blind_vertical else False
                windows_data["blender_objects"][f"{window_id}_blinds"] = {
                    "type": "Blinds",
                    "args": {
                        "name": f"{self.name}Blinds",
                        "n_blinds": n_blinds,
                        "angle": angle,
                        "vertical": vertical,
                    },
                    "parents": [window_id],
                }
            elif decorator_p < self.blinds_probability + self.muntins_probability:
                size = random.uniform(*self.muntin_size_range)
                n_muntins_width = random.randint(*self.n_muntins_width_range)
                n_muntins_height = random.randint(*self.n_muntins_height_range)
                windows_data["blender_objects"][f"{window_id}_muntins"] = {
                    "type": "Muntins",
                    "args": {
                        "name": f"{self.name}Muntins",
                        "size": size,
                        "n_muntins_width": n_muntins_width,
                        "n_muntins_height": n_muntins_height,
                    },
                    "parents": [window_id],
                }

        # Update existing objects on the used wall
        existing_objects_per_wall[self.type] = existing_objects
        
        return windows_data, existing_objects_per_wall
