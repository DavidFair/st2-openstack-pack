import unittest
from unittest.mock import MagicMock, NonCallableMock, ANY

from nose.tools import raises

from exceptions.item_not_found_error import ProjectNotFoundError
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_api.openstack_security_groups import OpenstackSecurityGroups


class OpenstackNetworkTests(unittest.TestCase):
    def setUp(self) -> None:
        """
        Sets up the various mocks required in this test
        """
        super().setUp()
        self.mocked_connection = MagicMock()
        self.instance = OpenstackSecurityGroups(self.mocked_connection)
        self.identity_api = (
            self.mocked_connection.return_value.__enter__.return_value.identity
        )
        self.network_api = (
            self.mocked_connection.return_value.__enter__.return_value.network
        )

    @raises(MissingMandatoryParamError)
    def test_find_security_group_raises_for_missing_identifier(self):
        """
        Tests that find security group raises if no identifier is provided
        """
        self.instance.find_security_group(
            NonCallableMock(),
            project_identifier=NonCallableMock(),
            security_group_identifier=" \t",
        )

    @raises(ProjectNotFoundError)
    def test_find_security_group_raises_for_project_not_found(self):
        self.identity_api.find_project.return_value = None
        self.instance.find_security_group(
            NonCallableMock(), NonCallableMock(), NonCallableMock()
        )

    def test_find_security_group_forwards_result(self):
        cloud, project, security_group = (
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
        )
        return_val = self.instance.find_security_group(cloud, project, security_group)

        self.identity_api.find_project.assert_called_once_with(
            project.strip(), ignore_missing=ANY
        )
        self.mocked_connection.assert_called_with(cloud)
        self.network_api.find_security_group.assert_called_once_with(
            security_group.strip(),
            project_id=self.identity_api.find_project.return_value.id,
            ignore_missing=True,
        )
        assert return_val == self.network_api.find_security_group.return_value
