from unittest.mock import create_autospec, NonCallableMock

from enums.network_providers import NetworkProviders
from enums.rbac_network_actions import RbacNetworkActions
from openstack_network import OpenstackNetwork
from src.network_actions import NetworkActions
from tests.openstack_action_test_case import OpenstackActionTestCase


class TestNetworkActions(OpenstackActionTestCase):
    """
    Unit tests for the Network.* actions
    """

    action_cls = NetworkActions

    def setUp(self):
        super().setUp()
        self.network_mock = create_autospec(OpenstackNetwork)
        self.action: NetworkActions = self.get_action_instance(
            api_mock=self.network_mock
        )

    def test_find_network_found(self):
        returned = self.action.network_find(NonCallableMock(), NonCallableMock())
        expected = self.network_mock.find_network.return_value
        assert returned == (True, expected)

    def test_find_network_not_found(self):
        self.network_mock.find_network.return_value = None
        returned = self.action.network_find(NonCallableMock(), NonCallableMock())
        assert returned[0] is False
        assert "could not be found" in returned[1]

    def test_find_rbac_found(self):
        returned = self.action.network_rbac_find(NonCallableMock(), NonCallableMock())
        expected = self.network_mock.find_network_rbac.return_value
        assert returned == (True, expected)

    def test_find_rbac_not_found(self):
        self.network_mock.find_network_rbac.return_value = None
        returned = self.action.network_rbac_find(NonCallableMock(), NonCallableMock())
        assert returned[0] is False
        assert "could not be found" in returned[1]

    def test_create_network_failed(self):
        self.network_mock.create_network.return_value = None
        returned = self.action.network_create(
            cloud_account=NonCallableMock(),
            project_identifier=NonCallableMock(),
            network_name=NonCallableMock(),
            network_description=NonCallableMock(),
            provider_network_type=NetworkProviders.VXLAN.value,
            port_security_enabled=NonCallableMock(),
            has_external_router=NonCallableMock(),
        )

        assert returned == (False, None)

    def test_create_network_successful(self):
        returned = self.action.network_create(
            cloud_account=NonCallableMock(),
            project_identifier=NonCallableMock(),
            network_name=NonCallableMock(),
            network_description=NonCallableMock(),
            provider_network_type=NetworkProviders.VXLAN.value,
            port_security_enabled=NonCallableMock(),
            has_external_router=NonCallableMock(),
        )

        expected = self.network_mock.create_network.return_value
        assert returned == (True, expected)

    def test_create_rbac_successful(self):
        for action in ["external", "shared"]:
            returned = self.action.network_rbac_create(
                NonCallableMock(), NonCallableMock(), NonCallableMock(), action
            )
            expected = self.network_mock.create_network_rbac.return_value
            assert returned == (True, expected)

    def test_create_rbac_failed(self):
        self.network_mock.create_network_rbac.return_value = None
        returned = self.action.network_rbac_create(
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
            RbacNetworkActions.SHARED.value,
        )
        assert returned == (False, None)

    def test_delete_network_success(self):
        self.network_mock.delete_network.return_value = True
        returned = self.action.network_delete(NonCallableMock(), NonCallableMock())
        assert returned == (True, "")

    def test_delete_network_failed(self):
        self.network_mock.delete_network.return_value = False
        returned = self.action.network_delete(NonCallableMock(), NonCallableMock())
        assert returned[0] is False
        assert "could not be found" in returned[1]

    def test_run_method(self):
        expected_methods = [
            "network_find",
            "network_rbac_find",
            "network_create",
            "network_rbac_create",
            "network_delete",
            "network_rbac_delete",
        ]
        self._test_run_dynamic_dispatch(expected_methods)
