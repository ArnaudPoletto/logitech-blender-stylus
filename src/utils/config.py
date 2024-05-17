import os
import numpy as np

wrk_dir = os.getcwd()
DATA_PATH = os.path.join(wrk_dir, "..", "data")
INPUTS_FOLDER = os.path.join(DATA_PATH, "inputs")
RENDER_FOLDER_PATH = os.path.join(DATA_PATH, "renders")

SEED = None
if SEED is None:
    SEED = np.random.randint(0, 2**32 - 1, dtype=np.uint32)
    print(f"Running with random seed: {SEED}.")

CAMERA_NAME = "Camera"
ARMATURE_NAME = "Armature"
BACKGROUND_COLLECTION_NAME = "Background"

CAMERA_TYPE = "PERSP"
CAMERA_FOCAL_LENGTH = 25
CAMERA_FOV_DEGREES = 110 # Not used for PERSP

FRAME_RATE = 24
RESOLUTION_DIGITS = 2
RENDER_RESOLUTION = (640, 480) # (640, 480) # (3840, 2160)
GROUND_TRUTH_WITH_ARM_MODEL = True # Whether to render the ground truth with the arm model hiding the LEDS, but without reflections on the arm
HIDE_ARMATURE_PROBABILITY = 0.5
ANIMATION_LENGTH = 100
BACKGROUND_COLOR_SKEW_FACTOR = 1.5

MIN_PRIORITY = np.iinfo(np.int32).max
MAX_PRIORITY = 0