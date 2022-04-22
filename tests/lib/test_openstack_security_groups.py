import unittest
from unittest.mock import MagicMock, NonCallableMock, create_autospec

from nose.tools import raises

from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_security_groups import OpenstackSecurityGroups


class OpenstackNetworkTests(unittest.TestCase):
    def setUp(self) -> None:
        """
        Sets up the various mocks required in this test
        """
        super().setUp()
        self.mocked_connection = MagicMock()
        self.instance = OpenstackSecurityGroups(self.mocked_connection)
        self.identity_module = create_autospec(OpenstackIdentity)
        self.instance._identity_api = self.identity_module
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

    def test_find_security_group_forwards_result(self):
        cloud, project, security_group = (
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
        )
        return_val = self.instance.find_security_group(cloud, project, security_group)

        self.identity_module.find_mandatory_project.assert_called_once_with(
            cloud, project
        )
        self.mocked_connection.assert_called_with(cloud)
        self.network_api.find_security_group.assert_called_once_with(
            security_group.strip(),
            project_id=self.identity_module.find_mandatory_project.return_value.id,
            ignore_missing=True,
        )
        assert return_val == self.network_api.find_security_group.return_value

    @raises(MissingMandatoryParamError)
    def test_create_security_group_missing_name_raises(self):
        self.instance.create_security_group(
            cloud_account=NonCallableMock(),
            group_description=NonCallableMock(),
            project_identifier=NonCallableMock(),
            group_name=" \t",
        )

    def test_create_security_group_forwards_result(self):
        cloud, name, description, project = (NonCallableMock() for _ in range(4))
        result = self.instance.create_security_group(cloud, name, description, project)

        self.identity_module.find_mandatory_project.assert_called_once_with(
            cloud, project
        )
        self.mocked_connection.assert_called_once_with(cloud)
        self.network_api.create_security_group.assert_called_once_with(
            project_id=self.identity_module.find_mandatory_project.return_value.id,
            name=name.strip(),
            description=description,
        )
        assert result == self.network_api.create_security_group.return_value
