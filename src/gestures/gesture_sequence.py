import bpy
import random
import math
from typing import List, Tuple
from mathutils import Vector, Euler

from gestures.gesture import Gesture
from events.event import Event


class GestureSequence:
    """
    A sequence of gestures that can be applied to an armature.
    """

    def __init__(
        self,
        gestures_events: List[Tuple[type, List[dict]]],
        scene: bpy.types.Scene,
        arm: bpy.types.Bone,
        forearm: bpy.types.Bone,
        hand: bpy.types.Bone,
    ) -> None:
        """
        Initialize the gesture sequence.

        Args:
            gestures_events (Tuple[type, List[dict]]): The gesturesor events to apply, as a tuple of the gesture and its arguments.
            scene (bpy.types.Scene): The scene.
            arm (bpy.types.Bone): The arm bone.
            forearm (bpy.types.Bone): The forearm bone.
            hand (bpy.types.Bone): The hand bone.
        """
        self.gestures_events = gestures_events
        self.remaining_gestures_events: List[Tuple[type, dict]] = (
            gestures_events  # Remaining gestures/events over time
        )
        self.current_gestures_events: List[Tuple[Gesture | Event, dict]] = (
            []
        )  # Current gestures/events over time
        self.scene = scene
        self.arm = arm
        self.forearm = forearm
        self.hand = hand

    def _get_end_frame(self) -> int:
        """
        Get the end frame of the gesture sequence.

        Returns:
            int: The end frame.
        """
        end_frame = 0
        for _, args in self.gestures_events:
            current_end_frame = (
                args["end_frame"] if "end_frame" in args else args["start_frame"] + 1
            )
            end_frame = max(end_frame, current_end_frame)

        return end_frame
    
    def _insert_keyframe(self, bone: bpy.types.Bone, displacement_data: dict) -> None:
        # Location
        if displacement_data[bone]["location"] != Vector((0, 0, 0)):
            bone.location += displacement_data[bone]["location"]
            bone.keyframe_insert(data_path="location", index=-1)

        # Rotation
        if displacement_data[bone]["rotation_euler"] != Euler((0, 0, 0)):
            bone.rotation_mode = 'XYZ'
            bone.rotation_euler.x += displacement_data[bone]["rotation_euler"].x
            bone.rotation_euler.y += displacement_data[bone]["rotation_euler"].y
            bone.rotation_euler.z += displacement_data[bone]["rotation_euler"].z
            bone.keyframe_insert(data_path="rotation_euler", index=-1)

    def apply(self) -> None:
        """
        Apply the gesture sequence to the armature.
        """
        start_frame = 1
        end_frame = self._get_end_frame()

        # Apply gestures/events over time
        for current_frame in range(start_frame, end_frame):
            bpy.context.scene.frame_set(current_frame)

            # Remove gesture/event objects from current gesture/event objects if end frame is reached
            new_current_gestures_events = []
            for current_gesture_event in self.current_gestures_events:
                if (
                    "end_frame" in current_gesture_event[1]
                    and current_frame == current_gesture_event[1]["end_frame"]
                ) or (
                    "end_frame" not in current_gesture_event[1]
                    and current_frame == current_gesture_event[1]["start_frame"] + 1
                ):
                    continue
                new_current_gestures_events.append(current_gesture_event)
            self.current_gestures_events = new_current_gestures_events

            # Add new gesture/event objects to current gesture/event objects if start frame is reached
            new_remaining_gestures_events = []
            for (
                gesture_event_type,
                gesture_event_args,
            ) in self.remaining_gestures_events:
                if current_frame == gesture_event_args["start_frame"]:
                    gesture_event_object = gesture_event_type(
                        scene=self.scene,
                        arm=self.arm,
                        forearm=self.forearm,
                        hand=self.hand,
                        **gesture_event_args,
                    )
                    self.current_gestures_events.append(
                        (gesture_event_object, gesture_event_args)
                    )
                else:
                    new_remaining_gestures_events.append(
                        (gesture_event_type, gesture_event_args)
                    )
            self.remaining_gestures_events = new_remaining_gestures_events

            # Compute movement difference for current frame
            displacement_data = {
                self.arm: {
                    "location": Vector((0, 0, 0)),
                    "rotation_euler": Euler((0, 0, 0)),
                },
                self.forearm: {
                    "location": Vector((0, 0, 0)),
                    "rotation_euler": Euler((0, 0, 0)),
                },
                self.hand: {
                    "location": Vector((0, 0, 0)),
                    "rotation_euler": Euler((0, 0, 0)),
                },
            }

            for (
                gesture_event_object,
                gesture_event_args,
            ) in self.current_gestures_events:
                displacement_data = gesture_event_object.apply(displacement_data, current_frame)

            # Set the armature location and rotation for the current frame
            self._insert_keyframe(self.arm, displacement_data)
            self._insert_keyframe(self.forearm, displacement_data)
            self._insert_keyframe(self.hand, displacement_data)
            
        # Set general start and end frame
        bpy.context.scene.frame_start = 0
        bpy.context.scene.frame_end = end_frame - 1
