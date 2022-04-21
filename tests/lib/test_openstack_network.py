import unittest
from unittest.mock import NonCallableMock, patch, Mock, ANY

from nose.tools import raises

from enums.rbac_network_actions import RbacNetworkActions
from exceptions.item_not_found_error import ItemNotFoundError
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_network import OpenstackNetwork


class OpenstackNetworkTests(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.instance = OpenstackNetwork()
        connection_patch = patch("openstack_network.OpenstackConnection")
        self.mocked_connection = connection_patch.start()
        self.addCleanup(connection_patch.stop)
        self.network_api = (
            self.mocked_connection.return_value.__enter__.return_value.network
        )

    @raises(MissingMandatoryParamError)
    def test_find_network_raises_for_missing_param(self):
        """
        Tests that find network will raise if the identifier is missing
        """
        self.instance.find_network(NonCallableMock(), " ")

    def test_find_network_with_found_result(self):
        """
        Tests that find network returns the result as-is
        """
        cloud, identifier = NonCallableMock(), NonCallableMock()
        returned = self.instance.find_network(cloud, identifier)

        self.mocked_connection.assert_called_once_with(cloud)
        self.network_api.find_network.assert_called_once_with(
            identifier.strip(), ignore_missing=True
        )
        assert returned == self.network_api.find_network.return_value

    @raises(ItemNotFoundError)
    def test_create_network_rbac_network_not_found(self):
        self.instance.find_network = Mock(return_value=None)
        self.instance.create_network_rbac(NonCallableMock(), NonCallableMock())

    @raises(ItemNotFoundError)
    def test_create_network_rbac_project_not_found(self):
        with patch("openstack_network.OpenstackIdentity") as patched_ident:
            patched_ident.find_project.return_value = None
            self.instance.create_network_rbac(NonCallableMock(), NonCallableMock())

    def test_create_rbac_uses_found_project_and_network(self):
        with patch("openstack_network.OpenstackIdentity") as patched_ident:
            cloud, rbac_details = NonCallableMock(), NonCallableMock()
            self.instance.find_network = Mock()
            rbac_details.action = RbacNetworkActions.SHARED

            returned = self.instance.create_network_rbac(cloud, rbac_details)

            self.mocked_connection.assert_called_once_with(cloud)
            self.network_api.create_rbac_policy.assert_called_once_with(
                object_id=self.instance.find_network.return_value,
                target_project_id=patched_ident.find_project.return_value,
                action=ANY,
            )
            assert returned == self.network_api.create_rbac_policy.return_value

    def test_create_rbac_serialises_enum_correctly(self):
        expected_serialisation = {
            RbacNetworkActions.EXTERNAL: "access_as_external",
            RbacNetworkActions.SHARED: "access_as_shared",
        }

        for enum_val, expected_val in expected_serialisation.items():
            rbac_details = NonCallableMock()
            rbac_details.action = enum_val

            with patch("openstack_network.OpenstackIdentity"):
                self.instance.create_network_rbac(NonCallableMock(), rbac_details)
                self.network_api.create_rbac_policy.assert_called_once_with(
                    object_id=ANY, target_project_id=ANY, action=expected_val
                )
                self.network_api.create_rbac_policy.reset_mock()
