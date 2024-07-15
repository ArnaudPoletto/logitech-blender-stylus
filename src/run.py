# This script runs a single Blender instance for synthetic data generation.
# Run this script with the following command:
# blender ../data/base_multi_new.blend --python run.py -- --render --quit
# , where:
#   --render is a flag indicating whether to render the animation after generating the scene, leaving it out will not render the animation.
#   --quit is a flag indicating whether to quit Blender after rendering the animation, leaving it out will keep Blender open.

import os
import bpy
import sys
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
    os.path.join(wrk_dir, "config/__init__.py"),
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
    "config",
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
from config.config import (
    ROOM_NAME,
    ROOM_ID,
    CAMERA_NAME,
    CAMERA_ID,
    CAMERA_TYPE,
    CAMERA_FOCAL_LENGTH,
    CAMERA_FOV_DEGREES,
    RENDER_RESOLUTION,
    BACKGROUND_COLLECTION_NAME,
    HIDE_ARMATURE_PROBABILITY,
    ANIMATION_LENGTH,
    BACKGROUND_COLOR_SKEW_FACTOR,
)


def setup_armature() -> Tuple[bpy.types.Object, str]:
    """
    Setup the armature by choosing a random armature among the existing ones and deleting the rest.

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
    print(f"➡️  Using armature {armature_suffix}.")

    for obj in bpy.data.objects:
        if armature_suffix not in obj.name:
            bpy.data.objects.remove(obj)
    armature = bpy.data.objects[armature_name]
    armature.location = Vector((0, 0, 0))

    return armature, armature_suffix


def set_random_bones_rotation(
    arm: bpy.types.Bone, forearm: bpy.types.Bone, hand: bpy.types.Bone
) -> None:
    """
    Set random rotation to the given bones.

    Args:
        arm (bpy.types.Bone): The arm bone.
        forearm (bpy.types.Bone): The forearm bone.
        hand (bpy.types.Bone): The hand bone.
    """

    def get_random_euler_rotation(min: float, max: float) -> Euler:
        """
        Get a random Euler rotation.

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

    arm.rotation_euler = get_random_euler_rotation(-np.pi, np.pi)
    forearm.rotation_euler = get_random_euler_rotation(-np.pi / 2, np.pi / 2)
    hand.rotation_euler = get_random_euler_rotation(-np.pi / 2, np.pi / 2)


def set_hide_armature(armature_suffix: str, hide_armature_probability: float) -> None:
    """
    Hide the armature with a given probability.

    Args:
        armature_suffix (str): The armature suffix.
        hide_armature_probability (float): The probability of hiding the armature.

    Raises:
        ValueError: If the armature model is not found.
    """
    # Get the armature model
    armature_arm = bpy.data.objects.get(f"Arm{armature_suffix}")
    if armature_arm is None:
        raise ValueError(f"❌ Arm model {armature_arm} not found.")

    # Hide the armature with the given probability
    p = np.random.rand()
    hide_armature = p < hide_armature_probability
    armature_arm.hide_render = hide_armature
    if hide_armature:
        print(f"➡️  Hiding armature for rendering.")


def setup_scene_and_get_objects(
    hide_armature_probability: float,
) -> Tuple[bpy.types.Bone, bpy.types.Bone, bpy.types.Bone, str]:
    """
    Setup the scene and get the objects.

    Args:
        hide_armature_probability (float): The probability of hiding the armature.

    Raises:
        ValueError: If the bones are not found.

    Returns:
        Tuple[bpy.types.Bone, bpy.types.Bone, bpy.types.Bone, str]: The armature, arm, forearm, hand, and armature suffix.
    """
    # Choose a random armature and get the bones
    armature, armature_suffix = setup_armature()
    pose = armature.pose
    arm = pose.bones.get(Bone.Arm.value)
    forearm = pose.bones.get(Bone.Forearm.value)
    hand = pose.bones.get(Bone.Hand.value)

    if arm is None or forearm is None or hand is None:
        raise ValueError(f"❌ Bones of armature {armature_suffix} not found.")

    # Set random rotation to the bones
    set_random_bones_rotation(arm, forearm, hand)

    # Randomly choose not to render the armature
    set_hide_armature(armature_suffix, hide_armature_probability)

    return armature, arm, forearm, hand, armature_suffix


def get_parser() -> argument_parser.ArgumentParserForBlender:
    """
    Get the argument parser for Blender.

    Returns:
        argparse.ArgumentParser: The argument parser.
    """
    parser = argument_parser.ArgumentParserForBlender()

    parser.add_argument(
        "-r",
        "--render",
        help="Whether to render the animation after applying the gestures.",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "-q",
        "--quit",
        help="Whether to quit Blender after rendering the animation.",
        action="store_true",
        default=False,
    )

    return parser


def get_module_generators() -> Tuple[ModuleGenerator, ModuleGenerator, List[ModuleGenerator]]:
    """
    Get the module generators, used to generate random synthetic data.
    
    Returns:
        ModuleGenerator: The room module generator.
        ModuleGenerator: The camera module generator.
        List[ModuleGenerator]: The list of module generators.
    """
    room_module = RandomRoomModuleGenerator(
        name=ROOM_NAME,
        id=ROOM_ID,
        xy_scale_range=(20, 100),
        z_scale_range=(10, 25),
    )
    camera_module = RandomCameraModuleGenerator(
        name=CAMERA_NAME,
        id=CAMERA_ID,
        xy_distance_range=(4, 6),
        z_distance_range=(0, 1),
        fixation_point_range=0.5,
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
                    room_id=ROOM_ID,
                    height_range=(5, 10),
                    radius_range=(1, 2),
                    n_leds_range=(25, 200),
                    led_radius_range=(0.03, 0.06),
                    emission_range=(1, 5),
                    flicker_probability_range=(0.00, 0.01),
                    padding=0.1,
                ),
                RandomChristmasTreeModuleGenerator(
                    name="ChristmasTreeMedium",
                    id="christmas_tree_medium",
                    room_id=ROOM_ID,
                    height_range=(5, 8),
                    radius_range=(0.75, 1.5),
                    n_leds_range=(20, 100),
                    led_radius_range=(0.03, 0.06),
                    emission_range=(1, 5),
                    flicker_probability_range=(0.00, 0.01),
                    padding=0.1,
                ),
                RandomChristmasTreeModuleGenerator(
                    name="ChristmasTreeSmall",
                    id="christmas_tree_small",
                    room_id=ROOM_ID,
                    height_range=(5, 6),
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
            room_id=ROOM_ID,
            n_wall_lamps=10,
            xy_scale_range=(0.5, 5),
            emission_strength_range=(0.1, 1),
            padding=0.1,
        ),
        RandomWindowModuleGenerator(
            wall_type=ModuleGeneratorType.FRONT_WALL,
            name="WindowFront",
            id="window_front",
            room_id=ROOM_ID,
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
            room_id=ROOM_ID,
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
            room_id=ROOM_ID,
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
            room_id=ROOM_ID,
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
                    room_id=ROOM_ID,
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
                    room_id=ROOM_ID,
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
                    room_id=ROOM_ID,
                    n_tables=3,
                    xy_scale_range=(5, 8),
                    z_scale_range=(2, 3),
                    top_thickness_range=(0.4, 0.6),
                    leg_thickness_range=(0.4, 0.6),
                    padding=0.1,
                ),
            ],
        ),
        OneOf(
            modules=[
                PerlinRotationSineGestureModuleGenerator(
                    id="perlin_rotation_sine_1",
                    start_frame=1,
                    end_frame=ANIMATION_LENGTH // 3,
                    period_range=(100, 200),
                    amplitude_range=(0.0, 1e-10),
                    persistance=0.0,
                    n_octaves_range=(1, 2),
                ), # No movement
                PerlinRotationSineGestureModuleGenerator(
                    id="perlin_rotation_sine_2",
                    start_frame=1,
                    end_frame=ANIMATION_LENGTH // 3,
                    period_range=(1, 4),
                    amplitude_range=(0.5, 2),
                    persistance=0.3,
                    n_octaves_range=(1, 5),
                ), # Baseline movements
                PerlinRotationSineGestureModuleGenerator(
                    id="perlin_rotation_sine_3",
                    start_frame=1,
                    end_frame=ANIMATION_LENGTH // 3,
                    period_range=(3, 6),
                    amplitude_range=(1, 4),
                    persistance=0.1,
                    n_octaves_range=(1, 3),
                ), # Slower but bigger and smoother movements
                PerlinRotationSineGestureModuleGenerator(
                    id="perlin_rotation_sine_4",
                    start_frame=1,
                    end_frame=ANIMATION_LENGTH // 3,
                    period_range=(4, 8),
                    amplitude_range=(0.1, 5),
                    persistance=0.5,
                    n_octaves_range=(1, 3),
                ), # Slower, smaller but more rough movements
            ]
        ),
        OneOf(
            modules=[
                PerlinRotationSineGestureModuleGenerator(
                    id="perlin_rotation_sine_5",
                    start_frame=ANIMATION_LENGTH // 3,
                    end_frame=2 * ANIMATION_LENGTH // 3,
                    period_range=(100, 200),
                    amplitude_range=(0.0, 1e-10),
                    persistance=0.0,
                    n_octaves_range=(1, 2),
                ), # No movement
                PerlinRotationSineGestureModuleGenerator(
                    id="perlin_rotation_sine_6",
                    start_frame=ANIMATION_LENGTH // 3,
                    end_frame=2 * ANIMATION_LENGTH // 3,
                    period_range=(0.5, 2),
                    amplitude_range=(1, 4),
                    persistance=0.5,
                    n_octaves_range=(1, 5),
                ), # Bigger, faster and rougher movements
                PerlinRotationSineGestureModuleGenerator(
                    id="perlin_rotation_sine_7",
                    start_frame=ANIMATION_LENGTH // 3,
                    end_frame=2 * ANIMATION_LENGTH // 3,
                    period_range=(1, 4),
                    amplitude_range=(4, 6),
                    persistance=0.1,
                    n_octaves_range=(1, 3),
                ), # Bigger, slower and smoother movements
            ]
        ),
        OneOf(
            modules=[
                PerlinRotationSineGestureModuleGenerator(
                    id="perlin_rotation_sine_8",
                    start_frame=2 * ANIMATION_LENGTH // 3,
                    end_frame=ANIMATION_LENGTH,
                    period_range=(100, 200),
                    amplitude_range=(0.0, 1e-10),
                    persistance=0.0,
                    n_octaves_range=(1, 2),
                ), # No movement
                PerlinRotationSineGestureModuleGenerator(
                    id="perlin_rotation_sine_9",
                    start_frame=2 * ANIMATION_LENGTH // 3,
                    end_frame=ANIMATION_LENGTH,
                    period_range=(1, 4),
                    amplitude_range=(0.5, 6),
                    persistance=0.3,
                    n_octaves_range=(1, 5),
                ), # More diverse amplitude
                PerlinRotationSineGestureModuleGenerator(
                    id="perlin_rotation_sine_10",
                    start_frame=2 * ANIMATION_LENGTH // 3,
                    end_frame=ANIMATION_LENGTH,
                    period_range=(0.5, 8),
                    amplitude_range=(0.5, 2),
                    persistance=0.2,
                    n_octaves_range=(1, 5),
                ), # More diverse period
            ]
        ),
        OneOf(
            modules=[
                PerlinRotationWaveGestureModuleGenerator(
                    id="perlin_rotation_wave_1",
                    start_frame=1,
                    end_frame=ANIMATION_LENGTH // 2,
                    period_range=(100, 200),
                    amplitude_range=(0.0, 1e-10),
                    persistance=0.0,
                    n_octaves_range=(1, 2),
                ), # No movements
                PerlinRotationWaveGestureModuleGenerator(
                    id="perlin_rotation_wave_2",
                    start_frame=1,
                    end_frame=ANIMATION_LENGTH // 2,
                    period_range=(1, 3),
                    amplitude_range=(1, 2),
                    persistance=0.1,
                    n_octaves_range=(1, 3),
                ), # Baseline movements
            ]
        ),
        OneOf(
            modules=[
                PerlinRotationWaveGestureModuleGenerator(
                    id="perlin_rotation_wave_3",
                    start_frame=ANIMATION_LENGTH // 2,
                    end_frame=ANIMATION_LENGTH,
                    period_range=(100, 200),
                    amplitude_range=(0.0, 1e-10),
                    persistance=0.0,
                    n_octaves_range=(1, 2),
                ), # No movements
                PerlinRotationWaveGestureModuleGenerator(
                    id="perlin_rotation_wave_4",
                    start_frame=ANIMATION_LENGTH // 2,
                    end_frame=ANIMATION_LENGTH,
                    period_range=(1, 3),
                    amplitude_range=(4, 6),
                    persistance=0.1,
                    n_octaves_range=(1, 3),
                ), # Bigger movements
                PerlinRotationWaveGestureModuleGenerator(
                    id="perlin_rotation_wave_5",
                    start_frame=ANIMATION_LENGTH // 2,
                    end_frame=ANIMATION_LENGTH,
                    period_range=(0.5, 1),
                    amplitude_range=(4, 6),
                    persistance=0.1,
                    n_octaves_range=(1, 3),
                ), # Faster movements
            ]
        )
    ]

    return room_module, camera_module, modules


def get_background(blender_objects: dict) -> BlenderCollection:
    """
    Get the background collection.

    Args:
        blender_objects (dict): The blender objects.

    Returns:
        BlenderCollection: The background collection.
    """
    background_collection = BlenderCollection(BACKGROUND_COLLECTION_NAME)

    objects = []
    for _, blender_object_args in blender_objects.items():
        blender_object = blender_object_args["object"]
        blender_object_parents = blender_object_args["parents"]
        
        # Objects with parents are linked to their parents, not the background collection
        if blender_object_parents is None:
            objects.append(blender_object)
        else:
            for blender_object_parent in blender_object_parents:
                blender_object_parent.add_relative_blender_object(blender_object)

    background_collection.add_all_objects(objects)

    return background_collection


def main() -> None:
    """
    Run a Blender scene for synthetic data generation.
    """
    # Parse the arguments
    parser = get_parser()
    args = parser.parse_args()
    
    set_seed()

    # Get bones
    armature, arm, forearm, hand, armature_suffix = setup_scene_and_get_objects(
        hide_armature_probability=HIDE_ARMATURE_PROBABILITY,
    )

    # Generate input data
    print("⏳ Generating input data...")
    room_module, camera_module, modules = get_module_generators()

    input_data_generator = InputDataGenerator(
        room_module=room_module, 
        camera_module=camera_module, 
        modules=modules,
    )
    input_data = input_data_generator.generate_input_data()
    input_file_parser = InputDataParser(input_data)
    input_data = input_file_parser.parse(armature)

    # Add gesture sequence
    print("⏳ Applying gestures...")
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
    print("⏳ Adding background...")
    blender_objects = input_data["blender_objects"]
    background = get_background(blender_objects)
    background.apply()

    # Add background image
    print("⏳ Adding background image...")
    random_background_image_generator = RandomBackgroundImageGenerator(
        width=RENDER_RESOLUTION[0],
        height=RENDER_RESOLUTION[1],
        n_patches_range=(1000, 10000),
        n_patch_corners_range=(1, 10),
        patch_size_range=(1, 50),
        n_lines_range=(10, 100),
        line_size_range=(1, 100),
        n_line_points_range=(3, 25),
        line_thickness_range=(1, 3),
        smooth_gaussian_kernel_size=301,
        n_blur_steps=5,
        max_blur=5,
        color_skew_factor=BACKGROUND_COLOR_SKEW_FACTOR,
    )
    random_background_image_generator.apply_to_scene()

    # Set output resolution
    print(f"➡️  Resolution set to {RENDER_RESOLUTION[0]}×{RENDER_RESOLUTION[1]}.")
    bpy.context.scene.render.resolution_x = RENDER_RESOLUTION[0]
    bpy.context.scene.render.resolution_y = RENDER_RESOLUTION[1]

    # Render the animation if specified
    if args.render:
        print("⏳ Rendering...")
        render(armature_suffix, random_background_image_generator)

    print("✅ Done!")

    # Close Blender
    if args.quit:
        print("⏹️ Quitting Blender.")
        bpy.ops.wm.quit_blender()


if __name__ == "__main__":
    main()
