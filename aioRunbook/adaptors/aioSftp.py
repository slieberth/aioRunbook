# Copyright (c) 2018 by Stefan Lieberth <stefan@lieberth.net>.
# All rights reserved.
#
# This program and the accompanying materials are made available under
# the terms of the Eclipse Public License v1.0 which accompanies this
# distribution and is available at:
#
#     http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#     Stefan Lieberth - initial implementation, API, and documentation

#  \version   0.1.2
#  \date      01.02.2018
#  \modification:
#  0.1.1 - get started

#  \modification
#  0.1.1 base line for history
#  0.1.2 work for await - universalize adapter access

import asyncio, asyncssh, sys
import logging
import os
#sys.path.insert(0, os.path.abspath('../tools'))
from aioRunbook.tools.helperFunctions import _isInDictionary



class aioSftp:
    """asyncio sftp client based on asyncssh

          :param stepDict: the specific test step dictionary. The stepDict includes the attributes for device access and the commands to be executed.
          :param stepDict["device"]: defines the IP address of the device under test. tested with IPv4 only. 
          :param stepDict["port"]: defines the TCP port for the session. Optional, default = 22.
          :param stepDict["user"]: defines the user for ssh authentication
          :param stepDict["password"]: defines the clear text password for user authentication
          :param stepDict["enc-password"]: defines the encrypted password for user authentication
          :param stepDict["direction"]: defines the direction of the ftp file transfer. either get or put, optional, default is "get"
          :param stepDict["remote"]: defines the remote file name. Madatory for direction get
          :param stepDict["local"]: defines the local file name. Madatory for direction put
          :param stepDict["timeout"]: defines a specific timeout for this step for ssh interactions, default = 60 secs.
          :param configDict: optional, the overall test dictionary.
          :param configDict["config"]["timeout"]: optional, defines the generic timeout for all steps
          :param configDict["config"]["user"]: optional, defines the generic user for all steps. Has lower precedence than the user attribute in stepDict.
          :param configDict["config"]["password"]: optional, defines the generic clear-text password for all steps. Has lower precedence than the user attribute in stepDict.
          :param configDict["config"]["enc-password"]: optional, defines the generic encrypted password for all steps. Has lower precedence than the user attribute in stepDict.
          :type stepDict: dict
          :type stepDict["device"]: string   
          :type stepDict["port"]: int  
          :type stepDict["user"]: string   
          :type stepDict["password"]: string   
          :type stepDict["enc-password"]: string   
          :type stepDict["direction"]: string  
          :type stepDict["remote"]: string
          :type stepDict["local"]: string
          :type stepDict["timeout"]: int
          :type configDict: dict
          :type configDict["config"]["timeout"]: int
          :type configDict["config"]["user"]: string   
          :type configDict["config"]["password"]: string   
          :type configDict["config"]["enc-password"]: string   

    """

    def __init__(self,stepDict,configDict = {"config":{}},port=22,eventLoop=None,**kwargs): 
        self.stepDict = stepDict
        self.hostname = stepDict["device"]
        self.port = _isInDictionary ("port",stepDict,port)
        self.stepDict = stepDict
        self.username = _isInDictionary ("user",configDict["config"],None)
        self.username = _isInDictionary ("user",stepDict,self.username)
        self.password = _isInDictionary ("password",configDict["config"],None)     
        if "enc-password" in configDict["config"].keys():
            logging.debug('enc-password: {0}'.format(configDict["config"]["enc-password"]))
            self.password = base64.b64decode(base64.b64decode(configDict["config"]["enc-password"]).decode('utf-8')).decode('utf-8') ##SECURE##
        self.password = _isInDictionary ("password",stepDict,self.password)
        if "enc-password" in stepDict.keys():
            logging.debug('enc-password: {0}'.format(stepDict["enc-password"]))
            self.password = base64.b64decode(base64.b64decode(stepDict["enc-password"]).decode('utf-8')).decode('utf-8') ##SECURE##
            logging.debug('password: {0}'.format(self.password))     
        if self.password == None:
            logging.error('password not set for stepDict: {0}'.format(stepDict)) 
        self.timeout = _isInDictionary ("timeout",configDict["config"],60)
        self.timeout = _isInDictionary ("timeout",stepDict,self.timeout)
        #self.sshConnectLoop = asyncio.new_event_loop()
        #self.sshConnectLoop.set_debug(True)
        #asyncio.set_event_loop(self.sshConnectLoop)


    async def execCopy (self):
        logging.debug('execCopy {0}'.format(self.stepDict["hostname"]))
        direction = _isInDictionary ("direction",self.stepDict,"get")


        try:
            self._conn = await asyncio.wait_for(asyncssh.connect(self.hostname, 
                                username=self.username, 
                                password=self.password), timeout=self.timeout)
            self.sftpClient = await asyncio.wait_for(self._conn.start_sftp_client(),timeout=self.timeout)    
        except:
            logging.error ("aioSftp connect to {} finally failed".format(self.hostname))  
            self._conn = None
            return False
        else:
            logging.debug ("aioSftp connect login {} succeeded".format(self.hostname)) 
        if direction == "get":
            try: 
                remoteFile = self.stepDict["remote"]
            except:
                logging.error ("aiosFTP get without remote attribute".format(self.hostname))  
                return False    
            try: 
                await asyncio.wait_for(self.sftpClient.get(remoteFile),timeout=self.timeout) 
            except:
                logging.error ("aioSshConnect.execCopy from {} {}".format(self.hostname,remoteFile))  
                return False        
            else:
                logging.error ("aioSshConnect.execCopy get {} succeeded" .format(remoteFile))  
                self._conn.close()
        if direction == "put":
            try: 
                localFile = self.stepDict["local"]
            except:
                logging.error ("aiosFTP put without local attribute".format(self.hostname))  
                return False    
            try: 
                await asyncio.wait_for(self.sftpClient.put(localFile),timeout=self.timeout) 
            except:
                logging.error ("aioSshConnect.execCopy to {} {}".format(self.hostname,localFile))  
                return False        
            else:
                logging.error ("aioSshConnect.execCopy put {} succeeded" .format(localFile))  
                self._conn.close()

        #self.sshConnectLoop.run_until_complete(task(self))





