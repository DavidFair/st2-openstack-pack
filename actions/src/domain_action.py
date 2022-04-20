from typing import Tuple, Optional

from openstack.identity.v3.domain import Domain

from openstack_action import OpenstackAction
from openstack_identity import OpenstackIdentity


class DomainAction(OpenstackAction):
    def __init__(self, *args, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)

        # DI handled in OpenstackActionTestCase
        self._api: OpenstackIdentity = kwargs["config"].get(
            "openstack_api", OpenstackIdentity()
        )

        # lists possible functions that could be run as an action
        self.func = {"domain_find": self.find_domain}

    def find_domain(
        self, cloud_account: str, domain: str
    ) -> Tuple[bool, Optional[Domain]]:
        """
        find and return a given project's properties
        :param cloud_account: The account from the clouds configuration to use
        :param domain: DomainAction Name or ID
        :return: (status (Bool), reason (String))
        """
        found_domain = self._api.find_domain(cloud_account=cloud_account, domain=domain)
        return bool(found_domain), found_domain
