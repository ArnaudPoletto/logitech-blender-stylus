import bpy
import json
from mathutils import Vector, Euler

from utils.axis import Axis
from utils.bone import Bone
from blender_objects.wall import Wall
from blender_objects.room import Room
from blender_objects.blinds import Blinds
from blender_objects.shades import Shades
from blender_objects.window import Window
from blender_objects.muntins import Muntins
from gestures.rotation_gesture import RotationGesture
from blender_objects.christmas_tree import ChristmasTree
from gestures.translation_gesture import TranslationGesture
from gestures.rotation_sine_gesture import RotationSineGesture
from gestures.rotation_wave_gesture import RotationWaveGesture
from gestures.translation_sine_gesture import TranslationSineGesture

# TODO: refactor code repetition
# TODO: add fail cases for missing keys


class InputFileParser:
    """
    An input file parser that reads an input JSON file and parses the data into a format that can be used by the program.
    """

    def __init__(
        self,
        input_file_path: str,
    ) -> None:
        """
        Initialize the input file parser.
        """
        self.input_file_path = input_file_path

    def _parse_gestures(self, input_data: dict, armature: bpy.types.Object) -> dict:
        """
        Parse the gestures data from the input file.

        Args:
            input_data (dict): The input data.
            armature (bpy.types.Object): The armature object.

        Returns:
            dict: The parsed gestures data.

        Raises:
            ValueError: If no gestures are found in the input file.
        """
        if "gestures" not in input_data:
            raise ValueError("No gestures found in the input file.")
        gestures = input_data["gestures"]

        # Reformat gestures
        gestures = [
            (globals()[gesture["type"]], gesture["args"]) for gesture in gestures
        ]

        for _, gesture_args in gestures:
            if "axis" in gesture_args:
                axis_name = gesture_args["axis"]
                if axis_name not in Axis.__members__:
                    raise ValueError(f"Axis {axis_name} not found.")

                gesture_args["axis"] = Axis(axis_name)

            if "vector" in gesture_args:
                x = gesture_args["vector"]["x"]
                y = gesture_args["vector"]["y"]
                z = gesture_args["vector"]["z"]
                gesture_args["vector"] = Vector((x, y, z))

            if "euler" in gesture_args:
                x = gesture_args["euler"]["x"]
                y = gesture_args["euler"]["y"]
                z = gesture_args["euler"]["z"]
                gesture_args["euler"] = Euler((x, y, z))

            if "bone" in gesture_args:
                bone_name = gesture_args["bone"]
                if bone_name not in Bone.__members__:
                    raise ValueError(f"Bone {bone_name} not found.")

                bone = armature.pose.bones.get(bone_name)
                gesture_args["bone"] = bone

        return gestures

    def _parse_blender_objects(self, input_data: dict) -> dict:
        """
        Parse the blender objects data from the input file.

        Args:
            input_data (dict): The input file.

        Returns:
            dict: The parsed blender objects data.
            
        Raises:
            ValueError: If no blender_objects is found in the input file.
        """
        if "blender_objects" not in input_data:
            raise ValueError("No blender_objects found in the input file.")
        blender_objects = input_data["blender_objects"]
        
        background_data = {}
        for blender_object_name, blender_object in blender_objects.items():
            # Get object information
            blender_object_type = globals()[blender_object["type"]]
            blender_object_args = blender_object["args"]
            
            if "location" in blender_object_args:
                x = blender_object_args["location"]["x"]
                y = blender_object_args["location"]["y"]
                if "z" in blender_object_args["location"]:
                    z = blender_object_args["location"]["z"]
                    blender_object_args["location"] = Vector((x, y, z))
                else:
                    blender_object_args["location"] = Vector((x, y))
            if "scale" in blender_object_args:
                x = blender_object_args["scale"]["x"]
                y = blender_object_args["scale"]["y"]
                if "z" in blender_object_args["scale"]:
                    z = blender_object_args["scale"]["z"]
                    blender_object_args["scale"] = Vector((x, y, z))
                else:
                    blender_object_args["scale"] = Vector((x, y))
            
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
                    blender_object_parent_object = background_data[blender_object_parent]["object"]
                    new_blender_object_parents.append(blender_object_parent_object)
                else:
                    # To access an object as a parameter of another object, we need to traverse the object attributes...
                    blender_object_parent_name = blender_object_parent_split[0]
                    blender_object_parent_parameters = blender_object_parent_split[1:]
                    blender_object_parent_object = background_data[blender_object_parent_name]["object"]
                    for blender_object_parent_parameter in blender_object_parent_parameters:
                        blender_object_parent_object = getattr(blender_object_parent_object, blender_object_parent_parameter)
                    new_blender_object_parents.append(blender_object_parent_object)
            background_data[blender_object_name]["parents"] = new_blender_object_parents
            
        return background_data

    def parse(self, armature: bpy.types.Object) -> dict:
        """
        Parse the input file.

        Args:
            armature (bpy.types.Object): The armature object.

        Returns:
            dict: The parsed data as a dictionary of the form {"gestures": gestures_data, "blender_objects": blender_objects_data}.
        """
        with open(self.input_file_path, "r") as input_file:
            input_data = json.load(input_file)
            gestures_data = self._parse_gestures(input_data, armature)
            blender_objects_data = self._parse_blender_objects(input_data)

        return {
            "gestures": gestures_data,
            "blender_objects": blender_objects_data,
        }
