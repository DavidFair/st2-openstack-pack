from abc import ABC

from openstack_api.openstack_connection import OpenstackConnection


# pylint: disable=too-few-public-methods
class OpenstackWrapperBase(ABC):
    def __init__(self, connection_cls=OpenstackConnection):
        """
        Constructs a wrapper for the Openstack wrapper module
        @param connection_cls: The class to used for connections (allowing DI)
        """
        self._connection_cls = connection_cls
