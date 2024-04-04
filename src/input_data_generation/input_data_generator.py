import math
import json
import random
from typing import Tuple
import matplotlib.pyplot as plt
import numpy as np


# TODO: add documentation
class InputDataGenerator:
    def __init__(self, seed):
        self.seed = seed

    def _generate_gestures_data(self):
        # TODO: Implement this method and add documentation
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
        scale_range: Tuple[float, float],
        resolution: float,
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
        # TODO: use decimals in more efficient way
        scale_x = int(int(random.uniform(*scale_range) * resolution) / resolution)
        scale_y = int(int(random.uniform(*scale_range) * resolution) / resolution)
        scale_z = int(int(random.uniform(*scale_range) * resolution) / resolution)
        
        room_data = {
            id: {
                "type": "Room",
                "args": {
                    "name": name,
                    "location": {"x": 0, "y": 0, "z": 0},
                    "scale": {"x": scale_x, "y": scale_y, "z": scale_z},
                },
            }
        }
        floor_scale = (scale_y, scale_x)

        return room_data, floor_scale

    # TODO: Refactorize
    def _get_random_tables(
        self,
        room_id: str,
        floor_scale: Tuple[float, float],
        n_tables: int,
        xy_scale_range: Tuple[float, float],
        z_scale_range: Tuple[float, float],
        top_thickness_range: Tuple[float, float],
        leg_thickness_range: Tuple[float, float],
        padding: float, # TODO: add padding
        resolution: float,
    ) -> dict:
        # TODO: documentation
        width, length = floor_scale
        tables = []

        tables_data = {}
        n_placed_tables = 0
        while n_tables == -1 or n_placed_tables < n_tables:
            print("RUN")
            # Get random table dimensions
            w = int(random.uniform(*xy_scale_range) * resolution)
            l = int(random.uniform(*xy_scale_range) * resolution)

            # Get the map of possible positions for the table (0: cannot place, 1: can place)
            position_map = np.ones((width * resolution, length * resolution))
            for table in tables:
                # Add wall bounds
                position_map[:w, :] = 0
                position_map[-w:, :] = 0
                position_map[:, :l] = 0
                position_map[:, -l:] = 0

                # TODO: add padding
                # Add table bounds
                tx, ty, tw, tl = table
                min_x = max(0, tx - tw - w)
                max_x = min(width * resolution, tx + tw + w)
                min_y = max(0, ty - tl - l)
                max_y = min(length * resolution, ty + tl + l)
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

        plt.imshow(position_map)
        plt.show()

        return tables_data

    def _generate_blender_objects_data(self, resolution=100) -> dict:
        # TODO: Implement this method and add documentation

        data = {}
        data.update(self._get_random_sun(id="sun", name="Sun", energy_range=(0.5, 1.5)))
        room_id = "room"
        room_data, floor_scale = self._get_random_room(
            id=room_id, name="Room", scale_range=(30, 100), resolution=resolution
        )
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
                padding=0.0,
                resolution=resolution,
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

        return {"gestures": gestures_data, "blender_objects": blender_objects_data}

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
