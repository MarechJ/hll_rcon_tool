import os
from urllib.parse import urljoin

import requests


# TODO finish this stuff
class Central:
    def __init__(self, group_key=None, token=None, central_url=None):
        self.token = token or os.getenv("HLL_CENTRAL_TOKEN", None)
        self.central_url = central_url or os.getenv("HLL_CENTRAL_URL")
        self.group_key = group_key or os.getenv("HLL_CENTRAIL_GROUP_KEY", "test")

    def checkin(self, server_name, version):
        try:
            requests.post(
                urljoin(self.central_url, "checking"),
                timeout=10,
                data={
                    "server_name": server_name,
                    "version": version,
                    "group_key": group_key,
                },
                auth=("bearer", self.token),
            )
        except:
            pass

    def push_ban_list(self, ban_list):
        pass

    def pull_ban_list(self):
        pass

    def subscribe(self, foreign_group_key):
        pass
