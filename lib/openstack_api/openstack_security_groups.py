from typing import Optional

from openstack.network.v2.security_group import SecurityGroup

from exceptions.item_not_found_error import ItemNotFoundError, ProjectNotFoundError
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase


class OpenstackSecurityGroups(OpenstackWrapperBase):
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

        project = OpenstackIdentity(self._connection_cls).find_project(
            cloud_account, project_identifier
        )
        if not project:
            raise ProjectNotFoundError()

        with self._connection_cls(cloud_account) as conn:
            return conn.network.find_security_group(
                security_group_identifier, project_id=project.id, ignore_missing=True
            )
