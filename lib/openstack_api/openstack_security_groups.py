from typing import Optional

from openstack.network.v2.security_group import SecurityGroup

from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase


class OpenstackSecurityGroups(OpenstackWrapperBase):
    def __init__(self, connection_cls=OpenstackConnection):
        super().__init__(connection_cls)
        self._identity_api = OpenstackIdentity(self._connection_cls)

    def find_security_group(
        self,
        cloud_account: str,
        project_identifier: str,
        security_group_identifier: str,
    ) -> Optional[SecurityGroup]:
        """
        Finds a given security group
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier:
        :param security_group_identifier:
        :return: The security group if found
        """
        security_group_identifier = security_group_identifier.strip()
        if not security_group_identifier:
            raise MissingMandatoryParamError("A security group identifier is required")

        project = self._identity_api.find_mandatory_project(
            cloud_account, project_identifier
        )

        with self._connection_cls(cloud_account) as conn:
            return conn.network.find_security_group(
                security_group_identifier, project_id=project.id, ignore_missing=True
            )

    def create_security_group(
        self,
        cloud_account: str,
        group_name: str,
        group_description: str,
        project_identifier: str,
    ) -> SecurityGroup:
        group_name = group_name.strip()
        if not group_name:
            raise MissingMandatoryParamError(
                "A group name is required for the new security group"
            )

        project = self._identity_api.find_mandatory_project(
            cloud_account, project_identifier
        )
        with self._connection_cls(cloud_account) as conn:
            return conn.network.create_security_group(
                name=group_name,
                description=group_description,
                project_id=project.id,
            )
