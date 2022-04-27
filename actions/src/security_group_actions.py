from typing import Dict, Tuple, Union, Optional, List

from openstack.network.v2.security_group import SecurityGroup

from enums.ip_version import IPVersion
from enums.network_direction import NetworkDirection
from enums.protocol import Protocol
from openstack_action import OpenstackAction
from openstack_api.openstack_security_groups import OpenstackSecurityGroups
from structs.security_group_rule_details import SecurityGroupRuleDetails


class SecurityGroupActions(OpenstackAction):
    def __init__(self, *args, config: Dict, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)
        self._api: OpenstackSecurityGroups = config.get(
            "openstack_api", OpenstackSecurityGroups()
        )

        # lists possible functions that could be run as an action
        self.func = {
            "security_group_create": self.security_group_create,
            "security_group_rule_create": self.security_group_rule_create,
            "security_group_show": self.security_group_find,
            "security_group_list": self.security_group_list
            # security_group_delete
            # security_group_update
        }

    def security_group_create(
        self,
        cloud_account: str,
        group_name: str,
        group_description: str,
        project_identifier: str,
    ) -> Tuple[bool, SecurityGroup]:
        """
        Create a Security Group for a Project
        :param cloud_account: The associated clouds.yaml account
        :param group_name: The new name for the security group
        :param group_description: The description to associate with the new group
        :param project_identifier: Openstack Project ID or Name,
        :return: status, the new Security group or None
        """
        security_group = self._api.create_security_group(
            cloud_account, group_name, group_description, project_identifier
        )
        return bool(security_group), security_group

    def security_group_find(
        self,
        cloud_account: str,
        project_identifier: str,
        security_group_identifier: str,
    ) -> Tuple[bool, Union[SecurityGroup, str]]:
        """
        Show a security group
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: Openstack Project ID or Name,
        :param security_group_identifier: Openstack Security Group ID or Name
        :return: status, Security Group object or error message
        """
        security_group = self._api.find_security_group(
            cloud_account, project_identifier, security_group_identifier
        )
        output = (
            security_group
            if security_group
            else "The requested security group could not be found"
        )
        return bool(security_group), output

    def security_group_list(
        self, cloud_account: str, project_identifier
    ) -> Tuple[bool, List[SecurityGroup]]:
        """
        List Security groups for a project
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: Openstack Project ID or Name,
        :return: status, list of associated security groups
        """
        found = self._api.search_security_group(cloud_account, project_identifier)
        return bool(found), found

    def security_group_rule_create(
        self,
        cloud_account: str,
        project_identifier: str,
        security_group_identifier: str,
        direction: str,
        ether_type: str,
        protocol: str,
        remote_ip_prefix: str,
        rule_name: Optional[str],
        start_port: int,
        end_port: int,
    ):
        """
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: Openstack Project ID or Name,
        :param security_group_identifier: Openstack Security Group ID or Name
        :param direction: the direction this rule applies to (ingress/egress)
        :param ether_type: the IP version this rule applies to (IPV4/IPV6)
        :param protocol: the protocol this rule applies to (TCP/UDP/ICMP)
        :param remote_ip_prefix: The destination CIDR this applies to
        :param rule_name: An optional name for this new rule
        :param start_port: The starting port this applies to
        :param end_port: The final port (inclusive) this applies to
        :return: status, Security Group object or error message
        """
        details = SecurityGroupRuleDetails(
            security_group_identifier=security_group_identifier,
            project_identifier=project_identifier,
            direction=NetworkDirection[direction.upper()],
            ip_version=IPVersion[ether_type.upper()],
            protocol=Protocol[protocol.upper()],
            remote_ip_cidr=remote_ip_prefix,
            port_range=(start_port, end_port),
            rule_name=rule_name,
        )
        rule = self._api.create_security_group_rule(cloud_account, details)
        return bool(rule), rule
