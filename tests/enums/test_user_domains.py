from parameterized import parameterized

from enums.user_domains import UserDomains


@parameterized(["stfc", "StFC", "STFC"])
def test_stfc_serialization(val):
    """
    Tests that variants of STFC can be serialized
    """
    assert UserDomains.from_string(val) is UserDomains.STFC


@parameterized(["default", "deFauLt", "DEFAULT"])
def test_default_serialization(val):
    """
    Tests that variants of DEFAULT can be serialized
    """
    assert UserDomains.from_string(val) is UserDomains.DEFAULT
