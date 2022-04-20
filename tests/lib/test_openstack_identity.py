from unittest import mock
from unittest.mock import NonCallableMock

from nose.tools import raises

from openstack_identity import OpenstackIdentity
from missing_mandatory_param_error import MissingMandatoryParamError
from structs.create_project import ProjectDetails


@raises(MissingMandatoryParamError)
def test_create_project_name_missing_throws():
    """
    Tests calling the API wrapper without a domain will throw
    """
    OpenstackIdentity().create_project(
        "", ProjectDetails(name="", description="", is_enabled=False)
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
