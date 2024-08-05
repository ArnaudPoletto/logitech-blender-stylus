# This file contains the random sun module generator class.

import bpy
import math
import random
from typing import Tuple, Dict, Any

from utils.seed import set_seed
from config.config import MAX_PRIORITY
from input_data_generation.module_generator import ModuleGenerator
from input_data_generation.module_generator_type import ModuleGeneratorType


class RandomSunModuleGenerator(ModuleGenerator):
    """
    A random sun module generator, linked to an input data generator to generate sun data.
    """

    def __init__(
        self,
        name: str,
        id: str,
        energy_range: Tuple[float, float],
        weight: float = 1.0,
    ) -> None:
        """
        Initialize the random sun module generator.

        Args:
            name (str): The name of the sun.
            energy_range (Tuple[float, float]): The range of energy values for the sun.
            weight (float): The weight of the module, used to determine the probability of the module being selected. Defaults to 1.0.

        Raises:
            ValueError: If the minimum energy is less than 0 or the maximum energy is less than the minimum energy.
            ValueError: If the maximum energy is less than the minimum energy.
        """
        if energy_range[0] < 0:
            raise ValueError("❌ The minimum energy must be greater than or equal to 0.")
        if energy_range[1] < energy_range[0]:
            raise ValueError(
                "❌ The maximum energy must be greater than or equal to the minimum energy."
            )

        super(RandomSunModuleGenerator, self).__init__(
            type=ModuleGeneratorType.GLOBAL,
            name=name,
            id=id,
            weight=weight,
            priority=MAX_PRIORITY,
        )

        self.energy_range = energy_range

    def generate(
        self,
        wall_scales_per_wall: Dict[str, Any] | None = None,
        existing_objects_per_wall: Dict[str, Any] | None = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any] | None]:
        set_seed()

        # Get random sun parameters
        rotation_y = random.uniform(-math.pi / 2, math.pi / 2)
        rotation_z = random.uniform(0, 2 * math.pi)
        energy = random.uniform(*self.energy_range)

        # Define sun data
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

        # Also set the background emission to that value
        bpy.context.scene.world.node_tree.nodes["Emission"].inputs["Strength"].default_value = energy

        return sun_data, existing_objects_per_wall
