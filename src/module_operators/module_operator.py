# This file contains the base abstract class for a module operator, used to combine and generate modules for more complex scenarios.

from typing import List, Tuple, Union, Dict, Any
from abc import abstractmethod

from config.config import MIN_PRIORITY
from input_data_generation.module_generator import ModuleGenerator
from input_data_generation.random_room_module_generator import RandomRoomModuleGenerator

class ModuleOperator:
    """
    A module operator, generating data based on the given modules.
    """
    def __init__(
        self,
        modules: List[Union[ModuleGenerator, 'ModuleOperator']],
        weight: float = 1.0,
        priority: int = MIN_PRIORITY,
    ):
        """
        Initialize the module operator.
        
        Args:
            modules (List[ModuleGenerator|ModuleOperator]): The modules to use.
            weight (float, optional): The weight of the operator, used to determine the probability of the operator being selected. Defaults to 1.0.
            priority (int, optional): The priority of the operator, used to determine the order of the operator being selected. Defaults to the minimum priority.
            
        Raises:
            ValueError: If the weight is less than 0.
            ValueError: If the modules list is empty.
            ValueError: If the modules list contains a RandomRoomModuleGenerator.
        """
        if weight < 0:
            raise ValueError("❌ The weight must be greater than or equal to 0.")
        if len(modules) == 0:
            raise ValueError("❌ The modules list must contain at least one module.")
        if any(isinstance(module, RandomRoomModuleGenerator) for module in modules):
            raise ValueError("❌ The modules list must not contain any RandomRoomModuleGenerator modules.")
        self.modules = modules
        self.weight = weight
        self.priority = priority
    
    @abstractmethod
    def generate(
        self,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        raise NotImplementedError("The generate method must be implemented.")