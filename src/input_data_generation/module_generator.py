# This file contains the module generator class, which is an abstract class for all module generators.

from abc import abstractmethod
from typing import Tuple, Dict, Any

from config.config import MIN_PRIORITY, MAX_PRIORITY
from input_data_generation.module_generator_type import ModuleGeneratorType


class ModuleGenerator:
    """
    A module generator, linked to an input data generator to generate data.
    """

    def __init__(
        self,
        type: ModuleGeneratorType,
        name: str,
        id: str,
        weight: float = 1.0,
        priority: int = MIN_PRIORITY,
    ) -> None:
        """
        Initialize the module generator.

        Args:
            type (ModuleGeneratorType): The type of the module generator.
            name (str): The name of the module.
            id (str): The id of the module.
            weight (float, optional): The weight of the module, used to determine the probability of the module being selected. Defaults to 1.0.
            priority (int, optional): The priority of the module, used to determine the order of the module being selected. Defaults to the minimum priority.
            
        Raises:
            ValueError: If the priority is less than the maximum priority.
        """
        if priority < MAX_PRIORITY:
            raise ValueError(f"❌ The priority must be less than or equal to the maximum priority {MAX_PRIORITY}: found {priority}.")
        
        self.type = type
        self.name = name
        self.id = id
        self.weight = weight
        self.priority = priority

    @abstractmethod
    def generate(
        self,
        wall_scales_per_wall: Dict[str, Any] | None = None,
        existing_objects_per_wall: Dict[str, Any] | None = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Generate the module.

        Args:
            wall_scales_per_wall (Dict[str, Any] | None): The scale of each wall.
            existing_objects_per_wall (Dict[str, Any] | None): The existing objects for each wall.

        Returns:
            Dict[str, Any]: The module data.
            Dict[str, Any]: Updated data of existing objects or scales for the room.
        """
        raise NotImplementedError("❌ The generate method must be implemented.")
