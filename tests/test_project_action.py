from unittest.mock import create_autospec, NonCallableMock

from openstack_identity import OpenstackIdentity
from src.project_action import ProjectAction
from structs.create_project import ProjectDetails
from tests.openstack_action_test_case import OpenstackActionTestCase


class TestActionProject(OpenstackActionTestCase):
    """
    Unit tests the Project.* actions
    """

    action_cls = ProjectAction

    # pylint: disable=invalid-name
    def setUp(self):
        """
        Initialises the API mock used in the unit tests
        """
        super().setUp()
        self.identity_mock = create_autospec(OpenstackIdentity)
        self.action: ProjectAction = self.get_action_instance(
            api_mock=self.identity_mock
        )

    def test_project_action_can_be_instantiated(self):
        """
        Tests the action can be instantiated without errors
        """
        action = self.get_action_instance()
        assert action

    def test_create_project_when_successful(self):
        """
        Tests that create project forwards the result when successful
        """
        expected_proj_params = {
            i: NonCallableMock() for i in ["name", "description", "is_enabled"]
        }
        # Check that default gets hard-coded in too
        packaged_proj = ProjectDetails(**expected_proj_params)

        returned_values = self.action.project_create(
            cloud_account="foo", **expected_proj_params
        )
        self.identity_mock.create_project.assert_called_once_with(
            cloud_account="foo", project_details=packaged_proj
        )

        assert returned_values[0] is True
        assert returned_values[1] == self.identity_mock.create_project.return_value

    def test_project_create_when_failed(self):
        """
        Tests that create domain returns None and an error
        when the domain is not found
        """
        self.identity_mock.create_project.return_value = None

        returned_values = self.action.project_create(
            *{NonCallableMock() for _ in range(4)}
        )
        assert returned_values[0] is False
        assert returned_values[1] is None

    def test_project_delete_success(self):
        """
        Tests that on successful deletion it returns the correct status and string
        """
        self.identity_mock.delete_project.return_value = True
        returned_values = self.action.project_delete(
            NonCallableMock(), NonCallableMock()
        )
        assert returned_values == (True, "")

    def test_project_find_success(self):
        """
        Tests that the correct results are given for a found project
        """
        expected = NonCallableMock()
        self.identity_mock.find_project.return_value = expected
        returned_values = self.action.project_find(NonCallableMock(), NonCallableMock())
        assert returned_values == (True, expected)

    def test_project_find_failure(self):
        """
        Tests that the correct return is given when a project is not found
        """
        self.identity_mock.find_project.return_value = None
        returned_values = self.action.project_find(NonCallableMock(), NonCallableMock())
        assert returned_values == (False, None)
