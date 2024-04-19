import os
import bpy
import json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

CAMERA_NAME = "Camera"
FRAME_STEP = 1
RENDER = False

RENDER_FOLDER_PATH = os.path.join(os.getcwd(), "data", "images")
JSON_FILE_PATH = os.path.join(os.getcwd(), "data", "data.json")


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


def render_and_get_frame_info(frame, camera, stylus_outer, leds) -> dict:
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
    if RENDER:
        bpy.data.scenes["Scene"].render.filepath = os.path.join(
            RENDER_FOLDER_PATH, f"{frame:04d}.png"
        )
        bpy.ops.render.render(write_still=True)

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

    print(f"Frame {frame} complete...")

    return leds_data


if __name__ == "__main__":
    camera = bpy.data.objects[CAMERA_NAME]
    stylus_outer = bpy.data.objects[STYLUS_OUTER_NAME]
    leds = [obj for obj in bpy.data.objects if "LED" in obj.name]

    data = {}
    for frame in range(
        bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1, FRAME_STEP
    ):
        data[frame] = render_and_get_frame_info(frame, camera, stylus_outer, leds)

    # Write data to JSON file
    with open(JSON_FILE_PATH, "w") as f:
        json.dump(data, f, indent=4)

    print("Data collection complete!")
