from enum import Enum


class Bone(Enum):
    """
    Represents the bones of an armature.
    """

    Arm = "Arm"
    Forearm = "Forearm"
    Hand = "Hand"
    
    def index(self) -> int:
        """
        Returns the index of the bone.

        Returns:
            int: The index of the bone.
        """
        return {
            Bone.Arm: 0,
            Bone.Forearm: 1,
            Bone.Hand: 2,
        }[self]
