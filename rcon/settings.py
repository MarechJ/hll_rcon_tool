import os

# TODO: Use a config style that is not required at import time
try:
    SERVER_INFO = {        
        "host": os.getenv("HLL_HOST"),
        "port": int(os.getenv("HLL_PORT")),
        "password": os.getenv("HLL_PASSWORD")
    }
except ValueError as e:
    raise ValueError("HLL_PORT must be an integer") from e

for k, v in SERVER_INFO.items():
    if not v:
        raise ValueError(f"{k} environment variable must be set")
