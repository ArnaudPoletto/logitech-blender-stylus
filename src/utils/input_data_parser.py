import bpy
import json
from mathutils import Vector, Euler

from utils.axis import Axis
from utils.bone import Bone
from blender_objects.sun import Sun
from blender_objects.wall import Wall
from blender_objects.room import Room
from blender_objects.table import Table
from blender_objects.blinds import Blinds
from blender_objects.shades import Shades
from blender_objects.camera import Camera
from blender_objects.window import Window
from blender_objects.muntins import Muntins
from blender_objects.wall_lamp import WallLamp
from gestures.rotation_gesture import RotationGesture
from blender_objects.christmas_tree import ChristmasTree
from gestures.translation_gesture import TranslationGesture
from gestures.rotation_sine_gesture import RotationSineGesture
from gestures.rotation_wave_gesture import RotationWaveGesture
from gestures.translation_sine_gesture import TranslationSineGesture


class InputDataParser:
    """
    An input data parser that parses the input data from a JSON dictionary.
    """

    def __init__(
        self,
        input_data: str,
    ) -> None:
        """
        Initialize the input data parser.
        """
        self.input_data = input_data

    @staticmethod
    def _parse_dimension_argument(args, arg_name, arg_type):
        """
        Parse a 2D or 3D dimension argument from the arguments dictionary.

        Args:
            args (dict): The arguments dictionary.
            arg_name (str): The name of the argument.
            arg_type (type): The type of the argument.

        Raises:
            ValueError: If the argument is not found in the arguments dictionary.
            ValueError: If the argument is not a dimension argument.
        """
        if arg_name not in args:
            raise ValueError(f"Argument {arg_name} not found in the arguments.")

        if "x" not in args[arg_name] or "y" not in args[arg_name]:
            raise ValueError(f"Argument {arg_name} is not a 2D or 3D argument.")

        x = args[arg_name]["x"]
        y = args[arg_name]["y"]

        if "z" not in args[arg_name]:
            return arg_type((x, y))

        z = args[arg_name]["z"]

        return arg_type((x, y, z))

    def _parse_gestures(self, input_data: dict, armature: bpy.types.Object) -> dict:
        """
        Parse the gestures data from the input data.

        Args:
            input_data (dict): The input data.
            armature (bpy.types.Object): The armature object.

        Returns:
            dict: The parsed gestures data.

        Raises:
            ValueError: If no gestures section are found in the input data.
            ValueError: If the gesture type of a gesture is not specified.
            ValueError: If the gesture args of a gesture is not specified.
            ValueError: If the gesture type of a gesture is not found.
            ValueError: If the axis of a gesture is invalid.
            ValueError: If the bone of a gesture is invalid.
        """
        if "gestures" not in input_data:
            raise ValueError("No gestures found in the input data.")
        gestures = input_data["gestures"]

        # Reformat gestures
        new_gestures = []
        for _, gesture_object in gestures.items():
            if "type" not in gesture_object:
                raise ValueError("No gesture type found in the input data.")

            if "args" not in gesture_object:
                raise ValueError("No gesture args found in the input data.")

            if gesture_object["type"] not in globals():
                raise ValueError(f"Gesture type {gesture_object['type']} not found.")

            gesture_type = globals()[gesture_object["type"]]
            gesture_args = gesture_object["args"]
            new_gestures.append((gesture_type, gesture_args))
        gestures = new_gestures

        for _, gesture_args in gestures:
            if "axis" in gesture_args:
                axis_name = gesture_args["axis"]
                if not Axis.is_valid_axis_string(axis_name):
                    raise ValueError(f"Axis {axis_name} not found.")

                gesture_args["axis"] = Axis(axis_name)

            if "vector" in gesture_args:
                gesture_args["vector"] = InputDataParser._parse_dimension_argument(
                    gesture_args, "vector", Vector
                )

            if "euler" in gesture_args:
                gesture_args["euler"] = InputDataParser._parse_dimension_argument(
                    gesture_args, "euler", Euler
                )

            if "bone" in gesture_args:
                bone_name = gesture_args["bone"]
                if bone_name not in Bone.__members__:
                    raise ValueError(f"Bone {bone_name} not found.")

                bone = armature.pose.bones.get(bone_name)
                gesture_args["bone"] = bone

        return gestures
    
    def _parse_blender_objects(self, input_data: dict) -> dict:
        """
        Parse the blender objects data from the input data.

        Args:
            input_data (dict): The input data.

        Returns:
            dict: The parsed blender objects data.

        Raises:
            ValueError: If no blender_objects section is found in the input daata.
            ValueError: If the blender object type is not specified.
            ValueError: If the blender object args are not specified.
            ValueError: If the blender object type is not found.
        """
        if "blender_objects" not in input_data:
            raise ValueError("No blender_objects found in the input dat.")
        blender_objects = input_data["blender_objects"]

        background_data = {}
        for blender_object_name, blender_object in blender_objects.items():
            if "type" not in blender_object:
                raise ValueError("No type found in the blender object.")

            if "args" not in blender_object:
                raise ValueError("No args found in the blender object.")

            if blender_object["type"] not in globals():
                raise ValueError(
                    f"Blender object type {blender_object['type']} not found."
                )

            # Get object information
            blender_object_type = globals()[blender_object["type"]]
            blender_object_args = blender_object["args"]
            
            mathutils_names = ["location", "relative_location", "scale", "rotation"]
            mathutils_types = [Vector, Vector, Vector, Euler]
            for mathutils_name, mathutils_type in zip(mathutils_names, mathutils_types):
                if mathutils_name in blender_object_args:
                    blender_object_args[mathutils_name] = (
                        InputDataParser._parse_dimension_argument(
                            blender_object_args, mathutils_name, mathutils_type
                        )
                    )

            # Get parents information
            blender_object_parents = None
            if "parents" in blender_object:
                blender_object_parents = blender_object["parents"]

            blender_object_data = {
                "object": blender_object_type(**blender_object_args),
                "parents": blender_object_parents,
            }
            background_data[blender_object_name] = blender_object_data

        # Traverse the background data to set the parents as objects
        for blender_object_name, blender_object_data in background_data.items():
            if blender_object_data["parents"] is None:
                continue

            blender_object_parents = blender_object_data["parents"]
            new_blender_object_parents = []
            for blender_object_parent in blender_object_parents:
                blender_object_parent_split = blender_object_parent.split(".")
                if len(blender_object_parent_split) == 1:
                    # If the parent is a direct object...
                    blender_object_parent_object = background_data[
                        blender_object_parent
                    ]["object"]
                    new_blender_object_parents.append(blender_object_parent_object)
                else:
                    # To access an object as a parameter of another object, we need to traverse the object attributes...
                    blender_object_parent_name = blender_object_parent_split[0]
                    blender_object_parent_parameters = blender_object_parent_split[1:]
                    blender_object_parent_object = background_data[
                        blender_object_parent_name
                    ]["object"]
                    for (
                        blender_object_parent_parameter
                    ) in blender_object_parent_parameters:
                        blender_object_parent_object = getattr(
                            blender_object_parent_object,
                            blender_object_parent_parameter,
                        )
                    new_blender_object_parents.append(blender_object_parent_object)
            background_data[blender_object_name]["parents"] = new_blender_object_parents

        return background_data

    def parse(self, armature: bpy.types.Object) -> dict:
        """
        Parse the input data.

        Args:
            armature (bpy.types.Object): The armature object.

        Returns:
            dict: The parsed data as a dictionary of the form {"gestures": gestures_data, "blender_objects": blender_objects_data}.
        """
        gestures_data = self._parse_gestures(self.input_data, armature)
        blender_objects_data = self._parse_blender_objects(self.input_data)

        return {
            "gestures": gestures_data,
            "blender_objects": blender_objects_data,
        }
