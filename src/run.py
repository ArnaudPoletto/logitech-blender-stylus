import os
import bpy
import sys
import math
import random
import importlib.util
from typing import Tuple
from mathutils import Vector

wrk_dir = os.getcwd()
paths = [
    os.path.join(wrk_dir, "utils/__init__.py"),
    os.path.join(wrk_dir, "gestures/__init__.py"),
    os.path.join(wrk_dir, "events/__init__.py"),
]
names = ["utils", "gestures", "events"]

for path, name in zip(paths, names):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

from utils.axis import Axis
from utils import argumentparser
from events.rotation_event import RotationEvent
from gestures.gesture_sequence import GestureSequence
from events.translation_event import TranslationEvent
from gestures.rotation_wave_gesture import RotationWaveGesture
from gestures.translation_wave_gesture import TranslationWaveGesture

BASE_BLENDER_FILE = os.path.join(wrk_dir, "..", "data", "base.blend")

ARMATURE_NAME = "Armature"
ARM_NAME = "Arm"
FOREARM_NAME = "Forearm"
HAND_NAME = "Hand"

FRAME_RATE = 60


def get_parser() -> argumentparser.ArgumentParserForBlender:
    """
    Get the argument parser for Blender.

    Returns:
        argparse.ArgumentParser: The argument parser.
    """
    parser = argumentparser.ArgumentParserForBlender()

    return parser


def get_bones() -> Tuple[bpy.types.Bone, bpy.types.Bone, bpy.types.Bone]:
    """
    Get the bones from the armature.

    Returns:
        Tuple[bpy.types.Bone, bpy.types.Bone, bpy.types.Bone]: The arm, forearm, and hand bones.
    """
    # Get armature
    armature = bpy.data.objects.get("Armature")
    if armature is None or armature.type != "ARMATURE":
        raise ValueError("Armature not found or not of type ARMATURE.")

    # Get bones
    pose = armature.pose

    arm = pose.bones.get("Arm")
    forearm = pose.bones.get("Forearm")
    hand = pose.bones.get("Hand")

    if arm is None or forearm is None or hand is None:
        raise ValueError("Bones not found.")

    return arm, forearm, hand


def main(args) -> None:
    """
    The main function.

    Args:
        args (argparse.Namespace): The command line arguments.
    """
    # Load the base Blender file
    bpy.ops.wm.open_mainfile(filepath=BASE_BLENDER_FILE)

    arm, forearm, hand = get_bones()

    gestures_events = [
        (
            RotationWaveGesture,
            {
                "start_frame": 1,
                "end_frame": 120,
                "frame_rate": FRAME_RATE,
                "axis": Axis.X_AXIS,
                "wave_frequency": 1.0,
                "wave_amplitude": 0.5,
                "arm_phase_shift": 0.0,
                "forearm_phase_shift": math.pi / 4,
                "hand_phase_shift": math.pi / 4,
                "hand_amplitude_factor": 0.5,
            },
        ),
        (
            RotationWaveGesture,
            {
                "start_frame": 1,
                "end_frame": 120,
                "frame_rate": FRAME_RATE,
                "axis": Axis.X_AXIS,
                "wave_frequency": 2.5,
                "wave_amplitude": 0.2,
                "arm_phase_shift": 0.0,
                "forearm_phase_shift": math.pi / 4,
                "hand_phase_shift": math.pi / 4,
                "hand_amplitude_factor": 0.5,
            },
        ),
        (
            RotationWaveGesture,
            {
                "start_frame": 1,
                "end_frame": 120,
                "frame_rate": FRAME_RATE,
                "axis": Axis.X_AXIS,
                "wave_frequency": 5.5,
                "wave_amplitude": 0.05,
                "arm_phase_shift": 0.0,
                "forearm_phase_shift": math.pi / 4,
                "hand_phase_shift": math.pi / 4,
                "hand_amplitude_factor": 0.5,
            },
        ),
        (
            TranslationWaveGesture,
            {
                "start_frame": 1,
                "end_frame": 120,
                "frame_rate": FRAME_RATE,
                "axis": Axis.Y_AXIS,
                "phase_shift": 0,
                "wave_frequency": 3.0,
                "wave_amplitude": 0.1,
            },
        ),

        (
            RotationWaveGesture,
            {
                "start_frame": 120,
                "end_frame": 240,
                "frame_rate": FRAME_RATE,
                "axis": Axis.X_AXIS,
                "wave_frequency": 2.0,
                "wave_amplitude": 0.3,
                "arm_phase_shift": 0.0,
                "forearm_phase_shift": math.pi / 4,
                "hand_phase_shift": math.pi / 4,
                "hand_amplitude_factor": 0.5,
            },
        ),
        (
            RotationWaveGesture,
            {
                "start_frame": 120,
                "end_frame": 240,
                "frame_rate": FRAME_RATE,
                "axis": Axis.Y_AXIS,
                "wave_frequency": 1.0,
                "wave_amplitude": 0.7,
                "arm_phase_shift": 0.0,
                "forearm_phase_shift": math.pi / 4,
                "hand_phase_shift": math.pi / 4,
                "hand_amplitude_factor": 0.5,
            },
        ),
        (
            RotationWaveGesture,
            {
                "start_frame": 120,
                "end_frame": 240,
                "frame_rate": FRAME_RATE,
                "axis": Axis.Z_AXIS,
                "wave_frequency": 5.0,
                "wave_amplitude": 0.2,
                "arm_phase_shift": 0.0,
                "forearm_phase_shift": math.pi / 4,
                "hand_phase_shift": math.pi / 4,
                "hand_amplitude_factor": 0.5,
            },
        ),
        (
            TranslationWaveGesture,
            {
                "start_frame": 120,
                "end_frame": 240,
                "frame_rate": FRAME_RATE,
                "axis": Axis.X_AXIS,
                "phase_shift": math.pi / 2,
                "wave_frequency": 1.0,
                "wave_amplitude": 0.5,
            },
        ),
        (
            TranslationWaveGesture,
            {
                "start_frame": 120,
                "end_frame": 240,
                "frame_rate": FRAME_RATE,
                "axis": Axis.Z_AXIS,
                "phase_shift": 0,
                "wave_frequency": 1.0,
                "wave_amplitude": 0.5,
            },
        ),
    ]

    gesture_sequence = GestureSequence(
        gestures_events=gestures_events,
        scene=bpy.context.scene,
        arm=arm,
        forearm=forearm,
        hand=hand,
    )
    gesture_sequence.apply()


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    main(args)
