# This utility file contains the Axis enum class, which represents the axis of a 3D space.

from enum import Enum


class Axis(Enum):
    """
    Represents the axis of a 3D space.
    """

    X_AXIS = "X"
    Y_AXIS = "Y"
    Z_AXIS = "Z"

    def index(self) -> int:
        """
        Returns the index of the axis.

        Returns:
            int: The index of the axis.
        """
        return {
            Axis.X_AXIS: 0,
            Axis.Y_AXIS: 1,
            Axis.Z_AXIS: 2,
        }[self]
        
    @staticmethod
    def is_valid_axis_string(axis_str):
        """
        Check if the axis string is a valid axis.
        
        Args:
            axis_str (str): The axis string to check.
            
        Returns:
            bool: True if the axis string is a valid axis, False otherwise.
        """
        return any(axis_str == member.value for member in Axis)
