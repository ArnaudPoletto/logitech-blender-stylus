import os
import bpy
import sys
import json
import math
import importlib.util
from tqdm import tqdm
from typing import Tuple
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

wrk_dir = os.getcwd()
paths = [
    os.path.join(wrk_dir, "utils/__init__.py"),
    os.path.join(wrk_dir, "gestures/__init__.py"),
    os.path.join(wrk_dir, "blender_objects/__init__.py"),
    os.path.join(wrk_dir, "blender_collections/__init__.py"),
    os.path.join(wrk_dir, "input_data_generation/__init__.py"),
    os.path.join(wrk_dir, "module_operators/__init__.py"),
]
names = [
    "utils",
    "gestures",
    "blender_objects",
    "blender_collections",
    "input_data_generation",
    "module_operators",
]

for path, name in zip(paths, names):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

from utils.bone import Bone
from utils.seed import set_seed
from utils import argument_parser
from module_operators.all_of import AllOf
from module_operators.one_of import OneOf
from module_operators.some_of import SomeOf
from utils.input_data_parser import InputDataParser
from gestures.gesture_sequence import GestureSequence
from blender_collections.blender_collection import BlenderCollection
from input_data_generation.input_data_generator import InputDataGenerator
from input_data_generation.module_generator_type import ModuleGeneratorType
from input_data_generation.random_sun_module_generator import RandomSunModuleGenerator
from input_data_generation.random_room_module_generator import RandomRoomModuleGenerator
from input_data_generation.random_table_module_generator import (
    RandomTableModuleGenerator,
)
from input_data_generation.random_window_module_generator import (
    RandomWindowModuleGenerator,
)
from input_data_generation.random_wall_lamp_module_generator import (
    RandomWallLampModuleGenerator,
)
from input_data_generation.random_christmas_tree_module_generator import (
    RandomChristmasTreeModuleGenerator,
)
from input_data_generation.perlin_rotation_sine_gesture_module_generator import (
    PerlinRotationSineGestureModuleGenerator,
)
from input_data_generation.perlin_rotation_wave_gesture_module_generator import (
    PerlinRotationWaveGestureModuleGenerator,
)
from input_data_generation.random_camera_module_generator import (
    RandomCameraModuleGenerator,
)
from utils.config import (
    INPUTS_FOLDER,
    OUTPUT_FILE,
    RENDER_FOLDER_PATH,
    CAMERA_NAME,
    STYLUS_OUTER_NAME,
    ARMATURE_NAME,
)


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


def is_led_occluded(led, camera, stylus_outer, leds) -> bool:
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


def get_object_center(object) -> Vector:
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
                blender_object_parent.add_relative_blender_object(blender_object_object)

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
        default=None,
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
    # Get parameters
    input_file = args.input_file

    # Get bones
    armature, arm, forearm, hand, hand_end = get_bones()
    if hand_end is not None:
        armature.data.bones.remove(hand_end)

    # Get input data
    if input_file is None:
        print("Generating input data...")
        room_id = "room"
        room_module = RandomRoomModuleGenerator(
            weight=1,
            name="Room",
            id=room_id,
            xy_scale_range=(20, 100),
            z_scale_range=(10, 25),
        )
        modules = [
            RandomCameraModuleGenerator(
                name="Camera",
                id="camera",
                xy_distance_range=(3, 9),
                z_distance_range=(0, 1),
                fixation_point_range=0,
            ),
            RandomSunModuleGenerator(
                weight=1, name="Sun", id="sun", energy_range=(0.5, 1.5)
            ),
            RandomChristmasTreeModuleGenerator(
                weight=1,
                priority=0,
                name="ChristmasTree",
                id="christmas_tree",
                room_id=room_id,
                height_range=(5, 10),
                radius_range=(1, 2),
                n_leds_range=(50, 200),
                led_radius_range=(0.03, 0.06),
                emission_range=(1, 5),
                flicker_probability_range=(0, 0.1),
                padding=0.1,
            ),
            RandomWallLampModuleGenerator(
                weight=1,
                priority=0,
                name="WallLamp",
                id="wall_lamp",
                room_id=room_id,
                n_wall_lamps=10,
                xy_scale_range=(1, 2),
                emission_strength_range=(1, 5),
                padding=0.1,
            ),
            RandomWindowModuleGenerator(
                weight=1,
                priority=0,
                wall_type=ModuleGeneratorType.FRONT_WALL,
                name="WindowFront",
                id="window_front",
                room_id=room_id,
                n_windows=10,
                xy_scale_range=(1, 4),
                shades_probability=0.5,
                shade_ratio_range=(0.1, 0.9),
                shade_transmission_range=(0.1, 0.9),
                blinds_probability=0.3,
                n_blinds_range=(5, 20),
                blind_angle_range=(0, math.pi),
                blind_vertical=True,
                muntins_probability=0.3,
                muntin_size_range=(0.1, 0.2),
                n_muntins_width_range=(1, 4),
                n_muntins_height_range=(1, 4),
                padding=0.1,
            ),
            RandomWindowModuleGenerator(
                weight=1,
                priority=0,
                wall_type=ModuleGeneratorType.BACK_WALL,
                name="WindowBack",
                id="window_back",
                room_id=room_id,
                n_windows=10,
                xy_scale_range=(1, 4),
                shades_probability=0.5,
                shade_ratio_range=(0.1, 0.9),
                shade_transmission_range=(0.1, 0.9),
                blinds_probability=0.3,
                n_blinds_range=(5, 20),
                blind_angle_range=(0, math.pi),
                blind_vertical=True,
                muntins_probability=0.3,
                muntin_size_range=(0.1, 0.2),
                n_muntins_width_range=(1, 4),
                n_muntins_height_range=(1, 4),
                padding=0.1,
            ),
            RandomWindowModuleGenerator(
                weight=1,
                priority=0,
                wall_type=ModuleGeneratorType.LEFT_WALL,
                name="WindowLeft",
                id="window_left",
                room_id=room_id,
                n_windows=10,
                xy_scale_range=(1, 4),
                shades_probability=0.5,
                shade_ratio_range=(0.1, 0.9),
                shade_transmission_range=(0.1, 0.9),
                blinds_probability=0.3,
                n_blinds_range=(5, 20),
                blind_angle_range=(0, math.pi),
                blind_vertical=True,
                muntins_probability=0.3,
                muntin_size_range=(0.1, 0.2),
                n_muntins_width_range=(1, 4),
                n_muntins_height_range=(1, 4),
                padding=0.1,
            ),
            RandomWindowModuleGenerator(
                weight=1,
                priority=0,
                wall_type=ModuleGeneratorType.RIGHT_WALL,
                name="WindowRight",
                id="window_right",
                room_id=room_id,
                n_windows=10,
                xy_scale_range=(1, 4),
                shades_probability=0.5,
                shade_ratio_range=(0.1, 0.9),
                shade_transmission_range=(0.1, 0.9),
                blinds_probability=0.3,
                n_blinds_range=(5, 20),
                blind_angle_range=(0, math.pi),
                blind_vertical=True,
                muntins_probability=0.3,
                muntin_size_range=(0.1, 0.2),
                n_muntins_width_range=(1, 4),
                n_muntins_height_range=(1, 4),
                padding=0.1,
            ),
            SomeOf(
                modules=[
                    RandomTableModuleGenerator(
                        weight=3,
                        priority=1,
                        name="TableUnlimited",
                        id="table_unlimited",
                        room_id=room_id,
                        n_tables=-1,
                        xy_scale_range=(2, 5),
                        z_scale_range=(1, 3),
                        top_thickness_range=(0.1, 0.2),
                        leg_thickness_range=(0.1, 0.2),
                        padding=0.1,
                    ),
                    RandomTableModuleGenerator(
                        weight=1,
                        priority=0,
                        name="TableSmall",
                        id="table_small",
                        room_id=room_id,
                        n_tables=5,
                        xy_scale_range=(1, 2),
                        z_scale_range=(1, 3),
                        top_thickness_range=(0.1, 0.2),
                        leg_thickness_range=(0.1, 0.2),
                        padding=0.1,
                    ),
                    RandomTableModuleGenerator(
                        weight=1,
                        priority=0,
                        name="TableBig",
                        id="table_big",
                        room_id=room_id,
                        n_tables=3,
                        xy_scale_range=(5, 8),
                        z_scale_range=(2, 3),
                        top_thickness_range=(0.4, 0.6),
                        leg_thickness_range=(0.4, 0.6),
                        padding=0.1,
                    ),
                ],
                weight=1,
                priority=1,
            ),
            PerlinRotationSineGestureModuleGenerator(
                id="perlin_rotation",
                start_frame=1,
                end_frame=250,
                period_range=(1, 4),
                amplitude_range=(0.5, 2),
                persistance=0.3,
                n_octaves=5,
            ),
            PerlinRotationWaveGestureModuleGenerator(
                id="perlin_rotation",
                start_frame=250,
                end_frame=500,
                period_range=(1, 4),
                amplitude_range=(0.5, 2),
                persistance=0.3,
                n_octaves=5,
            ),
        ]
        input_data_generator = InputDataGenerator(
            room_module=room_module, modules=modules
        )
        input_data = input_data_generator.generate_input_data()
        # input_data = input_data_generator.generate_input_data()
        input_file_parser = InputDataParser(input_data)
        input_data = input_file_parser.parse(armature)
    else:
        print("Parsing input data...")
        input_file_path = os.path.join(INPUTS_FOLDER, input_file)
        with open(input_file_path, "r") as f:
            input_data = json.load(f)
            input_file_parser = InputDataParser(input_data)
            input_data = input_file_parser.parse(armature)

    # Apply gesture sequence
    print("Applying gestures...")
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
    print("Adding background...")
    blender_objects = input_data["blender_objects"]
    background = get_background(blender_objects)
    background.apply()

    # Render the animation if specified
    if args.render:
        print("Rendering...")
        render()

    print("Done!")


if __name__ == "__main__":
    # blender --python run.py -- -gef "gestures.json" -r false
    set_seed()

    parser = get_parser()
    args = parser.parse_args()

    main(args)
