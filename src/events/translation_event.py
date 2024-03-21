import bpy
from typing import Tuple
from mathutils import Vector

from events.event import Event


class TranslationEvent(Event):
    """
    An event that sets the location of an armature.
    """

    def __init__(
        self,
        start_frame: int,
        scene: bpy.types.Scene,
        arm: bpy.types.Bone,
        forearm: bpy.types.Bone,
        hand: bpy.types.Bone,
        location: Vector,
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
            location (Vector): The location to set the armature.
            relative (bool): Whether the location is relative to the current location. Defaults to True.

        Raises:
            ValueError: If the location is None.
        """
        super(TranslationEvent, self).__init__(start_frame, scene, arm, forearm, hand)
        
        if location is None:
            raise ValueError("The location must not be None.")
        
        self.location = location
        self.relative = relative
        
    def apply(self, displacement_data: dict, current_frame: int) -> None:
        """
        Set the location of the armature.
        """
        if self.relative:
            self.arm.location += self.location
        else:
            self.arm.location = self.location
        
        self.arm.keyframe_insert(data_path="location", index=-1)
        
