from typing import List, Tuple

from input_data_generation.module_operator import ModuleOperator
from input_data_generation.module_generator import ModuleGenerator

class AllOf(ModuleOperator):
    def __init__(
        self,
        modules: List[ModuleGenerator|ModuleOperator],
        weight: float,
        priority: int,
        ) -> None:
        """
        Initialize the all of operator.
        
        Args:
            modules (List[ModuleGenerator|OneOf|AllOf]): The modules to select from.
            weight (float): The weight of the operator, used to determine the probability of the operator being selected.
            priority (int): The priority of the operator, used to determine the order of the operator being selected.
        """
        super().__init__(modules=modules, weight=weight, priority=priority)
        
    @staticmethod
    def _update_input_data(input_data: dict, update_data: dict) -> dict:
        if "gestures" in update_data:
            if update_data["gestures"].keys() & input_data["gestures"].keys():
                raise ValueError(
                    "Gesture names must be unique: cannot add the same gesture twice."
                )
            input_data["gestures"].update(update_data["gestures"])

        if "blender_objects" in update_data:
            if (
                update_data["blender_objects"].keys()
                & input_data["blender_objects"].keys()
            ):
                print(
                    update_data["blender_objects"].keys(),
                    input_data["blender_objects"].keys(),
                )
                raise ValueError(
                    "Blender object names must be unique: cannot add the same object twice."
                )
            input_data["blender_objects"].update(update_data["blender_objects"])
            
    def generate(
        self,
        wall_scales_per_wall: dict = None,
        existing_objects_per_wall: dict = None,
        ) -> Tuple[dict, dict]:
        """
        Generate the modules in order of priority.
        
        Args: 
            wall_scales_per_wall (dict): The scale of each wall.
            existing_objects_per_wall (dict): The existing objects for each wall.
        
        Returns:
            dict: The generated data.
            dict: The updated data of existing objects.
        """
        sorted_modules = sorted(self.modules, key=lambda x: x.priority)
        all_of_data = {
            "gestures": {},
            "blender_objects": {},
        }
        for module in sorted_modules:
            module_data, existing_objects_per_wall = module.generate(wall_scales_per_wall, existing_objects_per_wall)
            AllOf._update_input_data(all_of_data, module_data)
        
        return all_of_data, existing_objects_per_wall