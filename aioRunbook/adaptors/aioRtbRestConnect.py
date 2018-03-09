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

#  \version   0.1.3
#  \date      01.02.2018
#  \modification:
#  0.1.2 - get started
#  0.1.2 - completed COMMAND_DICT


 #  \modification
#  0.1.1 base line for history
#  0.1.2 work for asyncio loop fix
#  0.1.3 cleanup: COMMAND_DICT 

import asyncio
import logging
import json
import yaml
import pprint
import datetime
import os
import sys
import aiohttp
from aioRunbook.tools.helperFunctions import _isInDictionary, _addTimeStampsToStepDict

COMMAND_DICT = {"setObjectsFromJsonFile"    : { "urlSuffix": "/bds/object/add", "httpCommand": "POST" },
                "delObjectsFromJsonFile"    : { "urlSuffix": "/bds/object/delete", "httpCommand": "POST" },
                "setTableFromJsonFile"      : { "urlSuffix": "/bds/table/create", "httpCommand": "POST" },
                "delTableFromJsonFile"      : { "urlSuffix": "/bds/table/delete", "httpCommand": "POST" },
                "set"                       : { "urlSuffix": "/bds/object/add", "httpCommand": "POST" },
                "setTable"                  : { "urlSuffix": "/bds/table/create", "httpCommand": "POST" },
                "setObject"                 : { "urlSuffix": "/bds/object/add", "httpCommand": "POST" },
                "delete"                    : { "urlSuffix": "/bds/object/delete", "httpCommand": "POST" },
                "del"                       : { "urlSuffix": "/bds/object/delete", "httpCommand": "POST" },
                "delObject"                 : { "urlSuffix": "/bds/object/delete", "httpCommand": "POST" },
                "delTable"                  : { "urlSuffix": "/bds/table/delete", "httpCommand": "POST" },
                "show"                      : { "urlSuffix": "/bds/object/get", "httpCommand": "POST" },
                "get"                       : { "urlSuffix": "/bds/object/get", "httpCommand": "POST" },
                "["                         : {},           #List comprehension ... will be set below ... 
                "cmd"                       : { "urlSuffix": "/bds/object/get", "httpCommand": "POST" },
                "dump"                      : { "urlSuffix": "/bds/object/walk", "httpCommand": "POST" },      
                "walk"                      : { "urlSuffix": "/bds/object/walk", "httpCommand": "POST" }}        


class aioRtbRestConnect:
    """asyncio(aiohttp) REST client for interactions with the RtBrick API

          :param stepDict: the specific test step dictionary. The stepDict includes the attributes for device access
          :param stepDict["device"]: defines the IP address of the device under test. tested with IPv4 only. 
          :param stepDict["port"]: defines the TCP port for the session. Optional, default = 80.
          :type stepDict: python dict object
          :type stepDict["device"]: string   
          :type stepDict["port"]: int  
          :param stepDict["commands"]: defines the list for all commands. 
          :type stepDict["commands"]: list of strings  
          :param stepDict["commands"][<n>]: defines the contents of the REST API call to the rtBrick system. A specific parser is used to extract the http-method, url, url-suffix and json body from this string\n
            ``set table-name a-v-tuples`` performs a POST "/bds/object/add" action. \n
            ``get table-name a-v-tuples`` performs a POST "/bds/object/get" action. \n
            ``del table-name a-v-tuples`` performs a POST "/bds/object/del" action. \n
            ``setObjectsFromJsonFile & file-name`` performs a POST "/bds/object/" action using the JSON body from the file . \n
            ``delObjectsFromJsonFile & file-name`` performs a DELETE "/bds/object/" action using the JSON body from the file. \n
            ``setTableFromJsonFile & file-name`` performs a POST "/bds/object/" action using the JSON body from the file. \n
            ``delTableFromJsonFile & file-name`` performs a DELETE "/bds/object/" action using the JSON body from the file. \n 
            ``setTable & table-name a-v-tuples`` performs a POST "/bds/table/create" action. \n
            ``delTable & table-name a-v-tuples`` performs a DELETE "/bds/table/delete" action. \n
            ``dump; walk & table-name a-v-tuples`` performs a POST "/bds/object/walk" action. \n
            ``cmd; exec & space separated string`` performs a GET  /cmd/cmd-word1/cmd-word2/.. action. \n     
            ``[] python list comprehension`` support of nested list comprehension, this allows to do a kind of 'for x in []' list iterations over command strings. Could also be nested.        
          :type stepDict["commands"][<n>]: string  
          :param stepDict["includeRequestInOutput"]: Flag for inlduing the request to the output 
          :type stepDict["includeRequestInOutput"]: boolean  

    """

    def __init__(self,stepDict,**kwargs):
        self.stepDict = stepDict
        self.hostname = stepDict["device"]
        #self.vendor= stepDict["vendor"]
        self.port = _isInDictionary ("port",stepDict,80)

    async def runCommands (self,delayTimer=0):
        """sends all commands from the the test step and stores the REST response as YAML conform string in stepDict output section

              :param delayTimer: a waiting time (in seconds) periods before the commands are executed. required for await.
              :type delayTimer: int

              :return: a copy of the stepDict["output"]

        """

        async with aiohttp.ClientSession() as session:
            # FIXME delay timer ####
            for i,command in enumerate(self.stepDict["commands"]):
                t1=datetime.datetime.now()
                self.stepDict["output"][i]["startTS"] = t1.strftime('%Y-%m-%d %H:%M:%S.%f')  
                if isinstance(command, dict): 
                    pass
                elif isinstance(command, str): 
                    if command.startswith ("["):
                        commandList = eval(command)  
                    else:
                        commandList = [command]
                    logging.debug ("commandList: {}".format(commandList))  
                    execCommand = commandList[0]
                    _cmdInCommandStr, _bdsTableString, _attributeDict = self._splitCommandLine(execCommand)
                    requestData={}
                    requestData["table"] =  {}
                    requestData["table"]['table_name'] = _bdsTableString
                    commandChunks = []
                    chunkSize = 1000
                    while commandList:
                        commandChunks.append(commandList[:chunkSize])
                        commandList = commandList[chunkSize:]
                    for commandChunk in commandChunks:
                        requestData["objects"] =  []
                        for execCommand in commandChunk:            
                            _cmdInCommandStr, _bdsTableString, _attributeDict = self._splitCommandLine(execCommand)
                            #print(execCommand,_cmdInCommandStr, _bdsTableString, _attributeDict)
                            #requestData["objects"].append({})
                            #requestData["objects"][-1]["attribute"] = _attributeDict
                            headers = {'Content-Type': 'application/json'}  
                            urlSuffix = COMMAND_DICT[_cmdInCommandStr]["urlSuffix"]  
                            httpCommand = COMMAND_DICT[_cmdInCommandStr]["httpCommand"] 
                            url = 'http://'+self.hostname+":"+str(self.port)+urlSuffix
                            if _cmdInCommandStr in ["setObjectsFromJsonFile","delObjectsFromJsonFile",
                                               "setTableFromJsonFile","delTableFromJsonFile"]:
                                jsonFileName = _bdsTableString
                                jsonFh = open(jsonFileName,"r")
                                requestData = json.load(jsonFh)
                                print (requestData)
                            elif _cmdInCommandStr in ["setTable"]:       
                                requestData["table"].update(_attributeDict)  
                            else:
                                requestData["objects"].append({})
                                requestData["objects"][-1]["attribute"] = _attributeDict       
                            try:       
                                async with session.post(url,
                                                data=json.dumps(requestData),
                                                headers=headers) as self.response:
                                    jsonResponse = await self.response.json()
                            except:
                                self.response = None
                    _addTimeStampsToStepDict(t1,self.stepDict,i)

                    responseDict = {}
                    if _isInDictionary ("includeRequestInOutput",self.stepDict,False):                   
                        responseDict["request"] = {}  
                        responseDict["request"]["url"] = url          
                        responseDict["request"]["command"] = httpCommand  
                        if len(json.dumps(requestData)) < 500:         
                            responseDict["request"]["json"] = requestData
                        else:         
                            responseDict["request"]["json"] = {"text": "request longer than 500 chars"}
                    if self.response:
                        logging.info (self.response.status)
                        #logging.info (self.response.headers)   
                        responseDict["returnCode"] = self.response.status
                        responseDict["json"] = jsonResponse
                        try:
                            responseDict["header"] = {}
                            for headerkey in self.response.headers:
                                responseDict["header"][headerkey] = str(self.response.headers[headerkey])
                        except ValueError:
                            responseDict["headerString"] = str(self.response.headers)
                        try:
                            out = yaml.dump(responseDict, default_flow_style=False)
                        except:
                            out = "yaml coding error"
                        #pprint.pprint ( responseDict )
                        #print (out)
                        self.stepDict["output"][i]["output"] = out
                    else:
                        self.stepDict["output"][i]["output"] = "aiohttp connect error"
                        responseDict["returnCode"] = 500
                        responseDict["json"] = "aiohttp connect error"
                        responseDict["headerString"] = "aiohttp connect error"
                        try:
                            out = yaml.dump(responseDict, default_flow_style=False)
                        except:
                            out = "yaml coding error"
                        self.stepDict["output"][i]["output"] = out


    def _splitCommandLine(self,commandStr,rtbCmd = False):
        if " " in commandStr:
            _cmdInCommandStr,_restOfCommandStr = commandStr[:commandStr.find(" ")],commandStr[commandStr.find(" ")+1:].lstrip()
        else:
            ### FIXME cover Exception
            raise Exception ("rtbrick execCommand string must have two words, seperated by space {}".format(_command))
        if _cmdInCommandStr not in COMMAND_DICT.keys():
            raise Exception ("rtrick execCommand string must start with {} \nbut you sent {}".format(COMMAND_DICT.keys(),_cmdInCommandStr))
        if _cmdInCommandStr  == "cmd":
            return _cmdInCommandStr, _restOfCommandStr, {}      
        if " " in _restOfCommandStr:
            _bdsTableString,_restOfCommandStr = _restOfCommandStr[:_restOfCommandStr.find(" ")],_restOfCommandStr[_restOfCommandStr.find(" ")+1:].lstrip()
        else:
            _bdsTableString = _restOfCommandStr
            _restOfCommandStr = ""
        attributeDict = {}
        while " " in _restOfCommandStr:
            _attributeName,_restOfCommandStr = _restOfCommandStr[:_restOfCommandStr.find(" ")],_restOfCommandStr[_restOfCommandStr.find(" ")+1:].lstrip()
            if _restOfCommandStr.startswith('"'):
                _restOfCommandStr = _restOfCommandStr[1:]
                _attributeValue,_restOfCommandStr = _restOfCommandStr[:_restOfCommandStr.find('"')],_restOfCommandStr[_restOfCommandStr.find('"')+2:]
                attributeDict[_attributeName] = _attributeValue
            elif _restOfCommandStr.startswith('['):
                _attributeValue,_restOfCommandStr = _restOfCommandStr[:_restOfCommandStr.find(']')+1],_restOfCommandStr[_restOfCommandStr.find(']')+2:]            
                attributeDict[_attributeName] = json.loads(_attributeValue)
            else:
                if " " in _restOfCommandStr:
                    _attributeValue,_restOfCommandStr = _restOfCommandStr[:_restOfCommandStr.find(" ")],_restOfCommandStr[_restOfCommandStr.find(" ")+1:].lstrip()
                else:
                    _attributeValue = _restOfCommandStr
                if _attributeValue.isdigit():
                    attributeDict[_attributeName] = int(_attributeValue)
                else:
                    attributeDict[_attributeName] = _attributeValue
        return _cmdInCommandStr, _bdsTableString, attributeDict




