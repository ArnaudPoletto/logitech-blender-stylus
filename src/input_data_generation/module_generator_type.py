# This file contains the module generator type enumeration.

from enum import Enum
from typing import List


class ModuleGeneratorType(Enum):
    """
    A type of module generator.
    """

    GESTURE = "gesture"
    GLOBAL = "global"
    FLOOR = "floor"
    CEILING = "ceiling"
    LEFT_WALL = "left_wall"
    RIGHT_WALL = "right_wall"
    FRONT_WALL = "front_wall"
    BACK_WALL = "back_wall"
    
    def get_vertical_wall_types() -> List["ModuleGeneratorType"]:
        """
        Get the vertical wall types.
        
        Returns:
            List[ModuleGeneratorType]: The vertical wall types.
        """
        return [
            ModuleGeneratorType.LEFT_WALL,
            ModuleGeneratorType.RIGHT_WALL,
            ModuleGeneratorType.FRONT_WALL,
            ModuleGeneratorType.BACK_WALL,
        ]
