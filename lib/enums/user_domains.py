from enum import auto

from enums.auto_name import _AutoName


# pylint: disable=too-few-public-methods
class UserDomains(_AutoName):
    """
    Holds a list of domains where users can be found
    """

    DEFAULT = auto()
    STFC = auto()

    @staticmethod
    def from_string(val: str):
        return UserDomains[val.upper()]
