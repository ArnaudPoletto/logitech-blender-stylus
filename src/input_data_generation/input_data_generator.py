import random
import numpy as np
from typing import List

from input_data_generation.module_operator import ModuleOperator
from input_data_generation.module_generator import ModuleGenerator
from input_data_generation.random_room_module_generator import RandomRoomModuleGenerator


# TODO: add documentation
class InputDataGenerator:
    """
    An input data generator.
    """

    def __init__(
        self,
        room_module: RandomRoomModuleGenerator, 
        modules: List[ModuleGenerator|ModuleOperator], seed: int | None
    ) -> None:
        """
        Initialize the input data generator.

        Args:
            room_module (RandomRoomModuleGenerator): The room module.
            modules (List[ModuleGenerator|ModuleOperator]): The modules, as a list of module generators or operators.
            
        Raises:
        """
        self.room_module = room_module
        self.modules = modules
        self.seed = seed

    # def get_random_windows(
    #     self,
    #     room_id: str,
    #     wall_name: str,
    #     wall_scale: Tuple[float, float],
    #     n_windows: int,
    #     xy_scale_range: Tuple[float, float],
    #     padding: float,
    #     resolution_digits: int,
    # ) -> dict:
    #     # TODO: documentation
    #     """
    #     Get random windows on the specified room wall.
    #     """
    #     width, length = wall_scale
    #     resolution = 10**resolution_digits
    #     padding_resolution = int(padding * resolution)

    #     windows = []
    #     windows_data = {}
    #     n_placed_windows = 0
    #     while n_windows == -1 or n_placed_windows < n_windows:
    #         # Get random window dimensions
    #         w = int(random.uniform(*xy_scale_range) * resolution)
    #         l = int(random.uniform(*xy_scale_range) * resolution)

    #         # Get the binary map of possible positions for the window
    #         position_map = np.ones((width * resolution, length * resolution))
    #         # Add wall bounds
    #         position_map[: w + padding_resolution, :] = 0
    #         position_map[-w - padding_resolution :, :] = 0
    #         position_map[:, : l + padding_resolution] = 0
    #         position_map[:, -l - padding_resolution :] = 0
    #         for window in windows:
    #             # Add window bounds
    #             wx, wy, ww, wl = window
    #             min_x = max(0, wx - ww - w - padding_resolution)
    #             max_x = min(width * resolution, wx + ww + w + padding_resolution)
    #             min_y = max(0, wy - wl - l - padding_resolution)
    #             max_y = min(length * resolution, wy + wl + l + padding_resolution)
    #             position_map[min_x:max_x, min_y:max_y] = 0

    #         # Get random position for the window
    #         xs, ys = np.where(position_map == 1)
    #         if len(xs) == 0:
    #             break
    #         idx = random.randint(0, len(xs) - 1)
    #         x = xs[idx]
    #         y = ys[idx]

    #         # Add the window to the room and set the data
    #         window = (x, y, w, l)
    #         windows.append(window)
    #         window_name = f"{wall_name}_window_{n_placed_windows}"
    #         windows_data[window_name] = {
    #             "type": "Window",
    #             "args": {
    #                 "name": f"Window{n_placed_windows}",
    #                 "relative_location": {
    #                     "x": x / resolution - width / 2,
    #                     "y": y / resolution - length / 2,
    #                 },
    #                 "scale": {
    #                     "x": 2 * w / resolution,
    #                     "y": 2 * l / resolution,
    #                 },
    #             },
    #             "parents": [f"{room_id}.{wall_name}"],
    #         }

    #         # Add random window decorator
    #         random_decorator = random.choice(["blinds", "muntins"])
    #         if random_decorator == "blinds":
    #             windows_data[f"{window_name}_blinds"] = {
    #                 "type": "Blinds",
    #                 "args": {
    #                     "name": f"Window{n_placed_windows}Blinds",
    #                     "n_blinds": random.randint(5, 20),
    #                     "angle": random.uniform(0, math.pi),
    #                     "vertical": random.choice([True, False]),
    #                 },
    #                 "parents": [window_name],
    #             }
    #         elif random_decorator == "muntins":
    #             windows_data[f"{window_name}_muntins"] = {
    #                 "type": "Muntins",
    #                 "args": {
    #                     "name": f"Window{n_placed_windows}Muntins",
    #                     "size": random.uniform(0.1, 0.2),
    #                     "n_muntins_width": random.randint(1, 5),
    #                     "n_muntins_height": random.randint(1, 5),
    #                 },
    #                 "parents": [window_name],
    #             }
    #         add_shades = random.choice([True, False])
    #         if add_shades:
    #             windows_data[f"{window_name}_shades"] = {
    #                 "type": "Shades",
    #                 "args": {
    #                     "name": f"Window{n_placed_windows}Shades",
    #                     "shade_ratio": random.uniform(0.1, 0.9),
    #                     "transmission": random.uniform(0.1, 0.9),
    #                 },
    #                 "parents": [window_name],
    #             }

    #         n_placed_windows += 1

    #     return windows_data

    @staticmethod
    def _update_input_data(input_data: dict, update_data: dict) -> dict:
        if "gestures" in update_data:
            if update_data["gestures"].keys() & input_data["gestures"].keys():
                raise ValueError(
                    "Gesture names must be unique: cannot add the same gesture twice."
                )
            input_data["gestures"].update(update_data["gestures"])

        if "blender_objects" in update_data:
            if (
                update_data["blender_objects"].keys()
                & input_data["blender_objects"].keys()
            ):
                print(
                    update_data["blender_objects"].keys(),
                    input_data["blender_objects"].keys(),
                )
                raise ValueError(
                    "Blender object names must be unique: cannot add the same object twice."
                )
            input_data["blender_objects"].update(update_data["blender_objects"])

    def generate_input_data(self) -> dict:
        """
        Generate input data from the modules.

        Returns:
            dict: The input data.
        """
        # Set the seed
        random.seed(self.seed)
        np.random.seed(self.seed)

        input_data = {
            "gestures": {},
            "blender_objects": {},
        }

        # Generate the room and define room masks
        room_data, wall_scales_per_wall = self.room_module.generate()
        InputDataGenerator._update_input_data(input_data, room_data)
        existing_objects_per_wall = {k: [] for k in wall_scales_per_wall.keys()}

        # Apply other modules
        for module in self.modules:
            module_data, existing_objects_per_wall = module.generate(wall_scales_per_wall, existing_objects_per_wall)
            InputDataGenerator._update_input_data(input_data, module_data)
            
        return input_data