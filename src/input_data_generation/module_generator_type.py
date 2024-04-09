from enum import Enum


class ModuleGeneratorType(Enum):
    """
    A type of module generator.
    """

    GLOBAL = "global"
    ROOM_FLOOR = "room_floor"
    ROOM_CEILING = "room_ceiling"
    ROOM_LEFT_WALL = "room_left_wall"
    ROOM_RIGHT_WALL = "room_right_wall"
    ROOM_FRONT_WALL = "room_front_wall"
    ROOM_BACK_WALL = "room_back_wall"
