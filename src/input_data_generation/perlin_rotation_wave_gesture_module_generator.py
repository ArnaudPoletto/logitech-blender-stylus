import numpy as np
from typing import Tuple

from utils.axis import Axis
from utils.seed import set_seed
from config.config import FRAME_RATE
from input_data_generation.module_generator import ModuleGenerator
from input_data_generation.module_generator_type import ModuleGeneratorType


class PerlinRotationWaveGestureModuleGenerator(ModuleGenerator):
    """
    A perlin rotation wave gesture module generator, linked to an input data generator to generate perlin rotation wave gesture data.
    """
    def __init__(
        self,
        id: str,
        start_frame: int,
        end_frame: int,
        period_range: Tuple[float, float],
        amplitude_range: Tuple[float, float],
        persistance: float,
        n_octaves_range: Tuple[int, int],
    ) -> None:
        """
        Initialize the perlin rotation wave gesture module generator.
        
        Args:
            id (str): The id of the module.
            start_frame (int): The start frame.
            end_frame (int): The end frame.
            period_range (Tuple[float, float]): The range of the period of the noise function.
            amplitude_range (Tuple[float, float]): The range of the amplitude of the noise function.
            persistance (float): The persistance of the perlin noise.
            n_octaves_range (Tuple[int, int]): The range of the number of octaves.
            
        Raises:
            ValueError: If the start frame is less than 0.
            ValueError: If the end frame is less than the start frame.
            ValueError: If the minimum period is greater than the maximum period.
            ValueError: If the minimum amplitude is greater than the maximum amplitude.
            ValueError: If the persistance is less than 0.
            ValueError: If the persistance is greater than 1.
            ValueError: If the minimum number of octaves is less than 1.
            ValueError: If the minimum number of octaves is greater than the maximum number of octaves.
        """
        if start_frame < 0:
            raise ValueError("The start frame must be greater than or equal to 0.")
        if end_frame < start_frame:
            raise ValueError("The end frame must be greater than or equal to the start frame.")
        if period_range[1] < period_range[0]:
            raise ValueError("The minimum period must be less than or equal to the maximum period.")
        if amplitude_range[1] < amplitude_range[0]:
            raise ValueError("The minimum amplitude must be less than or equal to the maximum amplitude.")
        if persistance < 0:
            raise ValueError("The persistance must be greater than or equal to 0.")
        if persistance > 1:
            raise ValueError("The persistance must be less than or equal to 1.")
        if n_octaves_range[0] < 1:
            raise ValueError("The number of octaves must be greater than or equal to 1.")
        if n_octaves_range[1] < n_octaves_range[0]:
            raise ValueError("The minimum number of octaves must be less than or equal to the maximum number of octaves.")
        
        super(PerlinRotationWaveGestureModuleGenerator, self).__init__(
            type=ModuleGeneratorType.GESTURE,
            name=None,
            id=id,
        )
        
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.period_range = period_range
        self.amplitude_range = amplitude_range
        self.persistance = persistance
        self.n_octaves_range = n_octaves_range

    def generate(
        self,
        wall_scales_per_wall: dict = None,
        existing_objects_per_wall: dict = None,
    ) -> dict:
        set_seed()
        
        perlin_data = {"gestures": {}}
        for axis in Axis.__members__.values():
            axis = axis.value
            n_octaves = np.random.randint(*self.n_octaves_range)
            for octave in range(n_octaves):
                period = np.random.uniform(*self.period_range)
                amplitude = np.random.uniform(*self.amplitude_range)
                wave_period = (2 ** octave) * period
                amplitude = (self.persistance ** octave) * amplitude
                perlin_data["gestures"][f"{self.id}_{axis}_{octave}"] = {
                    "type": "RotationWaveGesture",
                    "args": {
                        "start_frame": self.start_frame,
                        "end_frame": self.end_frame,
                        "frame_rate": FRAME_RATE,
                        "axis": axis,
                        "wave_period": wave_period,
                        "wave_amplitude": amplitude,
                        "arm_phase_shift": 0, # TODO: change
                        "forearm_phase_shift": 0, # TODO: change
                        "forearm_amplitude_factor": 0.5, # TODO: change
                        "hand_phase_shift": 0, # TODO: change
                        "hand_amplitude_factor": 0.5, # TODO: change
                    }
                }
            
        return perlin_data, existing_objects_per_wall
