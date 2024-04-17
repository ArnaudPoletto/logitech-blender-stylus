import os
import bpy
import json
from tqdm import tqdm
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

from background_image.black_background_image_generator import (
    BlackBackgroundImageGenerator,
)
from utils.config import (
    OUTPUT_FILE,
    RENDER_FOLDER_PATH,
    CAMERA_NAME,
    BACKGROUND_COLLECTION_NAME,
    RENDER_RESOLUTION,
    GROUND_TRUTH_WITH_ARM_MODEL
)


def _get_object_center(object) -> Vector:
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


def _is_led_occluded(led, camera, leds) -> bool:
    """
    Check if an LED is occluded by any object between the camera and the LED.

    Args:
        camera: The camera object.
        led: The LED object.

    Returns:
        True if the LED is occluded, False otherwise.
    """
    # Get the direction from the camera to the LED
    led_location = _get_object_center(led)
    direction = camera.location - led_location
    direction.normalize()

    # Remove stylus outer and all LEDs from the scene
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
    for l in leds:
        l.hide_set(False)

    return result[0]


def _is_led_in_frame(led, camera) -> bool:
    """
    Check if an LED is in the camera frame.

    Args:
        camera: The camera object.
        led: The LED object.

    Returns:
        True if the LED is in the frame, False otherwise.
    """
    led_center = _get_object_center(led)
    led_projected_coordinates = world_to_camera_view(
        bpy.context.scene, camera, led_center
    )

    return (
        0 <= led_projected_coordinates.x <= 1 and 0 <= led_projected_coordinates.y <= 1
    )


def render_and_get_frame_info(frame, camera, leds, armature_suffix) -> dict:
    """
    Render a frame and get the camera projection coordinates of LED.

    Args:
        frame: The frame to render.
        leds: The LED objects to get the 3D object center of.
        camera: The camera to render from.

    Returns:
        The 3D object center in the frame.
    """
    # Camera
    bpy.context.scene.camera = camera

    # Render frame with background
    bpy.context.scene.frame_set(frame)
    bpy.data.scenes["Scene"].render.filepath = os.path.join(
        RENDER_FOLDER_PATH, f"{frame:04d}_bg.png"
    )
    bpy.ops.render.render(
        animation=False, write_still=True
    )  # Animation set to False to render the current frame only

    # Render frame without background
    bpy.data.scenes["Scene"].render.filepath = os.path.join(
        RENDER_FOLDER_PATH, f"{frame:04d}_no_bg.png"
    )
    # Hide background objects
    background_objects = bpy.data.collections[BACKGROUND_COLLECTION_NAME].objects
    old_hide_render_states = [obj.hide_render for obj in background_objects]
    for background_object in background_objects:
        background_object.hide_render = True
        background_object.keyframe_insert(data_path="hide_render", frame=frame)
    armature_arm = bpy.data.objects.get(f"Arm{armature_suffix}")
    if armature_arm is None:
            raise ValueError("Armature arm not found.")
    if not GROUND_TRUTH_WITH_ARM_MODEL:
        # Hide arm model
        old_armature_arm_hide_render = armature_arm.hide_render
        armature_arm.hide_render = True
    else:
        # Set model as black material
        material_name = "BlackMaterial"
        if material_name not in bpy.data.materials:
            black_material = bpy.data.materials.new(name=material_name)
            black_material.use_nodes = True
            black_material.node_tree.nodes.clear()
            black_material_output = black_material.node_tree.nodes.new(
                "ShaderNodeOutputMaterial"
            )
            black_material_diffuse = black_material.node_tree.nodes.new(
                "ShaderNodeBsdfDiffuse"
            )
            black_material_diffuse.inputs["Color"].default_value = (0, 0, 0, 1)
            black_material.node_tree.links.new(
                black_material_output.inputs["Surface"],
                black_material_diffuse.outputs["BSDF"],
            )
        else:
            black_material = bpy.data.materials.get(material_name)
        armature_arm.data.materials.clear()
        armature_arm.data.materials.append(black_material)

    black_background_image_generator = BlackBackgroundImageGenerator(
        width=RENDER_RESOLUTION[0], height=RENDER_RESOLUTION[1]
    )
    black_background_image_generator.apply_to_scene()
    bpy.ops.render.render(
        animation=False, write_still=True
    )  # Animation set to False to render the current frame only

    for background_object, old_hide_render_state in zip(background_objects, old_hide_render_states):
        background_object.hide_render = old_hide_render_state
        background_object.keyframe_insert(data_path="hide_render", frame=frame)
    if not GROUND_TRUTH_WITH_ARM_MODEL:
        armature_arm.hide_render = old_armature_arm_hide_render
    else:
        # Remove black material
        armature_arm.data.materials.clear()

    # Get pixel coordinates of LEDs
    leds_data = {}
    for led in leds:
        led_center = _get_object_center(led)
        led_projected_coordinates = world_to_camera_view(
            bpy.context.scene, camera, led_center
        )
        leds_data[led.name] = {
            "u": led_projected_coordinates.x,
            "v": led_projected_coordinates.y,
            "x": led_center.x,
            "y": led_center.y,
            "z": led_center.z,
            "is_occluded": _is_led_occluded(led, camera, leds),
            "is_in_frame": _is_led_in_frame(led, camera),
        }

    return leds_data


def render(armature_suffix: str):
    """
    Render the animation and collect data.

    Raises:
        ValueError: If the camera or stylus outer is not found.
    """
    camera = bpy.data.objects.get(CAMERA_NAME)
    if camera is None:
        raise ValueError("Camera not found.")

    leds = [obj for obj in bpy.data.objects if "LED" in obj.name]

    data = {}
    for frame in tqdm(
        range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1),
        desc="Rendering frames",
    ):
        data[frame] = render_and_get_frame_info(frame, camera, leds, armature_suffix)

    # Write data to JSON file
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=4)
