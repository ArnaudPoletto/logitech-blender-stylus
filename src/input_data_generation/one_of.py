import numpy as np
from typing import List, Tuple

from input_data_generation.module_operator import ModuleOperator
from input_data_generation.module_generator import ModuleGenerator

class OneOf(ModuleOperator):
    """
    A one of operator for module generators, generating one of the given modules, given their weights.
    """
    def __init__(
        self,
        modules: List[ModuleGenerator|ModuleOperator],
        weight: float,
        priority: int,
        ) -> None:
        """
        Initialize the one of operator.
        
        Args:
            modules (List[ModuleGenerator|OneOf|AllOf]): The modules to select from.
            weight (float): The weight of the operator, used to determine the probability of the operator being selected.
            priority (int): The priority of the operator, used to determine the order of the operator being selected.
        """
        super().__init__(modules=modules, weight=weight, priority=priority)
        
    def generate(
        self,
        wall_scales_per_wall: dict = None,
        existing_objects_per_wall: dict = None,
        ) -> Tuple[dict, dict]:
        """
        Generate one of the modules based on their weights.
        
        Args:
            wall_scales_per_wall (dict): The scale of each wall.
            existing_objects_per_wall (dict): The existing objects for each wall.
        
        Returns:
            dict: The generated data.
            dict: The updated data of existing objects.
        """
        probabilities = [module.weight for module in self.modules]
        probabilities = [probability / sum(probabilities) for probability in probabilities]
        chosen_module = np.random.choice(self.modules, p=probabilities)
        one_of_data, existing_objects_per_wall = chosen_module.generate(wall_scales_per_wall, existing_objects_per_wall)
        
        return one_of_data, existing_objects_per_wall