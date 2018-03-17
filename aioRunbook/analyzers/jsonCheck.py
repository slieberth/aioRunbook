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


import sys
import os
import shutil
import time
import pprint
import logging
import datetime
import re
import csv
import json
import yaml
from aioRunbook.tools.helperFunctions import _isInDictionary, _substitudeVarsInString


class jsonCheck:

    """class for verification of data structures (json, yaml).

    """

    @classmethod
    def checkOutputData (self,stepDict,varDict={},configDict={},**kwargs):

        """classmethod function for validatiting the CLI output of a stepdict.

              :param stepDict: The specific test step dictionary, which has both CLI outout and textFSM template attributes.
              :param stepDict["output"]: either a JSON or a YAML loadable string    
              :param stepDict["jsonOneLine"]: one line macro, which can be used for single data checks.   
              :param stepDict["jsonMultiLine"]: one line macro, which can be used for multiple data checks, which are and linked.   
              :param valueList: This list is used to substitude values, respectively store values. The list is derived from valueMatrix[loopCounter]
              :type stepDict: python dict object
              :type stepDict["output"]: either a JSON or a YAML loadable string
              :type stepDict["jsonOneLine"]: string   
              :type stepDict["jsonMultiLine"]: string
              :type valueList: list

        """

        def jsonOneLineStringCheck ( jsonOneLineStr , jsonOneLineStringCheckJsonObject ):
            separators = [ " == " ]
            separatorIncludedFlag = None
            for i,separator in enumerate(separators):
                if separator in jsonOneLineStr: separatorIncludedFlag = i
            if separatorIncludedFlag != None:
                jsonString = jsonOneLineStr.split(separators[i])[0]
                try:
                    responseObj = eval('jsonOneLineStringCheckJsonObject' + jsonString )
                except Exception as errmsg:
                    logging.error(errmsg)  
                    return False,[] 
                jsonMatch = jsonOneLineStr.split(separators[i])[1]
                evalString = str(responseObj) + " == " + jsonMatch
                return eval(evalString),str(responseObj)
            else:
                logging.error("jsonOnelLine split error")  
                return False,[] 

        checkCommandOffsetFromLastCommand = _isInDictionary("checkCommandOffsetFromLastCommand",stepDict,0) - 1        
        try:
            jsonObject = json.loads(stepDict["output"][checkCommandOffsetFromLastCommand]["output"])
        except:
            try:
                jsonObject = yaml.load(stepDict["output"][checkCommandOffsetFromLastCommand]["output"])
            except:
                return False,[],'jsonCheck Yaml Object load error'
            else:
                logging.debug ('jsonCheck Yaml Object loaded')
        else:
            logging.debug ('jsonCheck Json Object loaded')
        if "jsonString" in stepDict.keys():
            logging.debug ('jsonString: ' + stepDict["jsonString"])
            try:
                responseObj = eval('jsonObject' + stepDict["jsonString"] )
            except Exception as errmsg:
                logging.error(errmsg)  
                return False,[errmsg],stepDict["jsonString"] 
            jsonValueList = [responseObj] ###FIXME check for type !!!
            #logging.info ('jsonValueList: {}'.format(jsonValueList))



            #
            #  the remaing lines are related only relate to "jsonString" 
            #
            if "evalListElement" in stepDict:
                evalString = stepDict["evalListElement"].strip()
                #logging.info ('evalString : {}'.format(evalString))
                posOpeningBracket = evalString.find("[")
                posClosingBracket = evalString.find("]")
                jsonListIndex = int(evalString[posOpeningBracket+1:posClosingBracket].strip())
                #logging.info ('jsonListIndex : {}  {}-{}'.format(jsonListIndex,posOpeningBracket,posClosingBracket))
            elif "evalValue" in stepDict:
                evalString = stepDict["evalValue"].strip()
                #logging.info ('evalString : {}'.format(evalString))
                posOpeningBracket = evalString.find("{")
                posClosingBracket = evalString.find("}")
                jsonListIndex = 0

            logging.info ('jsonListIndex : {}  {}-{}'.format(jsonListIndex,posOpeningBracket,posClosingBracket))
            if len (jsonValueList) >= jsonListIndex:
                evalValue = jsonValueList[jsonListIndex]
                logging.info ('evalValue : {} '.format(evalValue))
                if posOpeningBracket > 0:
                    evalString1 = evalString[:posOpeningBracket-1].strip()
                    evalString1 = substitudeValue(evalString1,valueList)    
                    logging.debug ('evalString1: {} '.format(evalString1))         
                    if type( evalValue) == str:
                        result1 =  eval( "'" + evalString1 + "' " + evalValue)
                    else:
                        result1 =  eval( evalString1 + " " + evalValue)
                    logging.debug ("evalString1 {} evalValue {} result1 {}".format(evalString1,evalValue,result1))
                else:
                    result1 = True

                if posClosingBracket < len(evalString) - 1:
                    evalString2 = evalString[posClosingBracket+1:].strip()
                    evalString2 = substitudeValue(evalString2,valueList)  
                    logging.debug ('evalString2: {} '.format(evalString2))   
                    if type( evalValue) == str:
                        logging.info ("'" + evalValue + "' " + evalString2)
                        result2 =  eval("'" + evalValue + "' " + evalString2)
                    else:
                        logging.info ( str(evalValue) + " " + str(evalString2))
                        result2 =  eval(str(evalValue) + evalString2)
                    logging.debug ("evalValue {} evalString2 {} result2 {}".format(evalValue,evalString2,result2) )
                else:
                    result2 = True

                if result1 == True and result2 == True:
                    logging.info('json evalListElement returns: True')
                    return True,jsonValueList,stepDict["jsonString"] 
                else:
                    logging.info('json evalListElement returns: False')
                    return False,jsonValueList,stepDict["jsonString"] 
            else:
                logging.info('json evalListElement returns: False, short json output list ')
                return False,jsonValueList,stepDict["jsonString"] 



        elif "jsonOneLine" in stepDict.keys():     
            jsonOneLineStr = stepDict["jsonOneLine"]
            resVal, resList = list (jsonOneLineStringCheck ( jsonOneLineStr , jsonObject ))
            return resVal, resList, jsonOneLineStr
        elif "jsonMultiLine" in stepDict.keys():     
            jsonMultiLines = stepDict["jsonMultiLine"]
            resultTuples = []
            for jsonOneLineStr in jsonMultiLines:
                resultTuples.append ( list (jsonOneLineStringCheck ( jsonOneLineStr , jsonObject )))
            resVal = True
            resList = []
            for resultTuple in resultTuples:
                if resultTuple[0] == False: resVal = False
                resList += [resultTuple[1]]
            return resVal, resList, "\n".join(jsonMultiLines)
        else:
            logging.error("missing json check selector: jsonOneLine, jsonMultiLine or jsonString ")  
            return False,[],"missing json check selector: jsonOneLine, jsonMultiLine or jsonString "



