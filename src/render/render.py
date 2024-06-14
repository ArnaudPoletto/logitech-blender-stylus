# This file contains functions to render the animation and collect frame data.

import os
import bpy
import math
import json
from tqdm import tqdm
from mathutils import Vector
from typing import Tuple, List, Dict, Any
from bpy_extras.object_utils import world_to_camera_view

from background_image.black_background_image_generator import (
    BlackBackgroundImageGenerator,
)
from background_image.random_background_image_generator import (
    RandomBackgroundImageGenerator,
)
from config.config import (
    RENDER_FOLDER_PATH,
    CAMERA_NAME,
    CAMERA_TYPE,
    BACKGROUND_COLLECTION_NAME,
    RENDER_RESOLUTION,
)


def render_bg_frame(
    render_folder_path: str,
    frame_index: int,
) -> None:
    """
    Render a frame with a random background image.

    Args:
        render_folder_path (str): The folder path to render the frame to.
        frame_index (int): The frame index to render.
    """
    bpy.data.scenes["Scene"].render.filepath = os.path.join(
        render_folder_path, "bg", f"{frame_index}.png"
    )
    bpy.ops.render.render(animation=False, write_still=True)


def get_black_material(material_name: str = "BlackMaterial") -> bpy.types.Material:
    """
    Get a black material, creating it if it does not exist.

    Args:
        material_name (str): The name of the material.

    Returns:
        bpy.types.Material: The black material.
    """
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


def hide_background(
    frame_index: int,
    armature_suffix: str,
) -> Tuple[Dict[bpy.types.Object, bool], float]:
    """
    Hide the background in the scene.

    Args:
        frame_index (int): The frame index.
        armature_suffix (str): The suffix of the armature.

    Raises:
        ValueError: If the armature arm is not found.
        ValueError: If the inner stylus is not found.
        ValueError: If the glare node is not found.

    Returns:
        Dict[bpy.types.Object, bool]: The old hide render states of the background objects.
        float: The old glare value.
    """
    # Hide background objects and store old states
    background_objects = bpy.data.collections[BACKGROUND_COLLECTION_NAME].objects
    old_hide_render_states = {obj: obj.hide_render for obj in background_objects}
    for background_object in background_objects:
        background_object.hide_render = True
        background_object.keyframe_insert(data_path="hide_render", frame=frame_index)

    # Set black arm model
    armature_arm = bpy.data.objects.get(f"Arm{armature_suffix}")
    if armature_arm is None:
        raise ValueError("❌ Armature arm not found.")
    black_material = get_black_material()
    armature_arm.data.materials.clear()
    armature_arm.data.materials.append(black_material)

    # Set device as black material
    inner_stylus = bpy.data.objects.get(f"Inner{armature_suffix}")
    if inner_stylus is None:
        raise ValueError("❌ Inner stylus not found.")
    inner_stylus.data.materials.clear()
    inner_stylus.data.materials.append(black_material)

    # Add black background
    black_background_image_generator = BlackBackgroundImageGenerator(
        width=RENDER_RESOLUTION[0], height=RENDER_RESOLUTION[1]
    )
    black_background_image_generator.apply_to_scene()

    # Remove fog effect
    tree = bpy.context.scene.node_tree
    glare_node = tree.nodes.get("Glare")
    if glare_node is None:
        raise ValueError("❌ Glare node not found.")
    old_glare_value = glare_node.mix
    glare_node.mix = -1


    return old_hide_render_states, old_glare_value


def show_background(
    frame_index: int,
    armature_suffix: str,
    random_background_image_generator: RandomBackgroundImageGenerator,
    old_hide_render_states: Dict[bpy.types.Object, bool],
    old_glare_value: float,
) -> None:
    """
    Show the background in the scene.

    Args:
        frame_index (int): The frame index.
        armature_suffix (str): The suffix of the armature.
        random_background_image_generator (RandomBackgroundImageGenerator): The random background image generator.
        old_hide_render_states (Dict[bpy.types.Object, bool]): The old hide render states of the background objects.

    Raises:
        ValueError: If the armature arm is not found.
        ValueError: If the inner stylus is not found.
        ValueError: If the glare node is not found.
    """
    # Add back the random background image
    random_background_image_generator.apply_to_scene()

    # Add back the background objects
    for background_object, old_hide_render_state in old_hide_render_states.items():
        background_object.hide_render = old_hide_render_state
        background_object.keyframe_insert(data_path="hide_render", frame=frame_index)

    # Remove black material arm model
    armature_arm = bpy.data.objects.get(f"Arm{armature_suffix}")
    if armature_arm is None:
        raise ValueError("❌ Armature arm not found.")
    armature_arm.data.materials.clear()

    # Remove black device material
    inner_stylus = bpy.data.objects.get(f"Inner{armature_suffix}")
    if inner_stylus is None:
        raise ValueError("❌ Inner stylus not found.")
    inner_stylus.data.materials.clear()

    # Add back fog effect
    tree = bpy.context.scene.node_tree
    glare_node = tree.nodes.get("Glare")
    if glare_node is None:
        raise ValueError("❌ Glare node not found.")
    glare_node.mix = old_glare_value


def render_no_bg_frame(
    render_folder_path: str,
    frame_index: int,
    armature_suffix: str,
    random_background_image_generator: RandomBackgroundImageGenerator,
) -> None:
    """
    Render a frame without background noise.

    Args:
        render_folder_path (str): The folder path to render the frame to.
        frame_index (int): The frame index to render.
        armature_suffix (str): The suffix of the armature.
        random_background_image_generator (RandomBackgroundImageGenerator): The random background image generator.
    """
    old_hide_render_states, old_glare_value = hide_background(
        frame_index,
        armature_suffix,
    )

    # Render the frame
    bpy.data.scenes["Scene"].render.filepath = os.path.join(
        render_folder_path, "no-bg", f"{frame_index}.png"
    )
    bpy.ops.render.render(animation=False, write_still=True)

    show_background(
        frame_index,
        armature_suffix,
        random_background_image_generator,
        old_hide_render_states,
        old_glare_value
    )


def get_object_center(object: bpy.types.Object) -> Vector:
    """
    Get the center of an object, which has an associated arrow object.

    Args:
        object (bpy.types.Object): The object to get the center of.

    Raises:
        ValueError: If the associated arrow object is not found.

    Returns:
        Vector: The center of the object.
    """
    arrow_name = object.name.replace("LED", "Arrow")
    arrow = bpy.data.objects.get(arrow_name)
    if arrow is None:
        raise ValueError(
            f"❌ Associated arrow {arrow_name} for object {object.name} not found."
        )
    arrow_location = arrow.matrix_world.translation

    return arrow_location


def is_led_occluded(
    led: bpy.types.Object,
    camera_object: bpy.types.Object,
    leds: List[bpy.types.Object],
    armature_arm: bpy.types.Object,
    distance_eps: float = 1e-3,
) -> bool:
    """
    Check if an LED is occluded by any object between the camera and the LED.

    Args:
        led (bpy.types.Object): The LED object.
        camera_object (bpy.types.Object): The camera object.
        leds (List[bpy.types.Object]): The LED objects.
        armature_arm (bpy.types.Object): The armature arm object.
        distance_eps (float): The distance epsilon.

    Returns:
        bool: Whether the LED is occluded.
    """
    # Get the direction from the camera to the LED
    led_location = get_object_center(led)
    direction = camera_object.location - led_location
    length = direction.length
    direction.normalize()

    # Remove LEDs and add arm if needed from the scene
    for l in leds:
        l.hide_set(True)
    armature_arm.hide_set(armature_arm.hide_render)

    # Cast a ray from the camera to the LED
    scene = bpy.context.scene
    result = scene.ray_cast(
        depsgraph=bpy.context.evaluated_depsgraph_get(),
        origin=led_location,
        direction=direction,
        distance=length + distance_eps,
    )

    # Add back LEDs to the scene
    for l in leds:
        l.hide_set(False)

    return result[0]


def is_led_in_frame(led: bpy.types.Object, camera_object: bpy.types.Object) -> bool:
    """
    Check if a LED is in the camera frame.

    Args:
        led (bpy.types.Object): The LED object.
        camera_object (bpy.types.Object): The camera object.

    Returns:
        bool: Whether the LED is in the camera frame.
    """
    led_center = get_object_center(led)
    led_projected_coordinates = world_to_camera_view(
        bpy.context.scene, camera_object, led_center
    )

    return (
        0 <= led_projected_coordinates.x <= 1 and 0 <= led_projected_coordinates.y <= 1
    )


def get_object_relative_orientation(
    object: bpy.types.Object, object_vector: Vector, camera_object: bpy.types.Object
) -> float:
    """
    Get the relative orientation of an object to the camera.

    Args:
        object (bpy.types.Object): The object to get the relative orientation of.
        object_vector (Vector): The vector of the object.
        camera_object (bpy.types.Object): The camera object.
    """
    object_rotation = object.matrix_world.to_3x3()
    camera_rotation = camera_object.matrix_world.to_3x3()
    object_direction = object_rotation @ object_vector
    object_direction.normalize()
    camera_view_direction = camera_rotation @ Vector((0, 0, -1))
    camera_view_direction.normalize()
    relative_orientation = object_direction.dot(camera_view_direction)

    return relative_orientation


def get_projected_coordinates_perspective(led_center: Vector, camera_object: bpy.types.Object) -> Vector:
    """
    Get the projected coordinates of a point in the camera view for a perspective camera.

    Args:
        led_center (Vector): The center of the LED.
        camera_object (bpy.types.Object): The camera object.

    Returns:
        Vector: The projected coordinates of the LED.
    """
    scene = bpy.context.scene
    return world_to_camera_view(scene, camera_object, led_center)


def get_projected_coordinates_panoramic(led_center: Vector, camera: bpy.types.Camera, camera_object: bpy.types.Object) -> Vector:
    """
    Get the projected coordinates of a point in the camera view for a panoramic camera.
    From: https://blender.stackexchange.com/questions/40702/how-can-i-get-the-projection-matrix-of-a-panoramic-camera-with-a-fisheye-equisol.

    Args:
        led_center (Vector): The center of the LED.
        camera (bpy.types.Camera): The camera.
        camera_object (bpy.types.Object): The camera object.

    Returns:
        Vector: The projected coordinates of the LED.
    """
    scene = bpy.context.scene
    f = camera_object.data.fisheye_lens
    pixel_aspect_ratio = scene.render.resolution_x / scene.render.resolution_y
    if camera.sensor_fit == "VERTICAL":
        h = camera.sensor_height
        w = pixel_aspect_ratio * h
    else:
        w = camera.sensor_width
        h = w / pixel_aspect_ratio

    led_center = camera_object.matrix_world.inverted() @ led_center
    led_center.normalize()

    phi = math.atan2(led_center.y, led_center.x)
    l = (led_center.x**2 + led_center.y**2) ** 0.5
    theta = math.asin(l)

    # Equisolid projection
    r = 2.0 * f * math.sin(theta / 2.0)
    u = r * math.cos(phi) / w + 0.5
    v = r * math.sin(phi) / h + 0.5

    return Vector((u, v))


def get_frame_data(
    camera_object: bpy.types.Object,
    camera: bpy.types.Camera,
    stylus: bpy.types.Object,
    leds: List[bpy.types.Object],
    armature_suffix: str,
) -> Dict[str, Dict[str, Any]]:
    """
    Get the frame data.

    Args:
        camera_object (bpy.types.Object): The camera object.
        camera (bpy.types.Camera): The camera.
        stylus (bpy.types.Object): The stylus.
        leds (List[bpy.types.Object]): The LED objects.
        armature_suffix (str): The suffix of the armature.

    Raises:
        ValueError: If the armature arm is not found.

    Returns:
        Dict[str, Dict[str, Any]]: The frame data.
    """
    # Get armature arm
    armature_arm = bpy.data.objects.get(f"Arm{armature_suffix}")
    if armature_arm is None:
        raise ValueError("❌ Armature arm not found.")

    # Get frame data
    frame_data = {}
    stylus_relative_orientation = get_object_relative_orientation(
        stylus, Vector((1, 0, 0)), camera_object
    )
    frame_data["stylus_relative_orientation"] = stylus_relative_orientation
    frame_data["leds"] = {}
    for led in leds:
        # Get camera and world coordinates
        led_center = get_object_center(led)
        if CAMERA_TYPE == "PERSP":
            led_projected_coordinates = get_projected_coordinates_perspective(
                led_center, camera_object
            )
        elif CAMERA_TYPE == "PANO":
            led_projected_coordinates = get_projected_coordinates_panoramic(
                led_center, camera, camera_object
            )
        else:
            raise ValueError(f"Camera type {CAMERA_TYPE} not supported.")
        
        # Get location information
        is_occluded = is_led_occluded(led, camera_object, leds, armature_arm)
        is_in_frame = is_led_in_frame(led, camera_object)
        distance_from_camera = (camera_object.location - led_center).length

        # Get orientation information
        arrow_name = led.name.replace("LED", "Arrow")
        arrow = bpy.data.objects.get(arrow_name)
        if arrow is None:
            raise ValueError(f"❌ Arrow {arrow_name} not found.")
        led_relative_orientation = get_object_relative_orientation(
            arrow, Vector((0, 0, 1)), camera_object
        )

        frame_data["leds"][led.name] = {
            "u": led_projected_coordinates.x,
            "v": led_projected_coordinates.y,
            "x": led_center.x,
            "y": led_center.y,
            "z": led_center.z,
            "is_occluded": is_occluded,
            "is_in_frame": is_in_frame,
            "distance_from_camera": distance_from_camera,
            "led_relative_orientation": led_relative_orientation,
        }

    return frame_data


def render_and_get_frame_data(
    render_folder_path: str,
    frame_index: int,
    camera_object: bpy.types.Object,
    camera: bpy.types.Camera,
    stylus: bpy.types.Object,
    leds: List[bpy.types.Object],
    armature_suffix: str,
    random_background_image_generator: RandomBackgroundImageGenerator,
) -> dict:
    """
    Render a frame and get the camera projection coordinates of LED.

    Args:
        render_folder_path (str): The folder path to render the frame to.
        frame_index (int): The frame index to render.
        camera_object (bpy.types.Object): The camera object.
        camera (bpy.types.Camera): The camera.
        stylus (bpy.types.Object): The stylus object.
        leds (List[bpy.types.Object]): The LED objects.
        armature_suffix (str): The suffix of the armature.
        random_background_image_generator (RandomBackgroundImageGenerator): The random background image generator.

    Returns:
        dict: The frame data.
    """
    # Set camera and frame index for Blender
    bpy.context.scene.camera = camera_object
    bpy.context.scene.frame_set(frame_index)

    render_bg_frame(
        render_folder_path,
        frame_index,
    )

    render_no_bg_frame(
        render_folder_path,
        frame_index,
        armature_suffix,
        random_background_image_generator,
    )

    frame_data = get_frame_data(
        camera_object,
        camera,
        stylus,
        leds,
        armature_suffix,
    )

    return frame_data


def get_main_objects(
    armature_suffix: str,
) -> Tuple[
    bpy.types.Object, bpy.types.Camera, bpy.types.Object, List[bpy.types.Object]
]:
    """
    Get the main objects of the scene.

    Args:
        armature_suffix (str): The suffix of the armature.

    Raises:
        ValueError: If the camera is not found.
        ValueError: If the camera object is not found.
        ValueError: If the stylus is not found.
        ValueError: If no LED is found.

    Returns:
        bpy.types.Object: The camera object.
        bpy.types.Camera: The camera.
        bpy.types.Object: The stylus object.
        List[bpy.types.Object]: The LED objects.
    """
    camera_object = bpy.data.objects.get(CAMERA_NAME)
    if camera_object is None:
        raise ValueError("❌ Camera object not found.")

    camera = bpy.data.cameras.get(CAMERA_NAME)
    if camera is None:
        raise ValueError("❌ Camera not found.")

    stylus = bpy.data.objects.get(f"Stylus{armature_suffix}")
    if stylus is None:
        raise ValueError("❌ Stylus not found.")

    leds = [obj for obj in bpy.data.objects if "LED" in obj.name]
    if len(leds) == 0:
        raise ValueError("❌ No LED found.")
    print(f"➡️  Found {len(leds)} LEDs.")

    return camera_object, camera, stylus, leds


def get_render_subfolder() -> str:
    """
    Get the render subfolder path, and create it.

    Returns:
        str: The render subfolder path.
    """
    render_folder_path = RENDER_FOLDER_PATH
    render_subfolder_path = 1
    while os.path.exists(os.path.join(render_folder_path, str(render_subfolder_path))):
        render_subfolder_path += 1
    render_folder_path = os.path.join(render_folder_path, str(render_subfolder_path))
    os.makedirs(render_folder_path, exist_ok=True)
    print(f"➡️  Rendering to {os.path.abspath(render_folder_path)}.")

    return render_folder_path


def render(
    armature_suffix: str,
    random_background_image_generator: RandomBackgroundImageGenerator,
) -> None:
    """
    Render the animation and collect data.

    Raises:
        ValueError: If the camera is not found.
        ValueError: If the stylus is not found.
    """
    # Get objects
    camera_object, camera, stylus, leds = get_main_objects(armature_suffix)

    # Get render folder path
    render_folder_path = get_render_subfolder()

    data = {}
    for frame in tqdm(
        range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1),
        desc="🔄 Rendering frames...",
    ):
        data[frame] = render_and_get_frame_data(
            render_folder_path,
            frame,
            camera_object,
            camera,
            stylus,
            leds,
            armature_suffix,
            random_background_image_generator,
        )

    # Write data to JSON file
    print("⏳ Writing data to JSON file...")
    output_file_path = os.path.join(render_folder_path, "data.json")
    with open(output_file_path, "w") as f:
        json.dump(data, f, indent=4)
