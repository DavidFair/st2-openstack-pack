import unittest
from unittest.mock import NonCallableMock, ANY, Mock, MagicMock

from nose.tools import raises
from openstack.exceptions import ConflictException

from exceptions.item_not_found_error import ItemNotFoundError
from openstack_api.openstack_identity import OpenstackIdentity
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from structs.project_details import ProjectDetails


class OpenstackIdentityTests(unittest.TestCase):
    """
    Runs various tests to ensure we are using the Openstack
    Identity module in the expected way
    """

    def setUp(self) -> None:
        super().setUp()
        self.mocked_connection = MagicMock()
        self.instance = OpenstackIdentity(self.mocked_connection)
        self.identity_api = (
            self.mocked_connection.return_value.__enter__.return_value.identity
        )

    @raises(MissingMandatoryParamError)
    def test_create_project_name_missing_throws(self):
        """
        Tests calling the API wrapper without a domain will throw
        """
        self.instance.create_project(
            "", ProjectDetails(name="", description="", is_enabled=False)
        )

    def test_create_project_forwards_result(self):
        """
        Tests that the params and result are forwarded as-is to/from the
        create_project API
        """

        expected_details = ProjectDetails(
            name=NonCallableMock(),
            description=NonCallableMock(),
            is_enabled=NonCallableMock(),
        )

        found = self.instance.create_project(
            cloud_account="test", project_details=expected_details
        )

        self.mocked_connection.assert_called_once_with("test")

        assert found == self.identity_api.create_project.return_value
        self.identity_api.create_project.assert_called_once_with(
            name=expected_details.name,
            domain_id="default",
            description=expected_details.description,
            is_enabled=expected_details.is_enabled,
        )

    @raises(ConflictException)
    def test_create_project_forwards_conflict_exception(self):
        """
        Tests that a conflict exception doesn't get lost from Openstack
        """

        self.identity_api.create_project.side_effect = ConflictException
        self.instance.create_project(NonCallableMock(), NonCallableMock())

    @staticmethod
    @raises(MissingMandatoryParamError)
    def test_delete_project_throws_whitespace_args():
        """
        Test that if the user doesn't provide meaningful args to delete we throw
        """
        # Intentional spaces
        OpenstackIdentity().delete_project("", project_identifier=" \t")

    def test_delete_project_calls_find_project(self):
        """
        Since delete project expects either the OS UUID or a project instance
        we need to forward the call onto find before we call delete
        """

        identifier = NonCallableMock()

        self.instance.delete_project(NonCallableMock(), project_identifier=identifier)

        # We want this to throw to follow Pythonic E.A.F.P.
        self.identity_api.find_project.assert_called_once_with(
            identifier.strip(), ignore_missing=ANY
        )
        found_identifier = self.identity_api.find_project.return_value
        self.identity_api.delete_project.assert_called_once_with(
            project=found_identifier, ignore_missing=False
        )

    def test_delete_project_successful_with_name_or_id(self):
        """
        Tests delete project will use name or Openstack ID if provided
        and will return the result
        """

        self.instance.find_project = Mock()
        self.identity_api.delete_project.return_value = None

        identifier = NonCallableMock()
        result = self.instance.delete_project(
            cloud_account="test", project_identifier=identifier
        )

        assert result is True
        self.identity_api.delete_project.assert_called_once_with(
            project=self.instance.find_project.return_value, ignore_missing=False
        )

    def test_delete_project_handles_resource_not_found(self):
        """
        Tests that the delete method can handle resource not found. This is
        enabled, so it's easier to tell between a None (success) type and a
        failure
        """

        self.instance.find_project = Mock(return_value=None)
        result = self.instance.delete_project("", project_identifier="test")
        assert result is False

    @raises(MissingMandatoryParamError)
    def test_find_project_raises_missing_project_identifier(self):
        """
        Tests that a missing mandatory parameter is missing if a whitespace
        or empty string is passed
        """

        self.instance.find_project("set", " ")

    def test_find_project_forwards_result(self):
        """
        Tests that the call forwards the result as is, and the Openstack API
        is being used correctly
        """

        cloud_account, project_identifier = NonCallableMock(), NonCallableMock()
        found = self.instance.find_project(
            cloud_account=cloud_account, project_identifier=project_identifier
        )

        self.mocked_connection.assert_called_once_with(cloud_account)
        self.identity_api.find_project.assert_called_once_with(
            project_identifier.strip(), ignore_missing=True
        )
        assert found == self.identity_api.find_project.return_value

    def test_find_mandatory_project_forwards(self):
        """
        Check the arguments are forwarded as-is and the result returned
        """
        self.instance.find_project = Mock()
        args = (NonCallableMock(), NonCallableMock())
        returned = self.instance.find_mandatory_project(*args)

        self.instance.find_project.assert_called_once_with(*args)
        assert returned == self.instance.find_project.return_value

    @raises(ItemNotFoundError)
    def test_find_mandatory_project_raises_for_missing(self):
        """
        Check that a missing project will raise correctly
        """
        self.instance.find_project = Mock(return_value=None)
        self.instance.find_mandatory_project(NonCallableMock(), NonCallableMock())
