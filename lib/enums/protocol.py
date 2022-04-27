from enum import auto
from enums.auto_name import _AutoName


# pylint: disable=too-few-public-methods
class Protocol(_AutoName):
    TCP = auto()
    UDP = auto()
    ICMP = auto()
