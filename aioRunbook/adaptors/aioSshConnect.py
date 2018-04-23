#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

#  \modification
#  0.1.1 base line for history
#  0.1.2 add disconnect / close function
#  0.1.3 work in respect to asyncio loop fix
#  0.1.4 clean up 
#  0.1.5 clean up 


import asyncio
import random
import logging
import yaml
from copy import deepcopy
import asyncssh
import pprint
import datetime
import os
import sys
import base64
import re
#sys.path.insert(0, os.path.abspath('../tools'))
from aioRunbook.tools.helperFunctions import _isInDictionary, _addTimeStampsToStepDict


VENDOR_DICT = { "juniper" : { "initPrompt" : ">", 
                            "lambdaCliPrompt" : lambda output : [ output.rstrip().split("\n")[-1][:-1] + "(>|#)" ] ,
                            "stripPrologueLines" : 1,
                            "stripEpilogueLines" : 2,
                            "initCmds" : [ "set cli screen-length 0\n"],
                            "outputCorrections" : [ lambda output : re.sub(r'(\r\n|\r|\n)', '\n',  output) ] } ,
                "cisco" : { "initPrompt" : "#", 
                            "lambdaCliPrompt" : lambda output : [ output.strip(), output.strip()[:-1]+'\\(.*\\)#' ],
                            "stripPrologueLines" : 2,
                            "stripEpilogueLines" : 1,
                            "initCmds" : [ "terminal length 0\n"],
                            "outputCorrections" : [ lambda output : re.sub(r'(\r\n|\r|\n)', '\n',  output) , 
                                                    lambda output : re.sub(r'\x08','', output)                ] } ,   
                "ubuntu" : { "initPrompt" : "$ ", 
                            "lambdaCliPrompt" : lambda output : [ output.rstrip().lstrip()[:-2] + "\S*\$ " ],
                            "stripPrologueLines" : 1,
                            "stripEpilogueLines" : 1,
                            "initCmds" : [],
                            "outputCorrections" : [ lambda output : re.sub(r'(\r\n|\r|\n)', '\n',  output) , 
                                                    lambda output : re.sub(r'\[\d+(;\d+)*m', '', output)  ] } }

PERSISITANT_SSH_TIMER = 15


class aioSshConnect():
    """asyncio ssh client. Based in `asyncssh <http://asyncssh.readthedocs.io/en/latest/>`_

          :param stepDict: the specific test step dictionary. The stepDict includes the attributes for device access and the commands to be executed.
          :param stepDict["device"]: defines the IP address of the device under test. tested with IPv4 only. 
          :param stepDict["port"]: defines the TCP port for the session. Optional, default = 22.
          :param stepDict["vendor"]: defines the vendor type for this ssh connection. currently ubuntu, juniper and cisco are supported 
          :param stepDict["user"]: defines the user for ssh authentication
          :param stepDict["password"]: defines the clear text password for user authentication
          :param stepDict["enc-password"]: defines the encrypted password for user authentication
          :param stepDict["commands"]: defines the list for all commands. \n
          :param stepDict["timeout"]: defines a specific timeout for this step for ssh interactions, default = 60 secs.
          :param stepDict["optionalPrompt"]: is useful to react for confirmation request, for which the usuall prompt does not match
          :param stepDict["optionalPrompts"]: is useful to react for confirmation request, but for more than one optional prompts
          :param configDict: optional, the overall test dictionary.
          :param configDict["config"]["timeout"]: optional, defines the generic timeout for all steps
          :param configDict["config"]["user"]: optional, defines the generic user for all steps. Has lower precedence than the user attribute in stepDict.
          :param configDict["config"]["password"]: optional, defines the generic clear-text password for all steps. Has lower precedence than the user attribute in stepDict.
          :param configDict["config"]["enc-password"]: optional, defines the generic encrypted password for all steps. Has lower precedence than the user attribute in stepDict.
          :type stepDict: dict
          :type stepDict["device"]: string   
          :type stepDict["port"]: int  
          :type stepDict["vendor"]: string   
          :type stepDict["user"]: string   
          :type stepDict["password"]: string   
          :type stepDict["enc-password"]: string   
          :type stepDict["commands"]: list of strings  
          :type stepDict["timeout"]: int
          :type stepDict["optionalPrompt"]: string
          :type stepDict["optionalPrompts"]: list of strings
          :type configDict: dict
          :type configDict["config"]["timeout"]: int
          :type configDict["config"]["user"]: string   
          :type configDict["config"]["password"]: string   
          :type configDict["config"]["enc-password"]: string   

    """

    def __init__(self,stepDict,configDict = {"config":{}},port=22,eventLoop=None,**kwargs): 

        #def __init__(self,configDict,stepDict,method="ssh",port=22):
        self.hostname = stepDict["device"]
        self.vendor= stepDict["vendor"]
        self.port = _isInDictionary ("port",stepDict,port)
        #logging.debug('port: {0}'.format(self.port))
        self.startShellCommand = _isInDictionary ("startShellCommand",stepDict,"")
        if self.vendor in [ "juniper" , "cisco" , "ubuntu" ] :
            self.stripPrologueLines = _isInDictionary("stripPrologueLines",stepDict,VENDOR_DICT[self.vendor]["stripPrologueLines"])
            self.stripEpilogueLines = _isInDictionary("stripEpilogueLines",stepDict,VENDOR_DICT[self.vendor]["stripEpilogueLines"])
        self.stepDict = stepDict
        self.device = stepDict["device"]
        self.port = _isInDictionary ("port",stepDict,22)
        self.vendor = stepDict["vendor"]
        self.username = _isInDictionary ("user",configDict["config"],None)
        self.username = _isInDictionary ("user",stepDict,self.username)
        self.password = _isInDictionary ("password",configDict["config"],None)     
        if "enc-password" in configDict["config"].keys():
            logging.debug('generic enc-password: {0}'.format(configDict["config"]["enc-password"]))
            self.password = base64.b64decode(base64.b64decode(configDict["config"]["enc-password"]).decode('utf-8')).decode('utf-8') ##SECURE##
        self.password = _isInDictionary ("password",stepDict,self.password)
        if "enc-password" in stepDict.keys():
            logging.debug('device enc-password: {0}'.format(stepDict["enc-password"]))
            self.password = base64.b64decode(base64.b64decode(stepDict["enc-password"]).decode('utf-8')).decode('utf-8') ##SECURE##
            #logging.debug('password: {0}'.format(self.password))     
        if self.password == None:
            logging.error('password not set for stepDict: {0}'.format(stepDict)) 
        else
            logging.debug('password is set')     
        self.timeout = _isInDictionary ("timeout",configDict["config"],60)
        self.timeout = _isInDictionary ("timeout",stepDict,self.timeout)
        self.optionalPrompt = _isInDictionary("optionalPrompt",stepDict,None)
        if self.optionalPrompt: 
            self.optionalPrompts = [self.optionalPrompt]
        else:
            self.optionalPrompts = []
        self.optionalPrompts = _isInDictionary("optionalPrompts",stepDict,self.optionalPrompts)
        self.t1=datetime.datetime.now()

    async def connectAndRunCommands(self,**kwargs):
        """This function establishes the communication channel to the device by
        setting the pexpect.spawn object in self.device and perform the user auth with
        the credentials stored in self.username ans self.password.
        
        :param timeout: The timeout for user credential negotiation.
        :type timeout: int. 
        :returns: boolean -- True if channel has been established and  
        :raises: Exception if self.method is not ssh or telnet.

        """ 
        delayTimer=0 ###FIXME as kwargs
        t1 = datetime.datetime.now() 
        #
        #   FIXME implemnt mutual excluse of background and persistance
        # 
        self.reuseConnection = False
        self._conn = None
        self.backgroundStep = _isInDictionary("startInBackground",self.stepDict,False)
        self._sessionTag = self.getSessionTag()
        if not  self.backgroundStep:
            if "sshConnectionTags" in kwargs:
                logging.debug("_sessionTag: {}".format(self._sessionTag))
                if self._sessionTag in  kwargs["sshConnectionTags"]:
                    self.reuseConnection = True
                    logging.debug('reusing {} {}'.format(self.stepDict["name"],kwargs["sshConnectionTags"][self._sessionTag ]))
                    self._conn =   kwargs["sshConnectionTags"][self._sessionTag]["_conn"]
                    self._stdin =   kwargs["sshConnectionTags"][self._sessionTag]["_stdin"]
                    self._stdout =  kwargs["sshConnectionTags"][self._sessionTag]["_stdout"]
                    self._stderr =  kwargs["sshConnectionTags"][self._sessionTag]["_stderr"]
                    #self._sessionTag = kwargs["sshConnectionTags"][self.sessionTag]["_sessionTag"]
                    self.rePromptList = kwargs["sshConnectionTags"][self._sessionTag]["rePromptList"]   
        if not self.reuseConnection:
            logging.debug('connect {} {}'.format(self.stepDict["hostname"],self.stepDict["device"]))
            #def task(self):
            try:
                if self.stepDict["sshKnownHostsCheck"]:
                    self._conn = await asyncio.wait_for(asyncssh.connect(self.hostname,port=self.port,
                                        username=self.username, 
                                        password=self.password), timeout=self.timeout)
                else:
                    self._conn = await asyncio.wait_for(asyncssh.connect(self.hostname,port=self.port,
                                        username=self.username, 
                                        known_hosts = None,       
                                        password=self.password), timeout=self.timeout)
                self._stdin, self._stdout, self._stderr = await self._conn.open_session(term_type='Dumb', term_size=(200, 24))
            except:
                logging.error ("aioSshConnect.connect to {} failed".format(self.hostname))  
                self._conn = None
                #return False
            if self._conn:
                if self.vendor in [ "juniper" , "cisco" , "ubuntu" ] :
                    foundPrompt = False
                    while not foundPrompt:
                        output = await self._stdout.read(64000)
                        if VENDOR_DICT[self.vendor]["initPrompt"] in output: foundPrompt = True  
                    self.rePromptList = VENDOR_DICT[self.vendor]["lambdaCliPrompt"](output)
                    if self.optionalPrompts != []:
                        self.rePromptList += self.optionalPrompts
                    logging.debug ("{} set prompts to {}".format(self.stepDict["name"],self.rePromptList))
                    for initCmd in VENDOR_DICT[self.vendor]["initCmds"]:
                        self._stdin.write(initCmd )
                        output = ""
                        gotPrompt = False
                        while not gotPrompt:
                            output += await self._stdout.read(64000)
                            for rePattern in self.rePromptList:
                                if re.search(rePattern,output): gotPrompt = True   
                    if not self. backgroundStep:
                        kwargs["sshConnectionTags"][self._sessionTag] = {"_conn":self._conn,
                            "_stdin":self._stdin,
                            "_stdout":self._stdout,
                            "_stderr":self._stderr,
                            "rePromptList":self.rePromptList,
                            "_sessionTag":self._sessionTag,
                            "tsLastUsage":self.t1}

        if self._conn: 
            time = await asyncio.sleep(delayTimer)
            for i,command in enumerate(self.stepDict["commands"]):
                logging.debug("step {} sending command {}".format(self.stepDict["name"],command))
                #self.stepDict["output"][i]["startTS"] = t1.strftime('%Y-%m-%d %H:%M:%S.%f')   
                self._stdin.write(command + "\n")
                output = ""
                gotPrompt = False
                try:
                    while not gotPrompt:
                        output += await asyncio.wait_for(self._stdout.read(64000),timeout=self.timeout)
                        for rePattern in self.rePromptList:
                            if re.search(rePattern,output): gotPrompt = True
                except Exception as e:
                    logging.warning ("prompt timeout step {} command {} {}".format(self.stepDict["stepCounter"],i+1,e))
                t2=datetime.datetime.now()
                for correctionLambda in VENDOR_DICT[self.vendor]["outputCorrections"]:
                    output = correctionLambda(output)
                output = "\n".join(output.split("\n")[self.stripPrologueLines:-self.stripEpilogueLines])
                #logging.debug ("step {} output {}".format(self.stepDict["name"],output))
                logging.debug ("recv output step {} cmd {}".format(self.stepDict["name"],i+1))
                _addTimeStampsToStepDict(t1,self.stepDict,i)  
                self.stepDict["output"][i]["output"] = output
            if self.backgroundStep:
                self._conn.close()
                logging.debug ("disconnected ssh Session: {}".format(self._conn))
            return self.stepDict["output"]
        else:
            for i,command in enumerate(self.stepDict["commands"]):
                t1=datetime.datetime.now()
                self.stepDict["output"][i]["output"] = "ssh connect error"
                _addTimeStampsToStepDict(t1,self.stepDict,i)
                return self.stepDict["output"]


    async def disconnect (self):
        #print ("self._conn.close() {}".format(self._conn))
        if self._conn:
            self._conn.close()
            logging.debug ("disconnected ssh Session: {}".format(self._conn))
        return True

    def getSessionTag (self):
        backgroundStep = _isInDictionary("startInBackground",self.stepDict,False)
        if backgroundStep:
            return "ssh-{}-{}-{}-bg".format(self.hostname,self.port,self.username)
        else:
            return "ssh-{}-{}-{}-fg".format(self.hostname,self.port,self.username)

#     def setConn (self,connDict):
#         self._conn = connDict["_conn"]
#         self._stdin = connDict["_stdin"]
#         self._stdout = connDict["_stdout"]
#         self._stderr = connDict["_stderr"]
#         self.rePromptList = connDict["rePromptList"]   
#         self.tsLastUsage = datetime.datetime.now()       


    def getConn (self):
        return {"_conn":self._conn,
                "_stdin":self._stdin,
                "_stdout":self._stdout,
                "_stderr":self._stderr,
                "rePromptList":self.rePromptList,
                "_sessionTag":self._sessionTag,
                "tsLastUsage":self.t1}

    @classmethod
    def checkConnUsageTimer (self,connDict):
        t1 = connDict["tsLastUsage"] 
        t2 = datetime.datetime.now()
        if (t2-t1).total_seconds() < PERSISITANT_SSH_TIMER:
            return False
        else:
            return True

    @classmethod
    async def disconnectStoredSession (self,connTag,connDict):
        if connDict["_conn"]:
            connDict["_conn"].close()
            logging.debug ("disconnected ssh Session: {}".format(connTag))
        return True

    @classmethod
    async def pruneAgedSessions(self,sshConnectionTags):
        delKeys = []
        for connKey in sshConnectionTags.keys():  
            if aioSshConnect.checkConnUsageTimer(sshConnectionTags[connKey]):                
                await aioSshConnect.disconnectStoredSession(connKey,sshConnectionTags[connKey])
                delKeys.append(connKey)
                logging.debug ("destroyed session: {}".format(connKey))
            else:
                logging.debug ("keep session: {}".format(connKey))
        for connKey in delKeys:  
            del sshConnectionTags[connKey]



