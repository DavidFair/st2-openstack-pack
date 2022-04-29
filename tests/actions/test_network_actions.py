from unittest.mock import create_autospec, NonCallableMock

from enums.network_providers import NetworkProviders
from enums.rbac_network_actions import RbacNetworkActions
from openstack_api.openstack_network import OpenstackNetwork
from src.network_actions import NetworkActions
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestNetworkActions(OpenstackActionTestBase):
    """
    Unit tests for the Network.* actions
    """

    action_cls = NetworkActions

    # pylint: disable=invalid-name
    def setUp(self):
        """
        Prepares the mock API and injects it into a new instance
        """
        super().setUp()
        self.network_mock = create_autospec(OpenstackNetwork)
        self.action: NetworkActions = self.get_action_instance(
            api_mock=self.network_mock
        )

    def test_find_network_found(self):
        """
        Tests the action returns the found Network object
        """
        returned = self.action.network_find(NonCallableMock(), NonCallableMock())
        expected = self.network_mock.find_network.return_value
        assert returned == (True, expected)

    def test_find_network_not_found(self):
        """
        Tests the status and message when a network isn't found
        """
        self.network_mock.find_network.return_value = None
        returned = self.action.network_find(NonCallableMock(), NonCallableMock())
        assert returned[0] is False
        assert "could not be found" in returned[1]

    def test_find_rbac_forwards(self):
        """
        Tests the action returns the found RBACPolicy list as-is
        """
        returned = self.action.network_rbac_search(NonCallableMock(), NonCallableMock())
        expected = self.network_mock.search_network_rbacs.return_value
        assert returned == expected

    def test_create_network_failed(self):
        """
        Tests the status and message when a network failed to create
        """
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
        """
        Tests the action returns the new Network object
        """
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

    def test_create_network_mixed_case_enum(self):
        """
        Checks that regardless of case from Stackstorm the string
        can be converted to an enum type
        """
        returned = self.action.network_create(
            cloud_account=NonCallableMock(),
            project_identifier=NonCallableMock(),
            network_name=NonCallableMock(),
            network_description=NonCallableMock(),
            provider_network_type="vXLaN",
            port_security_enabled=NonCallableMock(),
            has_external_router=NonCallableMock(),
        )
        assert returned[0] is True

    def test_create_rbac_successful(self):
        """
        Tests the action returns the new RBAC policy
        """
        for action in ["external", "shared"]:
            returned = self.action.network_rbac_create(
                NonCallableMock(), NonCallableMock(), NonCallableMock(), action
            )
            expected = self.network_mock.create_network_rbac.return_value
            assert returned == (True, expected)

    def test_create_rbac_failed(self):
        """
        Tests the status and message when a RBAC can't be created
        """
        self.network_mock.create_network_rbac.return_value = None
        returned = self.action.network_rbac_create(
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
            RbacNetworkActions.SHARED.value,
        )
        assert returned == (False, None)

    def test_delete_network_success(self):
        """
        Tests the action returns success when a network is deleted
        """
        self.network_mock.delete_network.return_value = True
        returned = self.action.network_delete(NonCallableMock(), NonCallableMock())
        assert returned == (True, "")

    def test_delete_network_failed(self):
        """
        Tests the status and message when a network isn't deleted
        """
        self.network_mock.delete_network.return_value = False
        returned = self.action.network_delete(NonCallableMock(), NonCallableMock())
        assert returned[0] is False
        assert "could not be found" in returned[1]

    def test_delete_rbac_success(self):
        """
        Tests the action returns success when a RBAC policy is deleted
        """
        self.network_mock.delete_network_rbac.return_value = True
        returned = self.action.network_rbac_delete(NonCallableMock(), NonCallableMock())
        assert returned == (True, "")

    def test_delete_rbac_failed(self):
        """
        Tests the status and message when a policy isn't deleted
        """
        self.network_mock.delete_network_rbac.return_value = False
        returned = self.action.network_rbac_delete(NonCallableMock(), NonCallableMock())
        assert returned[0] is False
        assert "could not be found" in returned[1]

    def test_run_method(self):
        """
        Tests that run can dispatch to the Stackstorm facing methods
        """
        expected_methods = [
            "network_find",
            "network_rbac_search",
            "network_create",
            "network_rbac_create",
            "network_delete",
            "network_rbac_delete",
        ]
        self._test_run_dynamic_dispatch(expected_methods)
