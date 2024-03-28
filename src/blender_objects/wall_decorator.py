from mathutils import Vector

from blender_objects.blender_object import BlenderObject


class WallDecorator(BlenderObject):
    """
    A wall decorator of a wall.
    """

    def __init__(
        self,
        name: str,
        location: Vector,
    ) -> None:
        """
        Initialize the wall decorator.

        Args:
            name (str): The name of the wall decorator.
            location (Vector): The location of the wall decorator, generally the center of the window.
        """
        super(WallDecorator, self).__init__(name=name, location=location)
