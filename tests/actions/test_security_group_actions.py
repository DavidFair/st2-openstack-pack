from unittest.mock import create_autospec, NonCallableMock

from openstack_api.openstack_security_groups import OpenstackSecurityGroups
from src.security_group_actions import SecurityGroupActions
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestNetworkActions(OpenstackActionTestBase):
    """
    Unit tests for the SecurityGroup.* actions
    """

    action_cls = SecurityGroupActions

    def setUp(self):
        super().setUp()
        self.security_group_mock = create_autospec(OpenstackSecurityGroups)
        self.action: SecurityGroupActions = self.get_action_instance(
            api_mock=self.security_group_mock
        )

    def test_find_security_group_successful(self):
        cloud, project, group = NonCallableMock(), NonCallableMock(), NonCallableMock()
        returned = self.action.security_group_find(cloud, project, group)
        expected = self.security_group_mock.find_security_group.return_value

        self.security_group_mock.find_security_group.assert_called_with(
            cloud, project, group
        )
        assert returned == (True, expected)

    def test_find_security_group_failed(self):
        self.security_group_mock.find_security_group.return_value = None
        returned = self.action.security_group_find(
            NonCallableMock(), NonCallableMock(), NonCallableMock()
        )
        assert returned[0] is False
        assert "could not be found" in returned[1]
