class ItemNotFoundError(LookupError):
    pass


class ProjectNotFoundError(ItemNotFoundError):
    """
    Generates a ProjectNotFoundError with a preset message.
    This is common enough to justify a unified wrapper
    """

    def __init__(self):
        """
        Presets a standard message for a project not being found
        """
        super().__init__("The specified project was not found")
