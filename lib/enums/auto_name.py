from enum import Enum


class _AutoName(Enum):
    """
    Generates values matching the original key
    """

    @staticmethod
    def _generate_next_value_(name: str, *_, **__):
        return name
