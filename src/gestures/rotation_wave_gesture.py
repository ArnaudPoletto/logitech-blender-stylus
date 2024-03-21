import bpy
import math
from mathutils import Vector

from utils.axis import Axis
from gestures.gesture import Gesture


class RotationWaveGesture(Gesture):
    """
    A gesture that applies a waving effect to the armature.
    """

    def __init__(
        self,
        start_frame: int,
        end_frame: int,
        scene: bpy.types.Scene,
        arm: bpy.types.Bone,
        forearm: bpy.types.Bone,
        hand: bpy.types.Bone,
        frame_rate: int,
        axis: Axis,
        wave_frequency: float = 4.0,
        wave_amplitude: float = 0.1,
        arm_phase_shift: float = 0.0,
        forearm_phase_shift: float = math.pi / 4,
        hand_phase_shift = math.pi / 4,
        hand_amplitude_factor: float = 0.5,
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
            frame_rate (int): The frame rate.
            axis (str): The axis to rotate.
            wave_frequency (float): The frequency of the wave. Defaults to 4.0.
            wave_amplitude (float): The amplitude of the wave. Defaults to 0.1.
            arm_phase_shift (float): The phase shift of the arm wave. Defaults to 0.0.
            forearm_phase_shift (float): The phase shift of the forearm wave. Defaults to pi/4.
            hand_phase_shift (float): The phase shift of the hand wave. Defaults to pi/4.
            hand_amplitude_factor (float): The amplitude factor of the hand wave. Defaults to 0.5.
            
        Raises:
            ValueError: If the axis is not an instance of Axis.
            ValueError: If the wave frequency is less than or equal to 0.
        """
        super(RotationWaveGesture, self).__init__(
            start_frame, end_frame, scene, arm, forearm, hand
        )

        if not isinstance(axis, Axis):
            raise ValueError("The axis must be an instance of Axis.")
        
        if wave_frequency <= 0:
            raise ValueError("The wave frequency must be greater than 0.")
        
        self.frame_rate = frame_rate
        self.axis = axis
        self.wave_frequency = wave_frequency
        self.wave_amplitude = wave_amplitude
        self.arm_phase_shift = arm_phase_shift
        self.forearm_phase_shift = forearm_phase_shift
        self.hand_phase_shift = hand_phase_shift
        self.hand_amplitude_factor = hand_amplitude_factor

    def _bone_apply(self, displacement_data:dict, bone: bpy.types.Bone, rotation: float) -> dict:
        """
        Apply a rotation to a bone.

        Args:
            displacement_data (dict): The displacement data.
            bone (bpy.types.Bone): The bone to rotate.
            rotation (float): The rotation to apply to the bone in the specified axis.

        Returns:
            dict: The updated displacement data.
        """
        axis_index = Axis.index(self.axis)
        displacement_data[bone]["rotation_euler"][axis_index] += rotation

        return displacement_data
    
    def _get_arm_rotation_at_frame(self, frame):
        wave_offset = (frame - 1) / self.frame_rate * 2 * math.pi * self.wave_frequency
        phase_shift = self.arm_phase_shift
        wave_amplitude = self.wave_amplitude

        return math.sin(wave_offset + phase_shift) * wave_amplitude
    
    def _get_forearm_rotation_at_frame(self, frame):
        wave_offset = (frame - 1) / self.frame_rate * 2 * math.pi * self.wave_frequency
        phase_shift = self.arm_phase_shift + self.forearm_phase_shift
        wave_amplitude = self.wave_amplitude * self.hand_amplitude_factor

        return math.sin(wave_offset + phase_shift) * wave_amplitude
    
    def _get_hand_rotation_at_frame(self, frame):
        wave_offset = (frame - 1) / self.frame_rate * 2 * math.pi * self.wave_frequency
        phase_shift = self.arm_phase_shift + self.forearm_phase_shift + self.hand_phase_shift
        wave_amplitude = self.wave_amplitude * self.hand_amplitude_factor
        
        return math.sin(wave_offset + phase_shift) * wave_amplitude


    def apply(self, displacement_data: dict, current_frame: int) -> dict:
        # Calculate rotations for bones
        arm_rotation = self._get_arm_rotation_at_frame(current_frame) - self._get_arm_rotation_at_frame(current_frame - 1)
        forearm_rotation = self._get_forearm_rotation_at_frame(current_frame) - self._get_forearm_rotation_at_frame(current_frame - 1)
        hand_rotation = self._get_hand_rotation_at_frame(current_frame) - self._get_hand_rotation_at_frame(current_frame - 1)
        
        # Apply rotations to bones
        displacement_data = self._bone_apply(displacement_data, self.arm, arm_rotation)
        displacement_data = self._bone_apply(displacement_data, self.forearm, forearm_rotation)
        displacement_data = self._bone_apply(displacement_data, self.hand, hand_rotation)

        return displacement_data