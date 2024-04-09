import math
import json
import random
import numpy as np
from typing import Tuple, List

from utils.config import RESOLUTION_DIGITS
from input_data_generation.module_generator import ModuleGenerator
from input_data_generation.module_generator_type import ModuleGeneratorType
from input_data_generation.random_room_module_generator import RandomRoomModuleGenerator


# TODO: add documentation
class InputDataGenerator:
    """
    An input data generator.
    """

    def __init__(
        self, modules: List[ModuleGenerator | List[ModuleGenerator]], seed: int | None
    ) -> None:
        """
        Initialize the input data generator.

        Args:
            modules (List[ModuleGenerator|List[ModuleGenerator]]): The modules, as a list of module generators or list of module generators. Lists of module generators are modules that have the same type and are randomly selected among them.
            seed (int|None): The seed.
            
        Raises:
            ValueError: If a global module is grouped in a list of modules-
            ValueError: If a module is grouped with a module of a different type.
            ValueError: If a non-global module is not grouped in a list of modules.
        """
        for module in modules:
            if isinstance(module, list):
                module_type = None
                for m in module:
                    if m.type == ModuleGeneratorType.GLOBAL:
                        raise ValueError(
                            "Global modules cannot be grouped in a list of modules."
                        )
                    if module_type is not None and m.type != module_type:
                        raise ValueError(
                            "Modules in a list of modules must have the same type."
                        )
                    module_type = m.type
            elif module.type != ModuleGeneratorType.GLOBAL:
                raise ValueError(
                    "Non-global modules must be grouped in a list of modules."
                )
                
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

    def generate_input_data_from_modules(self):
        """
        Generate input data from the modules.

        Returns:
            dict: The input data.

        Raises:
            ValueError: If there is more than one room module.
            ValueError: If there is no room module.
        """
        # Set the seed
        random.seed(self.seed)
        np.random.seed(self.seed)

        input_data = {
            "gestures": {},
            "blender_objects": {},
        }
        
        modules = self.modules.copy()

        # Get and generate room module
        room_module = None
        for module in modules:
            if isinstance(module, RandomRoomModuleGenerator):
                if room_module is not None:
                    raise ValueError(
                        "Only one room module is allowed: found more than one."
                    )
                room_module = module
        if room_module is None:
            raise ValueError(
                "Could not find room module: at least one room module is required."
            )
        room_data, scales_per_wall = room_module.generate()
        InputDataGenerator._update_input_data(input_data, room_data)

        # Filter out room module that has already been generated
        modules = [module for module in modules if module != room_module]

        # Define room masks
        existing_objects_per_wall = {k: [] for k in scales_per_wall.keys()}

        # Apply other global modules
        for module in modules:
            if isinstance(module, ModuleGenerator): # Is always a GLOBAL module
                module_data = module.generate()
                InputDataGenerator._update_input_data(input_data, module_data)

        # Filter out global modules that have already been generated
        modules = [
            module
            for module in modules
            if isinstance(module, list)
        ]

        # For each module list, apply at least one module, and at most the total number of modules in the group.
        # The applied modules are chosen randomly based on their weight, and priority is used to determine the order.
        for module_list in modules:
            n_modules = len(module_list)
            n_applied_modules = random.randint(1, n_modules)
            p = [module.weight for module in module_list]
            p = [v / sum(p) for v in p]
            applied_modules = np.random.choice(
                module_list,
                size=n_applied_modules,
                replace=False,
                p=p,
            )
            sorted_applied_modules = sorted(
                applied_modules, key=lambda module: module.priority
            )
            for module in sorted_applied_modules:
                existing_objects = existing_objects_per_wall.get(module.type) # Should always be defined
                wall_scale = scales_per_wall.get(module.type) # Should always be defined
                module_data, existing_objects = module.generate(
                    wall_scale=wall_scale, existing_objects=existing_objects
                )

                # Update existing objects and input data
                existing_objects_per_wall[module.type] = existing_objects
                InputDataGenerator._update_input_data(input_data, module_data)

        return input_data
