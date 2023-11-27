import ftplib
import logging
import os
from configparser import ConfigParser
from io import BytesIO, StringIO

import paramiko
from ftpretty import ftpretty

from rcon.cache_utils import invalidates
from rcon.rcon import Rcon, invalidates
from rcon.user_config.gtx_server_name import GtxServerNameChangeUserConfig

logger = logging.getLogger(__name__)


class FTPAdapter:
    def __init__(self, ip, port, username, password) -> None:
        self.conn = ftpretty(ip, username, password, port=port)

    def get_base_path(self):
        return self.conn.list(".")[0]

    def get_file(self, remote_path, fp):
        return self.conn.get(remote_path, fp)

    def put_file(self, fp, remote_path):
        try:
            return self.conn.put(fp, remote_path)
        except ftplib.error_temp as e:
            # TODO there's a but in FTPlib when it tries to go back to the original directory
            logger.error(repr(e))


class SFTPAdapter:
    def __init__(self, ip, port, username, password) -> None:
        self.transport = paramiko.Transport((ip, port))
        self.transport.connect(username=username, password=password)
        self.conn = paramiko.SFTPClient.from_transport(self.transport)

    def get_base_path(self):
        return self.conn.listdir()[0]

    def get_file(self, remote_path, fp):
        return self.conn.getfo(remote_path, fp)

    def put_file(self, fp, remote_path):
        return self.conn.putfo(fp, remote_path)


class GTXFtp:
    def __init__(self, ip, port) -> None:
        username = os.getenv("GTX_SERVER_NAME_CHANGE_USERNAME")
        password = os.getenv("GTX_SERVER_NAME_CHANGE_PASSWORD")
        logger.info("Connecting to GTX SFTP %s@%s:%s", username, ip, port)

        if not username or not password:
            logger.error(
                "Both GTX_SERVER_NAME_CHANGE_USERNAME and GTX_SERVER_NAME_CHANGE_PASSWORD must be set in your .env"
            )
            raise ValueError(
                "Both GTX_SERVER_NAME_CHANGE_USERNAME and GTX_SERVER_NAME_CHANGE_PASSWORD must be set in your .env"
            )

        try:
            self.adapter = SFTPAdapter(ip, port, username, password)
        except:
            logger.info("Unable to use SFTP, falling back to FTP")
            self.adapter = FTPAdapter(ip, port, username, password)
        self.base_path = self.adapter.get_base_path()
        logger.debug("Connected to GTX SFTP %s@%s:%s", username, ip, port)

    @classmethod
    def from_config(cls):
        config = GtxServerNameChangeUserConfig.load_from_db()
        return cls(
            ip=config.ip,
            port=config.port,
        )

    def change_server_name(self, new_name):
        with invalidates(Rcon.get_name):
            remote_path = f"{self.base_path}/ServerConfig/Server.ini"
            logger.info("Updating name in %s", remote_path)
            f = BytesIO()
            self.adapter.get_file(remote_path, f)
            print(f.getvalue())
            config = ConfigParser()
            config.read_string(f.getvalue().decode())
            config.set("Server", "Name", f'"{new_name}"')
            temp_f = StringIO()
            config.write(temp_f)
            f = BytesIO(temp_f.getvalue().encode())
            self.adapter.put_file(f, remote_path)
            logger.info("Updated name to %s", new_name)
