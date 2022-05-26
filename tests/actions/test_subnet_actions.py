from unittest.mock import create_autospec, NonCallableMock

from openstack_api.openstack_network import OpenstackNetwork
from src.subnet_actions import SubnetActions
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestSubnetActions(OpenstackActionTestBase):
    """
    Unit tests for the Subnet.* actions
    """

    action_cls = SubnetActions

    # pylint: disable=invalid-name
    def setUp(self):
        """
        Initialises the action and injects mocks required for testing
        """
        super().setUp()
        self.network_mock = create_autospec(OpenstackNetwork)
        self.action: SubnetActions = self.get_action_instance(
            api_mock=self.network_mock
        )

    def test_create_subnet(self):
        """
        Tests create subnet action forwards the args and returns as expected
        """
        cloud, network = NonCallableMock(), NonCallableMock()
        name, description = NonCallableMock(), NonCallableMock()
        dhcp = NonCallableMock()

        returned = self.action.subnet_create(cloud, network, name, description, dhcp)
        self.network_mock.create_subnet.assert_called_once_with(
            cloud, network, name, description, dhcp
        )
        assert returned == self.network_mock.create_subnet.return_value

    def test_run_dispatches_correctly(self):
        """
        Tests that run has the expected methods
        """
        expected_methods = ["subnet_create"]
        self._test_run_dynamic_dispatch(expected_methods)
