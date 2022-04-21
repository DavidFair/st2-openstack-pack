import unittest
from typing import Callable
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

    @raises(MissingMandatoryParamError)
    def test_find_network_missing_identifier_raises(self):
        self.instance.find_network_rbac(NonCallableMock(), " \t")

    def test_find_network_forwards_results(self):
        cloud, identifier = NonCallableMock(), NonCallableMock()
        result = self.instance.find_network_rbac(cloud, identifier)

        self.mocked_connection.assert_called_once_with(cloud)
        self.network_api.find_rbac_policy.assert_called_once_with(
            identifier.strip(), ignore_missing=True
        )
        assert result == self.network_api.find_rbac_policy.return_value

    @raises(MissingMandatoryParamError)
    def test_create_network_no_name(self):
        mocked_details = NonCallableMock()
        mocked_details.name = " \t"
        self.instance.create_network(NonCallableMock(), mocked_details)

    @raises(ItemNotFoundError)
    def test_create_network_forwards_find_project(self):
        self._run_project_not_found_test(
            self.instance.create_network, NonCallableMock(), NonCallableMock()
        )

    def test_create_project_forwards_result(self):
        with patch("openstack_network.OpenstackIdentity") as patched_ident:
            cloud_account, details = NonCallableMock(), NonCallableMock()

            returned = self.instance.create_network(cloud_account, details)
            self.mocked_connection.assert_called_once_with(cloud_account)
            self.network_api.create_network(
                project_id=patched_ident.find_project.return_value,
                name=details.name,
                description=details.description,
                provider_network_type=details.provider_network_type,
                is_port_security_enabled=details.port_security_enabled,
                is_router_external=details.has_external_router,
            )
            assert returned == self.network_api.create_network.return_value

    @staticmethod
    def _run_project_not_found_test(method: Callable, *args, **kwargs):
        with patch("openstack_network.OpenstackIdentity") as patched_ident:
            patched_ident.find_project.return_value = None
            method(*args, **kwargs)

    @raises(ItemNotFoundError)
    def test_create_network_rbac_network_not_found(self):
        self.instance.find_network = Mock(return_value=None)
        self.instance.create_network_rbac(NonCallableMock(), NonCallableMock())

    @raises(ItemNotFoundError)
    def test_create_network_rbac_project_not_found(self):
        self._run_project_not_found_test(
            self.instance.create_network_rbac, NonCallableMock(), NonCallableMock()
        )

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

    def test_delete_network_forwards_find_network(self):
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
        self.instance.find_network = Mock(return_value=None)
        cloud, network_identifier = NonCallableMock(), NonCallableMock()
        result = self.instance.delete_network(cloud, network_identifier)

        assert result is False
        self.instance.find_network.assert_called_once_with(cloud, network_identifier)
        self.network_api.delete_network.assert_not_called()

    def test_delete_network_rbac_forwards_find_rbac(self):
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
        self.instance.find_network_rbac = Mock(return_value=None)
        cloud, network_identifier = NonCallableMock(), NonCallableMock()
        result = self.instance.delete_network_rbac(cloud, network_identifier)

        assert result is False
        self.instance.find_network_rbac.assert_called_once_with(
            cloud, network_identifier
        )
        self.network_api.delete_rbac_policy.assert_not_called()
