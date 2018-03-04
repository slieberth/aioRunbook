#!/usr/bin/env python3


import asyncssh
import asyncio
import logging
import sys
import os


EXIT_OK = 0
EXIT_BAD = 1

log = logging.getLogger('noAuthSftp')

class NoAuthSSHServer(asyncssh.SSHServer):
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
        log.info("User is attempting to connect as user %s", username)
        return False # user does not require auth to connect

    def public_key_auth_supported(self):
        return False
    
    def password_auth_supported(self):
        return False
    
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


def handle_session(stdin, stdout, stderr):
    stdout.write('This is an anonymous SSH server, all actions are logged')
    stdout.channel.exit(0)



def main(argv=sys.argv[1:]):
    

    class ChrootSFTPServer(asyncssh.SFTPServer):
        def __init__(self, conn):
            super().__init__(conn, chroot="/aioRunbook/")
    
    async def start_server():
        await asyncssh.create_server(NoAuthSSHServer, '', 4712, server_host_keys=['id_rsa'],
                                     session_factory=handle_session,
                                     sftp_factory=ChrootSFTPServer)

    loop = asyncio.get_event_loop()
    
    try:
        loop.run_until_complete(start_server())
    except Exception as e:
        log.exception("Error starting server {}".format(e))



    try:
        loop.run_forever()
    except KeyboardInterrupt:
        log.info("User abort")
    
    
if __name__ == "__main__":
    main()


