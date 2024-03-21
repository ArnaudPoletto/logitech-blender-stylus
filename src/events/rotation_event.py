import bpy
from typing import Tuple
from mathutils import Vector

from events.event import Event


class RotationEvent(Event):
    """
    An event that sets the rotation of a bone.
    """

    def __init__(
        self,
        start_frame: int,
        scene: bpy.types.Scene,
        arm: bpy.types.Bone,
        forearm: bpy.types.Bone,
        hand: bpy.types.Bone,
        bone: bpy.types.Bone,
        rotation: Vector,
        relative: bool= True
    ) -> None:
        """
        Initialize the event.

        Args:
            frame (int): The frame to apply the event.
            scene (bpy.types.Scene): The scene.
            arm (bpy.types.Bone): The arm bone.
            forearm (bpy.types.Bone): The forearm bone.
            hand (bpy.types.Bone): The hand bone.
            bone (bpy.types.Bone): The bone to rotate.
            location (Vector): The location to set the armature.
            relative (bool): Whether the rotation is relative to the current rotation. Defaults to True.
        """
        super(RotationEvent, self).__init__(start_frame, scene, arm, forearm, hand)
        
        self.bone = bone
        self.rotation = rotation
        self.relative = relative
        
    def apply(self, displacement_data: dict, current_frame: int) -> None:
        self.bone.rotation_mode = "XYZ"
        if self.relative:
            self.bone.rotation_euler.x += self.rotation.x
            self.bone.rotation_euler.y += self.rotation.y
            self.bone.rotation_euler.z += self.rotation.z
        else:
            self.bone.rotation_euler.x = self.rotation.x
            self.bone.rotation_euler.y = self.rotation.y
            self.bone.rotation_euler.z = self.rotation.z
            
        self.bone.keyframe_insert(data_path="rotation_euler", index=-1)
        
