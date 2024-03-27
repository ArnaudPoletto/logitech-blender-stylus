import os
import bpy
import sys
import json
import math
import importlib.util
from tqdm import tqdm
from typing import Tuple, List
from mathutils import Vector, Euler
from bpy_extras.object_utils import world_to_camera_view

wrk_dir = os.getcwd()
paths = [
    os.path.join(wrk_dir, "utils/__init__.py"),
    os.path.join(wrk_dir, "gestures/__init__.py"),
    os.path.join(wrk_dir, "blender_objects/__init__.py"),
    os.path.join(wrk_dir, "blender_collections/__init__.py"),
]
names = [
    "utils",
    "gestures",
    "blender_objects",
    "blender_collections",
]

for path, name in zip(paths, names):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

from utils.axis import Axis
from utils.bone import Bone
from utils import argumentparser
from blender_objects.room import Room
from blender_objects.wall import Wall
from blender_objects.blinds import Blinds
from blender_objects.shades import Shades
from blender_objects.window import Window
from blender_objects.muntins import Muntins
from gestures.gesture_sequence import GestureSequence
from gestures.rotation_gesture import RotationGesture
from gestures.translation_gesture import TranslationGesture
from gestures.rotation_sine_gesture import RotationSineGesture
from gestures.rotation_wave_gesture import RotationWaveGesture
from blender_collections.blender_collection import BlenderCollection
from gestures.translation_sine_gesture import TranslationSineGesture

INPUTS_FOLDER = os.path.join(wrk_dir, "..", "data", "inputs")
OUTPUT_FILE = os.path.join(wrk_dir, "..", "data", "output.json")
RENDER_FOLDER_PATH = os.path.join(wrk_dir, "..", "data", "images")

CAMERA_NAME = "Camera"
STYLUS_OUTER_NAME = "Outer"
ARMATURE_NAME = "Armature"
FRAME_RATE = 60


def get_bones() -> (
    Tuple[bpy.types.Bone, bpy.types.Bone, bpy.types.Bone, bpy.types.Bone | None]
):
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
    hand_end = pose.bones.get("Hand_end")

    if arm is None or forearm is None or hand is None:
        raise ValueError("Bones not found.")

    return armature, arm, forearm, hand, hand_end


def get_gestures(file_path: str, armature: bpy.types.Object) -> List[Tuple[type, dict]]:
    """
    Get the gestures from the file.

    Args:
        file_path (str): The file path to the input file.

    Returns:
        List[type, dict]: The gestures.

    Raises:
        ValueError: If no gestures are found in the input file.
        ValueError: If the bone is not found.
    """
    with open(file_path, "r") as file:
        input = json.load(file)
        if "gestures" not in input:
            raise ValueError("No gestures found in the input file.")
        gestures = input["gestures"]

        # Reformat gestures
        gestures = [
            (globals()[gesture["type"]], gesture["args"]) for gesture in gestures
        ]

        # Reformat the arguments
        for gesture in gestures:
            gesture_args = gesture[1]
            if "axis" in gesture_args:
                axis_name = gesture_args["axis"]
                if axis_name not in Axis.__members__:
                    raise ValueError(f"Axis {axis_name} not found.")

                gesture_args["axis"] = Axis(axis_name)

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


def is_led_occluded(led, camera, stylus_outer, leds):
    """
    Check if an LED is occluded by any object between the camera and the LED.

    Args:
        camera: The camera object.
        led: The LED object.

    Returns:
        True if the LED is occluded, False otherwise.
    """
    # Get the direction from the camera to the LED
    led_location = get_object_center(led)
    direction = camera.location - led_location
    direction.normalize()

    # Remove stylus outer and all LEDs from the scene
    stylus_outer.hide_set(True)
    for l in leds:
        l.hide_set(True)

    # Cast a ray from the camera to the LED
    scene = bpy.context.scene
    result = scene.ray_cast(
        depsgraph=bpy.context.evaluated_depsgraph_get(),
        origin=led_location,
        direction=direction,
    )

    # Add stylus outer back to the scene
    stylus_outer.hide_set(False)
    for l in leds:
        l.hide_set(False)

    return result[0]


def get_object_center(object):
    """
    Get the bounding box center of an object.

    Args:
        object: The object to get the bounding box center of.

    Returns:
        The bounding box center of the object.
    """

    local_bbox_center = 0.125 * sum((Vector(b) for b in object.bound_box), Vector())
    global_bbox_center = object.matrix_world @ local_bbox_center

    return global_bbox_center


def render_and_get_frame_info(frame, camera, stylus_outer, leds):
    """
    Render a frame and get the camera projection coordinates of LED.

    Args:
        frame: The frame to render.
        leds: The LED objects to get the 3D object center of.
        camera: The camera to render from.

    Returns:
        The 3D object center in the frame.
    """

    # Render frame
    bpy.context.scene.frame_set(frame)
    bpy.data.scenes["Scene"].render.filepath = os.path.join(
        RENDER_FOLDER_PATH, f"{frame:04d}.png"
    )
    bpy.ops.render.render(
        animation=False, write_still=True
    )  # Animation set to False to render the current frame only

    # Get pixel coordinates of LEDs
    leds_data = {}
    for led in leds:
        led_center = get_object_center(led)
        led_projected_coordinates = world_to_camera_view(
            bpy.context.scene, camera, led_center
        )
        leds_data[led.name] = {
            "x_cam": led_projected_coordinates.x,
            "y_cam": led_projected_coordinates.y,
            "x_world": led_center.x,
            "y_world": led_center.y,
            "z_world": led_center.z,
            "occluded": is_led_occluded(led, camera, stylus_outer, leds),
        }

    return leds_data


def render():
    """
    Render the animation and collect data.

    Raises:
        ValueError: If the camera or stylus outer is not found.
    """
    camera = bpy.data.objects.get(CAMERA_NAME)
    if camera is None:
        raise ValueError("Camera not found.")

    stylus_outer = bpy.data.objects.get(STYLUS_OUTER_NAME)
    if stylus_outer is None:
        raise ValueError("Stylus outer not found.")

    leds = [obj for obj in bpy.data.objects if "LED" in obj.name]

    data = {}
    for frame in tqdm(
        range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1),
        desc="Rendering frames",
    ):
        data[frame] = render_and_get_frame_info(frame, camera, stylus_outer, leds)

    # Write data to JSON file
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_background() -> BlenderCollection:
    # TODO: remove hardcoding
    # TODO: add documentation
    # Get objects
    objects = []

    room = Room(
        name="Room",
        location=Vector((0, 0, 0)),
        width=50,
        height=25,
        depth=75,
    )

    back_wall_window = Window(
        name="Window",
        location=Vector((0, 0)),
        scale=Vector((10, 5)),
    )
    back_wall_window_decorator = Blinds(
        name="Blinds",
        n_blinds=10,
        angle=math.pi / 4,
        vertical=False,
    )
    back_wall_window.add_decorator(back_wall_window_decorator)
    room.back_wall.add_window(back_wall_window)

    right_wall_window = Window(
        name="Window",
        location=Vector((-1, -31)),
        scale=Vector((10, 5)),
    )
    right_wall_window_decorator = Muntins(
        name="Muntins",
        size=0.1,
        n_muntins_width=5,
        n_muntins_height=5,
    )
    right_wall_window.add_decorator(right_wall_window_decorator)
    room.right_wall.add_window(right_wall_window)

    left_wall_window = Window(
        name="Window",
        location=Vector((-1, -31)),
        scale=Vector((10, 5)),
    )
    left_wall_window_decorator = Muntins(
        name="Muntins",
        size=0.1,
        n_muntins_width=5,
        n_muntins_height=5,
    )
    left_wall_window.add_decorator(left_wall_window_decorator)
    room.left_wall.add_window(left_wall_window)

    objects.append(room)

    # Get background and all objects
    background_collection = BlenderCollection(
        name="Background",
        parent_collection=bpy.context.scene.collection,
    )
    background_collection.add_all_objects(objects)

    return background_collection


def get_parser() -> argumentparser.ArgumentParserForBlender:
    """
    Get the argument parser for Blender.

    Returns:
        argparse.ArgumentParser: The argument parser.
    """
    parser = argumentparser.ArgumentParserForBlender()

    parser.add_argument(
        "-if",
        "--input_file",
        metavar="INPUT_FILE",
        help="The input file containing the data to apply gestures and background.",
        type=str,
        default="input.json",
    )

    parser.add_argument(
        "-r",
        "--render",
        metavar="RENDER",
        help="Whether to render the animation after applying the gestures.",
        type=bool,
        default=False,
    )

    return parser


def main(args) -> None:
    """
    The main function.

    Args:
        args (argparse.Namespace): The command line arguments.
    """
    # Get bones and gestures
    armature, arm, forearm, hand, hand_end = get_bones()
    if hand_end is not None:
        armature.data.bones.remove(hand_end)
    input_file = os.path.join(INPUTS_FOLDER, args.input_file)
    gestures = get_gestures(input_file, armature)

    # Apply gesture sequence
    gesture_sequence = GestureSequence(
        gestures=gestures,
        scene=bpy.context.scene,
        arm=arm,
        forearm=forearm,
        hand=hand,
    )
    gesture_sequence.apply()

    # Add background
    # TODO: add background information to input file and remove hardcoding
    background = get_background()
    background.apply()

    # Render the animation if specified
    if args.render:
        render()


if __name__ == "__main__":
    # blender --python run.py -- -gef "gestures.json" -r false
    parser = get_parser()
    args = parser.parse_args()

    main(args)
