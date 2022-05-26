from typing import Dict, Callable

from openstack.exceptions import ResourceNotFound
from openstack.network.v2.subnet import Subnet
from st2common.runners.base_action import Action

from openstack_api.openstack_network import OpenstackNetwork


class SubnetActions(Action):
    def __init__(self, *args, config: Dict, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)
        self._api: OpenstackNetwork = config.get("openstack_api", OpenstackNetwork())

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    def subnet_show(self, subnet):
        """
        Show subnet properties
        :param subnet: Name or ID
        :return: (status (Bool), reason/output (String/Dict))
        """
        try:
            subnet = self.conn.network.find_subnet(subnet, ignore_missing=False)
        except ResourceNotFound as err:
            return False, f"Subnet not found {repr(err)}"
        return True, subnet

    def subnet_create(
        self,
        cloud_account: str,
        network: str,
        subnet_name: str,
        subnet_description: str,
        dhcp_enabled: bool,
    ) -> Subnet:
        """
        Create a Subnet on a Network
        :param cloud_account: The account from the clouds configuration to use
        :param network: Network ID or Name to add the subnet to
        :param subnet_name: Name of the new subnet
        :param subnet_description: Description of the new subnet
        :param dhcp_enabled: Whether to enable DHCP on the new subnet
        :return: status, new subnet
        """

        return self._api.create_subnet(
            cloud_account, network, subnet_name, subnet_description, dhcp_enabled
        )
