#!/usr/bin/env python3


import asyncssh
import asyncio
import logging
import sys
import os
import yaml
from collections import namedtuple
import pprint

EXIT_OK = 0
EXIT_BAD = 1

log = logging.getLogger('authSftpServer')


ymlConfigString = """#
httpPort: 4711
userAuth:
- - username: MajorTom
  - password: test
  - permissions: 
    - viewResults
    - runTests
    - editTests
"""

configDict = yaml.load(ymlConfigString)

userNamedTuple = namedtuple('User', ['username', 'password', 'permissions'])
authUserDict = {}
user_map = {}
for authUser in configDict["userAuth"]:
    user = userNamedTuple(authUser[0]["username"],authUser[1]["password"],authUser[2]["permissions"])
    user_map[authUser[0]["username"]] = userNamedTuple(authUser[0]["username"],authUser[1]["password"],authUser[2]["permissions"])


class authSSHServer(asyncssh.SSHServer):
    def connection_made(self, conn):
        self._conn = conn
        peer = conn.get_extra_info('peername')
        username = conn.get_extra_info('username')
        log.info("New connection from: {} {} {}".format(self._conn,peer,username))

        
    def connection_lost(self, exc):
        conn = self._conn

        if exc:
            log.info('Error during connection {}'.format(exc))
            
    
    ################
    # Auth Methods #
    ################
    def begin_auth(self, username):
        return True

    def public_key_auth_supported(self):
        return False
    
    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        #pw = passwords.get(username, '*')
        return password == user_map[username][1]
    
    def kbdint_auth_supported(self):
        return False
        
    ##############
    # Subsystems #
    ##############
    # sftp is a subssytem inside a session, dont override this
    # and we can reuse the default implementation
#    def session_requested(self):
#        return False
    
    def connection_requested(self, *args):
        return False
    
    def unix_connection_requested(self, *args):
        return False
        
    def server_requested(self, *args):
        return False

    def unix_server_requested(self, *args):
        return False

######

class ChrootSFTPServer(asyncssh.SFTPServer):
    def __init__(self, conn):
        super().__init__(conn, chroot=".")
    
    async def start_server(configDict):
        #pprint.pprint(configDict)
        sftpPort = configDict["sftpPort"]
        sftpServerHostKeyFile = os.path.abspath(configDict["sftpServerHostKeyFile"])

        await asyncssh.create_server(authSSHServer, '', sftpPort, server_host_keys=sftpServerHostKeyFile,
                                     session_factory=ChrootSFTPServer.handle_session,
                                     sftp_factory=ChrootSFTPServer)


    def handle_session(self,stdin, stdout, stderr):
        stdout.channel.exit(0)

####

    
    
if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    
    try:
        loop.run_until_complete(ChrootSFTPServer.start_server(configDict))
    except Exception as e:
        log.exception("Error starting server {}".format(e))


    try:
        loop.run_forever()
    except KeyboardInterrupt:
        log.info("User abort")


