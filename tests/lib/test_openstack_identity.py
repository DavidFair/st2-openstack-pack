from unittest import mock
from unittest.mock import NonCallableMock

from nose.tools import raises

from openstack_identity import OpenstackIdentity
from missing_mandatory_param_error import MissingMandatoryParamError
from structs.create_project import ProjectDetails


@raises(MissingMandatoryParamError)
def test_domain_missing_throws():
    """
    Tests calling the API wrapper without a domain will throw
    """
    OpenstackIdentity().find_domain("account", domain="")


def test_forwards_find_domain_result():
    """
    Tests that the params and result are forwarded as-is to/from the
    find_domain API
    """
    instance = OpenstackIdentity()
    with mock.patch("openstack_identity.OpenstackConnection") as patched_connection:
        identity_api = patched_connection.return_value.__enter__.return_value.identity
        expected = NonCallableMock()

        found = instance.find_domain(cloud_account="test", domain=expected)

        patched_connection.assert_called_once_with("test")

        assert found == identity_api.find_domain.return_value
        identity_api.find_domain.assert_called_once_with(
            name_or_id=expected, ignore_missing=True
        )


def test_forwards_create_project():
    """
    Tests that the params and result are forwarded as-is to/from the
    create_project API
    """
    instance = OpenstackIdentity()

    expected_details = ProjectDetails(
        name=NonCallableMock(),
        description=NonCallableMock(),
        is_enabled=NonCallableMock(),
        domain_id=NonCallableMock(),
    )

    with mock.patch("openstack_identity.OpenstackConnection") as patched_connection:
        identity_api = patched_connection.return_value.__enter__.return_value.identity
        found = instance.create_project(
            cloud_account="test", project_details=expected_details
        )

        patched_connection.assert_called_once_with("test")

        assert found == identity_api.create_project.return_value
        identity_api.create_project.assert_called_once_with(
            name=expected_details.name,
            description=expected_details.description,
            domain_id=expected_details.domain_id,
            is_enabled=expected_details.is_enabled,
        )
