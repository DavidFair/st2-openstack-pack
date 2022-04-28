import unittest
from unittest.mock import patch, MagicMock

from openstack_api.openstack_roles import OpenstackRoles


class OpenstackSecurityGroupsTests(unittest.TestCase):
    def setUp(self) -> None:
        """
        Sets up the various mocks required in this test
        """
        super().setUp()
        self.mocked_connection = MagicMock()
        with patch(
            "openstack_api.openstack_security_groups.OpenstackIdentity"
        ) as identity_mock:
            self.instance = OpenstackRoles(self.mocked_connection)
            self.identity_module = identity_mock.return_value

        self.role_api = self.mocked_connection.return_value.__enter__.return_value.role
