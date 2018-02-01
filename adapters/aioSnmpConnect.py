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

#  \version   0.1.1
#  \date      01.02.2018
#  \modification:
#  0.1.1 - get started


import logging
import argparse
from pysnmp.hlapi import *                              #used for v2x
from pysnmp.entity import engine, config                #used for v3
from pysnmp.carrier.asynsock.dgram import udp           #used for v3
from pysnmp.entity.rfc3413 import cmdgen                #used for v3
import datetime
import sys
import os
import time
import pprint


import asyncio
#from threading import Thread

sys.path.insert(0, os.path.abspath('../tools'))
from tools.helperFunctions import _isInDictionary

class aioSnmpConnect:

    def __init__(self,stepDict,method="snmp",port=161,configDict={}):
        #logging.info ("snmpConnect stepDict: {}".format(stepDict))   
        self.stepDict = stepDict
        self.configDict = configDict
        self.hostname = stepDict["device"]
        #self.vendor= "snmp"   
        self.port = _isInDictionary ("port",stepDict,port)
        self.startShellCommand = ""         
        self.initConnectTs = datetime.datetime.now()
        self.snmpEngine = SnmpEngine()
        self.snmpVersion = _isInDictionary ("version",stepDict,"v2c")
        if self.snmpVersion == "v2c":
            self.udpTransportTarget = UdpTransportTarget((self.hostname, self.port),
                                                      retries=0, 
                                                      timeout=3)
            communityString = _isInDictionary ("community",stepDict,"")
            self.snmpCommunity = CommunityData(communityString)
        elif self.snmpVersion == "v3":
            # Create SNMP engine instance
            self.snmpEngine = engine.SnmpEngine()
            logging.debug("v3 self.snmpEngine {} ".format(self.snmpEngine))
            self.securityLevel = _isInDictionary ("securityLevel",stepDict,"")
            self.securityName = _isInDictionary ("securityName",stepDict,"")
            self.authProtocol = _isInDictionary ("authProtocol",stepDict,"SHA")
            self.privProtocol = _isInDictionary ("privProtocol",stepDict,"AES")
            self.authKey = _isInDictionary ("authKey",stepDict,"")
            self.privkey = _isInDictionary ("privkey",stepDict,"")
            if self.authProtocol == "SHA" and self.privProtocol == "AES":
                config.addV3User(
                    self.snmpEngine, self.securityName,
                    config.usmHMACSHAAuthProtocol, self.authKey,
                    config.usmAesCfb128Protocol, self.privkey
                    )
                logging.debug("config.addV3User {} ".format(config.addV3User))
                config.addTargetParams(self.snmpEngine, 'my-creds', self.securityName, self.securityLevel)
            else:
                logging.debug("unsopprted authProtocol {} privProtocol {}".format(self.authProtocol,self.privProtocol))
                raise Exception ("unsopprted authProtocol {} privProtocol {}".format(self.authProtocol,self.privProtocol))
            config.addSocketTransport(
                self.snmpEngine,
                udp.domainName,
                udp.UdpSocketTransport().openClientMode()
            )
            config.addTargetAddr(
                self.snmpEngine, 'my-router',
                udp.domainName, (self.hostname, self.port),
                'my-creds'
            )
        else:
            logging.error("unsopprted snmp version {}".format(self.snmpVersion))
            raise Exception ("unsopprted snmp version {}".format(self.snmpVersion))
        logging.debug ("snmpConnect.__init__ succeeded to host: " + self.hostname)   
  

    async def sendSnmpRequests(self,loopExector,timeout = -1):
        def blocking_task ():
            for i,command in enumerate(self.stepDict["commands"]):
                #print(self.stepDict["commands"])
                logging.debug('sendSnmpRequests command: {}'.format(command))
                t1=datetime.datetime.now()
                self.stepDict["output"][i]["startTS"] = t1.strftime('%Y-%m-%d %H:%M:%S.%f')  
                if isinstance(command, str):
                    splitList = command.split(" ")
                    if len(splitList) < 2:
                        logging.error ("incorrect snmp command length: {}".format(command))
                    elif len(splitList) == 2:
                        snmpCommand = splitList[0]
                        # currently only support for get command
                        snmpOid = splitList[1]
                    elif len(splitList) == 3:
                        # set type not supported yet ...
                        snmpCommand = splitList[0]
                        snmpOid = splitList[1]
                        snmpValue = splitList[2]
                    else :
                        logging.error ("incorrect snmp command length: {}".format(command))
                logging.debug('sendSnmpRequest command {} oid {}'.format(snmpCommand,snmpOid))


                if self.snmpVersion == "v2c":
                    # currently only support for get command
                    errorIndication, errorStatus, errorIndex, varBinds = next(
                        getCmd(self.snmpEngine,
                               self.snmpCommunity,
                               self.udpTransportTarget,
                               ContextData(),
                               ObjectType(ObjectIdentity(snmpOid)))
                    )

                    if errorIndication:
                        logging.warning('OID {} not fetched: {}'.format(snmpOid, errorIndication))

                    elif errorStatus:
                        logging.warning('OID {} not fetched: {}'.format(snmpOid, errorStatus.prettyPrint()))
                    else:
                        returnStringList = []
                        for varBind in varBinds:
                            logging.info('fetched {}'.format(' = '.join([x.prettyPrint() for x in varBind])))
                            #logging.info('varbind {}'.format([x.prettyPrint() for x in varBind]))
                            #returnStringList.append(' = '.join([x.prettyPrint() for x in varBind]))
                            returnStringList.append(str(varBind[1]))
                    t2=datetime.datetime.now()
                    self.stepDict["output"][i]["endTS"] = t2.strftime('%Y-%m-%d %H:%M:%S.%f')   
                    self.stepDict["output"][i]["elapsed"] = str((t2-t1))
                    self.stepDict["output"][i]["elapsedRaw"] = (t2-t1).total_seconds()
                    self.stepDict["output"][i]["output"] = '\n'.join(returnStringList)
                    #return '\n'.join(returnStringList)

                elif self.snmpVersion == "v3":
                    self.returnStringList = []
                    def cbFun(sendRequestHandle,
                              errorIndication, errorStatus, errorIndex,
                              varBindTable, cbCtx):
                        if errorIndication:
                            logging.error("cbFun errorIndication: {}".format(errorIndication))
                        elif errorStatus:
                            logging.error('cbFun errorStatus %s at %s' % (
                                errorStatus.prettyPrint(),
                                errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'
                                )
                            )
                        else:
                            for varBind in varBindTable:
                                logging.debug('fetched {}'.format(' = '.join([x.prettyPrint() for x in varBind])))
                                #logging.debug('varbind {}'.format([x.prettyPrint() for x in varBind]))
                                self.returnStringList.append(str(varBind[1]))


                    # Prepare and send a request message

                    commaSeparatedOidList = [ int(x) for x in snmpOid.split(".") ]
                    cmdgen.GetCommandGenerator().sendReq(
                        self.snmpEngine,
                        'my-router',
                        ( (commaSeparatedOidList, None), ),
                        cbFun
                    )

                    # Run I/O dispatcher which would send pending queries and process responses
                    self.snmpEngine.transportDispatcher.runDispatcher()
                    logging.debug('returnlist: {}'.format(self.returnStringList))
                    returnString = '\n'.join(self.returnStringList)
                    logging.info('snmp returnString: {}'.format(returnString))
                    t2=datetime.datetime.now()
                    self.stepDict["output"][i]["endTS"] = t2.strftime('%Y-%m-%d %H:%M:%S.%f')   
                    self.stepDict["output"][i]["elapsed"] = str((t2-t1))
                    self.stepDict["output"][i]["elapsedRaw"] = (t2-t1).total_seconds()
                    self.stepDict["output"][i]["output"] = returnString
                    #return returnString
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(loopExector,blocking_task, )

 
