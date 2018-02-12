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
import zlib
import binascii


class diffCheck:

    """class for verification of CLI output, based on googles textfsm engine.

    """

    def __init__(self):
        pass    

    def _compress(clearTestString):
        return binascii.hexlify(zlib.compress(clearTestString.encode()))

    def _deCompress(compressedDiffStringInHex):
        return zlib.decompress(binascii.unhexlify(compressedDiffStringInHex)).decode()

    @classmethod
    def checkCliOutputString (self,stepDict,valueList,configDict={}):
        """classmethod function for validatiting the CLI output with apreviously recorded snapshot of the CLI output

              :param stepDict: The specific test step dictionary, which has both CLI outout and textFSM template attributes.
              :param stepDict["output"]: either a JSON or a YAML loadable string     
              :param valueList: This list is used to substitude values, respectively store values. The list is derived from valueMatrix[loopCounter]
              :param configDict: The config dictionary, required for access to the recorded snapshot section.
              :type stepDict: python dict object
              :type stepDict["output"]: either a JSON or a YAML loadable string
              :type valueList: list
              :type configDict: python dict object

        """

        checkCommandOffsetFromLastCommand = _isInDictionary("checkCommandOffsetFromLastCommand",stepDict,0) - 1   
        diffInformationTag = ("loop_{}_step_{}".format(stepDict["loopCounter"],stepDict["stepCounter"])) 
        self.output = stepDict["output"][checkCommandOffsetFromLastCommand]["output"]
        if "diffSnapshot" in configDict:
            logging.debug ('existing diffSnapshot in ConfigDict'.format(stepDict["stepCounter"])) 
            if diffInformationTag  in configDict["diffSnapshot"].keys():
                outputStringList = self.output.split("\n")
                #diffStringList = configDict["diffStrings"][diffInformationTag].split("\n")
                compressedDiffStringInHex = configDict["diffSnapshot"][diffInformationTag]
                diffStringList = self._deCompress(compressedDiffStringInHex).split("\n")
                diffResultList = list(difflib.unified_diff(diffStringList,outputStringList))
                if len(diffResultList) == 0:
                    return True, ""
                else:
                    return False, "\n".join(diffResultList)
            else:
                logging.debug ('missing diffSnapshot for {} in ConfigDict'.format(diffInformationTag)) 
                #configDict["diffStrings"][diffInformationTag] = stepDict["output"][checkCommandOffsetFromLastCommand]["output"]
                outputString = stepDict["output"][checkCommandOffsetFromLastCommand]["output"]
                compressedStringInHex = self._compress(outputString)
                #compressedStringInHex = binascii.hexlify(zlib.compress(outputString.encode()))
                configDict["diffSnapshot"][diffInformationTag] = compressedStringInHex 
                return False, "diffSnapshotModified"
        else:
            logging.debug ('missing diffSnapshot in ConfigDict'.format(stepDict["stepCounter"])) 
            outputString = stepDict["output"][checkCommandOffsetFromLastCommand]["output"]
            compressedStringInHex = self._compress(outputString)
            #diffStringsDict = {diffInformationTag:stepDict["output"][checkCommandOffsetFromLastCommand]["output"]}
            diffStringsDict = {diffInformationTag:compressedStringInHex}
            configDict["diffSnapshot"] = diffStringsDict
            return False, "diffSnapshotInitalized"

    @classmethod
    def setModificationFlag (self,stepDict):
        checkCommandOffsetFromLastCommand = _isInDictionary("checkCommandOffsetFromLastCommand",stepDict,0) - 1  
        if stepDict["output"][checkCommandOffsetFromLastCommand]["checkResult"].startswith("diffSnapshotModified") or \
           stepDict["output"][checkCommandOffsetFromLastCommand]["checkResult"].startswith("diffSnapshotInitalized"):
            return True
        else:
            return False

    @classmethod
    def getDiffSnapshotYamlBlockLines (self,configDict):
        configDict["diffSnapshot"]["created"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') 
        return yaml.dump({"diffSnapshot":configDict["diffSnapshot"]},default_flow_style = False).split("\n")
        

