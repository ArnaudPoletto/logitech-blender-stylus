from abc import abstractmethod

from input_data_generation.module_generator_type import ModuleGeneratorType


class ModuleGenerator:
    """
    A module generator, linked to an input data generator to generate data.
    """

    def __init__(
        self,
        weight: float,
        priority: int,
        type: ModuleGeneratorType,
        name: str,
        id: str,
    ) -> None:
        """
        Initialize the module generator.

        Args:
            weight (float): The weight of the module, used to determine the probability of the module being selected.
            priority (int): The priority of the module, used to determine the order of the module being selected.
            type (ModuleGeneratorType): The type of the module generator.
            name (str): The name of the module.
            id (str): The id of the module.
        """
        self.weight = weight
        self.priority = priority
        self.type = type
        self.name = name
        self.id = id

    @abstractmethod
    def generate(
        self,
    ) -> dict:
        """
        Generate the module.

        Args:
            mask (np.array): The mask of the module. Defaults to None.

        Returns:
            dict: The module data.
        """
        raise NotImplementedError("The generate method must be implemented.")
