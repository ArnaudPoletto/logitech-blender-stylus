import bpy
import math
from mathutils import Euler

from utils.axis import Axis
from gestures.gesture import Gesture


class RotationGesture(Gesture):
    """
    A gesture that applies a linear rotation to the bone of the armature.
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
        euler: Euler,
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
            bone (bpy.types.Bone): The bone to rotate.
            euler (Vector): The euler rotation to apply.
            relative (bool): Whether the translation is relative to the current rotation. Defaults to True.
        """
        super(RotationGesture, self).__init__(
            start_frame=start_frame,
            end_frame=end_frame,
            scene=scene,
            arm=arm,
            forearm=forearm,
            hand=hand,
        )

        self.bone = bone
        self.euler = euler
        self.relative = relative
        self.duration = self.end_frame - self.start_frame

        # The object is always instantiated at the start frame, so we can store the initial rotation
        self.initial_rotation = self.bone.rotation_euler.copy()

    def apply(self, displacement_data: dict, current_frame: int) -> dict:
        euler = self.euler.copy()
        if not self.relative:
            euler.x -= self.initial_rotation.x
            euler.y -= self.initial_rotation.y
            euler.z -= self.initial_rotation.z
        euler.x /= self.duration
        euler.y /= self.duration
        euler.z /= self.duration

        displacement_data[self.bone]["rotation_euler"].x += euler.x
        displacement_data[self.bone]["rotation_euler"].y += euler.y
        displacement_data[self.bone]["rotation_euler"].z += euler.z

        return displacement_data
