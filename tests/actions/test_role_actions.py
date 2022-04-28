from unittest.mock import create_autospec

from openstack_api.openstack_roles import OpenstackRoles
from src.role_actions import RoleActions
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestRoleActions(OpenstackActionTestBase):
    """
    Unit tests for the SecurityGroup.* actions
    """

    action_cls = RoleActions

    # pylint: disable=invalid-name
    def setUp(self):
        """
        Initialises the action and injects mocks required for testing
        """
        super().setUp()
        self.role_mock = create_autospec(OpenstackRoles)
        self.action: RoleActions = self.get_action_instance(
            api_mock=self.security_group_mock
        )
