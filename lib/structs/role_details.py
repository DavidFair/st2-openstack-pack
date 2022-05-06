from dataclasses import dataclass

from enums.user_domains import UserDomains


@dataclass
class RoleDetails:
    """
    Holds relevant details for finding a user role
    """

    user_identifier: str
    user_domain: UserDomains
    project_identifier: str
    role_identifier: str
