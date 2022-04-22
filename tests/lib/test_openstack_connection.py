from unittest import mock

from nose.tools import raises

from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_api.openstack_connection import OpenstackConnection


def test_openstack_connection_connects_first_time():
    """
    Tests that connect it correctly called on entry.
    Does not check the args passed to connect
    """
    with mock.patch("openstack_api.openstack_connection.connect") as patched_connect:
        with OpenstackConnection("a") as instance:
            patched_connect.assert_called_once()
            assert instance == patched_connect.return_value


def test_openstack_connection_uses_cloud_name():
    """
    Tests that the cloud name gets used in the call to connect correctly
    """
    expected_cloud = "foo"
    with mock.patch("openstack_api.openstack_connection.connect") as patched_connect:
        with OpenstackConnection(expected_cloud):
            patched_connect.assert_called_once_with(cloud=expected_cloud)


@raises(MissingMandatoryParamError)
def test_connection_throws_for_no_cloud_name():
    """
    Tests a None type will throw if used as the account name
    """
    with mock.patch("openstack_api.openstack_connection.connect"):
        with OpenstackConnection(None):
            pass


@raises(MissingMandatoryParamError)
def test_connection_throws_for_empty_cloud_name():
    """
    Tests an empty string will throw for the cloud name
    """
    with mock.patch("openstack_api.openstack_connection.connect"):
        with OpenstackConnection(""):
            pass


@raises(MissingMandatoryParamError)
def test_connection_throws_for_whitespace_cloud_name():
    """
    Tests a whitespace string will throw for the cloud name
    """
    with mock.patch("openstack_api.openstack_connection.connect"):
        with OpenstackConnection(" \t"):
            pass


def test_openstack_connection_disconnects():
    """
    Checks the session is correctly closed (to not leak handles)
    when the context manager exits
    """
    with mock.patch("openstack_api.openstack_connection.connect") as patched_connect:
        with OpenstackConnection("a") as instance:
            connection_handle = patched_connect.return_value
            assert instance == connection_handle
        connection_handle.close.assert_called_once()


def test_openstack_connection_connects_second_time():
    """
    Tests that creating two connections calls connect twice.
    Why, because Singletons are evil and cause nothing but problems
    """
    with mock.patch("openstack_api.openstack_connection.connect") as patched_connect:
        with OpenstackConnection("a"):
            pass
        with OpenstackConnection("a"):
            assert patched_connect.call_count == 2
