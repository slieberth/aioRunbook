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

#  \version   0.2.2
#  \date      09.02.2018

#  \modification
#  0.1.1 base line for history
#  0.1.2 work for await - universalize adapter access
#  0.1.3 first try for asyncio loop to adapter fix - have just in event loop
#  0.1.4 get rid of callback
#  0.1.5 prepare for blocking functions; test with SNMP, first successful implementation
#  0.1.6 continue work on blocking functions, cleanup ... 
#  0.1.7 integration of aioNetconfConnect
#  0.1.11 work on diff analyzer
#         change to ...counter and ...index for loop, step, command
#         index starts with 0, whereas counter starts with 1
#  0.2.1 change naming aioRunbook to aioRunbookScheduler
#  0.2.2 added StepRange 

import asyncio
import concurrent.futures
#import random
import logging
import yaml
from copy import deepcopy
import pprint
import re
import datetime
import json

from aioRunbook.adaptors.aioError import aioError
from aioRunbook.adaptors.aioStdin import aioStdin
from aioRunbook.adaptors.aioSshConnect import aioSshConnect
from aioRunbook.adaptors.aioTelnetConnect import aioTelnetConnect
from aioRunbook.adaptors.aioRtbRestConnect import aioRtbRestConnect
from aioRunbook.adaptors.aioLocalShellConnect import aioLocalShellConnect
from aioRunbook.adaptors.aioSftp import aioSftp
from aioRunbook.adaptors.aioSnmpConnect import aioSnmpConnect
from aioRunbook.adaptors.aioNetconfConnect import aioNetconfConnect
from aioRunbook.analyzers.textFsmCheck import textFsmCheck
from aioRunbook.analyzers.jsonCheck import jsonCheck
from aioRunbook.analyzers.diffCheck import diffCheck
from aioRunbook.tools.helperFunctions import _isInDictionary, _substitudeValue, _addTimeStampsToStepDict
from aioRunbook.tools.helperFunctions import _createOutputList, _setHostfileAttributes
from aioRunbook.tools.aioRunbookYmlBlockParser import aioRunbookYmlBlockParser

_GENENERIC_TIMEOUT = 60 #set generic timeout to 60 seconds

class aioRunbookScheduler():
    """assyncio scheduler core, loads the config file and administers the step execution

          :param configFile: File location for the YAML File which contains the test step configuration. 
                File ending must be .yml. 
                The configfile must include a YAML string, which is parsed into the configDict structure:
          :type configDict["config"]: string
          :param configDict["config"]["hostfiles"]: Those files declare the device-under-test access paramters.
          :type configDict["config"]["hostfiles"]: list of strings
          :param configDict["config"]["steps"]: This list defines the test steps.
          :type configDict["config"]["steps"]: list of dicts
          :param configDict["config"]["steps"][<n>][<id>]: defines the actual step attribute. Refered in the code as stepDict. 
                Following <id> are supported: "record", "config", "check", "await", "sleep", "break", "comment", "copy".
          :type configDict["config"]["steps"][<n>][<id>]: dict
          :param configDict["config"]["steps"][<n>][<id>]["startInBackground"]: Flag defining the nature of this step.
                If ommitted or set to "false", then this step is executed as blocking step in the foreground.
                If set to "true", then this step is executed as non-blocking in the background.
          :type configDict["config"]["steps"][<n>][<id>]["startInBackground"]: boolean
          :param configDict["config"]["steps"][<n>][<id>]["randomStartDelay"]: Defines a waiting time, before the test is executed. 
                For chaos testing it might be desirable to execute the steps almost simulatanously,
                but not always in the same order. Applicable only to background test steps. ###review-code###
          :type configDict["config"]["steps"][<n>][<id>]["randomStartDelay"]: int or float
          :param configDict["config"]["steps"][<n>][<id>]["name"]: The name of the test step. Mandatory Attribute. The first word of this line shall be used as 
                reference to a host file entry. If the reference matches, than all device access parameters are derived from
                this host file entry.
          :type configDict["config"]["steps"][<n>][<id>]["name"]: string
          :param configDict["config"]["steps"][<n>][<id>][<attr>]: Any arbitrary object can be added to a stepdict, giving the flexibility to 
                provide this information to a variance of IO adapters, respectively to any rendering post-process.
          :type configDict["config"]["steps"][<n>][<id>][<attr>]: obj


          :return: Returns the number of testcases which have failed. Returns 0 if all 
                   test cases have succeeded.
          :type return: int

    """

    def __init__(self,configFile):    
        self.errorCounter = 0
        self.configLoaded = self._readYamlFile(configFile)
        self.loops = 1

    @classmethod
    def errorAdaptor(self,stepDict):
            t1=datetime.datetime.now()
            stepDict["output"][0]["output"] = "error adpater selection ###"
            _addTimeStampsToStepDict(t1,stepDict)

    async def _asyncTestStep(self,stepDict,eventLoop,threadExecutor,stepRange = []):
        """method asyncTestStep


        """
        name = stepDict["name"]
        stepCounter = stepDict["stepCounter"]
        stepIndex = stepDict["stepIndex"]
        logging.debug ("async step: {} started {}".format(stepCounter,name))
        stepListItem = self.configDict["config"]["steps"][stepIndex]
        stepId = list(stepListItem.keys())[0]
        if stepId not in ["sleep", "break", "comment"]:
            _setHostfileAttributes(stepDict,self.hostDict)
        if "randomStartDelay" in stepDict:
            randomSleepTime = random.random() * stepDict["randomStartDelay"]
            logging.debug ("sleep random delay {}".format(randomSleepTime))
            await asyncio.sleep(randomSleepTime)
        vendor = _isInDictionary("vendor",stepDict,"")
        method = _isInDictionary("method",stepDict,"")
        timeout = _GENENERIC_TIMEOUT
        stepDict["loopCounter"] = self.loopCounter
        _createOutputList(stepCounter,stepId,stepDict,self.loopCounter)
        t1=datetime.datetime.now()
        if stepId in  [ "check", "await","config","record"]:
            self.disconnectFunction = None
            if method in ["ssh"]: 
                self.adaptor = aioSshConnect(stepDict)
                await self.adaptor.connect()
                self.commandFunction =  self.adaptor.runCommands        
                await self.commandFunction()
                self.disconnectFunction = self.adaptor.disconnect
                await self.disconnectFunction()
            elif method in ["telnet"]: 
                self.adaptor = aioTelnetConnect(stepDict,eventLoop=eventLoop)      
                await self.adaptor.connect()
                self.commandFunction =  self.adaptor.runCommands        
                await self.commandFunction()
                self.disconnectFunction = self.adaptor.disconnect
                await self.disconnectFunction()   
            elif method in ["rest"] and vendor in ["rtbrick"]: 
                self.adaptor = aioRtbRestConnect(stepDict)      
                self.commandFunction =  self.adaptor.runCommands     
                await self.commandFunction()
            elif method in ["local-shell"]: 
                self.adaptor = aioLocalShellConnect(stepDict,eventLoop=eventLoop)      
                self.commandFunction =  self.adaptor.runCommands     
                await self.commandFunction()
            elif method in ["snmp"]:            ### TESTME ####
                self.adaptor = aioSnmpConnect(stepDict)      
                self.commandFunction =  self.adaptor.sendSnmpRequests   
                await self.commandFunction(threadExecutor) #this is a blocking function call
            elif method in ["netconf"]:            ### TESTME ####
                self.adaptor = aioNetconfConnect(stepDict)      
                self.commandFunction =  self.adaptor.sendNetconfRequests   
                await self.commandFunction(threadExecutor) #this is a blocking function call
            else: 
                logging.error('###error adpater selection step {}###'.format(stepCounter))
                self.adaptor = aioError(stepDict)      
                self.commandFunction =  self.adaptor.runCommands     
                await self.commandFunction()
            if stepId in  [ "check", "await"]:
                _checkMethod = _isInDictionary("checkMethod",stepDict,"textFSM")
                if "jsonOneLine" in stepDict.keys(): _checkMethod = "json"
                if "jsonMultiLine" in stepDict.keys(): _checkMethod = "json"
                if _checkMethod == "textFSM":
                    analyserFunction = textFsmCheck.checkCliOutputString
                elif _checkMethod == "json":
                    analyserFunction = jsonCheck.checkOutputData
                elif _checkMethod == "diff":
                    analyserFunction = diffCheck.checkCliOutputString
                else:
                    logging.error('###error analyzer selection step {}###'.format(stepCounter))
                    analyserFunction = None                    
                logging.debug('analyserFunction set to {0}'.format(analyserFunction))
                checkCommandOffsetFromLastCommand = _isInDictionary("checkCommandOffsetFromLastCommand",stepDict,0) - 1
                logging.debug(' checkCommandOffsetFromLastCommand set to {0}'.format(checkCommandOffsetFromLastCommand))
                #valueList = self.configDict["config"]["valueMatrix"][self.loopCounter-1]  ###FIXME###
                valueList = self.valueMatrix[self.loopCounter-1]
                try:
                    (stepDict["output"][checkCommandOffsetFromLastCommand]["pass"],
                    stepDict["output"][checkCommandOffsetFromLastCommand]["checkResult"]) = \
                                analyserFunction(stepDict,valueList,configDict = self.configDict)           
                except Exception as errmsg:
                    logging.error(errmsg) 
                    stepDict["output"][checkCommandOffsetFromLastCommand]["pass"] = False
                    stepDict["output"][checkCommandOffsetFromLastCommand]["checkResult"] = ["!!! Analyser Error !!!"]
                    logging.error('check function {0}'.format(analyserFunction))
                    #raise
                logging.info('check/await analyserfuntion returns: {0}'.format(stepDict["output"][checkCommandOffsetFromLastCommand]["pass"]))
                if stepId == "await":
                    _tWait = _isInDictionary("command-repetition-timer",stepDict,1)
                    _tGiveUp = _isInDictionary("give-up-timer",stepDict,30)
                    t2 = datetime.datetime.now()
                    t3 = t2 -t1
                    #stepDict["output"][-1]["startTS"] = t1.strftime('%Y-%m-%d %H:%M:%S.%f')
                    while stepDict["output"][-1]["pass"] == False and t3 < datetime.timedelta(seconds=_tGiveUp):
                        await self.commandFunction(delayTimer=_tWait)
                        #
                        try:
                            (stepDict["output"][checkCommandOffsetFromLastCommand]["pass"],
                            stepDict["output"][checkCommandOffsetFromLastCommand]["checkResult"]) = \
                                        analyserFunction(stepDict,valueList,configDict = self.configDict)           
                        except Exception as errmsg:
                            logging.error(errmsg) 
                            stepDict["output"][checkCommandOffsetFromLastCommand]["pass"] = False
                            stepDict["output"][checkCommandOffsetFromLastCommand]["checkResult"] = ["!!! Analyser Error !!!"]
                            logging.error('check function {0}'.format(analyserFunction))
                            raise
                    if self.disconnectFunction != None and stepId in ["await"] :
                        self.disconnectFunction()
                    _addTimeStampsToStepDict(t1,stepDict)
        elif stepId == "sleep":
            #stepDict["output"][0]["startTS"] = t1.strftime('%Y-%m-%d %H:%M:%S.%f')   
            if "seconds" not in stepDict.keys():
                match = re.search(r'\d+', stepDict["name"])
                if match:                      
                    timer = int(match.group())
                else:
                    logging.error('step:{} unable to identify sleep timer {}'.format(stepCounter,stepDict["name"]))
            else:
                timer = _substitudeValue (stepDict["seconds"],self.valueMatrix[self.loopCounter-1])   ###FIXME###
            logging.info('step:{0} {1} sleep: {2}'.format(stepCounter,stepDict["name"],timer))
            await asyncio.sleep(timer)
            _addTimeStampsToStepDict(t1,stepDict)
        elif stepId == "break":
            _display = _isInDictionary("display",stepDict,"please hit return key")
            stdinPrompt = aioStdin(eventLoop=eventLoop)
            #raw_input = functools.partial(prompt, end='', flush=True)
            myInput = await stdinPrompt(_display)
            _addTimeStampsToStepDict(t1,stepDict)
        elif stepId == "copy":
            if "remote" in stepDict.keys():
                stepDict["remote"] = _substitudeValue (stepDict["remote"],self.valueMatrixLoopList)
            if "local" in stepDict.keys():
                stepDict["local"] = _substitudeValue (stepDict["local"],self.valueMatrixLoopList)
            mySftpClient = aioSftp(stepDict)         
            await mySftpClient.execCopy()
            _addTimeStampsToStepDict(t1,stepDict)
        return stepDict

    def _readYamlFile (self,configFile):
        self.yamlConfigFile = configFile
        logging.info('reading config file: {0}'.format(configFile))
        try:
            with open(configFile) as fh:
                YamlDictString = fh.read ()
                fh.close ()
        except:
            logging.error('cannot open configFile {}'.format(configFile))
            return False   
        try:     
            self.configDict = yaml.load(YamlDictString)
        except:
            logging.error('cannot load YAML File {}'.format(configFile))
            return False  
        self.configDict["yamlConfigFile"] = self.yamlConfigFile #for pdfRender
        #
        #   FIXME Start Host Dict Reader should be a function
        #
        self.hostDict = {'SELF': {'device': 'self','vendor': 'self', 'method': 'self'}}
        self.hostfiles = _isInDictionary("hostfiles",self.configDict["config"],[])
        logging.debug('configured hostfiles: {0}'.format(self.hostfiles))
        if len(self.hostfiles) > 0:
            for hostfileString in self.hostfiles:
                logging.info('reading config host file: {0}'.format(hostfileString))
                with open(hostfileString) as fh:
                    YamlDictString = fh.read ()
                    fh.close ()
                newHostDict = yaml.load(YamlDictString)
                if "defaults" in newHostDict.keys():
                    defaultDict = newHostDict["defaults"]
                else:
                    defaultDict = {}
                for newHost in newHostDict:
                    if newHost != "defaults":
                        if "invoke" in newHostDict[newHost].keys():
                            newHostDict[newHost].update(defaultDict[newHostDict[newHost]["invoke"]])
                        self.hostDict[newHost] = deepcopy(newHostDict[newHost])
        #
        #   FIXME End Host Dict Reader
        #
        self.valueMatrix = _isInDictionary("valueMatrix",self.configDict["config"],[[""]])
        return True   

    def writeDiffSnapshotToFile (self):
        """function to write the current output string to the diffSnapshot section of the YAML config file.

        FIXME - change to coroutine, once aiohttp server can concur simultanously.

        """

        logging.info('writing config file: {0}'.format(self.yamlConfigFile))
        diffStringYamlBlockLines = diffCheck.getDiffSnapshotYamlBlockLines(self.configDict)
        configBlockLines = aioRunbookYmlBlockParser.getConfigBlock(configFile=self.yamlConfigFile).split("\n")
        newYamlConfigString = "\n".join(configBlockLines+diffStringYamlBlockLines)
        fh = open(self.yamlConfigFile,'w') 
        fh.write(newYamlConfigString)  
        fh.close() 




    async def execSteps (self,eventLoop,threadExecutor=None,stepRange = []): 
        """coroutine to execute the testhost-dict lookup failed for step steps, which are defined in a YAML config file.

          :param eventLoop: defines the encpomassing asyncio event loop
          :type eventLoop: asyncio.event_loop
          :param threadExecutor: required for blocking tasks
          :type threadExecutor: concurrent.futures.ThreadPoolExecutor
          :param stepRange: defines the list of steps (counter starts with 1) 
          :type stepRange: list of int

        """

        async def awaitOpenedTasksToBeDone(numberOfTasksBeforeStarted):
            while len([task for task in asyncio.Task.all_tasks() if not task.done()]) > numberOfTasksBeforeStarted:
                await asyncio.sleep(0.001)

        if self.configLoaded == False:
            logging.error("execSteps without loaded config")  
            return False            

        numberOfTasksBeforeStart =  len([task for task in asyncio.Task.all_tasks() if not task.done()])
        for self.loopCounter in range(1,self.loops+1):
            logging.info('start loop {}'.format(self.loopCounter))
            self.loopIndex = self.loopCounter - 1
            bgList = []
            #
            #  Begin Change to stepRange
            #
            #self.configDict["config"]["steps"] = deepcopy(origDict)    #reset the configDict as start of loops
            stepRangeList = []
            if stepRange == []:
                for i in range(len(self.configDict["config"]["steps"])):
                    stepRangeList.append([i,self.configDict["config"]["steps"][i]]) 
            else:
                for i in stepRange:
                    stepRangeList.append([i-1,self.configDict["config"]["steps"][i-1]]) ###FIXME catch possible user errors
            logging.debug('set stepRangeList Indexes to {}'.format([x[0] for x in stepRangeList]))
            #
            #  End Change to stepRange
            #    
            self.valueMatrixLoopList = self.valueMatrix[self.loopCounter-1]
            #for stepIndex,stepListItem in enumerate(self.configDict["config"]["steps"]):
            for stepIndex,stepListItem  in stepRangeList:   
                stepCounter = stepIndex + 1
                stepId = list(stepListItem.keys())[0]
                stepDict = stepListItem[list(stepListItem.keys())[0]]
                stepDict["stepIndex"] = stepIndex
                stepDict["stepCounter"] = stepCounter
                backgroundStep = _isInDictionary("startInBackground",stepDict,False)
                blockingAdapter = _isInDictionary("blockingAdapter",stepDict,False)
                if backgroundStep:
                    logging.debug("adding background tasks {}".format(stepDict["name"]))                        
                    bgTask = eventLoop.create_task(self._asyncTestStep(stepDict,eventLoop,threadExecutor))
                    bgList.append(bgTask)
                else:
                    await self._asyncTestStep(stepDict,eventLoop,threadExecutor)  
            logging.info("waiting for background tasks to be done")   
            await awaitOpenedTasksToBeDone(numberOfTasksBeforeStart)
            logging.info("background tasks done")   
        return True


    async def saveConfigDictToJsonFile (self,*args):
        """coroutine to save the current processed configDict to a JSON File.

          :param jsonConfigFile: optional positional parameter at pos 0, which defines the 
                target JSON file.
          :type jsonConfigFile: string

        """

        if len(args) > 0:
            jsonConfigFile = args[0]
        else:
            yamlConfigFile = self.yamlConfigFile
            if yamlConfigFile.endswith(".yml"):
                jsonConfigFile = yamlConfigFile[:-4] + ".json"
            elif yamlConfigFile.endswith(".yaml"):
                jsonConfigFile = yamlConfigFile[:-5] + ".json"
            else:
                logging.error('saving saveConfigDictToJsonFile cannot detect json file name')
                return
        logging.info('saving configDict to Json: {}'.format(jsonConfigFile))
        with open(jsonConfigFile, 'w') as outfile:          ###FIXME potential error if file cannot be written
            json.dump(self.configDict, outfile)

    async def updateConfigDictStepInJsonFile (self,jsonConfigFile,stepListToBeUpdated):
        """coroutine to update specifc parts of the configDict.

          :param jsonConfigFile: defines the target JSON file.
          :type jsonConfigFile: string
          :param stepListToBeUpdated: defines the target JSON file, Step counter, starting with step 1
          :type stepListToBeUpdated: list of int

        """

        logging.info('update configDict from Json: {}, step {}'.format(jsonConfigFile,stepListToBeUpdated))
        with open(jsonConfigFile) as infile:                ###FIXME potential error if file cannot be read
            tempConfigDict = json.load(infile)
        for stepToBeUpdated in stepListToBeUpdated:
            tempConfigDict["config"]["steps"][stepToBeUpdated-1] = self.configDict["config"]["steps"][stepToBeUpdated-1]
        with open(jsonConfigFile, 'w') as outfile:          ###FIXME potential error if file cannot be written
            json.dump(tempConfigDict, outfile)

    async def loadConfigDictFromJsonFile (self,jsonConfigFile):
        """coroutine to load an existing json file configDict into memory.

          :param jsonConfigFile: defines the source JSON file.
          :type jsonConfigFile: stringt

        """

        logging.info('loading configDict from Json: {}'.format(jsonConfigFile))
        with open(jsonConfigFile) as infile:                ###FIXME potential error if file cannot be read
            self.configDict = json.load(infile)

