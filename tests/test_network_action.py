from src.network_action import NetworkAction
from tests.openstack_action_test_case import OpenstackActionTestCase


class TestNetworkAction(OpenstackActionTestCase):
    action_cls = NetworkAction

    def test_something(self):
        assert True
