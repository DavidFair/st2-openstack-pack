from enum import auto

from enums.auto_name import _AutoName


# pylint: disable=too-few-public-methods
class RbacNetworkActions(_AutoName):
    """
    Holds the list of support RBAC network actions
    """

    EXTERNAL = auto()
    SHARED = auto()
