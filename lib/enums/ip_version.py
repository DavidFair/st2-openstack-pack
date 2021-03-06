from enum import auto
from enums.auto_name import _AutoName


# pylint: disable=too-few-public-methods
class IPVersion(_AutoName):
    IPV4 = auto()
    IPV6 = auto()
