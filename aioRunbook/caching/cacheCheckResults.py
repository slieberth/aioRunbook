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
#  0.1.2 - catch possible exception on missing textFSM attribute.

import sys
import os
import shutil
import time
import pprint
import logging
import yaml
import datetime
import re
import csv
import jtextfsm as textfsm
from six import StringIO
from aioRunbook.tools.helperFunctions import _isInDictionary, _substitudeVarsInString
from jinja2 import Template


class cacheCheckResults:

    """class for storing/retrieving the results of check/await in named variables

    """

    def __init__(self):
        pass    


    @classmethod
    def storeCheckResultToVarDict (self,stepDict,varDict={},configDict={}):
        """function to store the results of checks in named variables.

              :param stepDict: The specific test step dictionary, which has both CLI outout and textFSM template attributes.
              :param stepDict["output"]: either a JSON or a YAML loadable string     
              :param varDict: Dictionary containing the variable definitions
              :param configDict: optional for further use.
              :type stepDict: python dict object
              :type stepDict["output"]: either a JSON or a YAML loadable string
              :type varDict: dict
              :type configDict: python dict object

            if the relevant filed contains a number, then this number is converted to python int/float type

        """
        checkCommandOffsetFromLastCommand = _isInDictionary("checkCommandOffsetFromLastCommand",stepDict,0) - 1  
        #pprint.pprint(   stepDict["output"])
        loopCounter = stepDict["output"][checkCommandOffsetFromLastCommand]["loopCounter"]
        stepCounter = stepDict["output"][checkCommandOffsetFromLastCommand]["stepCounter"]
        try:        
             checkResult = stepDict["output"][checkCommandOffsetFromLastCommand]["checkResult"]
        except:
             checkResult = "erroneousCheckResult"
        if "storeFirstTextFsMElementToVariable" in stepDict:
            #listIndex = int(stepDict["storeTextFsMListelementToVariable"].split("->")[0])
            varName = stepDict["storeFirstTextFsMElementToVariable"]
            try:        
                 checkResultItemFromMatrix = checkResult[0][0]
            except:
                 checkResultItemFromMatrix = "erroneousCheckResultMatrix"
            logging.debug('storeCheckResultToVariable checkResultItemFromMatrix:{} varName:{} '.format(checkResultItemFromMatrix,varName)) 
            logging.debug('storeCheckResultToVariable varDict: {}'.format(varDict))
            try:
                try:
                    varDict[varName] = eval(checkResultItemFromMatrix)
                except:
                    varDict[varName] = checkResultItemFromMatrix
            except:
                varDict[varName] = "ERROR in storeCheckResultToVariable"
            logging.debug(("new varDict: {}".format(varDict)))

    @classmethod
    def retrieveVarFromVarDict (self,inObject,varDict={},loopIndex=0,stepIndex=0):
        """function to retrieve values from the valueDict via Jinja2 and conversion for numbers. 

              :param stepDict: The specific test step dictionary, which has both CLI outout and textFSM template attributes.
              :param stepDict["output"]: either a JSON or a YAML loadable string     
              :param varDict: Dictionary containing the variable definitions
              :param configDict: The config dictionary, required for access to the recorded snapshot section.
              :type stepDict: python dict object
              :type stepDict["output"]: either a JSON or a YAML loadable string
              :type varDict: dict
              :type configDict: python dict object

        """
        if isinstance(inObject,str):
            try:
                template = Template(inObject) 
                renderedString = template.render(varDict,loopIndex=loopIndex,stepIndex=stepIndex) 
            except:
                logging.error("retrieveVarFromVarDict jinja2 rendering error")
                renderedString = "Error in retrieveVarFromVarDict"
            try:
                retValue = eval(renderedString)
            except:
                retValue = renderedString
            return retValue     
        else:
            return myObject


