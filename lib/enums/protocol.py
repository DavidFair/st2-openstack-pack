from enum import auto
from enums.auto_name import _AutoName


class Protocol(_AutoName):
    TCP = auto()
    UDP = auto()
    ICMP = auto()
