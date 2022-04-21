from typing import Optional

from openstack.network.v2.network import Network

from missing_mandatory_param_error import MissingMandatoryParamError
from openstack_connection import OpenstackConnection


class OpenstackNetwork:
    @staticmethod
    def find_network(cloud_account: str, network_identifier: str) -> Optional[Network]:
        """
        Finds a given network using the name or ID
        :param cloud_account: The associated clouds.yaml account
        :param network_identifier: The ID or name to search for
        :return: The found network or None
        """
        network_identifier = network_identifier.strip()
        if not network_identifier:
            raise MissingMandatoryParamError("A network identifier is required")

        with OpenstackConnection(cloud_account) as conn:
            return conn.network.find_network(network_identifier, ignore_missing=True)
