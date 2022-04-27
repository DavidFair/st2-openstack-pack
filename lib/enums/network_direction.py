from enum import auto
from enums.auto_name import _AutoName


# pylint: disable=too-few-public-methods
class NetworkDirection(_AutoName):
    EGRESS = auto()
    INGRESS = auto()
