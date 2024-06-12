import os
import bpy
import math
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
from src.utils import (
    RENDER_FOLDER_PATH,
    CAMERA_NAME,
    CAMERA_TYPE,
    BACKGROUND_COLLECTION_NAME,
    RENDER_RESOLUTION,
    GROUND_TRUTH_WITH_ARM_MODEL,
)


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


def _get_object_bbox(object) -> list:
    """
    Get the bounding box of an object.

    Args:
        object: The object to get the bounding box of.

    Returns:
        The bounding box of the object.
    """
    bbox = []
    for i in range(8):
        bbox.append(object.matrix_world @ Vector(object.bound_box[i]))

    return bbox


def _is_led_occluded(led, camera_object, leds, armature_arm, distance_eps: float = 1e-3) -> bool:
    """
    Check if an LED is occluded by any object between the camera and the LED.

    Args:
        camera_object: The camera object.
        leds: The LEDs object.
        armature_arm: The armature arm object.
        distance_eps: The distance epsilon to cast the ray.

    Returns:
        True if the LED is occluded, False otherwise.
    """
    # Get the direction from the camera to the LED
    led_locations = _get_object_bbox(led)
    is_led_occluded = True
    for led_location in led_locations:
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

        # Add stylus outer back to the scene
        for l in leds:
            l.hide_set(False)

        if not result[0]:
            is_led_occluded = False
            break

    return is_led_occluded


def _is_led_in_frame(led, camera_object) -> bool:
    """
    Check if an LED is in the camera frame.

    Args:
        camera_object: The camera object.
        led: The LED object.

    Returns:
        True if the LED is in the frame, False otherwise.
    """
    led_center = get_object_center(led)
    led_projected_coordinates = world_to_camera_view(
        bpy.context.scene, camera_object, led_center
    )

    return (
        0 <= led_projected_coordinates.x <= 1 and 0 <= led_projected_coordinates.y <= 1
    )


def _get_relative_orientation(
    object: bpy.types.Object, object_vector: Vector, camera_object: bpy.types.Object
) -> float:
    """
    Get the relative orientation of the stylus to the camera.

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

# TODO: documentation
def _get_projected_coordinates_perspective(led_center, camera_object) -> Vector:
    scene = bpy.context.scene
    return world_to_camera_view(
        scene, camera_object, led_center
    )

def _get_projected_coordinates_panoramic(led_center, camera, camera_object) -> Vector:
    # TODO from https://blender.stackexchange.com/questions/40702/how-can-i-get-the-projection-matrix-of-a-panoramic-camera-with-a-fisheye-equisol
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
    l = (led_center.x ** 2 + led_center.y ** 2) ** 0.5
    theta = math.asin(l)
    
    # Equisolid projection
    r = 2.0 * f * math.sin(theta / 2.0)
    u = r * math.cos(phi) / w + 0.5
    v = r * math.sin(phi) / h + 0.5
    
    return Vector((u, v))

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
def _render_and_get_frame_info(
    render_folder_path,
    frame,
    camera_object,
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
        camera_object: The camera object to render from.
        camera: The camera.
        sylus: The stylus object.
        leds: The LED objects to get the 3D object center of.
        armature_suffix: The suffix of the armature.
        random_background_image_generator: The random background image generator.

    Returns:
        The 3D object center in the frame.
    """
    # Camera
    bpy.context.scene.camera = camera_object

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
    stylus_relative_orientation = _get_relative_orientation(
        stylus, Vector((1, 0, 0)), camera_object
    )
    for led in leds:
        led_center = get_object_center(led)
        # TODO: as enum type, and get projected coordinates in camera class
        if CAMERA_TYPE == "PERSP":
            led_projected_coordinates = _get_projected_coordinates_perspective(led_center, camera_object)
        elif CAMERA_TYPE == "PANO":
            led_projected_coordinates = _get_projected_coordinates_panoramic(led_center, camera, camera_object)
        else:
            raise ValueError(f"Camera type {CAMERA_TYPE} not supported.")
        is_occluded = _is_led_occluded(led, camera_object, leds, armature_arm)
        is_in_frame = _is_led_in_frame(led, camera_object)
        distance_from_camera = (camera_object.location - led_center).length
        led_relative_orientation = _get_relative_orientation(
            led, Vector((0, 0, 1)), camera_object
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
        ValueError: If the camera is not found.
        ValueError: If the stylus is not found.
    """
    camera_object = bpy.data.objects.get(CAMERA_NAME)
    if camera_object is None:
        raise ValueError("Camera object not found.")
    
    camera = bpy.data.cameras.get(CAMERA_NAME)
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
        data[frame] = _render_and_get_frame_info(
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
    output_file_path = os.path.join(render_folder_path, "data.json")
    with open(output_file_path, "w") as f:
        json.dump(data, f, indent=4)
