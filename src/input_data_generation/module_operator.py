from typing import List, Tuple, Union
from abc import abstractmethod

from input_data_generation.module_generator import ModuleGenerator
from input_data_generation.random_room_module_generator import RandomRoomModuleGenerator

class ModuleOperator:
    """
    A module operator, generating data based on the given modules.
    """
    def __init__(
        self,
        modules: List[Union[ModuleGenerator, 'ModuleOperator']],
        weight: float,
        priority: int,
    ):
        """
        Initialize the module operator.
        
        Args:
            modules (List[ModuleGenerator|ModuleOperator]): The modules to use.
            weight (float): The weight of the operator, used to determine the probability of the operator being selected.
            priority (int): The priority of the operator, used to determine the order of the operator being selected.
            
        Raises:
            ValueError: If the weight is less than 0.
            ValueError: If the modules list is empty.
            ValueError: If the modules list contains a RandomRoomModuleGenerator.
        """
        if weight < 0:
            raise ValueError("The weight must be greater than or equal to 0.")
        if len(modules) == 0:
            raise ValueError("The modules list must contain at least one module.")
        if any(isinstance(module, RandomRoomModuleGenerator) for module in modules):
            raise ValueError("The modules list must not contain any RandomRoomModuleGenerator modules.")
        self.modules = modules
        self.weight = weight
        self.priority = priority
    
    @abstractmethod
    def generate(
        self,
    ) -> Tuple[dict, dict]:
        raise NotImplementedError("The generate method must be implemented.")