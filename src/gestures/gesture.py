import bpy
from abc import abstractmethod


class Gesture:
    """
    A sequence of movements that can be applied to an armature.
    """

    def __init__(
        self,
        start_frame: int,
        end_frame: int,
        scene: bpy.types.Scene,
        arm: bpy.types.Bone,
        forearm: bpy.types.Bone,
        hand: bpy.types.Bone,
    ) -> None:
        """
        Initialize the gesture.

        Args:
            start_frame (int): The start frame.
            end_frame (int): The end frame.
            scene (bpy.types.Scene): The scene.
            arm (bpy.types.Bone): The arm bone.
            forearm (bpy.types.Bone): The forearm bone.
            hand (bpy.types.Bone): The hand bone.

        Raises:
            ValueError: If the start frame or end frame is less than 0.
            ValueError: If the start frame is greater than or equal to the end frame.
            ValueError: If the scene is None.
            ValueError: If the arm, forearm, or hand bones are None.

        """
        if start_frame < 0 or end_frame < 0:
            raise ValueError(
                "The start frame and end frame must be greater than or equal to 0."
            )

        if start_frame >= end_frame:
            raise ValueError("The start frame must be less than the end frame.")

        if scene is None:
            raise ValueError("The scene must not be None.")

        if arm is None or forearm is None or hand is None:
            raise ValueError("The arm, forearm, and hand bones must not be None.")

        self.start_frame = start_frame
        self.end_frame = end_frame
        self.scene = scene
        self.arm = arm
        self.forearm = forearm
        self.hand = hand

    @abstractmethod
    def apply(self, displacement_data: dict, current_frame: int) -> dict:
        """
        Apply the gesture to the armature.

        Args:
            displacement_data (dict): The displacement data to update.
            current_frame (int): The current frame of the gesture.

        Returns:
            dict: The updated displacement data.
        """
        raise NotImplementedError("The apply method must be implemented.")
