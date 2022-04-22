from enum import auto
from enums.auto_name import _AutoName


class NetworkDirection(_AutoName):
    EGRESS = auto()
    INGRESS = auto()
