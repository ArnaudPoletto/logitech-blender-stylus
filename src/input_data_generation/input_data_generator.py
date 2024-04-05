import math
import json
import random
import numpy as np
from typing import Tuple


# TODO: add documentation
class InputDataGenerator:
    """
    An input data generator.
    """

    def __init__(self, seed: int) -> None:
        """
        Initialize the input data generator.

        Args:
            seed (int): The seed.
        """
        self.seed = seed

    def _generate_gestures_data(self) -> dict:
        """
        Generate gestures data.

        Returns:
            dict: The gestures data.
        """
        # TODO: Implement this method
        return {}

    def _get_random_sun(
        self,
        id: str,
        name: str,
        energy_range: Tuple[float, float],
    ) -> dict:
        """
        Get a random sun.

        Args:
            id (str): The id.
            name (str): The name.
            energy_range (Tuple[float, float]): The energy range.

        Returns:
            dict: The random sun data.
        """
        rotation_y = random.uniform(-math.pi / 2, math.pi / 2)
        rotation_z = random.uniform(0, 2 * math.pi)
        energy = random.uniform(*energy_range)
        return {
            id: {
                "type": "Sun",
                "args": {
                    "name": name,
                    "rotation": {"x": 0, "y": rotation_y, "z": rotation_z},
                    "energy": energy,
                },
            }
        }

    def _get_random_room(
        self,
        id: str,
        name: str,
        xy_scale_range: Tuple[float, float],
        z_scale_range: Tuple[float, float],
        resolution_digits: int,
    ) -> Tuple[dict, Tuple[float, float]]:
        """
        Get a random room.

        Args:
            id (str): The id.
            name (str): The name.
            scale_range (Tuple[float, float]): The scale range.
            resolution (float): The number of decimal places, i.e. with resolution=100, 1.234 becomes 1.23.

        Returns:
            dict: The random room data.
            Tuple[float, float]: The floor scale.
        """
        # TODO: add value errors
        scale_x = int(round(random.uniform(*xy_scale_range), resolution_digits))
        scale_y = int(round(random.uniform(*xy_scale_range), resolution_digits))
        scale_z = int(round(random.uniform(*z_scale_range), resolution_digits))

        room_data = {
            id: {
                "type": "Room",
                "args": {
                    "name": name,
                    "location": {"x": 0, "y": 0, "z": scale_z / 2 - 2}, # TODO: remove hardcoding
                    "scale": {"x": scale_x, "y": scale_y, "z": scale_z},
                },
            }
        }
        floor_scale = (scale_y, scale_x)
        front_wall_scale = (scale_x, scale_z)
        back_wall_scale = (scale_x, scale_z)
        left_wall_scale = (scale_y, scale_z)
        right_wall_scale = (scale_y, scale_z)

        scales = {
            "floor": floor_scale,
            "front_wall": front_wall_scale,
            "back_wall": back_wall_scale,
            "left_wall": left_wall_scale,
            "right_wall": right_wall_scale,
        }

        return room_data, scales

    # TODO: Refactorize
    def _get_random_tables(
        self,
        room_id: str,
        floor_scale: Tuple[float, float],  # TODO: could be vector
        n_tables: int,
        xy_scale_range: Tuple[float, float],
        z_scale_range: Tuple[float, float],
        top_thickness_range: Tuple[float, float],
        leg_thickness_range: Tuple[float, float],
        padding: float,  # TODO: add padding
        resolution_digits: float,
    ) -> dict:
        """
        Get random tables on the specified room floor.

        Args:
            room_id (str): The room id in the input data.
            floor_scale (Tuple[float, float]): The floor scale.
            n_tables (int): The maximum number of tables to place. If set to -1, place as many tables as possible.
            xy_scale_range (Tuple[float, float]): The xy scale range of the tables.
            z_scale_range (Tuple[float, float]): The z scale range of the tables.
            top_thickness_range (Tuple[float, float]): The top thickness range of the tables.
            leg_thickness_range (Tuple[float, float]): The leg thickness range of the tables.
            padding (float): The minimum distance between tables and walls, in default units, i,e. not dependent on resolution. Should be set at least to a small value to avoid floating point imprecision when computing intersection between objects.
            resolution (float): The number of decimal places, i.e. with resolution=100, 1.234 becomes 1.23.
        """
        width, length = floor_scale
        resolution = 10**resolution_digits
        padding_resolution = int(padding * resolution)

        tables = []
        tables_data = {}
        n_placed_tables = 0
        while n_tables == -1 or n_placed_tables < n_tables:
            # Get random table dimensions
            w = int(random.uniform(*xy_scale_range) * resolution)
            l = int(random.uniform(*xy_scale_range) * resolution)

            # Get the binary map of possible positions for the table
            position_map = np.ones((width * resolution, length * resolution))
            # Add wall bounds
            position_map[: w + padding_resolution, :] = 0
            position_map[-w - padding_resolution :, :] = 0
            position_map[:, : l + padding_resolution] = 0
            position_map[:, -l - padding_resolution :] = 0
            # Add tables bounds
            for table in tables:
                tx, ty, tw, tl = table
                min_x = max(0, tx - tw - w - padding_resolution)
                max_x = min(width * resolution, tx + tw + w + padding_resolution)
                min_y = max(0, ty - tl - l - padding_resolution)
                max_y = min(length * resolution, ty + tl + l + padding_resolution)
                position_map[min_x:max_x, min_y:max_y] = 0

            # Get random position for the table
            xs, ys = np.where(position_map == 1)
            if len(xs) == 0:
                break
            idx = random.randint(0, len(xs) - 1)
            x = xs[idx]
            y = ys[idx]

            # Add the table to the room and set the data
            table = (x, y, w, l)
            tables.append(table)
            tables_data[f"table_{n_placed_tables}"] = {
                "type": "Table",
                "args": {
                    "name": f"Table{n_placed_tables}",
                    "relative_location": {
                        "x": x / resolution - width / 2,
                        "y": y / resolution - length / 2,
                    },
                    "scale": {
                        "x": 2 * w / resolution,
                        "y": 2 * l / resolution,
                        "z": random.uniform(*z_scale_range),
                    },
                    "top_thickness": random.uniform(*top_thickness_range),
                    "leg_thickness": random.uniform(*leg_thickness_range),
                },
                "parents": [f"{room_id}.floor"],
            }

            n_placed_tables += 1

        return tables_data
    
    def get_random_windows(
        self,
        room_id: str,
        wall_name: str,
        wall_scale: Tuple[float, float],
        n_windows: int,
        xy_scale_range: Tuple[float, float],
        padding: float,
        resolution_digits: int,
    ) -> dict:
        # TODO: documentation
        """
        Get random windows on the specified room wall.
        """
        width, length = wall_scale
        resolution = 10**resolution_digits
        padding_resolution = int(padding * resolution)

        windows = []
        windows_data = {}
        n_placed_windows = 0
        while n_windows == -1 or n_placed_windows < n_windows:
            # Get random window dimensions
            w = int(random.uniform(*xy_scale_range) * resolution)
            l = int(random.uniform(*xy_scale_range) * resolution)

            # Get the binary map of possible positions for the window
            position_map = np.ones((width * resolution, length * resolution))
            # Add wall bounds
            position_map[: w + padding_resolution, :] = 0
            position_map[-w - padding_resolution :, :] = 0
            position_map[:, : l + padding_resolution] = 0
            position_map[:, -l - padding_resolution :] = 0
            for window in windows:
                # Add window bounds
                wx, wy, ww, wl = window
                min_x = max(0, wx - ww - w - padding_resolution)
                max_x = min(width * resolution, wx + ww + w + padding_resolution)
                min_y = max(0, wy - wl - l - padding_resolution)
                max_y = min(length * resolution, wy + wl + l + padding_resolution)
                position_map[min_x:max_x, min_y:max_y] = 0

            # Get random position for the window
            xs, ys = np.where(position_map == 1)
            if len(xs) == 0:
                break
            idx = random.randint(0, len(xs) - 1)
            x = xs[idx]
            y = ys[idx]

            # Add the window to the room and set the data
            window = (x, y, w, l)
            windows.append(window)
            window_name = f"{wall_name}_window_{n_placed_windows}"
            windows_data[window_name] = {
                "type": "Window",
                "args": {
                    "name": f"Window{n_placed_windows}",
                    "relative_location": {
                        "x": x / resolution - width / 2,
                        "y": y / resolution - length / 2,
                    },
                    "scale": {
                        "x": 2 * w / resolution,
                        "y": 2 * l / resolution,
                    },
                },
                "parents": [f"{room_id}.{wall_name}"],
            }

            # Add random window decorator
            random_decorator = random.choice(["blinds", "muntins"])
            if random_decorator == "blinds":
                windows_data[f"{window_name}_blinds"] = {
                    "type": "Blinds",
                    "args": {
                        "name": f"Window{n_placed_windows}Blinds",
                        "n_blinds": random.randint(5, 20),
                        "angle": random.uniform(0, math.pi),
                        "vertical": random.choice([True, False]),
                    },
                    "parents": [window_name],
                }
            elif random_decorator == "muntins":
                windows_data[f"{window_name}_muntins"] = {
                    "type": "Muntins",
                    "args": {
                        "name": f"Window{n_placed_windows}Muntins",
                        "size": random.uniform(0.1, 0.2),
                        "n_muntins_width": random.randint(1, 5),
                        "n_muntins_height": random.randint(1, 5),
                    },
                    "parents": [window_name],
                }
            add_shades = random.choice([True, False])
            if add_shades:
                windows_data[f"{window_name}_shades"] = {
                    "type": "Shades",
                    "args": {
                        "name": f"Window{n_placed_windows}Shades",
                        "shade_ratio": random.uniform(0.1, 0.9),
                        "transmission": random.uniform(0.1, 0.9),
                    },
                    "parents": [window_name],
                }

            n_placed_windows += 1

        return windows_data

    def _generate_blender_objects_data(self, resolution_digits: int = 1, padding: float = 0.1) -> dict:
        # TODO: Implement this method and add documentation

        data = {}
        data.update(self._get_random_sun(id="sun", name="Sun", energy_range=(0.5, 1.5)))
        room_id = "room"
        room_data, scales = self._get_random_room(
            id=room_id,
            name="Room",
            xy_scale_range=(30, 100),
            z_scale_range=(20, 40),
            resolution_digits=resolution_digits,
        )
        floor_scale = scales["floor"]
        data.update(room_data)
        data.update(
            self._get_random_tables(
                room_id=room_id,
                floor_scale=floor_scale,
                n_tables=-1,
                xy_scale_range=(2, 5),
                z_scale_range=(1, 3),
                top_thickness_range=(0.1, 0.2),
                leg_thickness_range=(0.1, 0.2),
                padding=padding,
                resolution_digits=resolution_digits,
            )
        )
        for wall_name in ["front_wall", "back_wall", "left_wall", "right_wall"]:
            data.update(
                self.get_random_windows(
                    room_id=room_id,
                    wall_name=wall_name,
                    wall_scale=scales[wall_name],
                    n_windows=-1,
                    xy_scale_range=(1, 4),
                    padding=padding,
                    resolution_digits=resolution_digits,
                )
            )

        return data

    def generate_input_data(self) -> dict:
        """
        Generate input data.

        Returns:
            dict: The input data.
        """
        random.seed(self.seed)

        gestures_data = self._generate_gestures_data()
        blender_objects_data = self._generate_blender_objects_data()

        input_data = {
            "gestures": gestures_data,
            "blender_objects": blender_objects_data,
        }

        return input_data

    def generate_input_file(self, input_file_path: str) -> None:
        """
        Generate input data and write it to the specified file.

        Args:
            input_file_path (str): The input file path.
            seed (int): The seed.

        Returns:
            dict: The input data.
        """
        with open(input_file_path, "w") as input_file:
            input_data = self.generate_input_data()
            input_file.write(json.dumps(input_data, indent=4))
