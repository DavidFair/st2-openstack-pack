import unittest
from unittest.mock import NonCallableMock, patch

from nose.tools import raises
from openstack.exceptions import ResourceNotFound

from openstack_identity import OpenstackIdentity
from missing_mandatory_param_error import MissingMandatoryParamError
from structs.create_project import ProjectDetails


class OpenstackIdentityTests(unittest.TestCase):
    """
    Runs various tests to ensure we are using the Openstack
    Identity module in the expected way
    """

    def setUp(self) -> None:
        connection_patch = patch("openstack_identity.OpenstackConnection")
        self.mocked_connection = connection_patch.start()
        self.addCleanup(connection_patch.stop)
        self.identity_api = (
            self.mocked_connection.return_value.__enter__.return_value.identity
        )

    @staticmethod
    @raises(MissingMandatoryParamError)
    def test_create_project_name_missing_throws():
        """
        Tests calling the API wrapper without a domain will throw
        """
        OpenstackIdentity().create_project(
            "", ProjectDetails(name="", description="", is_enabled=False)
        )

    def test_create_project_forwards_result(self):
        """
        Tests that the params and result are forwarded as-is to/from the
        create_project API
        """
        instance = OpenstackIdentity()

        expected_details = ProjectDetails(
            name=NonCallableMock(),
            description=NonCallableMock(),
            is_enabled=NonCallableMock(),
        )

        found = instance.create_project(
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

    @staticmethod
    @raises(MissingMandatoryParamError)
    def test_delete_project_throws_whitespace_args():
        """
        Test that if the user doesn't provide meaningful args to delete we throw
        """
        # Intentional spaces
        OpenstackIdentity().delete_project("", project_identifier=" \t")

    def test_delete_project_successful_with_name_or_id(self):
        """
        Tests delete project will use name or Openstack ID if provided
        and will return the result
        """
        instance = OpenstackIdentity()
        self.identity_api.delete_project.return_value = None

        identifier = NonCallableMock()
        result = instance.delete_project(
            cloud_account="test", project_identifier=identifier
        )

        assert result is True
        self.identity_api.delete_project.assert_called_once_with(
            project=identifier.strip(), ignore_missing=False
        )

    def test_delete_project_handles_resource_not_found(self):
        """
        Tests that the delete method can handle resource not found. This is
        enabled, so it's easier to tell between a None (success) type and a
        failure
        """
        instance = OpenstackIdentity()
        self.identity_api.delete_project.side_effect = ResourceNotFound
        result = instance.delete_project("", project_identifier="test")
        assert result is False

    @staticmethod
    @raises(MissingMandatoryParamError)
    def test_find_project_raises_missing_project_identifier():
        """
        Tests that a missing mandatory parameter is missing if a whitespace
        or empty string is passed
        """
        instance = OpenstackIdentity()
        instance.find_project("set", " ")

    def test_find_project_forwards_result(self):
        """
        Tests that the call forwards the result as is, and the Openstack API
        is being used correctly
        """
        instance = OpenstackIdentity()
        cloud_account, project_identifier = NonCallableMock(), NonCallableMock()
        found = instance.find_project(
            cloud_account=cloud_account, project_identifier=project_identifier
        )

        self.mocked_connection.assert_called_once_with(cloud_account)
        self.identity_api.find_project.assert_called_once_with(
            project_identifier.strip(), ignore_missing=True
        )
        assert found == self.identity_api.find_project.return_value
