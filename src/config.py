# This file contains the configuration parameters for the whole project.

import os
import numpy as np

wrk_dir = os.getcwd()
DATA_PATH = os.path.join(wrk_dir, "..", "data")
INPUTS_FOLDER = os.path.join(DATA_PATH, "inputs")
RENDER_FOLDER_PATH = os.path.join(DATA_PATH, "renders")

SEED = None
if SEED is None:
    SEED = int(np.random.randint(0, 2**32 - 1, dtype=np.uint32))
    print(f"✅ Running with random seed: {SEED}.")

ROOM_NAME = "Room"
ROOM_ID = "room"
CAMERA_NAME = "Camera"
CAMERA_ID = "camera"
ARMATURE_NAME = "Armature"
BACKGROUND_COLLECTION_NAME = "Background"

CAMERA_TYPE = "PERSP" # Either PERSP or PANO
CAMERA_FOCAL_LENGTH = 25 # Camera focal length parameter
CAMERA_FOV_DEGREES = 110 # Camera field of view parameter, not used for PERSP

FRAME_RATE = 24
RESOLUTION_DIGITS = 2 # Grid space resolution in the Blender scene, as an exponent of 10.
RENDER_RESOLUTION = (640, 480) # Is generally (640, 480), (1280, 720), (1920, 1080), or (3840, 2160)
GROUND_TRUTH_WITH_ARM_MODEL = True # Whether to render the ground truth with the arm model hiding the LEDS, but without reflections on the arm.
HIDE_ARMATURE_PROBABILITY = 0.75 # Probability of hiding the armature during rendering.
ANIMATION_LENGTH = 100
BACKGROUND_COLOR_SKEW_FACTOR = 1.5

MIN_PRIORITY = np.iinfo(np.int32).max
MAX_PRIORITY = 0