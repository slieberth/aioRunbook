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
from aioRunbook.tools.helperFunctions import _isInDictionary, _substitudeValue


class cacheCheckResults:

    """class for TBD

    """

    def __init__(self):
        pass    


    @classmethod
    def storeCheckResultToVarDict (self,stepDict,varDict={},configDict={}):
        """TBD

        """
        checkCommandOffsetFromLastCommand = _isInDictionary("checkCommandOffsetFromLastCommand",stepDict,0) - 1     
        loopCounter = stepDict["output"][checkCommandOffsetFromLastCommand]["loopCounter"]
        stepCounter = stepDict["output"][checkCommandOffsetFromLastCommand]["stepCount"]
        stepCounter = stepDict["output"][checkCommandOffsetFromLastCommand]["stepCount"]
        try:        
             checkResult = stepDict["output"][checkCommandOffsetFromLastCommand]["checkResult"]
        except:
             checkResult = "erroneousCheckResult"
        if "storeTextFsMListelementToVariable" in stepDict:
            listIndex = int(stepDict["storeTextFsMListelementToVariable"].split("->")[0])
            varName = stepDict["storeTextFsMListelementToVariable"].split("->")[1]
            try:        
                 checkResultItemFromMatrix = checkResult[0][listIndex]
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
            logging.debug(("new varDict: {}".format(varDict))

