import os
import bpy
import sys
import json
import math
import importlib.util
from tqdm import tqdm
from typing import Tuple, List
from mathutils import Vector
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
from utils import argument_parser
from blender_objects.room import Room
from blender_objects.wall import Wall
from blender_objects.blinds import Blinds
from blender_objects.shades import Shades
from blender_objects.window import Window
from blender_objects.muntins import Muntins
from utils.input_file_parser import InputFileParser
from gestures.gesture_sequence import GestureSequence
from blender_collections.blender_collection import BlenderCollection

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


def get_background(blender_objects: dict) -> BlenderCollection:
    """
    Get the blender objects to add to the background.
    
    Args:
        blender_objects (dict): The blender objects.
        
    Returns:
        BlenderCollection: The background collection.
    """
    background_collection = BlenderCollection("Background")
    
    objects = []
    for _, blender_object_args in blender_objects.items():
        blender_object_object = blender_object_args["object"]
        blender_object_parents = blender_object_args["parents"]
        if blender_object_parents is None:
            objects.append(blender_object_object)
        else:
            for blender_object_parent in blender_object_parents:
                blender_object_parent.add_decorator(blender_object_object)

    background_collection.add_all_objects(objects)

    return background_collection


def get_parser() -> argument_parser.ArgumentParserForBlender:
    """
    Get the argument parser for Blender.

    Returns:
        argparse.ArgumentParser: The argument parser.
    """
    parser = argument_parser.ArgumentParserForBlender()

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
    # Get bones
    armature, arm, forearm, hand, hand_end = get_bones()
    if hand_end is not None:
        armature.data.bones.remove(hand_end)
        
    # Get input data
    input_file_path = os.path.join(INPUTS_FOLDER, args.input_file)
    input_file_parser = InputFileParser(input_file_path)
    input_data = input_file_parser.parse(armature)

    # Apply gesture sequence
    gestures = input_data["gestures"]
    gesture_sequence = GestureSequence(
        gestures=gestures,
        scene=bpy.context.scene,
        arm=arm,
        forearm=forearm,
        hand=hand,
    )
    gesture_sequence.apply()

    # Add background
    blender_objects = input_data["blender_objects"]
    background = get_background(blender_objects)
    background.apply()

    # Render the animation if specified
    if args.render:
        render()


if __name__ == "__main__":
    # blender --python run.py -- -gef "gestures.json" -r false
    parser = get_parser()
    args = parser.parse_args()

    main(args)
