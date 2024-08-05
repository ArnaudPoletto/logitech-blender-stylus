# This file contains an all of operator for module generators, generating all of the given modules. This is used to combine and generate modules for more complex scenarios.

from typing import List, Tuple, Dict, Any

from module_operators.module_operator import ModuleOperator
from input_data_generation.module_generator import ModuleGenerator
from config.config import MIN_PRIORITY


class AllOf(ModuleOperator):
    """
    An all of operator for module generators, generating all of the given modules.
    """

    def __init__(
        self,
        modules: List[ModuleGenerator | ModuleOperator],
        weight: float = 1.0,
        priority: int = MIN_PRIORITY,
    ) -> None:
        """
        Initialize the all of operator.

        Args:
            modules (List[ModuleGenerator|ModuleOperator]): The modules to select from.
            weight (float, optonal): The weight of the operator, used to determine the probability of the operator being selected. Defaults to 1.0.
            priority (int, optional): The priority of the operator, used to determine the order of the operator being selected. Defaults to the minimum priority.
        """
        super().__init__(modules=modules, weight=weight, priority=priority)

    @staticmethod
    def __update_input_data(input_data: Dict[str, Any], update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the input data with the update data.
        
        Args:
            input_data (Dict[str, Any]): The input data.
            update_data (Dict[str, Any]): The update data.
            
        Returns:
            Dict[str, Any]: The updated input data.
        """
        if "gestures" in update_data:
            if update_data["gestures"].keys() & input_data["gestures"].keys():
                raise ValueError(
                    "❌ Gesture names must be unique: cannot add the same gesture twice."
                )
            input_data["gestures"].update(update_data["gestures"])

        if "blender_objects" in update_data:
            if (
                update_data["blender_objects"].keys()
                & input_data["blender_objects"].keys()
            ):
                raise ValueError(
                    "❌ Blender object names must be unique: cannot add the same object twice."
                )
            input_data["blender_objects"].update(update_data["blender_objects"])

    def generate(
        self,
        wall_scales_per_wall: Dict[str, Any] | None = None,
        existing_objects_per_wall: Dict[str, Any] | None = None,
    ) -> Tuple[Dict[str, Any] | None, Dict[str, Any] | None]:
        """
        Generate the modules in order of priority.

        Args:
            wall_scales_per_wall (Dict[str, Any] | None, optional): The scale of each wall. Defaults to None.
            existing_objects_per_wall (Dict[str, Any] | None, optional): The existing objects for each wall. Defaults to None.

        Returns:
            Dict[str, Any] | None: The generated data.
            Dict[str, Any] | None: The updated data of existing objects.
        """
        sorted_modules = sorted(self.modules, key=lambda x: x.priority)
        all_of_data = {
            "gestures": {},
            "blender_objects": {},
        }
        for module in sorted_modules:
            module_data, existing_objects_per_wall = module.generate(
                wall_scales_per_wall, existing_objects_per_wall
            )
            AllOf.__update_input_data(all_of_data, module_data)

        return all_of_data, existing_objects_per_wall
