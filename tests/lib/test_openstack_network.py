import ipaddress
import unittest
from unittest.mock import NonCallableMock, Mock, ANY, MagicMock, patch

from nose.tools import raises
from openstack.exceptions import ResourceNotFound

from enums.network_providers import NetworkProviders
from enums.rbac_network_actions import RbacNetworkActions
from exceptions.item_not_found_error import ItemNotFoundError
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_api.openstack_network import OpenstackNetwork


class OpenstackNetworkTests(unittest.TestCase):
    def setUp(self) -> None:
        """
        Sets up the various mocks required in this test
        """
        super().setUp()
        self.mocked_connection = MagicMock()
        with patch(
            "openstack_api.openstack_network.OpenstackIdentity"
        ) as identity_mock:
            self.instance = OpenstackNetwork(self.mocked_connection)
            self.identity_module = identity_mock.return_value

        self.network_api = (
            self.mocked_connection.return_value.__enter__.return_value.network
        )

    @raises(ItemNotFoundError)
    def test_allocate_floating_ip_raises_network_not_found(self):
        """
        Tests that allocating a floating IP will raise if the network was not found
        """
        self.instance.find_network = Mock(return_value=None)
        self.instance.allocate_floating_ips(
            NonCallableMock(), NonCallableMock(), NonCallableMock(), NonCallableMock()
        )

    def test_allocate_floating_ip_zero_ips(self):
        """
        Tests allocate floating IP does not make any calls when 0 is passed
        """
        returned = self.instance.allocate_floating_ips(
            NonCallableMock(), NonCallableMock(), NonCallableMock(), number_to_create=0
        )
        self.network_api.create_ip.assert_not_called()
        assert returned == []

    def test_allocate_floating_ip_single_ip(self):
        """
        Tests allocate floating IP makes a single call to create IP
        """
        returned = self._assert_allocate_queries(num_to_allocate=1)
        self.network_api.create_ip.assert_called_once_with(
            project_id=self.identity_module.find_mandatory_project.return_value.id,
            floating_network_id=self.instance.find_network.return_value.id,
        )

        assert len(returned) == 1
        assert returned[0] == self.network_api.create_ip.return_value

    def _assert_allocate_queries(self, num_to_allocate: int):
        self.instance.find_network = Mock()
        cloud, network, project = (
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
        )
        returned = self.instance.allocate_floating_ips(
            cloud, network, project, number_to_create=num_to_allocate
        )
        self.identity_module.find_mandatory_project.assert_called_once_with(
            cloud, project
        )
        self.instance.find_network.assert_called_once_with(cloud, network)
        return returned

    def test_allocate_floating_ip_multiple_ips(self):
        """
        Tests allocating multiple IPs makes the correct number of queries
        """
        returned = self._assert_allocate_queries(num_to_allocate=2)
        assert self.network_api.create_ip.call_count == 2
        self.network_api.create_ip.assert_called_with(
            project_id=self.identity_module.find_mandatory_project.return_value.id,
            floating_network_id=self.instance.find_network.return_value.id,
        )

        expected = self.network_api.create_ip.return_value
        # Mock will return the same obj twice, but the real API generates
        # a new object each time
        assert returned == [expected, expected]

    @raises(MissingMandatoryParamError)
    def test_get_floating_ip_throws_missing_address(self):
        """
        Tests that get floating IP will throw for a missing address
        """
        self.instance.get_floating_ip(NonCallableMock(), " \t")

    def test_get_floating_ip_call_success(self):
        """
        Tests get floating IP returns correctly
        """
        cloud, ip = NonCallableMock(), NonCallableMock()
        returned = self.instance.get_floating_ip(cloud, ip)

        self.mocked_connection.assert_called_with(cloud)
        self.network_api.get_ip.assert_called_once_with(ip.strip())
        assert returned == self.network_api.get_ip.return_value

    def test_get_floating_ip_call_failure(self):
        """
        Tests get floating IP returns None if a result isn't found
        """
        cloud, ip = NonCallableMock(), NonCallableMock()
        self.network_api.get_ip.side_effect = ResourceNotFound
        returned = self.instance.get_floating_ip(cloud, ip)
        assert returned is None

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

    def test_search_network_forwards_results(self):
        """
        Tests that find network forwards its results as-is
        """
        cloud, identifier = NonCallableMock(), NonCallableMock()
        result = self.instance.search_network_rbacs(cloud, identifier)

        self.identity_module.find_mandatory_project.assert_called_once_with(
            cloud, identifier
        )
        self.mocked_connection.assert_called_once_with(cloud)
        self.network_api.rbac_policies.assert_called_once_with(
            project_id=self.identity_module.find_mandatory_project.return_value.id
        )
        assert result == list(self.network_api.rbac_policies.return_value)

    @raises(MissingMandatoryParamError)
    def test_create_network_no_name(self):
        """
        Tests that create network with no new network name throws
        """
        mocked_details = NonCallableMock()
        mocked_details.name = " \t"
        self.instance.create_network(NonCallableMock(), mocked_details)

    def test_create_network_serialises_enum(self):
        """
        Tests that the NetworkProviders enum gets serialised into
        Openstack compatible JSON
        """
        expected = {NetworkProviders.VXLAN: "vxlan"}

        for enum_key, expected_val in expected.items():
            mock_details = NonCallableMock()
            mock_details.provider_network_type = enum_key

            self.instance.create_network(NonCallableMock(), mock_details)
            self.network_api.create_network.assert_called_once_with(
                project_id=ANY,
                name=ANY,
                description=ANY,
                is_port_security_enabled=ANY,
                is_router_external=ANY,
                provider_network_type=expected_val,
            )

    def test_create_network_forwards_result(self):
        """
        Tests that create network will forward the result from Openstack
        """
        cloud_account, mock_details = NonCallableMock(), NonCallableMock()

        returned = self.instance.create_network(cloud_account, mock_details)
        self.mocked_connection.assert_called_with(cloud_account)
        self.network_api.create_network(
            project_id=self.identity_module.find_mandatory_project.return_value.id,
            name=mock_details.name,
            description=mock_details.description,
            provider_network_type=mock_details.provider_network_type,
            is_port_security_enabled=mock_details.port_security_enabled,
            is_router_external=mock_details.has_external_router,
        )
        assert returned == self.network_api.create_network.return_value

    @raises(ItemNotFoundError)
    def test_create_network_rbac_network_not_found(self):
        """
        Tests that create RBAC (network) will throw if a network isn't found
        """
        self.instance.find_network = Mock(return_value=None)
        self.instance.create_network_rbac(NonCallableMock(), NonCallableMock())

    def test_create_rbac_uses_found_project_and_network(self):
        """
        Tests that create RBAC uses the project and network found instead
        of the user's input
        """
        cloud, rbac_details = NonCallableMock(), NonCallableMock()
        self.instance.find_network = Mock()
        rbac_details.action = RbacNetworkActions.SHARED

        returned = self.instance.create_network_rbac(cloud, rbac_details)

        self.mocked_connection.assert_called_with(cloud)
        self.network_api.create_rbac_policy.assert_called_once_with(
            object_id=self.instance.find_network.return_value.id,
            object_type="network",
            target_project_id=self.identity_module.find_mandatory_project.return_value.id,
            action=ANY,
        )
        assert returned == self.network_api.create_rbac_policy.return_value

    @raises(KeyError)
    def test_create_rbac_unknown_key(self):
        """
        Tests a key error is thrown in an unknown var is passed to the serialisation logic
        """
        rbac_details = NonCallableMock()
        rbac_details.action = "unknown"
        self.instance.create_network_rbac(NonCallableMock(), rbac_details)

    def test_create_rbac_serialises_enum_correctly(self):
        """
        Tests that the RBAC access maps from the internal enum to the
        Openstack API string correctly
        """
        expected_serialisation = {
            RbacNetworkActions.EXTERNAL: "access_as_external",
            RbacNetworkActions.SHARED: "access_as_shared",
        }

        for enum_val, expected_val in expected_serialisation.items():
            rbac_details = NonCallableMock()
            rbac_details.action = enum_val

            self.instance.create_network_rbac(NonCallableMock(), rbac_details)
            self.network_api.create_rbac_policy.assert_called_once_with(
                object_id=ANY,
                object_type=ANY,
                target_project_id=ANY,
                action=expected_val,
            )
            self.network_api.create_rbac_policy.reset_mock()

    def test_delete_network_forwards_find_network(self):
        """
        Tests that delete network forwards the result from Openstack
        """
        self.instance.find_network = Mock()
        cloud, network_identifier = NonCallableMock(), NonCallableMock()
        self.network_api.delete_network.return_value = None
        result = self.instance.delete_network(cloud, network_identifier)

        self.instance.find_network.assert_called_once_with(cloud, network_identifier)
        self.network_api.delete_network.assert_called_once_with(
            self.instance.find_network.return_value, ignore_missing=False
        )
        assert result is True

    def test_delete_network_cant_find_network(self):
        """
        Tests that delete network returns false if it can't find the network to delete
        """
        self.instance.find_network = Mock(return_value=None)
        cloud, network_identifier = NonCallableMock(), NonCallableMock()
        result = self.instance.delete_network(cloud, network_identifier)

        assert result is False
        self.instance.find_network.assert_called_once_with(cloud, network_identifier)
        self.network_api.delete_network.assert_not_called()

    def xtest_delete_network_rbac_forwards_find_rbac(self):
        """
        Tests that delete RBAC policy forwards the result from Openstack
        """
        self.instance.find_network_rbac = Mock()
        cloud, network_identifier = NonCallableMock(), NonCallableMock()
        self.network_api.delete_rbac_policy.return_value = None
        result = self.instance.delete_network_rbac(cloud, network_identifier)

        self.instance.find_network_rbac.assert_called_once_with(
            cloud, network_identifier
        )
        self.network_api.delete_rbac_policy.assert_called_once_with(
            self.instance.find_network_rbac.return_value, ignore_missing=False
        )
        assert result is True

    def xtest_delete_network_rbac_cant_find_rbac(self):
        """
        Tests that delete RBAc returns false if it can't find the policy to delete
        """
        self.instance.find_network_rbac = Mock(return_value=None)
        cloud, network_identifier = NonCallableMock(), NonCallableMock()
        result = self.instance.delete_network_rbac(cloud, network_identifier)

        assert result is False
        self.instance.find_network_rbac.assert_called_once_with(
            cloud, network_identifier
        )
        self.network_api.delete_rbac_policy.assert_not_called()

    @raises(ItemNotFoundError)
    def test_create_router_missing_ext_network(self):
        """
        Tests that create router will throw if the specified ext network
        was not found
        """
        self.instance.find_network = Mock(return_value=None)
        self.instance.create_router(NonCallableMock(), NonCallableMock())

    def test_create_router_successful_call(self):
        """
        Tests that create router forwards the correct args to Openstack
        """
        cloud, details = NonCallableMock(), NonCallableMock()
        self.instance.find_network = Mock()
        returned = self.instance.create_router(cloud, details)

        self.identity_module.find_mandatory_project.assert_called_once_with(
            cloud, details.project_identifier
        )
        self.instance.find_network.assert_called_once_with(
            cloud, details.external_gateway
        )
        self.mocked_connection.assert_called_once_with(cloud)

        self.network_api.create_router.assert_called_once_with(
            project_id=self.identity_module.find_mandatory_project.return_value.id,
            name=details.router_name,
            description=details.router_description,
            external_gateway_info={
                "network_id": self.instance.find_network.return_value.id
            },
            is_distributed=details.is_distributed,
            is_ha=details.is_ha,
        )
        assert returned == self.network_api.create_router.return_value

    def test_get_router(self):
        """
        Tests the get router call is correct
        """
        cloud, project, router = NonCallableMock(), NonCallableMock(), NonCallableMock()
        returned = self.instance.get_router(cloud, project, router)

        self.identity_module.find_mandatory_project.assert_called_once_with(
            cloud, project
        )
        self.mocked_connection.assert_called_once_with(cloud)
        self.network_api.find_router.assert_called_once_with(
            name_or_id=router,
            project_id=self.identity_module.find_mandatory_project.return_value.id,
            ignore_missing=True,
        )
        assert returned == self.network_api.find_router.return_value

    @raises(ItemNotFoundError)
    def test_get_used_subnet_nets_throws_missing_network(self):
        """
        Tests the ItemNotFound error is thrown if a non-existent network is specified
        """
        cloud, network = NonCallableMock(), NonCallableMock()
        self.instance.find_network = Mock(return_value=None)
        self.instance.get_used_subnet_nets(cloud, network)

    def test_get_used_subnet_nets(self):
        """
        Tests that get used subnet nets returns the expected results
        """
        self.instance.find_network = Mock()
        cloud, network = NonCallableMock(), NonCallableMock()

        subnet_1 = NonCallableMock()
        subnet_2 = NonCallableMock()

        subnet_1.gateway_ip = "192.168.134.1"
        subnet_2.gateway_ip = "10.0.123.7"

        self.network_api.subnets.return_value = [subnet_1, subnet_2]
        result = self.instance.get_used_subnet_nets(cloud, network)

        self.mocked_connection.assert_called_once_with(cloud)
        self.network_api.subnets.assert_called_once_with(
            network_id=self.instance.find_network.return_value.id
        )
        assert result == [
            ipaddress.ip_network("192.168.134.0/24"),
            ipaddress.ip_network("10.0.123.0/24"),
        ]

    def test_get_used_subnet_nets_no_subnets(self):
        """
        Tests that get used subnet nets handles an empty network
        """
        self.instance.find_network = Mock()
        cloud, network = NonCallableMock(), NonCallableMock()

        self.network_api.subnets.return_value = []
        result = self.instance.get_used_subnet_nets(cloud, network)

        self.mocked_connection.assert_called_once_with(cloud)
        self.network_api.subnets.assert_called_once_with(
            network_id=self.instance.find_network.return_value.id
        )
        assert result == []

    def test_select_random_subnet(self):
        """
        Tests create subnet correctly filters out used subnets
        """
        cloud, network = NonCallableMock(), NonCallableMock()

        # Force our random selection to always give us 32
        used_networks = [
            ipaddress.ip_network(f"192.168.{i}.0/24")
            for i in range(1, 255)
            if i is not 32
        ]
        self.instance.get_used_subnet_nets = Mock(return_value=used_networks)

        subnet = self.instance.select_random_subnet(cloud, network)
        self.instance.get_used_subnet_nets.assert_called_once_with(cloud, network)
        assert subnet == ipaddress.ip_network("192.168.32.0/24")

    def test_select_random_does_not_pass_in_used_subnets(self):
        """
        Tests create subnet correctly filters out used subnets before calling random
        """
        cloud, network = NonCallableMock(), NonCallableMock()

        # Force our random selection to always give us 32
        used_networks = [
            ipaddress.ip_network(f"192.168.{i}.0/24") for i in range(1, 100)
        ]
        self.instance.get_used_subnet_nets = Mock(return_value=used_networks)

        with patch("openstack_api.openstack_network.random.choice") as mocked_choice:
            self.instance.select_random_subnet(cloud, network)
            mocked_choice.assert_called_once()
            assert used_networks not in mocked_choice.call_args[0][0]

    @raises(ItemNotFoundError)
    def test_select_random_subnet_no_subnets(self):
        """
        Tests select random subnet throws ItemNotFoundError if not subnets are found
        """
        used_subnets = [
            ipaddress.ip_network(f"192.168.{i}.0/24") for i in range(1, 255)
        ]
        self.instance.get_used_subnet_nets = Mock(return_value=used_subnets)
        self.instance.select_random_subnet(NonCallableMock(), NonCallableMock())

    def test_create_subnet(self):
        """
        Tests create subnet creates a subnet
        """
        expected_net = "192.168.37"
        self.instance.find_network = Mock()
        self.instance.select_random_subnet = Mock(
            return_value=ipaddress.ip_network(f"{expected_net}.0/24")
        )

        cloud, network, dhcp = NonCallableMock(), NonCallableMock(), NonCallableMock()
        name, description = NonCallableMock(), NonCallableMock()
        returned = self.instance.create_subnet(cloud, network, name, description, dhcp)

        self.mocked_connection.assert_called_once_with(cloud)
        self.instance.select_random_subnet.assert_called_once_with(
            cloud, self.instance.find_network.return_value.id
        )
        self.network_api.create_subnet.assert_called_once_with(
            ip_version=4,
            network_id=self.instance.find_network.return_value.id,
            allocation_pools=[
                {"start": f"{expected_net}.11", "end": f"{expected_net}.254"}
            ],
            cidr=f"{expected_net}.0/24",
            gateway_ip=f"{expected_net}.1",
            name=name,
            description=description,
            is_dhcp_enabled=dhcp,
        )

        assert returned == self.network_api.create_subnet.return_value

    @raises(ItemNotFoundError)
    def test_create_subnet_network_not_found(self):
        """
        Tests that create subnet throws if the network specified does not exist
        """
        self.instance.find_network = Mock(return_value=None)
        self.instance.create_subnet(
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
        )
