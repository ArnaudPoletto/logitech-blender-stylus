from mathutils import Vector

from blender_objects.blender_object import BlenderObject


class WindowDecorator(BlenderObject):
    """
    A window decorator of a window.
    """

    def __init__(
        self,
        name: str,
        location: Vector,
    ) -> None:
        """
        Initialize the window decorator.

        Args:
            name (str): The name of the window decorator.
            location (Vector): The location of the window decorator, generally the center of the window.
        """
        super(WindowDecorator, self).__init__(name=name, location=location)
