from unittest.mock import create_autospec, NonCallableMock

from openstack_identity import OpenstackIdentity
from src.domain_action import DomainAction
from src.project_action import ProjectAction
from structs.create_project import ProjectDetails
from tests.openstack_action_test_case import OpenstackActionTestCase


class TestActionProject(OpenstackActionTestCase):
    action_cls = ProjectAction

    def test_project_action_can_be_instantiated(self):
        """
        Tests the action can be instantiated without errors
        """
        action = self.get_action_instance()
        assert action

    def test_create_project_when_successful(self):
        """
        Tests that find domain forwards the result as-is when a domain is found
        """
        mock = create_autospec(OpenstackIdentity)
        action: ProjectAction = self.get_action_instance(api_mock=mock)

        expected_proj_params = {
            i: NonCallableMock()
            for i in ["domain_id", "name", "description", "is_enabled"]
        }
        packaged_proj = ProjectDetails(**expected_proj_params)

        returned_values = action.project_create(
            cloud_account="foo", **expected_proj_params
        )
        mock.create_project.assert_called_once_with(
            cloud_account="foo", project_details=packaged_proj
        )

        assert returned_values[0] is True
        assert returned_values[1] == mock.create_project.return_value

    def test_project_create_when_failed(self):
        """
        Tests that create domain returns None and an error
        when the domain is not found
        """
        mock = create_autospec(OpenstackIdentity)
        mock.create_project.return_value = None

        action: ProjectAction = self.get_action_instance(api_mock=mock)
        returned_values = action.project_create(*{NonCallableMock() for _ in range(5)})
        assert returned_values[0] is False
        assert returned_values[1] is None
