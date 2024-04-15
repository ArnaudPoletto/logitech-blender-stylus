import os
import numpy as np

wrk_dir = os.getcwd()
INPUTS_FOLDER = os.path.join(wrk_dir, "..", "data", "inputs")
OUTPUT_FILE = os.path.join(wrk_dir, "..", "data", "output.json")
RENDER_FOLDER_PATH = os.path.join(wrk_dir, "..", "data", "images")

CAMERA_NAME = "Camera"
STYLUS_OUTER_NAME = "Outer"
ARMATURE_NAME = "Armature"

SEED = 10

FRAME_RATE = 60
RESOLUTION_DIGITS = 2

MIN_PRIORITY = np.iinfo(np.int32).max
MAX_PRIORITY = 0
RENDER_RESOLUTION = (3840, 2160)