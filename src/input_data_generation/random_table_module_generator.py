import numpy as np

from input_data_generation.module_generator import ModuleGenerator

class RandomTableGenerator(ModuleGenerator):
    """
    A random table generator, linked to an input data generator to generate table data.
    """
    def __init__(
        self,
        weight: float,
        priority: int,
    ) -> None:
        """
        Initialize the random table generator.
        
        Args:
            weight (float): The weight of the module, used to determine the probability of the module being selected.
            priority (int): The priority of the module, used to determine the order in which the modules are executed, lower values are executed first.
        """
        super(RandomTableGenerator, self).__init__(weight=weight, priority=priority)
        
    def generate(
        self,
        mask: np.array = None,
    ) -> None:
        """
        Generate the random table.
        """
        # TODO
        pass