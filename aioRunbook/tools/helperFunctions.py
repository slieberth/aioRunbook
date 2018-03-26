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


import asyncio
import random
import logging
import yaml
from copy import deepcopy
import pprint
import re
import datetime
import jinja2
import os

def _isInDictionary (searchKey,inDictionary,defaultValue):
    """verify the presence of a dict key

              :param searchKey: attribute name to be checked
              :type searchKey: string
              :param inDictionary: the dictionary to be searched
              :type inDictionary: dict
              :param defaultValue: the default value, in case the attribute is not present
              :type defaultValue: object

              :return: either dict attribute object, respectively a default object.

    """
    if searchKey in inDictionary.keys():
        return inDictionary[searchKey]
    else:
        return defaultValue 

def _substitudeValue_Depr (myObject,valueList):
    logging.info ('substitudeValue: {} valuelist {}'.format(myObject,valueList))
    if type(myObject) == str:
        reCurlyBracketPattern = re.compile(r'\{\{\d+\}\}')
        substitudeList = reCurlyBracketPattern.findall(myObject)
        if len(substitudeList) > 0:
            if len(substitudeList) == 1:
                substitudeValue = valueList[int(substitudeList[0][2:-2])]
                if myObject == substitudeList[0]:
                    return substitudeValue
                else:
                    return myObject.replace(substitudeList[0],str(substitudeValue))
            else:
                returnString = myObject
                for substitudeCurlyBracketParameterString in substitudeList:
                    #print (int(substitudeCurlyBracketParameterString[2:-2]))
                    substitudeValue = valueList[int(substitudeCurlyBracketParameterString[2:-2])]
                    returnString = returnString.replace(substitudeCurlyBracketParameterString,str(substitudeValue))
                    #print (returnString)
                return returnString        
        else:
            return myObject
    else:                    
        return myObject  

def _substitudeVarsInString (myObject,varDict={},loopIndex=0,stepIndex=0):
    """variable substitution with Jinja2

              :param myObject: string which might contain Jinja2 variable patterns
              :type myObject: string
              :param varDict: dictionary which contains the variables. Could contain sub dicts and lists
              :type varDict: dict
              :param loopIndex: list iterator for loops. Will be set by aioRunbookScheduler.execSteps
              :type loopIndex: int
              :param stepIndex: list iterator for steps, Will be set by aioRunbookScheduler.execSteps
              :type loopIndex: int

              :return: possibly amended string, respctevely the original object

    """
    #logging.debug ('substitudeValue: {} varDict {}'.format(myObject,varDict))
    tE_jinja_env = jinja2.Environment(\
        block_start_string = '{{',
        block_end_string = '}}',
        variable_start_string = '.VAR.',
        variable_end_string = '.',
        comment_start_string = '#!#',
        comment_end_string = '#!#',
        line_statement_prefix = '%%_',
        line_comment_prefix = '%%#',
        trim_blocks = True,
        autoescape = False,
        loader = jinja2.FileSystemLoader("."))

    if isinstance(myObject,str):
        try:
            fh = open("aioRunbookVariable.tmp",'w')
            fh.write(myObject)
            fh.close()
            #template = jinja2.Template(myObject) 
            j2template = tE_jinja_env.get_template('aioRunbookVariable.tmp')
            renderedString = j2template.render(varDict,loopIndex=loopIndex,stepIndex=stepIndex)
            #renderedString = template.render(varDict,loopIndex=loopIndex,stepIndex=stepIndex) 
            os.remove("aioRunbookVariable.tmp")
        except:
            logging.error("_substitudeValue jinja2 rendering error")
            return myObject
        else:
            return renderedString
    else:
        logging.error("_substitudeValue jinja2 not yet implemented just for strings")
        return myObject

def _substitudeMacrosInString (configFileName,macroDict={}):
    macro_jinja_env = jinja2.Environment(\
        block_start_string = '#-MACRO-BLOCK',
        block_end_string = '-#',
        variable_start_string = '#-MACRO-',
        variable_end_string = '-#',
        comment_start_string = '#%#',
        comment_end_string = '#%#',
        line_statement_prefix = '#*#',
        line_comment_prefix = '#!#',
        trim_blocks = True,
        autoescape = False,
        loader = jinja2.FileSystemLoader("."))
    #logging.debug (' _substitudeMacro: {} macroDict {} '.format(myObject,macroDict))
    j2template = macro_jinja_env.get_template(configFileName)
    newConfigString = j2template.render(macroDict)
    return newConfigString


def _retrieveVarFromVarDict_Depr (myObject,varDict={}):     #Deprecated for cacheCheckResults._retrieveVarFromVarDict
    logging.debug ('substitudeValue: {} valueMatrix {} varDict {}'.format(myObject,valueMatrix,varDict))
    if isinstance(myObject,str):
        try:
            template = Template(myObject) 
            renderedString = template.render(varDict,loopIndex=loopIndex,stepIndex=stepIndex) 
        except:
            logging.error("_substitudeValue jinja2 rendering error")
            return myObject
        else:
            return renderedString
    else:
        try:
            template = Template(myObject) 
            renderedString = template.render(varDict,loopIndex=loopIndex,stepIndex=stepIndex) 
        except:
            return myObject
        else:
            try:
                return eval(renderedString) #convert numbers to python type
            except:
                return renderedString

def _addTimeStampsToStepDict(t1,stepDict,commandCounter=0):
    """simple function, which adds the end timestamps to the output dict.

              :param t1: timestamp for the start
              :type t1: datetime.datetime
              :param stepDict: applicable stepDict
              :type stepDict: dict
              :param commandCounter: provides the command index, in order to identify the proper output dict,
              :type commandCounter: int

    """
    stepDict["output"][commandCounter]["startTS"] = t1.strftime('%Y-%m-%d %H:%M:%S.%f')   
    t2=datetime.datetime.now()
    stepDict["output"][commandCounter]["endTS"] = t2.strftime('%Y-%m-%d %H:%M:%S.%f')   
    stepDict["output"][commandCounter]["elapsed"] = str((t2-t1))
    stepDict["output"][commandCounter]["elapsedRaw"] = (t2-t1).total_seconds()

def _createOutputList(stepCounter,stepType,stepDict,loopCounter):
    """simple function which adds the output dict for each command of a specific step

              :param stepCounter: stepCounter
              :type stepCounter: int
              :param stepType: copy of the stepId (=stepType)
              :type stepType: string
              :param stepDict: stepDict
              :type stepDict: dict
              :param loopCounter: loopCounter
              :type loopCounter: int

    """
    stepDict["output"] = []
    def enrichOutputContainer(i,command):
        outputContainer = {}
        outputContainer["name"] = stepDict["name"]
        if "device" in stepDict.keys():
            outputContainer["device"] = stepDict["device"]
        outputContainer["loopCounter"] = loopCounter
        outputContainer["stepCounter"] = stepCounter
        outputContainer["commandCounter"] = i + 1
        outputContainer["stepType"] = stepType
        outputContainer["commandOrig"] = str(command).replace("+","")
        outputContainer["pass"] = True  #default
        outputContainer["skip"] = False #default
        stepDict["output"].append(outputContainer)
    if "commands" in stepDict:
        for i,command in enumerate(stepDict["commands"]):
            enrichOutputContainer(i,command)
    else:
        enrichOutputContainer(0,"")

def _setHostfileAttributes(stepDict,hostDict):
    """searches for a host reference in the strpDict name and applies conditioanlly attributes from the host reference

              :param stepCounter: stepCounter
              :type stepCounter: int
              :param stepType: copy of the stepId (=stepType)
              :type stepType: string
              :param stepDict: stepDict
              :type stepDict: dict
              :param loopCounter: loopCounter
              :type loopCounter: int

    """
    hostReferenceName = stepDict["name"].split(" ")[0]
    logging.debug('checking hostReferenceName {}'.format(hostReferenceName))
    hostDictEntry = _isInDictionary(hostReferenceName,hostDict,None)
    stepDict["hostname"] = ""
    if hostDictEntry:
        stepDict["hostname"] = hostReferenceName
        stepDict["device"] = hostDictEntry["device"]
        for dictKey in hostDictEntry.keys():
            if dictKey not in stepDict:
                if dictKey in hostDictEntry.keys(): stepDict[dictKey] = hostDictEntry[dictKey]


def _getOutputInformationTag(stepCommandOutput):
        return "loop_{}_step_{}_command_{}".format\
               (stepCommandOutput["loopCounter"],
                stepCommandOutput["stepCounter"], 
                stepCommandOutput["commandCounter"])

def _decomposeOutputInformationTag(outputInformationTag):
        splitList = outputInformationTag.split("_")
        if len(splitList) == 4:
            return int(splitList[1]),int(splitList[3]),None
        elif len(splitList) == 6:
            return int(splitList[1]),int(splitList[3]),int(splitList[5])
        else:
            logging.error("error _decomposeOutputInformationTag: {}".format(outputInformationTag))
            return None,None,None

