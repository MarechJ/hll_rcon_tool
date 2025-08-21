from typing import Optional
from hllrcon.client import RconClient
from rcon.settings import RconCredentials, get_rcon_credentials

_CRCON: Optional("CRcon") = None

def get_crcon(credentials: RconCredentials | None = None):
    global _CRCON
    
    # Return already initialized CRcon instance if any exists
    if _CRCON is not None:
        return _CRCON

    # Load default rcon credentials from the environment if none provided
    if not credentials:
        credentials = get_rcon_credentials()

    # Create new instance and cache it
    _CRCON = CRcon(credentials)
    return _CRCON

    
class CRcon(RconClient):
    """A RconClient wrapper """

    def __init__(self, credentials: RconCredentials) -> None:
        super().__init__(credentials)
