import os
import bpy
import sys
import json
import math
import numpy as np
import importlib.util
from typing import Tuple, List
from mathutils import Vector, Euler

wrk_dir = os.getcwd()
paths = [
    os.path.join(wrk_dir, "utils/__init__.py"),
    os.path.join(wrk_dir, "gestures/__init__.py"),
    os.path.join(wrk_dir, "blender_objects/__init__.py"),
    os.path.join(wrk_dir, "blender_collections/__init__.py"),
    os.path.join(wrk_dir, "input_data_generation/__init__.py"),
    os.path.join(wrk_dir, "module_operators/__init__.py"),
    os.path.join(wrk_dir, "background_image/__init__.py"),
    os.path.join(wrk_dir, "render/__init__.py"),
]
names = [
    "utils",
    "gestures",
    "blender_objects",
    "blender_collections",
    "input_data_generation",
    "module_operators",
    "background_image",
    "render",
]

for path, name in zip(paths, names):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

from utils.bone import Bone
from utils.seed import set_seed
from render.render import render
from utils import argument_parser
from module_operators.all_of import AllOf
from module_operators.one_of import OneOf
from module_operators.some_of import SomeOf
from utils.input_data_parser import InputDataParser
from gestures.gesture_sequence import GestureSequence
from input_data_generation.module_generator import ModuleGenerator
from blender_collections.blender_collection import BlenderCollection
from input_data_generation.input_data_generator import InputDataGenerator
from input_data_generation.module_generator_type import ModuleGeneratorType
from background_image.random_background_image_generator import (
    RandomBackgroundImageGenerator,
)
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
    CAMERA_NAME,
    CAMERA_TYPE,
    CAMERA_FOCAL_LENGTH,
    CAMERA_FOV_DEGREES,
    RENDER_RESOLUTION,
    BACKGROUND_COLLECTION_NAME,
    HIDE_ARMATURE_PROBABILITY,
    ANIMATION_LENGTH,
    BACKGROUND_COLOR_SKEW_FACTOR,
)


def _setup_armature() -> Tuple[bpy.types.Object, str]:
    """
    Choose a random armature among the existing ones and delete the rest.

    Returns:
        bpy.types.Object: The armature object.
        str: The armature suffix.
    """
    # Get possible armatures
    armature_names = [
        armature
        for armature in bpy.data.objects.keys()
        if armature.startswith("Armature")
    ]

    # Choose one randomly and delete the rest
    armature_name = np.random.choice(armature_names)
    armature_suffix = armature_name.replace("Armature", "")
    for obj in bpy.data.objects:
        if armature_suffix not in obj.name:
            bpy.data.objects.remove(obj)
    armature = bpy.data.objects[armature_name]
    armature.location = Vector((0, 0, 0))

    return armature, armature_suffix


def _set_random_bones_rotation(
    arm: bpy.types.Bone, forearm: bpy.types.Bone, hand: bpy.types.Bone
) -> None:
    """
    Set random rotation to the bones.

    Args:
        arm (bpy.types.Bone): The arm bone.
        forearm (bpy.types.Bone): The forearm bone.
        hand (bpy.types.Bone): The hand bone.
    """

    def _get_random_rotation(min: float, max: float) -> Euler:
        """
        Get a random rotation.

        Args:
            min (float): The minimum value.
            max (float): The maximum value.

        Returns:
            Euler: The random rotation.
        """
        x_rotation = np.random.uniform(min, max)
        y_rotation = np.random.uniform(min, max)
        z_rotation = np.random.uniform(min, max)

        return Euler((x_rotation, y_rotation, z_rotation), "XYZ")

    arm.rotation_euler = _get_random_rotation(-np.pi, np.pi)
    forearm.rotation_euler = _get_random_rotation(-np.pi / 2, np.pi / 2)
    hand.rotation_euler = _get_random_rotation(-np.pi / 2, np.pi / 2)


def setup_scene_and_get_objects(
    hide_armature_probability: float,
) -> Tuple[bpy.types.Bone, bpy.types.Bone, bpy.types.Bone, str]:
    """
    Setup the scene and get the objects.

    Args:
        hide_armature_probability (float): The probability of hiding the armature.

    Returns:
        Tuple[bpy.types.Bone, bpy.types.Bone, bpy.types.Bone, str]: The armature, arm, forearm, hand, and armature suffix.
    """
    set_seed()

    armature, armature_suffix = _setup_armature()

    # Get bones
    pose = armature.pose
    arm = pose.bones.get(Bone.Arm.value)
    forearm = pose.bones.get(Bone.Forearm.value)
    hand = pose.bones.get(Bone.Hand.value)

    if arm is None or forearm is None or hand is None:
        raise ValueError("Bones not found.")

    _set_random_bones_rotation(arm, forearm, hand)

    return armature, arm, forearm, hand, armature_suffix


def get_background(blender_objects: dict) -> BlenderCollection:
    """
    Get the blender objects to add to the background.

    Args:
        blender_objects (dict): The blender objects.

    Returns:
        BlenderCollection: The background collection.
    """
    background_collection = BlenderCollection(BACKGROUND_COLLECTION_NAME)

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

    parser.add_argument(
        "-q",
        "--quit",
        metavar="QUIT",
        help="Whether to quit Blender after rendering the animation.",
        type=bool,
        default=False,
    )

    return parser


def _get_module_generators(
    room_id: str = "room",
) -> Tuple[ModuleGenerator, ModuleGenerator, List[ModuleGenerator]]:
    room_module = RandomRoomModuleGenerator(
        name="Room",
        id=room_id,
        xy_scale_range=(20, 100),
        z_scale_range=(10, 25),
    )
    camera_module = RandomCameraModuleGenerator(
        name=CAMERA_NAME,
        id="camera",
        xy_distance_range=(3, 6),
        z_distance_range=(0, 1),
        fixation_point_range=1,
        type=CAMERA_TYPE,
        focal_length=CAMERA_FOCAL_LENGTH,
        fov=math.radians(CAMERA_FOV_DEGREES),
    )
    modules = [
        RandomSunModuleGenerator(name="Sun", id="sun", energy_range=(0.0, 1.0)),
        SomeOf(
            [
                RandomChristmasTreeModuleGenerator(
                    name="ChristmasTreeTall",
                    id="christmas_tree_tall",
                    room_id=room_id,
                    height_range=(5, 10),
                    radius_range=(1, 2),
                    n_leds_range=(25, 200),
                    led_radius_range=(0.03, 0.06),
                    emission_range=(1, 5),
                    flicker_probability_range=(0.00, 0.01),
                    padding=0.1,
                ),
                RandomChristmasTreeModuleGenerator(
                    name="ChristmasTreeSmall",
                    id="christmas_tree_small",
                    room_id=room_id,
                    height_range=(5, 7),
                    radius_range=(0.5, 1),
                    n_leds_range=(10, 25),
                    led_radius_range=(0.03, 0.06),
                    emission_range=(1, 5),
                    flicker_probability_range=(0.00, 0.01),
                    padding=0.1,
                ),
            ]
        ),
        RandomWallLampModuleGenerator(
            name="WallLamp",
            id="wall_lamp",
            room_id=room_id,
            n_wall_lamps=10,
            xy_scale_range=(1, 5),
            emission_strength_range=(0.1, 1),
            padding=0.1,
        ),
        RandomWindowModuleGenerator(
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
        ),
        PerlinRotationSineGestureModuleGenerator(
            id="perlin_rotation_sine",
            start_frame=1,
            end_frame=ANIMATION_LENGTH // 2,
            period_range=(1, 4),
            amplitude_range=(0.5, 2),
            persistance=0.3,
            n_octaves=5,
        ),
        PerlinRotationWaveGestureModuleGenerator(
            id="perlin_rotation_wave",
            start_frame=ANIMATION_LENGTH // 2,
            end_frame=ANIMATION_LENGTH,
            period_range=(1, 3),
            amplitude_range=(1, 2),
            persistance=0.3,
            n_octaves=2,
        ),
    ] # TODO: fine tune the rules
    
    return room_module, camera_module, modules


def main(args) -> None:
    """
    The main function.

    Args:
        args (argparse.Namespace): The command line arguments.
    """
    set_seed()

    # Get bones
    armature, arm, forearm, hand, armature_suffix = setup_scene_and_get_objects(
        hide_armature_probability=HIDE_ARMATURE_PROBABILITY,
    )

    # Get input data
    print("Generating input data...")
    room_module, camera_module, modules = _get_module_generators()
    input_data_generator = InputDataGenerator(
        room_module=room_module, camera_module=camera_module, modules=modules
    )
    input_data = input_data_generator.generate_input_data()
    input_file_parser = InputDataParser(input_data)
    input_data = input_file_parser.parse(armature)

    # Add gesture sequence
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

    # Add background objects
    print("Adding background...")
    blender_objects = input_data["blender_objects"]
    background = get_background(blender_objects)
    background.apply()

    # Add background image
    print("Adding background image...")
    random_background_image_generator = RandomBackgroundImageGenerator(
        width=RENDER_RESOLUTION[0],
        height=RENDER_RESOLUTION[1],
        n_patches_range=(100, 10000),
        n_patch_corners_range=(3, 10),
        patch_size_range=(1, 50),
        n_lines_range=(10, 1000),
        line_size_range=(1, 50),
        n_line_points_range=(3, 25),
        line_thickness_range=(1, 3),
        smooth_gaussian_kernel_size=301,
        n_blur_steps=5,
        max_blur=5,
        color_skew_factor=BACKGROUND_COLOR_SKEW_FACTOR
    )
    random_background_image_generator.apply_to_scene()

    # Set output resolution
    print(f"Resolution set to {RENDER_RESOLUTION[0]}x{RENDER_RESOLUTION[1]}.")
    bpy.context.scene.render.resolution_x = RENDER_RESOLUTION[0]
    bpy.context.scene.render.resolution_y = RENDER_RESOLUTION[1]

    # Render the animation if specified
    if args.render:
        print("Rendering...")
        render(armature_suffix, random_background_image_generator)

    print("Done!")

    # Close Blender

    if args.quit:
        print("Quitting Blender.")
        bpy.ops.wm.quit_blender()


if __name__ == "__main__":
    # TODO: blender ..\data\base_multi.blend --python run.py -- -r True
    parser = get_parser()
    args = parser.parse_args()

    main(args)
