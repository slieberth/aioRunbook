#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  \author    Stefan Lieberth / Maik Pfeil
#  \version   3.01.04
#  \date      27.7.2017

import logging
import argparse
from ncclient import manager
import datetime
import sys
import os
import time
import pprint


import asyncio
from aioRunbook.tools.helperFunctions import _isInDictionary, _addTimeStampsToStepDict

class aioNetconfConnect:

    def __init__(self,stepDict,method="netconf",port=830,configDict={}):
        self.stepDict = stepDict
        self.configDict = configDict
        self.hostname = stepDict["device"]
        self.vendor = stepDict["ncclientVendor"]   
        self.port = _isInDictionary ("port",stepDict,port)
        self.startShellCommand = ""         
        self.initConnectTs = datetime.datetime.now()
        self.myNetconfConnection = manager.connect(host=self.hostname,
            port=self.port,
            username=stepDict["user"],
            password=stepDict["password"],
            timeout=10,
            device_params = {'name': stepDict["ncclientVendor"] },
            hostkey_verify=False)
        logging.info ("netconfConnect.__init__ succeeded: prompt {} {}".format(self.hostname,self.port ))   
  

    async def sendNetconfRequests(self,loopExector,timeout = -1):
        def blocking_task ():
            for i,command in enumerate(self.stepDict["commands"]):
                logging.debug('sendNetconfRequests {}'.format(command))
                t1=datetime.datetime.now()
                if isinstance(command, str):
                    splitList = command.split(" ")
                    if len(splitList) < 2:
                        logging.error ("incorrect netconf command length: {}".format(command))
                    elif len(splitList) == 2:
                        netconfCommand = splitList[0]
                        netconfAttribute = splitList[1]
                    else :
                        logging.error ("incorrect netconf command length: {}".format(command))
                logging.debug('sendNetconfRequests {}("{}")'.format(netconfCommand,netconfAttribute))
                netconfResponse = eval('self.myNetconfConnection.{}("{}")'.format(netconfCommand,netconfAttribute))
                #return str(netconfResponse)
                #output = "\n".join(output.split("\n")[self.stripPrologueLines:-self.stripEpilogueLines])
                _addTimeStampsToStepDict(t1,self.stepDict,i)  
                self.stepDict["output"][i]["output"] = str(netconfResponse)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(loopExector,blocking_task, )
