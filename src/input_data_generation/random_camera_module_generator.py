import math
import random
from typing import Tuple
from mathutils import Vector

from utils.seed import set_seed
from input_data_generation.module_generator import ModuleGenerator
from input_data_generation.module_generator_type import ModuleGeneratorType


class RandomCameraModuleGenerator(ModuleGenerator):
    """
    A random camera module generator, linked to an input data generator to generate random comera data.
    """
    def __init__(
        self,
        name: str,
        id: str,
        xy_distance_range: Tuple[float, float],
        z_distance_range: Tuple[float, float],
        fixation_point_range: float,
        ) -> None:
        """
        Initialize the random camera module generator.
        
        Args:
            name (str): The name of the random camera module generator.
            id (str): The id of the random camera module generator.
            xy_distance_range (Tuple[float, float]): The range of the xy distance of the camera from the origin.
            z_distance_range (Tuple[float, float]): The range of the z distance of the camera from the origin.
            fixation_point_range (float): The range of the distance of the fixation point from the origin for each axis.
            
        Raises:
            ValueError: If the minimum xy distance is less than 0.
            ValueError: If the maximum xy distance is less than the minimum xy distance.
            ValueError: If the minimum z distance is less than 0.
            ValueError: If the maximum z distance is less than the minimum z distance.
        """
        if xy_distance_range[0] < 0:
            raise ValueError("The minimum xy distance must be greater than or equal to 0.")
        if xy_distance_range[1] < xy_distance_range[0]:
            raise ValueError("The maximum xy distance must be greater than or equal to the minimum xy distance.")
        if z_distance_range[0] < 0:
            raise ValueError("The minimum z distance must be greater than or equal to 0.")
        if z_distance_range[1] < z_distance_range[0]:
            raise ValueError("The maximum z distance must be greater than or equal to the minimum z distance.")
        
        super(RandomCameraModuleGenerator, self).__init__(
            weight=1,
            priority=0,
            type=ModuleGeneratorType.GLOBAL,
            name=name,
            id=id,
        )
        
        self.xy_distance_range = xy_distance_range
        self.z_distance_range = z_distance_range
        self.fixation_point_range = fixation_point_range
        
    def generate(
        self,
        wall_scales_per_wall: dict = None,
        existing_objects_per_wall: dict = None,
    ) -> Tuple[dict, dict]:
        set_seed()
        
        # Generate random camera data as polar coordinates
        xy_distance = random.uniform(*self.xy_distance_range)
        z_distance = random.uniform(*self.z_distance_range)
        alpha = random.uniform(0, 2 * math.pi)
        
        # Convert polar coordinates to cartesian coordinates
        x = xy_distance * math.cos(alpha)
        y = xy_distance * math.sin(alpha)
        z = z_distance 
        
        # Get fixation point and rotation needed to look at the fixation point
        fixation_point = Vector((
            random.uniform(-self.fixation_point_range, self.fixation_point_range),
            random.uniform(-self.fixation_point_range, self.fixation_point_range),
            random.uniform(-self.fixation_point_range, self.fixation_point_range),
        ))
        fixation_direction = Vector((x, y, z)) - fixation_point
        fixation_direction.normalize()
        rotation = fixation_direction.to_track_quat("Z", "Y").to_euler()
        
        # Generate camera data
        camera_data = {
            "blender_objects": {
                self.id: {
                    "type": "Camera",
                    "args": {
                        "name": self.name,
                        "location": {
                            "x": x,
                            "y": y,
                            "z": z,
                        },
                        "rotation": {
                            "x": rotation.x,
                            "y": rotation.y,
                            "z": rotation.z,
                        }
                    }
                }
            }
        }
        
        return camera_data, existing_objects_per_wall
            
            
            