import os

wrk_dir = os.getcwd()
INPUTS_FOLDER = os.path.join(wrk_dir, "..", "data", "inputs")
OUTPUT_FILE = os.path.join(wrk_dir, "..", "data", "output.json")
RENDER_FOLDER_PATH = os.path.join(wrk_dir, "..", "data", "images")

CAMERA_NAME = "Camera"
STYLUS_OUTER_NAME = "Outer"
ARMATURE_NAME = "Armature"

SEED = None
FRAME_RATE = 60
RESOLUTION_DIGITS = 2