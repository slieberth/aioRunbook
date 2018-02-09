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
import difflib


class diffCheck:

    """class for verification of CLI output (text), based on googles textfsm engine.

    """

    def __init__(self):
        pass    


    @classmethod
    def checkCliOutputString (self,stepDict,valueList,configDict={}):
        """classmethod function for validatiting the CLI output of a stepdict with apreviously 
         recorded snapshot of the CLI output

        """
        checkCommandOffsetFromLastCommand = _isInDictionary("checkCommandOffsetFromLastCommand",stepDict,0) - 1   
        diffInformationTag = ("loop_{}_step_{}".format(stepDict["loopCounter"],stepDict["stepCounter"])) 
        if "diffStrings" in configDict:
            logging.debug ('existing diffStrings found in ConfigDict'.format(stepDict["stepCounter"])) 
            if diffInformationTag  in configDict["diffStrings"].keys():
                outputStringList = stepDict["output"][checkCommandOffsetFromLastCommand]["output"].split("\n")
                diffStringList = configDict["diffStrings"][diffInformationTag].split("\n")
                diffResultList = list(difflib.unified_diff(diffStringList,outputStringList))
                if len(diffResultList) == 0:
                    return True, ""
                else:
                    return False, "\n".join(diffResultList)
            else:
                configDict["diffStrings"][diffInformationTag] = stepDict["output"][checkCommandOffsetFromLastCommand]["output"]
                return False, "diffStringModified"
        else:
            logging.debug ('missing diffStrings in ConfigDict'.format(stepDict["stepCounter"])) 
            diffStringsDict = {diffInformationTag:stepDict["output"][checkCommandOffsetFromLastCommand]["output"]}
            configDict["diffStrings"] = diffStringsDict
            return False, "diffStringInitalized"

