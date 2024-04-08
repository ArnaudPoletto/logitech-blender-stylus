import math
import random
import numpy as np
from typing import Tuple

from input_data_generation.module_generator import ModuleGenerator
from input_data_generation.module_generator_type import ModuleGeneratorType


class RandomSunModuleGenerator(ModuleGenerator):
    """
    A random sun module generator, linked to an input data generator to generate sun data.
    """
    def __init__(
        self,
        weight: float,
        priority: int,
        name: str,
        id: str,
        energy_range: Tuple[float, float],
    ) -> None:
        """
        Initialize the random sun module generator.

        Args:
            weight (float): The weight of the module, used to determine the probability of the module being selected.
            priority (int): The priority of the module, used to determine the order in which the modules are executed, lower values are executed first.
            name (str): The name of the sun.
            energy_range (Tuple[float, float]): The range of energy values for the sun.

        Raises:
            ValueError: If the minimum energy is less than 0 or the maximum energy is less than the minimum energy.
            ValueError: If the maximum energy is less than the minimum energy.
        """
        if energy_range[0] < 0:
            raise ValueError("The minimum energy must be greater than or equal to 0.")
        if energy_range[1] < energy_range[0]:
            raise ValueError(
                "The maximum energy must be greater than or equal to the minimum energy."
            )

        super(RandomSunModuleGenerator, self).__init__(
            weight=weight,
            priority=priority,
            type=ModuleGeneratorType.GLOBAL,
            name=name,
            id=id,
        )

        self.energy_range = energy_range

    def generate(
        self,
        mask: np.array = None,
    ) -> dict:
        rotation_y = random.uniform(-math.pi / 2, math.pi / 2)
        rotation_z = random.uniform(0, 2 * math.pi)
        energy = random.uniform(*self.energy_range)

        sun_data = {
            "blender_objects": {
                self.id: {
                    "type": "Sun",
                    "args": {
                        "name": self.name,
                        "rotation": {"x": 0, "y": rotation_y, "z": rotation_z},
                        "energy": energy,
                    },
                }
            }
        }

        return sun_data
