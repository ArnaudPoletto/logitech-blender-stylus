import os
import numpy as np

wrk_dir = os.getcwd()
INPUTS_FOLDER = os.path.join(wrk_dir, "..", "data", "inputs")
RENDER_FOLDER_PATH = os.path.join(wrk_dir, "..", "data", "images")

CAMERA_NAME = "Camera"
STYLUS_OUTER_NAME = "Outer"
ARMATURE_NAME = "Armature"
BACKGROUND_COLLECTION_NAME = "Background"

SEED = None

DEFAULT_N_SCENES = 1

FRAME_RATE = 60
RESOLUTION_DIGITS = 2
RENDER_RESOLUTION = (640, 480) # (3840, 2160)
GROUND_TRUTH_WITH_ARM_MODEL = True # Whether to render the ground truth with the arm model hiding the LEDS, but without reflections on the arm
HIDE_ARMATURE_PROBABILITY = 0.5

MIN_PRIORITY = np.iinfo(np.int32).max
MAX_PRIORITY = 0