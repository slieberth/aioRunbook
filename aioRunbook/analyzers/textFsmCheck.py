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


class textFsmCheck:

    """class for verification of CLI output (text), based on googles textfsm engine.

    """

    def __init__(self):
        pass    


    @classmethod
    def checkCliOutputString (self,stepDict,valueList,configDict={}):
        """classmethod function for validatiting the CLI output of a stepdict.

              :param stepDict: The specific test step dictionary, which has both CLI outout and textFSM template attributes.
              :param stepDict["textFSM"]: defines the textFSM template.    
              :param stepDict["textFSMOneLine"]: one line macro, which can be used for single parameter checks.   
              :param stepDict["checkResultCount"]: defines the expected length of the textFSM match list.  
              :param stepDict["evalResultCount"]: defines a python expression for evaluation the number of textFSM matches, 
                     e.g. "[] >= 0". [] is the placeholder for the length of the textFSM match list.  
              :param stepDict["evalListElement"]: defines a python expression for evaluation the value of a textFSM list element.
                     e.g. "0 < [0] < 20". [0] is the placeholder for the value of the first textFSM list element.  
              :param stepDict["storeListElementInValueMatrix"]: stores the value of a textFSM list element in the valueMatrix. 
                     e.g. "0->0" stores the value of the first textFSM list element in first element of the valueMatrix[loopCounter] list.
              :param valueList: This list is used to substitude values, respectively store values. The list is derived from valueMatrix[loopCounter]
              :type stepDict: python dict object
              :type stepDict["textFSM"]: string   
              :type stepDict["textFSMOneLine"]: string   
              :type stepDict["checkResultCount"]: int 
              :type stepDict["evalResultCount"]: string  
              :type stepDict["evalListElement"]: string  
              :type stepDict["storeListElementInValueMatrix"]: string  
              :type valueList: list

        """

        checkCommandOffsetFromLastCommand = _isInDictionary("checkCommandOffsetFromLastCommand",stepDict,0) - 1        
        if "textFSMOneLine" in stepDict.keys():
            parameterString = " ".join(stepDict["textFSMOneLine"].split(" ")[:-1])
            stepDict["textFSM"] = "Value Required P0 {}\n\nStart\n".format(parameterString) + "  ^${P0} -> Record\n\nEnd"
            stepDict["checkResultCount"] = int((stepDict["textFSMOneLine"].split(" ")[-1]))
        try:        
            textFSMString = stepDict["textFSM"]
        except:
            logging.error('check: analyzer without textFSM attribute (textFSM is the default analyzer)')    
            return False,'check: analyzer without textFSM attribute (textFSM is the default analyzer)'        
        #textFSMString = substitudeValue (stepDict["textFSM"],valueList)
        re_table = textfsm.TextFSM(StringIO(textFSMString))
        logging.debug('before TextFSMOutput: offset {} relevant output {}'.format(checkCommandOffsetFromLastCommand,
                                               stepDict["output"][checkCommandOffsetFromLastCommand]["output"]))

        self.TextFSMOutput = re_table.ParseText(stepDict["output"][checkCommandOffsetFromLastCommand]["output"])
        logging.info('textfsmoutput: {0}'.format(self.TextFSMOutput))
        outerList = []
        if "storeListElementInValueMatrix" in stepDict:
            textFsmIndex = int(stepDict["storeListElementInValueMatrix"].split("->")[0])
            valueMatrixIndex = int(stepDict["storeListElementInValueMatrix"].split("->")[1])
            logging.debug('storeListElementInValueMatrix textFsmIndex:{} valueMatrixIndex:{} '.format(textFsmIndex,valueMatrixIndex)) 
            logging.debug('storeListElementInValueMatrix valuelist:'.format(valueList))
            if len(self.TextFSMOutput) > 0:
                if len(self.TextFSMOutput[0]) > textFsmIndex:
                    valueList[valueMatrixIndex] = self.TextFSMOutput[0][textFsmIndex]
                else:
                    logging.error ("errenous storeListElementInValueMatrix: " + stepDict["storeListElementInValueMatrix"])
                    valueList[valueMatrixIndex] = ""
            else:
                logging.error ("errenous storeListElementInValueMatrix: " + stepDict["storeListElementInValueMatrix"])
                valueList[valueMatrixIndex] = ""
            #print (self.valueMatrix[self.loopCounter][valueMatrixIndex])
        if "evalListElement" in stepDict:
            evalString = stepDict["evalListElement"].strip()
            posOpeningBracket = evalString.find("[")
            posClosingBracket = evalString.find("]")
            textFsmIndex = int(evalString[posOpeningBracket+1:posClosingBracket].strip())
            if len (self.TextFSMOutput) > 0:
                if len (self.TextFSMOutput[0]) > 0:
                    if posOpeningBracket > 0:
                        evalString1 = evalString[:posOpeningBracket-1].strip()
                        evalString1 = substitudeValue(evalString1,valueList)               
                        result1 =  eval(evalString1 + " " + self.TextFSMOutput[0][textFsmIndex])
                        #print (evalString1 + " " + self.TextFSMOutput[0][textFsmIndex],result1)
                    else:
                        result1 = True

                    if posClosingBracket < len(evalString) - 1:
                        evalString2 = evalString[posClosingBracket+1:].strip()
                        evalString2 = _substitudeValue(evalString2,valueList)      
                        result2 =  eval(self.TextFSMOutput[0][textFsmIndex] + " " + evalString2)
                        #print (self.TextFSMOutput[0][textFsmIndex] + " " + evalString2,result2)
                    else:
                        result2 = True

                    if result1 == True and result2 == True:
                        logging.info('textfsm evalListElement returns: True')
                        return True,self.TextFSMOutput
                    else:
                        logging.info('textfsm evalListElement returns: False')
                        return False,self.TextFSMOutput
                else:
                    logging.info('textfsm evalListElement returns: True, short textFSMOutputList ')
                    return False,self.TextFSMOutput
            else:
                return False,self.TextFSMOutput
        elif "evalResultCount" in stepDict:
            evalString = stepDict["evalResultCount"].strip()
            posOpeningBracket = evalString.find("[")
            posClosingBracket = evalString.find("]")
            #print(self.TextFSMOutput)
            countTextFsmRecordsAsString = str(len(self.TextFSMOutput))
            if posOpeningBracket > 0:
                evalString1 = evalString[:posOpeningBracket-1].strip()
                evalString1 = substitudeValue(evalString1,valueList)     
                result1 =  eval(evalString1 + " " + countTextFsmRecordsAsString)
                #print (evalString1 + " " + countTextFsmRecordsAsString,result1)
            else:
                result1 = True

            if posClosingBracket < len(evalString) - 1:
                evalString2 = evalString[posClosingBracket+1:].strip()
                evalString2 = substitudeValue(evalString2,valueList)      
                result2 =  eval(countTextFsmRecordsAsString + " " + evalString2)
                #print (countTextFsmRecordsAsString + " " + evalString2,result2)
            else:
                result2 = True

            if result1 == True and result2 == True:
                logging.info('textfsm evalResultCount returns: True')
                return True,self.TextFSMOutput
            else:
                logging.info('textfsm evalResultCount returns: False')
                return False,self.TextFSMOutput
        else:
            if len(self.TextFSMOutput) == stepDict["checkResultCount"]:
                return True,self.TextFSMOutput
                logging.info('textfsm evalResultCount returns: True')
            else:
                return False,self.TextFSMOutput
                logging.info('textfsm evalResultCount returns: False')
