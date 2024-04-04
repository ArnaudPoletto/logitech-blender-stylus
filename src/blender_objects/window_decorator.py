from mathutils import Vector

from blender_objects.relative_blender_object import RelativeBlenderObject


class WindowDecorator(RelativeBlenderObject):
    """
    A window decorator of a window.
    """

    def __init__(
        self,
        name: str,
    ) -> None:
        """
        Initialize the window decorator.

        Args:
            name (str): The name of the window decorator.
            location (Vector): The relative location of the window decorator from the location of the window as a 2D vector.
        """
        relative_location = Vector((0, 0, 0)) # The location of window decorators is always relative to the window.
        super(WindowDecorator, self).__init__(name=name, relative_location=relative_location)
