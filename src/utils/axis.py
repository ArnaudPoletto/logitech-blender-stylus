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
