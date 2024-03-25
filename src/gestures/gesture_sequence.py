import bpy
import random
import math
import numpy as np
from typing import List, Tuple
from mathutils import Vector, Euler

from gestures.gesture import Gesture


class GestureSequence:
    """
    A sequence of gestures that can be applied to an armature.
    """

    def __init__(
        self,
        gestures: List[Tuple[type, List[dict]]],
        scene: bpy.types.Scene,
        arm: bpy.types.Bone,
        forearm: bpy.types.Bone,
        hand: bpy.types.Bone,
        translation_acceleration_limit: float = 0.005,
        rotation_acceleration_limit: float = 0.005,
        location_range: Tuple[Vector, Vector] = (
            Vector((-5.0, -0.5, -1.5)),
            Vector((1.0, 2.0, 1.5)),
        ),
        arm_rotation_range: Tuple[Euler, Euler] = (
            Euler((-np.inf, -np.inf, -np.inf)),
            Euler((np.inf, np.inf, np.inf)),
        ),
        forearm_rotation_range: Tuple[Euler, Euler] = (
            Euler((-math.pi / 2, -math.pi / 2, -math.pi / 2)),
            Euler((math.pi / 2, math.pi / 2, math.pi / 2)),
        ),
        hand_rotation_range: Tuple[Euler, Euler] = (
            Euler((-math.pi / 2, -math.pi / 2, -math.pi / 2)),
            Euler((math.pi / 2, math.pi / 2, math.pi / 2)),
        ),
        momentum_weight: float = 0.7,
    ) -> None:
        """
        Initialize the gesture sequence.

        Args:
            gestures (Tuple[type, List[dict]]): The gestures to apply, as a tuple of the gesture and its arguments.
            scene (bpy.types.Scene): The scene.
            arm (bpy.types.Bone): The arm bone.
            forearm (bpy.types.Bone): The forearm bone.
            hand (bpy.types.Bone): The hand bone.
            translation_acceleration_limit (float, optional): The translation acceleration limit. Defaults to 0.1.
            rotation_acceleration_limit (float, optional): The rotation acceleration limit. Defaults to 0.1.
            location_range (Tuple[Vector, Vector], optional): The location range. Defaults to (Vector((-5.0, -0.5, -2.5)), Vector((2.5, 2.5, 2.5))).
            arm_rotation_range (Tuple[Euler, Euler], optional): The arm rotation range. Defaults to (Euler((-np.inf, -np.inf, -np.inf)), Euler((np.inf, np.inf, np.inf))).
            forearm_rotation_range (Tuple[Euler, Euler], optional): The forearm rotation range. Defaults to (Euler((-math.pi / 2, -math.pi / 2, -math.pi / 2)), Euler((math.pi / 2, math.pi / 2, math.pi / 2))).
            hand_rotation_range (Tuple[Euler, Euler], optional): The hand rotation range. Defaults to (Euler((-math.pi / 2, -math.pi / 2, -math.pi / 2)), Euler((math.pi / 2, math.pi / 2, math.pi / 2))).
            momentum_weight (float, optional): The ratio of the previous frame's displacement mixed with the current frame's displacement. Defaults to 0.1.

        Raises:
            ValueError: If the translation acceleration limit is not positive.
            ValueError: If the rotation acceleration limit is not positive.
            ValueError: If the momentum weight is not between 0 and 1.
        """
        if translation_acceleration_limit < 0:
            raise ValueError("Translation acceleration limit must be positive.")
        
        if rotation_acceleration_limit < 0:
            raise ValueError("Rotation acceleration limit must be positive.")
        
        if momentum_weight < 0 or momentum_weight > 1:
            raise ValueError("Momentum weight must be between 0 and 1.")

        self.gestures = gestures
        self.remaining_gestures: List[Tuple[type, dict]] = (
            gestures  # Remaining gestures over time, all at the beginning
        )
        self.current_gestures: List[Tuple[Gesture, dict]] = (
            []
        )  # Current gestures over time, empty at the beginning
        self.scene = scene
        self.arm = arm
        self.forearm = forearm
        self.hand = hand
        self.translation_acceleration_limit = translation_acceleration_limit
        self.rotation_acceleration_limit = rotation_acceleration_limit
        self.location_range = location_range
        self.arm_rotation_range = arm_rotation_range
        self.forearm_rotation_range = forearm_rotation_range
        self.hand_rotation_range = hand_rotation_range
        self.momentum_weight = momentum_weight

    def _get_end_frame(self) -> int:
        """
        Get the end frame of the gesture sequence.

        Returns:
            int: The end frame.
        """
        end_frame = 0
        for _, args in self.gestures:
            current_end_frame = (
                args["end_frame"] if "end_frame" in args else args["start_frame"] + 1
            )
            end_frame = max(end_frame, current_end_frame)

        return end_frame

    def _update_current_gestures(self, current_frame: int) -> None:
        """
        Update the current gestures over time by removing the ones that have ended.

        Args:
            current_frame (int): The current frame.
        """
        new_current_gestures = []
        for current_gesture in self.current_gestures:
            if (
                "end_frame" in current_gesture[1]
                and current_frame == current_gesture[1]["end_frame"]
            ) or (
                "end_frame" not in current_gesture[1]
                and current_frame == current_gesture[1]["start_frame"] + 1
            ):
                continue
            new_current_gestures.append(current_gesture)
        self.current_gestures = new_current_gestures

    def _update_remaining_gestures(self, current_frame: int) -> None:
        """
        Update the remaining gestures over time by adding the ones that have started.

        Args:
            current_frame (int): The current frame.
        """
        new_remaining_gestures = []
        for (
            gesture_type,
            gesture_args,
        ) in self.remaining_gestures:
            if current_frame == gesture_args["start_frame"]:
                gesture_object = gesture_type(
                    scene=self.scene,
                    arm=self.arm,
                    forearm=self.forearm,
                    hand=self.hand,
                    **gesture_args,
                )
                self.current_gestures.append((gesture_object, gesture_args))
            else:
                new_remaining_gestures.append((gesture_type, gesture_args))
        self.remaining_gestures = new_remaining_gestures
        
    def _get_default_displacement_data(self) -> dict:
        """
        Get the default displacement data, with no movement.
        
        Returns:
            dict: The default displacement data.
        """
        bones = [self.arm, self.forearm, self.hand]
        displacement_data = {}
        for bone in bones:
            displacement_data[bone] = {
                "location": Vector((0, 0, 0)),
                "rotation_euler": Euler((0, 0, 0)),
            }
            
        return displacement_data
        

    def _get_displacement_data(
        self, current_frame: int, previous_displacement_data: dict
    ) -> dict:
        """
        Get the displacement data for the current frame.

        Args:
            current_frame (int): The current frame.
            previous_displacement_data (dict): The displacement data for the previous frame.

        Returns:
            dict: The displacement data for the current frame.
        """
        displacement_data = self._get_default_displacement_data()

        # Compute movement difference for current frame
        for gesture_object, _ in self.current_gestures:
            displacement_data = gesture_object.apply(displacement_data, current_frame)
            
        # Apply momentum
        bones = [self.arm, self.forearm, self.hand]
        for bone in bones:
            for displacement_type in ["location", "rotation_euler"]:
                for i in range(3):
                    displacement_data[bone][displacement_type][i] = (
                        previous_displacement_data[bone][displacement_type][i]
                        * self.momentum_weight
                    ) + (
                        displacement_data[bone][displacement_type][i]
                        * (1 - self.momentum_weight)
                    )

        # Limit acceleration
        for bone in bones:
            for displacement_type, acceleration_limit in zip(
                ["location", "rotation_euler"],
                [self.translation_acceleration_limit, self.rotation_acceleration_limit],
            ):
                for i in range(3):
                    # Compute difference between consecutive displacements
                    previous_displacement = previous_displacement_data[bone][displacement_type][i]
                    current_displacement = displacement_data[bone][displacement_type][i]
                    displacement_difference = current_displacement - previous_displacement
                    
                    # Clip displacement if acceleration limit is exceeded
                    if np.abs(displacement_difference) > acceleration_limit:
                        current_displacement = previous_displacement + np.sign(displacement_difference) * acceleration_limit
                        
                    displacement_data[bone][displacement_type][i] = current_displacement

        return displacement_data

    def _get_limited_value(
        self, current: float, displacement_value: float, minimum: float, maximum: float
    ) -> float:
        """
        Get the limited value for the displacement, to avoid going beyond the location and rotation limits.

        Args:
            current (float): The current value.
            displacement_value (float): The displacement value.
            minimum (float): The minimum value.
            maximum (float): The maximum value.

        Returns:
            float: The limited value.
        """
        next = current + displacement_value

        def _slow_factor(x, k=10):
            return -2 / (1 + math.exp(-k * abs(x))) + 2

        if next < minimum and next < current:
            return displacement_value * _slow_factor(minimum - next)
        elif next > maximum and next > current:
            return displacement_value * _slow_factor(next - maximum)
        else:
            return displacement_value

    def _insert_location_keyframe(
        self, bone: bpy.types.Bone, displacement_data: dict
    ) -> None:
        """
        Insert a keyframe for the bone location with the displacement data for the current frame if necessary.

        Args:
            bone (bpy.types.Bone): The bone.
            displacement_data (dict): The displacement data for the current frame.
        """
        if displacement_data[bone]["location"] == Vector((0, 0, 0)):
            return

        # Limit displacement location
        displacement_data[bone]["location"].x = self._get_limited_value(
            bone.location.x,
            displacement_data[bone]["location"].x,
            self.location_range[0].x,
            self.location_range[1].x,
        )
        displacement_data[bone]["location"].y = self._get_limited_value(
            bone.location.y,
            displacement_data[bone]["location"].y,
            self.location_range[0].y,
            self.location_range[1].y,
        )
        displacement_data[bone]["location"].z = self._get_limited_value(
            bone.location.z,
            displacement_data[bone]["location"].z,
            self.location_range[0].z,
            self.location_range[1].z,
        )

        # Set location and insert keyframe
        bone.location += displacement_data[bone]["location"]
        bone.keyframe_insert(data_path="location", index=-1)

    def _insert_rotation_keyframe(
        self, bone: bpy.types.Bone, displacement_data: dict
    ) -> None:
        """
        Insert a keyframe for the bone rotation with the displacement data for the current frame if necessary.

        Args:
            bone (bpy.types.Bone): The bone.
            displacement_data (dict): The displacement data for the current frame.
        """
        if displacement_data[bone]["rotation_euler"] == Euler((0, 0, 0)):
            return

        bone.rotation_mode = "XYZ"
        # Limit rotation
        match bone:
            case self.arm:
                rotation_range = self.arm_rotation_range
            case self.forearm:
                rotation_range = self.forearm_rotation_range
            case self.hand:
                rotation_range = self.hand_rotation_range
        displacement_data[bone]["rotation_euler"].x = self._get_limited_value(
            bone.rotation_euler.x,
            displacement_data[bone]["rotation_euler"].x,
            rotation_range[0].x,
            rotation_range[1].x,
        )
        displacement_data[bone]["rotation_euler"].y = self._get_limited_value(
            bone.rotation_euler.y,
            displacement_data[bone]["rotation_euler"].y,
            rotation_range[0].y,
            rotation_range[1].y,
        )
        displacement_data[bone]["rotation_euler"].z = self._get_limited_value(
            bone.rotation_euler.z,
            displacement_data[bone]["rotation_euler"].z,
            rotation_range[0].z,
            rotation_range[1].z,
        )

        # Set rotation and insert keyframe
        bone.rotation_euler.x += displacement_data[bone]["rotation_euler"].x
        bone.rotation_euler.y += displacement_data[bone]["rotation_euler"].y
        bone.rotation_euler.z += displacement_data[bone]["rotation_euler"].z
        bone.keyframe_insert(data_path="rotation_euler", index=-1)

    def _insert_keyframe(self, bone: bpy.types.Bone, displacement_data: dict) -> None:
        """
        Insert a keyframe for the bone with the displacement data for the current frame if necessary.

        Args:
            bone (bpy.types.Bone): The bone.
            displacement_data (dict): The displacement data for the current frame.
        """
        self._insert_location_keyframe(bone, displacement_data)
        self._insert_rotation_keyframe(bone, displacement_data)

    def apply(self) -> None:
        """
        Apply the gesture sequence to the armature.
        """
        start_frame = 1
        end_frame = self._get_end_frame()

        # Apply gestures over time
        previous_displacement_data = self._get_default_displacement_data()
        for current_frame in range(start_frame, end_frame):
            bpy.context.scene.frame_set(current_frame)

            # Update current and remaining gestures
            self._update_current_gestures(current_frame)
            self._update_remaining_gestures(current_frame)

            # Set the armature location and rotation for the current frame
            displacement_data = self._get_displacement_data(
                current_frame, previous_displacement_data
            )
            self._insert_keyframe(self.arm, displacement_data)
            self._insert_keyframe(self.forearm, displacement_data)
            self._insert_keyframe(self.hand, displacement_data)

            previous_displacement_data = displacement_data

        # Set general start and end frame
        bpy.context.scene.frame_start = 0
        bpy.context.scene.frame_end = end_frame - 1
