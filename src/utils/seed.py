import random
import numpy as np

from utils.config import SEED

def set_seed():
    """
    Set the seed for the random number generator.
    """
    random.seed(SEED)
    np.random.seed(SEED)