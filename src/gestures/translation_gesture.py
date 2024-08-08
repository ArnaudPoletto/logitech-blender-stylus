# This file contains the translation gesture class.

import bpy
from typing import Dict, Any
from mathutils import Vector

from gestures.gesture import Gesture


class TranslationGesture(Gesture):
    """
    A gesture that applies a linear translation to the armature.
    """

    def __init__(
        self,
        start_frame: int,
        end_frame: int,
        scene: bpy.types.Scene,
        arm: bpy.types.Bone,
        forearm: bpy.types.Bone,
        hand: bpy.types.Bone,
        vector: Vector,
        relative: bool = True,
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
            vector (Vector): The translation vector to apply.
            relative (bool): Whether the translation is relative to the current location. Defaults to True.
        """
        super(TranslationGesture, self).__init__(
            start_frame=start_frame,
            end_frame=end_frame,
            scene=scene,
            arm=arm,
            forearm=forearm,
            hand=hand,
        )

        self.vector = vector
        self.relative = relative
        self.duration = self.end_frame - self.start_frame

        # The object is always instantiated at the start frame, so we can store the initial location
        self.initial_location = arm.location.copy()

    def apply(
        self,
        displacement_data: Dict[bpy.types.Bone, Dict[str, Any]],
        current_frame: int,
    ) -> Dict[bpy.types.Bone, Dict[str, Any]]:
        """
        Apply the translation to the armature.
        
        Args:
            displacement_data (Dict[bpy.types.Bone, Dict[str, Any]]): The displacement data.
            current_frame (int): The current frame.
        
        Returns:
            Dict[bpy.types.Bone, Dict[str, Any]]: The updated displacement data.
        """
        translation = self.vector.copy()
        if not self.relative:
            translation -= self.initial_location
        translation /= self.duration

        displacement_data[self.arm]["location"] += translation

        return displacement_data
