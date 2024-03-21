from enum import Enum

class Axis(Enum):
    X_AXIS = 'X'
    Y_AXIS = 'Y'
    Z_AXIS = 'Z'

    def index(self):
        return {
            Axis.X_AXIS: 0,
            Axis.Y_AXIS: 1,
            Axis.Z_AXIS: 2,
        }[self]