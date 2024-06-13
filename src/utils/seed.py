# This utility file is used to set the random seed for reproducibility.

import random
import numpy as np

from config.config import SEED

def set_seed() -> None:
    """
    Set the random seed for reproducibility.
    """
    random.seed(SEED)
    np.random.seed(SEED)