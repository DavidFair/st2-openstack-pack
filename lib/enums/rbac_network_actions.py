from enum import Enum, auto


class _AutoName(Enum):
    """
    Generates values matching the original key
    """

    @staticmethod
    def _generate_next_value_(name: str, *args, **kwargs):
        return name


class RbacNetworkActions(_AutoName):
    """
    Holds the list of support RBAC network actions
    """

    EXTERNAL = auto()
    SHARED = auto()
