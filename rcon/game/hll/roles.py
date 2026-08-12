"""HLL/WW2 role catalog compatibility exports."""

from rcon.types import ROLES_TO_LABELS, Roles

HLL_ROLES = frozenset(role.value for role in Roles)
HLL_ROLE_LABELS = {role.value: label for role, label in ROLES_TO_LABELS.items()}

__all__ = ["HLL_ROLES", "HLL_ROLE_LABELS"]
