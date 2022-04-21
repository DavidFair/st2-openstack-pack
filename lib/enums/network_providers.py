from enum import auto

from enums.auto_name import _AutoName


# pylint: disable=too-few-public-methods
class NetworkProviders(_AutoName):
    VXLAN = auto()
