import bpy
import math

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
        wave_frequency: float = 4.0,
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
            phase_shift (float): The phase shift of the wave. Defaults to 0.0.
            wave_frequency (float): The frequency of the wave. Defaults to 4.0.
            wave_amplitude (float): The amplitude of the wave. Defaults to 0.1.

        Raises:
            ValueError: If the axis is not an instance of Axis.
            ValueError: If the wave frequency is less than or equal to 0.
            ValueError: If the wave amplitude is less than 0.
        """
        super(RotationSineGesture, self).__init__(
            start_frame, end_frame, scene, arm, forearm, hand
        )

        if not isinstance(axis, Axis):
            raise ValueError("The axis must be an instance of Axis.")

        if wave_frequency <= 0:
            raise ValueError("The wave frequency must be greater than 0.")

        if wave_amplitude < 0:
            raise ValueError("The wave amplitude must be greater than or equal to 0.")

        self.bone = bone
        self.frame_rate = frame_rate
        self.axis = axis
        self.phase_shift = phase_shift
        self.wave_frequency = wave_frequency
        self.wave_amplitude = wave_amplitude

    def _get_bone_rotation_at_frame(self, frame: int) -> float:
        """
        Get the rotation of the bone at a given frame.

        Args:
            frame (int): The frame.

        Returns:
            float: The rotation of the bone.
        """
        wave_offset = (frame - 1) / self.frame_rate * 2 * math.pi * self.wave_frequency
        return math.sin(wave_offset + self.phase_shift) * self.wave_amplitude

    def apply(self, displacement_data: dict, current_frame: int) -> dict:
        # Calculate location offset
        rotation = self._get_bone_rotation_at_frame(
            current_frame
        ) - self._get_bone_rotation_at_frame(current_frame - 1)

        axis_index = Axis.index(self.axis)
        displacement_data[self.bone]["rotation_euler"][axis_index] += rotation

        return displacement_data
