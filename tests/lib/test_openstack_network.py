import unittest
from typing import Callable
from unittest.mock import NonCallableMock, Mock, ANY, MagicMock

from nose.tools import raises

from enums.network_providers import NetworkProviders
from enums.rbac_network_actions import RbacNetworkActions
from exceptions.item_not_found_error import ItemNotFoundError
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_api.openstack_network import OpenstackNetwork


class OpenstackNetworkTests(unittest.TestCase):
    def setUp(self) -> None:
        """
        Sets up the various mocks required in this test
        """
        super().setUp()
        self.mocked_connection = MagicMock()
        self.instance = OpenstackNetwork(self.mocked_connection)
        self.identity_api = (
            self.mocked_connection.return_value.__enter__.return_value.identity
        )
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

    @raises(MissingMandatoryParamError)
    def test_find_network_missing_identifier_raises(self):
        """
        Tests that a missing network identifier raises an error
        """
        self.instance.find_network_rbac(NonCallableMock(), " \t")

    def test_find_network_forwards_results(self):
        """
        Tests that find network forwards its results as-is
        """
        cloud, identifier = NonCallableMock(), NonCallableMock()
        result = self.instance.find_network_rbac(cloud, identifier)

        self.mocked_connection.assert_called_once_with(cloud)
        self.network_api.find_rbac_policy.assert_called_once_with(
            identifier.strip(), ignore_missing=True
        )
        assert result == self.network_api.find_rbac_policy.return_value

    @raises(MissingMandatoryParamError)
    def test_create_network_no_name(self):
        """
        Tests that create network with no new network name throws
        """
        mocked_details = NonCallableMock()
        mocked_details.name = " \t"
        self.instance.create_network(NonCallableMock(), mocked_details)

    @raises(ItemNotFoundError)
    def test_create_network_when_no_found_project(self):
        """
        Tests that create network will raise if no project is found
        """
        self._run_project_not_found_test(
            self.instance.create_network, NonCallableMock(), NonCallableMock()
        )

    def test_create_network_serialises_enum(self):
        """
        Tests that the NetworkProviders enum gets serialised into
        Openstack compatible JSON
        """
        expected = {NetworkProviders.VXLAN: "vxlan"}

        for enum_key, expected_val in expected.items():
            mock_details = NonCallableMock()
            mock_details.provider_network_type = enum_key

            self.instance.create_network(NonCallableMock(), mock_details)
            self.network_api.create_network.assert_called_once_with(
                project_id=ANY,
                name=ANY,
                description=ANY,
                is_port_security_enabled=ANY,
                is_router_external=ANY,
                provider_network_type=expected_val,
            )

    def test_create_network_forwards_result(self):
        """
        Tests that create network will forward the result from Openstack
        """
        cloud_account, mock_details = NonCallableMock(), NonCallableMock()

        returned = self.instance.create_network(cloud_account, mock_details)
        self.mocked_connection.assert_called_with(cloud_account)
        self.network_api.create_network(
            project_id=self.identity_api.find_project.return_value.id,
            name=mock_details.name,
            description=mock_details.description,
            provider_network_type=mock_details.provider_network_type,
            is_port_security_enabled=mock_details.port_security_enabled,
            is_router_external=mock_details.has_external_router,
        )
        assert returned == self.network_api.create_network.return_value

    def _run_project_not_found_test(self, method: Callable, *args, **kwargs):
        """
        Test helper which emulates what happens if the project is not found
        from the identity API.
        :param method: The method (as a callable) to test
        :param args: Args to forward to the method
        :param kwargs: Kwargs to forward to the method
        """
        self.identity_api.find_project.return_value = None
        return method(*args, **kwargs)

    @raises(ItemNotFoundError)
    def test_create_network_rbac_network_not_found(self):
        """
        Tests that create RBAC (network) will throw if a network isn't found
        """
        self.instance.find_network = Mock(return_value=None)
        self.instance.create_network_rbac(NonCallableMock(), NonCallableMock())

    @raises(ItemNotFoundError)
    def test_create_network_rbac_project_not_found(self):
        """
        Tests that create RBAC (network) will throw if a project isn't found
        """
        self._run_project_not_found_test(
            self.instance.create_network_rbac, NonCallableMock(), NonCallableMock()
        )

    def test_create_rbac_uses_found_project_and_network(self):
        """
        Tests that create RBAC uses the project and network found instead
        of the user's input
        """
        cloud, rbac_details = NonCallableMock(), NonCallableMock()
        self.instance.find_network = Mock()
        rbac_details.action = RbacNetworkActions.SHARED

        returned = self.instance.create_network_rbac(cloud, rbac_details)

        self.mocked_connection.assert_called_with(cloud)
        self.network_api.create_rbac_policy.assert_called_once_with(
            object_id=self.instance.find_network.return_value.id,
            object_type="network",
            target_project_id=self.identity_api.find_project.return_value.id,
            action=ANY,
        )
        assert returned == self.network_api.create_rbac_policy.return_value

    @raises(KeyError)
    def test_create_rbac_unknown_key(self):
        """
        Tests a key error is thrown in an unknown var is passed to the serialisation logic
        """
        rbac_details = NonCallableMock()
        rbac_details.action = "unknown"
        self.instance.create_network_rbac(NonCallableMock(), rbac_details)

    def test_create_rbac_serialises_enum_correctly(self):
        """
        Tests that the RBAC access maps from the internal enum to the
        Openstack API string correctly
        """
        expected_serialisation = {
            RbacNetworkActions.EXTERNAL: "access_as_external",
            RbacNetworkActions.SHARED: "access_as_shared",
        }

        for enum_val, expected_val in expected_serialisation.items():
            rbac_details = NonCallableMock()
            rbac_details.action = enum_val

            self.instance.create_network_rbac(NonCallableMock(), rbac_details)
            self.network_api.create_rbac_policy.assert_called_once_with(
                object_id=ANY,
                object_type=ANY,
                target_project_id=ANY,
                action=expected_val,
            )
            self.network_api.create_rbac_policy.reset_mock()

    def test_delete_network_forwards_find_network(self):
        """
        Tests that delete network forwards the result from Openstack
        """
        self.instance.find_network = Mock()
        cloud, network_identifier = NonCallableMock(), NonCallableMock()
        self.network_api.delete_network.return_value = None
        result = self.instance.delete_network(cloud, network_identifier)

        self.instance.find_network.assert_called_once_with(cloud, network_identifier)
        self.network_api.delete_network.assert_called_once_with(
            self.instance.find_network.return_value, ignore_missing=False
        )
        assert result is True

    def test_delete_network_cant_find_network(self):
        """
        Tests that delete network returns false if it can't find the network to delete
        """
        self.instance.find_network = Mock(return_value=None)
        cloud, network_identifier = NonCallableMock(), NonCallableMock()
        result = self.instance.delete_network(cloud, network_identifier)

        assert result is False
        self.instance.find_network.assert_called_once_with(cloud, network_identifier)
        self.network_api.delete_network.assert_not_called()

    def test_delete_network_rbac_forwards_find_rbac(self):
        """
        Tests that delete RBAC policy forwards the result from Openstack
        """
        self.instance.find_network_rbac = Mock()
        cloud, network_identifier = NonCallableMock(), NonCallableMock()
        self.network_api.delete_rbac_policy.return_value = None
        result = self.instance.delete_network_rbac(cloud, network_identifier)

        self.instance.find_network_rbac.assert_called_once_with(
            cloud, network_identifier
        )
        self.network_api.delete_rbac_policy.assert_called_once_with(
            self.instance.find_network_rbac.return_value, ignore_missing=False
        )
        assert result is True

    def test_delete_network_rbac_cant_find_rbac(self):
        """
        Tests that delete RBAc returns false if it can't find the policy to delete
        """
        self.instance.find_network_rbac = Mock(return_value=None)
        cloud, network_identifier = NonCallableMock(), NonCallableMock()
        result = self.instance.delete_network_rbac(cloud, network_identifier)

        assert result is False
        self.instance.find_network_rbac.assert_called_once_with(
            cloud, network_identifier
        )
        self.network_api.delete_rbac_policy.assert_not_called()
