from unittest.mock import create_autospec, NonCallableMock

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
        self.action: RoleActions = self.get_action_instance(api_mock=self.role_mock)

    def test_role_add(self):
        """
        Tests that role add forwards to the correct API
        """
        cloud = NonCallableMock()
        user, project, role = NonCallableMock(), NonCallableMock(), NonCallableMock()
        self.action.role_add(cloud, user, project, role)
        self.role_mock.assign_role_to_user.assert_called_once_with(
            cloud_account=cloud,
            user_identifier=user,
            project_identifier=project,
            role_identifier=role,
        )

    def test_role_remove(self):
        """
        Tests that role removal forwards to the correct API
        """
        cloud = NonCallableMock()
        user, project, role = NonCallableMock(), NonCallableMock(), NonCallableMock()
        self.action.role_remove(cloud, user, project, role)
        self.role_mock.remove_role_from_user.assert_called_once_with(
            cloud_account=cloud,
            user_identifier=user,
            project_identifier=project,
            role_identifier=role,
        )

    def test_has_role(self):
        """
        Tests has role makes the correct call and returns the result
        """
        cloud = NonCallableMock()
        user, project, role = NonCallableMock(), NonCallableMock(), NonCallableMock()

        returned = self.action.user_has_role(cloud, user, project, role)

        self.role_mock.has_role.assert_called_once_with(
            cloud_account=cloud,
            user_identifier=user,
            project_identifier=project,
            role_identifier=role,
        )
        expected = self.role_mock.has_role.return_value
        assert returned == expected
