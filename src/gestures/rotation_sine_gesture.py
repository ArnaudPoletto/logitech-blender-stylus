# This file contains the rotation sine gesture class.

import bpy
import math
from typing import Dict, Any

from utils.axis import Axis
from gestures.gesture import Gesture


class RotationSineGesture(Gesture):
    """
    A gesture that applies a sinusoidal rotation to a bone of the armature.
    """

    def __init__(
        self,
        start_frame: int,
        end_frame: int,
        scene: bpy.types.Scene,
        arm: bpy.types.Bone,
        forearm: bpy.types.Bone,
        hand: bpy.types.Bone,
        bone: bpy.types.Bone,
        frame_rate: int,
        axis: Axis,
        phase_shift: float = 0.0,
        wave_period: float = 4.0,
        wave_amplitude: float = 0.1,
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
            bone (bpy.types.Bone): The bone to rotate.
            frame_rate (int): The frame rate.
            axis (str): The axis to rotate.
            phase_shift (float, optional): The phase shift of the wave. Defaults to 0.0.
            wave_period (float, optional): The period of the wave. Defaults to 4.0.
            wave_amplitude (float, optional): The amplitude of the wave. Defaults to 0.1.

        Raises:
            ValueError: If the axis is not an instance of Axis.
            ValueError: If the wave period is less than or equal to 0.
            ValueError: If the wave amplitude is less than 0.
        """
        if wave_period <= 0:
            raise ValueError("❌ The wave period must be greater than 0.")
        if wave_amplitude < 0:
            raise ValueError(
                "❌ The wave amplitude must be greater than or equal to 0."
            )

        super(RotationSineGesture, self).__init__(
            start_frame=start_frame,
            end_frame=end_frame,
            scene=scene,
            arm=arm,
            forearm=forearm,
            hand=hand,
        )

        self.bone = bone
        self.frame_rate = frame_rate
        self.axis = axis
        self.phase_shift = phase_shift
        self.wave_period = wave_period
        self.wave_amplitude = wave_amplitude

    def __get_bone_rotation_at_frame(self, frame: int) -> float:
        """
        Get the rotation of the bone at a given frame.

        Args:
            frame (int): The frame.

        Returns:
            float: The rotation of the bone.
        """
        wave_offset = (frame - 1) / self.frame_rate * 2 * math.pi * self.wave_period
        return math.sin(wave_offset + self.phase_shift) * self.wave_amplitude

    def apply(
        self,
        displacement_data: Dict[bpy.types.Bone, Dict[str, Any]],
        current_frame: int,
    ) -> Dict[bpy.types.Bone, Dict[str, Any]]:
        """
        Apply the rotation sine gesture to the armature.

        Args:
            displacement_data (Dict[bpy.types.Bone, Dict[str, Any]]): The displacement data.
            current_frame (int): The current frame.

        Returns:
            Dict[bpy.types.Bone, Dict[str, Any]]: The updated displacement data.
        """
        # Calculate location offset
        rotation = self.__get_bone_rotation_at_frame(
            current_frame
        ) - self.__get_bone_rotation_at_frame(current_frame - 1)

        axis_index = Axis.index(self.axis)
        displacement_data[self.bone]["rotation_euler"][axis_index] += rotation

        return displacement_data
