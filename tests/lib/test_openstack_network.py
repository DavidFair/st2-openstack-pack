import unittest
from unittest.mock import NonCallableMock, patch

from nose.tools import raises

from missing_mandatory_param_error import MissingMandatoryParamError
from openstack_network import OpenstackNetwork


class OpenstackNetworkTests(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.instance = OpenstackNetwork()
        connection_patch = patch("openstack_network.OpenstackConnection")
        self.mocked_connection = connection_patch.start()
        self.addCleanup(connection_patch.stop)
        self.network_api = (
            self.mocked_connection.return_value.__enter__.return_value.network
        )

    @raises(MissingMandatoryParamError)
    def test_find_network_raises_for_missing_param(self):
        """
        Tests that find network will raise if the identifier is missing
        """
        self.instance.find_network(NonCallableMock(), " ")

    def test_find_network_with_found_result(self):
        """
        Tests that find network returns the result as-is
        """
        cloud, identifier = NonCallableMock(), NonCallableMock()
        returned = self.instance.find_network(cloud, identifier)

        self.mocked_connection.assert_called_once_with(cloud)
        self.network_api.find_network.assert_called_once_with(
            identifier.strip(), ignore_missing=True
        )
        assert returned == self.network_api.find_network.return_value
