import unittest
from unittest.mock import (
    MagicMock,
    NonCallableMock,
    create_autospec,
    Mock,
    NonCallableMagicMock,
)

from nose.tools import raises

from exceptions.item_not_found_error import ItemNotFoundError
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_security_groups import OpenstackSecurityGroups


class OpenstackSecurityGroupsTests(unittest.TestCase):
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

    @raises(ItemNotFoundError)
    def test_create_rule_rule_not_found_raises(self):
        self.instance.find_security_group = Mock(return_value=None)
        self.instance.create_security_group_rule(NonCallableMock(), NonCallableMock())

    @raises(ValueError)
    def test_create_rule_throws_for_missing_port_start(self):
        mocked_details = NonCallableMock()
        mocked_details.port_range = (None, 1)
        self.instance.create_security_group_rule(NonCallableMock(), mocked_details)

    @raises(ValueError)
    def test_create_rule_throws_for_missing_port_end(self):
        mocked_details = NonCallableMock()
        mocked_details.port_range = (1, None)
        self.instance.create_security_group_rule(NonCallableMock(), mocked_details)

    def test_create_rule_forwards_result(self):
        cloud, mock_details = NonCallableMock(), NonCallableMagicMock()
        self.instance.find_security_group = Mock()
        returned = self.instance.create_security_group_rule(cloud, mock_details)

        self.instance.find_security_group.assert_called_once_with(
            cloud,
            mock_details.project_identifier,
            mock_details.security_group_identifier,
        )
        self.identity_module.find_mandatory_project.assert_called_once_with(
            cloud, mock_details.project_identifier
        )

        self.network_api.create_security_group_rule.assert_called_once_with(
            project_id=self.identity_module.find_mandatory_project.return_value.id,
            security_group_id=self.instance.find_security_group.return_value.id,
            name=mock_details.rule_name,
            direction=mock_details.direction.value.lower(),
            ether_type=mock_details.ip_version.value.lower(),
            protocol=mock_details.protocol.value.lower(),
            remote_ip_prefix=mock_details.remote_ip_cidr,
            port_range_min=mock_details.port_range[0],
            port_range_max=mock_details.port_range[1],
        )
        assert returned == self.network_api.create_security_group_rule.return_value
