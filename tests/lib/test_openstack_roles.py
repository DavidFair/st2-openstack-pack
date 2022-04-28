import unittest
from unittest.mock import patch, MagicMock, NonCallableMock, Mock

from nose.tools import raises

from exceptions.item_not_found_error import ItemNotFoundError
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_api.openstack_roles import OpenstackRoles


class OpenstackSecurityGroupsTests(unittest.TestCase):
    def setUp(self) -> None:
        """
        Sets up the various mocks required in this test
        """
        super().setUp()
        self.mocked_connection = MagicMock()
        with patch("openstack_api.openstack_roles.OpenstackIdentity") as identity_mock:
            self.instance = OpenstackRoles(self.mocked_connection)
            self.identity_module = identity_mock.return_value

        self._api = self.mocked_connection.return_value.__enter__.return_value.identity

    @raises(ItemNotFoundError)
    def test_assign_roles_throws_missing_user(self):
        """
        Tests that an exception is thrown if the specified user is not found
        """
        self.identity_module.find_user.return_value = None
        self.instance.assign_role_to_user(*(NonCallableMock() for _ in range(4)))

    @raises(ItemNotFoundError)
    def test_assign_roles_throws_missing_role(self):
        """
        Tests that an exception is thrown if the specified role is not found
        """
        self.instance.find_role = Mock(return_value=None)
        self.instance.assign_role_to_user(*(NonCallableMock() for _ in range(4)))

    def test_assign_roles_makes_correct_call(self):
        """
        Tests that assign role forwards the found objects onto
        the assignment API
        """
        cloud = NonCallableMock()
        project, user, role = NonCallableMock(), NonCallableMock(), NonCallableMock()

        self.instance.find_role = Mock()
        self.instance.assign_role_to_user(cloud, user, project, role)

        self.identity_module.find_mandatory_project.assert_called_once_with(
            cloud, project
        )
        self.identity_module.find_user.assert_called_once_with(cloud, user)
        self.instance.find_role.assert_called_once_with(cloud, role)

        self._api.assign_project_role_to_user.assert_called_once_with(
            project=self.identity_module.find_mandatory_project.return_value,
            user=self.identity_module.find_user.return_value,
            role=self.instance.find_role.return_value,
        )

    @raises(MissingMandatoryParamError)
    def test_find_role_raises_missing(self):
        """
        Tests that an exception is thrown if an empty string is provided
        """
        self.instance.find_role(NonCallableMock(), " \t")

    def test_find_role_returns(self):
        """
        Tests find role calls the correct API and returns the result
        """
        cloud, role = NonCallableMock(), NonCallableMock()
        found = self.instance.find_role(cloud, role)

        self.mocked_connection.assert_called_once_with(cloud)
        self._api.find_role.assert_called_once_with(role.strip(), ignore_missing=True)
        expected = self._api.find_role.return_value
        assert found == expected

    @raises(ItemNotFoundError)
    def test_remove_role_throws_user_not_found(self):
        """
        Tests remove role throws if the user was not found
        """
        self.identity_module.find_user.return_value = None
        self.instance.remove_role_from_user(*(NonCallableMock() for _ in range(4)))

    @raises(ItemNotFoundError)
    def test_remove_role_throws_role_not_found(self):
        """
        Tests remove role throws if the role was not found
        """
        self.instance.find_role = Mock(return_value=None)
        self.instance.remove_role_from_user(*(NonCallableMock() for _ in range(4)))

    def test_remove_roles_makes_correct_call(self):
        """
        Tests that removal forwards the found objects onto
        the unassign API
        """
        cloud = NonCallableMock()
        project, user, role = NonCallableMock(), NonCallableMock(), NonCallableMock()

        self.instance.find_role = Mock()
        self.instance.remove_role_from_user(cloud, user, project, role)

        self.identity_module.find_mandatory_project.assert_called_once_with(
            cloud, project
        )
        self.identity_module.find_user.assert_called_once_with(cloud, user)
        self.instance.find_role.assert_called_once_with(cloud, role)

        self._api.unassign_project_role_from_user.assert_called_once_with(
            project=self.identity_module.find_mandatory_project.return_value,
            user=self.identity_module.find_user.return_value,
            role=self.instance.find_role.return_value,
        )

    @raises(ItemNotFoundError)
    def test_has_role_throws_user_not_found(self):
        """
        Tests has role throws if the user was not found
        """
        self.identity_module.find_user.return_value = None
        self.instance.has_role(*(NonCallableMock() for _ in range(4)))

    @raises(ItemNotFoundError)
    def test_has_role_throws_role_not_found(self):
        """
        Tests has role throws if the role was not found
        """
        self.instance.find_role = Mock(return_value=None)
        self.instance.has_role(*(NonCallableMock() for _ in range(4)))

    def test_has_roles_makes_correct_call(self):
        """
        Tests that has forwards the result
        """
        cloud = NonCallableMock()
        project, user, role = NonCallableMock(), NonCallableMock(), NonCallableMock()

        self.instance.find_role = Mock()
        returned = self.instance.has_role(cloud, user, project, role)

        self.identity_module.find_mandatory_project.assert_called_once_with(
            cloud, project
        )
        self.identity_module.find_user.assert_called_once_with(cloud, user)
        self.instance.find_role.assert_called_once_with(cloud, role)

        self._api.validate_user_has_role.assert_called_once_with(
            project=self.identity_module.find_mandatory_project.return_value,
            user=self.identity_module.find_user.return_value,
            role=self.instance.find_role.return_value,
        )
        expected = self._api.validate_user_has_role.return_value
        assert returned == expected
