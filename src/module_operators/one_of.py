import numpy as np
from typing import List, Tuple, Dict, Any

from config.config import MIN_PRIORITY
from module_operators.module_operator import ModuleOperator
from input_data_generation.module_generator import ModuleGenerator

class OneOf(ModuleOperator):
    """
    A one of operator for module generators, generating one of the given modules, given their weights.
    """
    def __init__(
        self,
        modules: List[ModuleGenerator|ModuleOperator],
        weight: float = 1.0,
        priority: int = MIN_PRIORITY,
        ) -> None:
        """
        Initialize the one of operator.
        
        Args:
            modules (List[ModuleGenerator|ModuleOperator]): The modules to select from.
            weight (float, optional): The weight of the operator, used to determine the probability of the operator being selected. Defaults to 1.0. 
            priority (int, optional): The priority of the operator, used to determine the order of the operator being selected. Defaults to the minimum priority.
        """
        super().__init__(modules=modules, weight=weight, priority=priority)
        
    def generate(
        self,
        wall_scales_per_wall: Dict[str, Any] | None = None,
        existing_objects_per_wall: Dict[str, Any] | None = None,
        ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Generate one of the modules based on their weights.
        
        Args:
            wall_scales_per_wall (dict): The scale of each wall.
            existing_objects_per_wall (dict): The existing objects for each wall.
        
        Returns:
            Dict[str, Any]: The generated data.
            Dict[str, Any]: The updated data of existing objects.
        """
        probabilities = [module.weight for module in self.modules]
        probabilities = [probability / sum(probabilities) for probability in probabilities]
        chosen_module = np.random.choice(self.modules, p=probabilities)
        one_of_data, existing_objects_per_wall = chosen_module.generate(wall_scales_per_wall, existing_objects_per_wall)
        
        return one_of_data, existing_objects_per_wall