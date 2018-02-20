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
import difflib
import zlib
import binascii
import textwrap


class diffCheck:

    """class for verification of CLI output, based on diff comaprision to existing results.

    """

    def __init__(self):
        pass    



    def _diffEncode(clearTextObject,compressFlag,diffTextFSMFilterFlag ):
        #return binascii.hexlify(zlib.compress(clearTestString.encode())).decode()
        if compressFlag:
            if not diffTextFSMFilterFlag:
                compressedObject = binascii.hexlify(zlib.compress(clearTextObject.encode())).decode()
            else:
                #compressedObject = binascii.hexlify(zlib.compress(clearTestObject)).decode()
                compressedObject = binascii.hexlify(zlib.compress("\n".join(clearTextObject).encode())).decode()
            wrappedList = textwrap.wrap(compressedObject)
            return wrappedList
        else:
            return clearTextObject

    def _diffDecode(listObj,compressFlag,diffTextFSMFilterFlag ):
        if compressFlag:
            if not diffTextFSMFilterFlag:
                return zlib.decompress(binascii.unhexlify("".join(listObj).encode())).decode()
            else:
                return zlib.decompress(binascii.unhexlify("".join(listObj).encode())).decode().split("\n")
        else:
            return listObj

    @classmethod
    #def checkCliOutputString (self,stepDict,varDict={},configDict={}):
    def checkCliOutputString (self,stepDict,configDict={},varDict={},**kwargs):
        """classmethod function for validatiting the CLI output with apreviously recorded snapshot of the CLI output

              :param stepDict: The specific test step dictionary, which has both CLI outout and textFSM template attributes.
              :param stepDict["output"]: either a JSON or a YAML loadable string     
              :param varDict: Dictionary containing the variable definitions
              :param configDict: The config dictionary, required for access to the recorded snapshot section.
              :type stepDict: python dict object
              :type stepDict["output"]: either a JSON or a YAML loadable string
              :type varDict: dict
              :type configDict: python dict object


        """
        #pprint.pprint(stepDict)
        checkCommandOffsetFromLastCommand = _isInDictionary("checkCommandOffsetFromLastCommand",stepDict,0) - 1   
        loopCounter = stepDict["output"][checkCommandOffsetFromLastCommand]["loopCounter"]
        stepCounter = stepDict["output"][checkCommandOffsetFromLastCommand]["stepCounter"]
        diffInformationTag = ("loop_{}_step_{}".format(loopCounter,stepCounter)) 
        compressFlag = _isInDictionary("diffZip",stepDict,False) 
        diffTextFSMFilterFlag = _isInDictionary("diffTextFSMFilter",stepDict,False)
        setDiffSnapshotFlag = _isInDictionary("setDiffSnapshot",kwargs,False)  
        outputString = stepDict["output"][checkCommandOffsetFromLastCommand]["output"]
        diffSource = _isInDictionary("diffSource",stepDict,"diffSnapshot")  
        logging.debug("diffSource  {} ".format(diffSource))
        if setDiffSnapshotFlag == True:
            configDict["diffSnapshot"] = _isInDictionary("diffSnapshot",configDict,{}) 
            logging.warning ('setting diffSnapshot for {} in ConfigDict'.format(diffInformationTag)) 
            if diffTextFSMFilterFlag:
                logging.debug('stepDict["diffTextFSMFilter"]{}'.format(stepDict["diffTextFSMFilter"]))
                existingTemplateString = stepDict["diffTextFSMFilter"]
                newTemplateString= _substitudeVarsInString(existingTemplateString,varDict=varDict)
                re_table = textfsm.TextFSM(StringIO(newTemplateString))
                textFSMMatrix = re_table.ParseText(outputString)
                textFSMOutputString  = [ str(x) for sublist in textFSMMatrix for x in sublist ]
                compressedStringInHex = self._diffEncode(textFSMOutputString,compressFlag,diffTextFSMFilterFlag )
            else:
                compressedStringInHex = self._diffEncode(outputString,compressFlag,diffTextFSMFilterFlag)
                print(compressedStringInHex)
            logging.debug("setting diff for {} to {}".format(diffInformationTag,compressedStringInHex))
            configDict["diffSnapshot"][diffInformationTag] = compressedStringInHex                  
            return True, "setDiffSnapshot"
        else:
            if diffSource == "diffSnapshot":
                if "diffSnapshot" in configDict:
                    logging.debug ('existing diffSnapshot in ConfigDict'.format(stepCounter)) 
                    compressedDiffStringInHex = configDict["diffSnapshot"][diffInformationTag]
                    if diffInformationTag  in configDict["diffSnapshot"].keys():
                        if diffTextFSMFilterFlag:
                            existingTemplateString = stepDict["diffTextFSMFilter"]
                            newTemplateString= _substitudeVarsInString(existingTemplateString,varDict=varDict)
                            re_table = textfsm.TextFSM(StringIO(newTemplateString))
                            textFSMMatrix = re_table.ParseText(outputString)
                            logging.debug("new textFSMMatrix:{}".format(textFSMMatrix))
                            outputString  = str(textFSMMatrix)
                            logging.debug("new outputString x:{}".format(outputString))
                            outputStringList  = [ str(x) for sublist in textFSMMatrix for x in sublist ]
                            logging.debug("new outputStringList x:{}".format(outputStringList))
                            diffStringList = self._diffDecode(compressedDiffStringInHex,compressFlag,diffTextFSMFilterFlag)
                        else:
                            outputStringList = outputString.split("\n")
                            diffStringList = self._diffDecode(compressedDiffStringInHex,compressFlag,diffTextFSMFilterFlag).split("\n")  
                        diffResultList = list(difflib.unified_diff(diffStringList,outputStringList))
                        if len(diffResultList) == 0:
                            return True, ""
                        else:
                            return False, "\n".join(diffResultList)
                    else:
                        logging.error ('missing diffSnapshot in ConfigDict'.format(stepCounter)) 
                        return False, "missingStepDiffSnapshop-{}".format(diffInformationTag)
                else:
                    logging.error ('missing diffSnapshot in ConfigDict'.format(stepDict["stepCounter"])) 
                    return False, "missingGlobalDiffSnapshot"
            elif diffSource.startswith("outputFromStep"):
                match = re.search(r'\d+', diffSource)
                if match:                      
                    sourceStep = int(match.group())
                else:
                    logging.error('step:{} unable to identify diffSource {}'.format(stepCounter,diffSource))
                    return False, "unable to identify outputFromStep diffSource "
                if sourceStep >= stepCounter:
                    return False, "outputFromStep diffSource must less than stepCounter"
                else:
                    sourceStepId = list(configDict["config"]["steps"][sourceStep-1].keys())[0]
                    diffSourceString = configDict["config"]["steps"][sourceStep-1][sourceStepId]['output'][checkCommandOffsetFromLastCommand]['output'] 
                logging.debug('step:{} set outputFromStep to step {}'.format(stepCounter,sourceStep))
                if diffTextFSMFilterFlag:
                    existingTemplateString = stepDict["diffTextFSMFilter"]
                    newTemplateString= _substitudeVarsInString(existingTemplateString,varDict=varDict)
                    re_table = textfsm.TextFSM(StringIO(newTemplateString))
                    textFSMMatrix = re_table.ParseText(outputString)
                    #logging.debug("new textFSMMatrix:{}".format(textFSMMatrix))
                    outputStringList  = [ str(x) for sublist in textFSMMatrix for x in sublist ]
                    #logging.debug("new outputStringList x:{}".format(outputStringList))
                    re_table = textfsm.TextFSM(StringIO(newTemplateString))
                    textFSMMatrix = re_table.ParseText(diffSourceString)
                    diffStringList  = [ str(x) for sublist in textFSMMatrix for x in sublist ]   
                    #logging.debug("diffStringList x:{}".format(diffStringList))                
                else:
                    outputStringList = outputString.split("\n")
                    diffStringList = diffSourceString.split("\n") 
                diffResultList = list(difflib.unified_diff(diffStringList,outputStringList))
                if len(diffResultList) == 0:
                    return True, ""
                else:
                    return False, "\n".join(diffResultList)
            elif diffSource.startswith("previousLoop"):
                if loopCounter == 1:
                    return True, "initial Loop" 
                else:       
                    sourceStepId = list(configDict["config"]["steps"][stepCounter-1].keys())[0]
                    diffSourceString = configDict["config"]["steps"][stepCounter-1][sourceStepId]['output'][checkCommandOffsetFromLastCommand]['output']
                    #print ( diffSourceString )  
                    if diffTextFSMFilterFlag:
                        existingTemplateString = stepDict["diffTextFSMFilter"]
                        newTemplateString= _substitudeVarsInString(existingTemplateString,varDict=varDict)
                        re_table = textfsm.TextFSM(StringIO(newTemplateString))
                        textFSMMatrix = re_table.ParseText(outputString)
                        #logging.debug("new textFSMMatrix:{}".format(textFSMMatrix))
                        outputStringList  = [ str(x) for sublist in textFSMMatrix for x in sublist ]
                        #logging.debug("new outputStringList x:{}".format(outputStringList))
                        re_table = textfsm.TextFSM(StringIO(newTemplateString))
                        textFSMMatrix = re_table.ParseText(diffSourceString)
                        diffStringList  = [ str(x) for sublist in textFSMMatrix for x in sublist ]   
                        #logging.debug("diffStringList x:{}".format(diffStringList))                
                    else:
                        outputStringList = outputString.split("\n")
                        diffStringList = diffSourceString.split("\n") 
                    diffResultList = list(difflib.unified_diff(diffStringList,outputStringList))
                    if len(diffResultList) == 0:
                        return True, ""
                    else:
                        return False, "\n".join(diffResultList)
            else: 
                return False, "incorrect diffsource attribute"


    @classmethod
    def getDiffSnapshotYamlBlockLines (self,configDict):
        configDict["diffSnapshot"]["created"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') 
        return yaml.dump({"diffSnapshot":configDict["diffSnapshot"]},default_flow_style = False).split("\n")


        

