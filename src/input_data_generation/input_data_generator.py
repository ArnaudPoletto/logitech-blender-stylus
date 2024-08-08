# This file contains the input data generator class, which generates input data from the modules.

from typing import List, Dict, Any
from utils.seed import set_seed

from module_operators.module_operator import ModuleOperator
from input_data_generation.module_generator import ModuleGenerator
from input_data_generation.random_room_module_generator import RandomRoomModuleGenerator
from input_data_generation.random_camera_module_generator import (
    RandomCameraModuleGenerator,
)


class InputDataGenerator:
    """
    An input data generator.
    """

    def __init__(
        self,
        room_module: RandomRoomModuleGenerator,
        camera_module: RandomCameraModuleGenerator,
        modules: List[ModuleGenerator | ModuleOperator],
    ) -> None:
        """
        Initialize the input data generator.

        Args:
            room_module (RandomRoomModuleGenerator): The room module.
            camera_module (RandomCameraModuleGenerator): The camera module.
            modules (List[ModuleGenerator|ModuleOperator]): The modules, as a list of module generators or operators.
        """
        self.room_module = room_module
        self.camera_module = camera_module
        self.modules = modules

    @staticmethod
    def __update_input_data(
        input_data: Dict[str, Any], update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
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

    def generate_input_data(self) -> Dict[str, Any]:
        """
        Generate input data from the modules.

        Returns:
            Dict[str, Any]: The input data.
        """
        set_seed()

        input_data = {
            "gestures": {},
            "blender_objects": {},
        }

        # Generate the room and define room masks
        room_data, wall_scales_per_wall = self.room_module.generate()
        InputDataGenerator.__update_input_data(input_data, room_data)
        existing_objects_per_wall = {k: [] for k in wall_scales_per_wall.keys()}

        # Generate the camera
        camera_data, _ = self.camera_module.generate()
        InputDataGenerator.__update_input_data(input_data, camera_data)

        # Generate data from other modules
        for module in self.modules:
            module_data, existing_objects_per_wall = module.generate(
                wall_scales_per_wall, existing_objects_per_wall
            )
            InputDataGenerator.__update_input_data(input_data, module_data)

        return input_data
