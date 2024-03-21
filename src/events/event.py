import bpy

from gestures.gesture import Gesture


class Event(Gesture):
    """
    A single movements that can be applied to an armature.
    """

    def __init__(
        self,
        start_frame: int,
        scene: bpy.types.Scene,
        arm: bpy.types.Bone,
        forearm: bpy.types.Bone,
        hand: bpy.types.Bone,
    ) -> None:
        """
        Initialize the gesture.

        Args:
            frame (int): The frame to apply the event.
            scene (bpy.types.Scene): The scene.
            arm (bpy.types.Bone): The arm bone.
            forearm (bpy.types.Bone): The forearm bone.
            hand (bpy.types.Bone): The hand bone.
            
        Raises:
            ValueError: If the frame is less than 0.
            ValueError: If the scene is None.
            ValueError: If the arm, forearm, or hand bones are None.
            
        """
        super(Event, self).__init__(
            start_frame, start_frame + 1, scene, arm, forearm, hand
        )
        
        self.scene = scene
        self.arm = arm
        self.forearm = forearm
        self.hand = hand

    def apply(self, current_frame) -> None:
        """
        Apply the event to the armature.
        """
        raise NotImplementedError("The apply method must be implemented.")
