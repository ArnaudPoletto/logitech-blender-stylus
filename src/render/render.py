import os
import bpy
import json
from tqdm import tqdm
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

from background_image.black_background_image_generator import (
    BlackBackgroundImageGenerator,
)
from background_image.random_background_image_generator import (
    RandomBackgroundImageGenerator,
)
from utils.config import (
    RENDER_FOLDER_PATH,
    CAMERA_NAME,
    BACKGROUND_COLLECTION_NAME,
    RENDER_RESOLUTION,
    GROUND_TRUTH_WITH_ARM_MODEL,
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


def _get_relative_orientation(
    object: bpy.types.Object, object_direction: Vector, camera: bpy.types.Object
) -> float:
    """
    Get the relative orientation of the stylus to the camera.

    Args:
        object (bpy.types.Object): The object to get the relative orientation of.
        object_direction (Vector): The direction of the object.
        camera (bpy.types.Object): The camera object.
    """
    stylus_rotation = object.matrix_world.to_3x3()
    camera_rotation = camera.matrix_world.to_3x3()
    stylus_x_axis = stylus_rotation @ object_direction
    camera_view_direction = camera_rotation @ Vector((0, 0, -1))
    relative_orientation = stylus_x_axis.dot(camera_view_direction)

    return relative_orientation

# TODO: doc and black_material name not hardcoded
def _get_black_material():
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

    return black_material

# TODO: add/update documentation and REFACTO
def render_and_get_frame_info(
    render_folder_path,
    frame,
    camera,
    stylus,
    leds,
    armature_suffix,
    random_background_image_generator,
) -> dict:
    """
    Render a frame and get the camera projection coordinates of LED.

    Args:
        render_folder_path: The folder path to render the frame to.
        frame: The frame to render.
        leds: The LED objects to get the 3D object center of.
        stylus: The stylus axis object.
        camera: The camera to render from.

    Returns:
        The 3D object center in the frame.
    """
    # Camera
    bpy.context.scene.camera = camera

    ## Render frame with background
    bpy.context.scene.frame_set(frame)

    # Add back the random background image
    random_background_image_generator.apply_to_scene()

    bpy.data.scenes["Scene"].render.filepath = os.path.join(
        render_folder_path, "bg", f"{frame}.png"
    )
    bpy.ops.render.render(
        animation=False, write_still=True
    )

    ## Render frame without background
    bpy.data.scenes["Scene"].render.filepath = os.path.join(
        render_folder_path, "no-bg", f"{frame}.png"
    )

    # Hide background objects
    background_objects = bpy.data.collections[BACKGROUND_COLLECTION_NAME].objects
    old_hide_render_states = [obj.hide_render for obj in background_objects]
    for background_object in background_objects:
        background_object.hide_render = True
        background_object.keyframe_insert(data_path="hide_render", frame=frame)

    # Hide/black arm model
    armature_arm = bpy.data.objects.get(f"Arm{armature_suffix}")
    if armature_arm is None:
        raise ValueError("Armature arm not found.")
    if not GROUND_TRUTH_WITH_ARM_MODEL:
        old_armature_arm_hide_render = armature_arm.hide_render
        armature_arm.hide_render = True
    else:
        # Set model as black material
        black_material = _get_black_material()
        armature_arm.data.materials.clear()
        armature_arm.data.materials.append(black_material)

    # Set device as black material
    inner_stylus = bpy.data.objects.get(f"Inner{armature_suffix}")
    if inner_stylus is None:
        raise ValueError("Inner stylus not found.")
    black_material = _get_black_material()
    inner_stylus.data.materials.clear()
    inner_stylus.data.materials.append(black_material)

    # Add black background
    black_background_image_generator = BlackBackgroundImageGenerator(
        width=RENDER_RESOLUTION[0], height=RENDER_RESOLUTION[1]
    )

    black_background_image_generator.apply_to_scene()
    bpy.ops.render.render(
        animation=False, write_still=True
    )

    # Add back the background objects
    for background_object, old_hide_render_state in zip(
        background_objects, old_hide_render_states
    ):
        background_object.hide_render = old_hide_render_state
        background_object.keyframe_insert(data_path="hide_render", frame=frame)

    # Show/remove black material arm model
    if not GROUND_TRUTH_WITH_ARM_MODEL:
        armature_arm.hide_render = old_armature_arm_hide_render
    else:
        armature_arm.data.materials.clear()

    # Remove black device material
    inner_stylus.data.materials.clear()

    # Get pixel coordinates of LEDs
    leds_data = {}
    for led in leds:
        led_center = _get_object_center(led)
        led_projected_coordinates = world_to_camera_view(
            bpy.context.scene, camera, led_center
        )
        is_occluded = _is_led_occluded(led, camera, leds)
        is_in_frame = _is_led_in_frame(led, camera)
        distance_from_camera = (camera.location - led_center).length
        stylus_relative_orientation = _get_relative_orientation(
            stylus, Vector((1, 0, 0)), camera
        )
        led_relative_orientation = _get_relative_orientation(
            led, Vector((0, 0, 1)), camera
        )
        leds_data[led.name] = {
            "u": led_projected_coordinates.x,
            "v": led_projected_coordinates.y,
            "x": led_center.x,
            "y": led_center.y,
            "z": led_center.z,
            "is_occluded": is_occluded,
            "is_in_frame": is_in_frame,
            "distance_from_camera": distance_from_camera,
            "stylus_relative_orientation": stylus_relative_orientation,
            "led_relative_orientation": led_relative_orientation,
        }

    return leds_data


def render(
    armature_suffix: str,
    random_background_image_generator: RandomBackgroundImageGenerator,
) -> None:
    """
    Render the animation and collect data.

    Raises:
        ValueError: If the camera or stylus outer is not found.
    """
    camera = bpy.data.objects.get(CAMERA_NAME)
    if camera is None:
        raise ValueError("Camera not found.")

    stylus = bpy.data.objects.get(f"Stylus{armature_suffix}")
    if stylus is None:
        raise ValueError("Stylus not found.")

    leds = [obj for obj in bpy.data.objects if "LED" in obj.name]

    # Get render folder path
    render_folder_path = RENDER_FOLDER_PATH
    render_subfolder_path = 1
    while os.path.exists(os.path.join(render_folder_path, str(render_subfolder_path))):
        render_subfolder_path += 1
    render_folder_path = os.path.join(render_folder_path, str(render_subfolder_path))
    os.makedirs(render_folder_path, exist_ok=True)

    data = {}
    for frame in tqdm(
        range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1),
        desc="Rendering frames",
    ):
        data[frame] = render_and_get_frame_info(
            render_folder_path,
            frame,
            camera,
            stylus,
            leds,
            armature_suffix,
            random_background_image_generator,
        )

    # Write data to JSON file
    output_file_path = os.path.join(render_folder_path, "data.json")
    with open(output_file_path, "w") as f:
        json.dump(data, f, indent=4)
