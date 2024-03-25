import os
import bpy
import sys
import json
import importlib.util
from mathutils import Vector, Euler
from typing import Tuple, List

wrk_dir = os.getcwd()
paths = [
    os.path.join(wrk_dir, "utils/__init__.py"),
    os.path.join(wrk_dir, "gestures/__init__.py"),
]
names = ["utils", "gestures"]

for path, name in zip(paths, names):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

from utils.axis import Axis
from utils.bone import Bone
from utils import argumentparser
from gestures.gesture_sequence import GestureSequence
from gestures.rotation_gesture import RotationGesture
from gestures.translation_gesture import TranslationGesture
from gestures.rotation_wave_gesture import RotationWaveGesture
from gestures.translation_wave_gesture import TranslationWaveGesture

BASE_BLENDER_FILE = os.path.join(wrk_dir, "..", "data", "base.blend")
GESTURES_FOLDER = os.path.join(wrk_dir, "..", "data", "gestures")

ARMATURE_NAME = "Armature"
FRAME_RATE = 60


def get_parser() -> argumentparser.ArgumentParserForBlender:
    """
    Get the argument parser for Blender.

    Returns:
        argparse.ArgumentParser: The argument parser.
    """
    parser = argumentparser.ArgumentParserForBlender()

    parser.add_argument(
        "-gef",
        "--gestures_file",
        metavar="GESTURES_FILE",
        help="The file name of gestures.",
        type=str,
        default="gestures.json",
    )

    return parser


def get_bones() -> Tuple[bpy.types.Bone, bpy.types.Bone, bpy.types.Bone]:
    """
    Get the bones from the armature.

    Returns:
        Tuple[bpy.types.Bone, bpy.types.Bone, bpy.types.Bone]: The arm, forearm, and hand bones.

    Raises:
        ValueError: If the armature or bones are not found.
    """
    # Get armature
    armature = bpy.data.objects.get(ARMATURE_NAME)
    if armature is None or armature.type != "ARMATURE":
        raise ValueError("Armature not found or not of type ARMATURE.")

    # Get bones
    pose = armature.pose
    arm = pose.bones.get(Bone.Arm.value)
    forearm = pose.bones.get(Bone.Forearm.value)
    hand = pose.bones.get(Bone.Hand.value)

    if arm is None or forearm is None or hand is None:
        raise ValueError("Bones not found.")

    return armature, arm, forearm, hand


def get_gestures(file_path: str, armature: bpy.types.Object) -> List[Tuple[type, dict]]:
    """
    Get the gestures from the file.

    Args:
        file_path (str): The file path to the gestures file.

    Returns:
        List[type, dict]: The gestures.

    Raises:
        ValueError: If the bone is not found.
    """
    with open(file_path, "r") as file:
        gestures = json.load(file)

        # Reformat gestures
        gestures = [
            (globals()[gesture["type"]], gesture["args"]) for gesture in gestures
        ]

        # Reformat the arguments
        for gesture in gestures:
            gesture_args = gesture[1]
            if "axis" in gesture_args:
                gesture_args["axis"] = Axis(gesture_args["axis"])
            if "vector" in gesture_args:
                x = gesture_args["vector"]["x"]
                y = gesture_args["vector"]["y"]
                z = gesture_args["vector"]["z"]
                gesture_args["vector"] = Vector((x, y, z))
            if "euler" in gesture_args:
                x = gesture_args["euler"]["x"]
                y = gesture_args["euler"]["y"]
                z = gesture_args["euler"]["z"]
                gesture_args["euler"] = Euler((x, y, z))
            if "bone" in gesture_args:
                bone_name = gesture_args["bone"]
                if bone_name not in Bone.__members__:
                    raise ValueError(f"Bone {bone_name} not found.")

                bone = armature.pose.bones.get(bone_name)
                gesture_args["bone"] = bone

        return gestures


def main(args) -> None:
    """
    The main function.

    Args:
        args (argparse.Namespace): The command line arguments.
    """
    bpy.ops.wm.open_mainfile(filepath=BASE_BLENDER_FILE)

    # Get bones and gestures
    armature, arm, forearm, hand = get_bones()
    gestures_file = os.path.join(GESTURES_FOLDER, args.gestures_file)
    gestures = get_gestures(gestures_file, armature)

    # Apply gesture sequence
    gesture_sequence = GestureSequence(
        gestures=gestures,
        scene=bpy.context.scene,
        arm=arm,
        forearm=forearm,
        hand=hand,
    )
    gesture_sequence.apply()

    # TODO: render the animation


if __name__ == "__main__":
    # blender --python run.py -- -gef "gestures.json"
    parser = get_parser()
    args = parser.parse_args()

    main(args)
