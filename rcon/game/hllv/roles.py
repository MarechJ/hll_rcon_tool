"""HLL Vietnam roles, keyed by the values returned by RCON."""

from hllrcon import HLLVRole

HLLV_ROLE_IDS = {role.name.lower(): role.id for role in HLLVRole.all()}
HLLV_ROLES = frozenset(HLLV_ROLE_IDS)
HLLV_ROLE_LABELS = {
    role.name.lower(): role.pretty_name for role in HLLVRole.all()
}

__all__ = ["HLLV_ROLES", "HLLV_ROLE_LABELS", "HLLV_ROLE_IDS"]
