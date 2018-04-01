#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  \author    Stefan Lieberth / Maik Pfeil
#  \version   3.03.01
#  \date      26.07.2017 

# change log: added versions

import yaml
from collections import OrderedDict
import pprint
from copy import deepcopy
import os
import sys
import shutil
import logging
import pprint


class aioRunbookYmlBlockParser(object):

    def __init__(self,**kwargs): 
        if "configFile" in kwargs.keys():
            with open(kwargs["configFile"]) as fh:
                YamlString = fh.read ()
                fh.close ()
            self.configLines = YamlString.split("\n")
        elif "configString" in kwargs.keys():
            self.configLines = kwargs["configString"].split("\n")


    def _findFirstLineStartingWith (searchStr,Lines):
        for i,line in enumerate(Lines):
            if line.startswith(searchStr) :
                return i
        return None

    def _getBlock (lineNr,allLines):
        lineStr = allLines[lineNr]
        indent = len (lineStr) - len(lineStr.lstrip())
        #print ("indent",indent,lineStr)
        for j,blockLine in enumerate(allLines[lineNr+1:]):
            newIndent = len (blockLine) - len(blockLine.lstrip())
            if newIndent == indent:
                #print (allLines[lineNr:lineNr+j+1])
                return allLines[lineNr:lineNr+j+1]
        return [] 

    def _getBlocks (indent,allLines):
        #pprint.pprint (allLines)
        blockStartLine = 0
        blockNr = 0
        returnBlocks =[[]]
        for j,blockLineStr in enumerate(allLines[1:]):      #exclude first line steps:
            newIndent = len (blockLineStr) - len(blockLineStr.lstrip())
            #if newIndent == indent and j > 0  #fix for check
            if newIndent == indent and j > 0 and len(blockLineStr) > indent:  #fix for check textfsm
                returnBlocks.append([])
                blockNr += 1
            returnBlocks[blockNr].append(blockLineStr)
        return returnBlocks


    @classmethod
    def getConfigBlock(self,**kwargs): 
        if "configFile" in kwargs.keys():
            with open(kwargs["configFile"]) as fh:
                YamlString = fh.read ()
                fh.close ()
            self.configLines = YamlString.split("\n")
        elif "configString" in kwargs.keys():
            self.configLines = kwargs["configString"].split("\n")
        configLine = self._findFirstLineStartingWith("config:",self.configLines )
        pdfLine = self._findFirstLineStartingWith("pdfRender:",self.configLines )
        diffStringLine = self._findFirstLineStartingWith("diffSnapshot:",self.configLines )
        #print (configLine,pdfLine,diffStringLine)
        if configLine and pdfLine:
            return "\n".join(self.configLines[configLine:pdfLine])
        elif configLine and diffStringLine:
            return "\n".join(self.configLines[configLine:diffStringLine])
        elif configLine:
            return "\n".join(self.configLines[configLine:])
        else:
            return "###Error###"



    @classmethod
    def getStepBlock(self,**kwargs): 
        if "configFile" in kwargs.keys():
            with open(kwargs["configFile"]) as fh:
                YamlString = fh.read ()
                fh.close ()
            self.configLines = YamlString.split("\n")
        elif "configString" in kwargs.keys():
            self.configLines = kwargs["configString"].split("\n")
        stepLine = self._findFirstLineStartingWith("  steps:",self.configLines )
        headerBlock = self.configLines[:stepLine]
        stepBlock = self._getBlock (stepLine,self.configLines)  #list of lines for all Blocks
        stepSubBlocks = self._getBlocks (4,stepBlock)    #list of list of lines for all discrete steps
        pdfOutputBlock = self.configLines[stepLine+len(stepBlock):]
        return "\n".join(stepSubBlocks[kwargs["blockNr"]])

    @classmethod
    def setStepBlock(self,**kwargs): 
        if "configFile" in kwargs.keys():
            with open(kwargs["configFile"]) as fh:
                YamlString = fh.read ()
                fh.close ()
            self.configLines = YamlString.split("\n")
        elif "configString" in kwargs.keys():
            self.configLines = kwargs["configString"].split("\n")
        stepLine = ymlBlockParser._findFirstLineStartingWith("  steps:",self.configLines )
        headerBlock = self.configLines[:stepLine+1]
        stepBlock = ymlBlockParser._getBlock (stepLine,self.configLines)  #list of lines for all Blocks
        stepSubBlocks = ymlBlockParser._getBlocks (4,stepBlock)    #list of list of lines for all discrete steps
        blockId = kwargs["blockNr"]
        pdfOutputBlock = self.configLines[stepLine+len(stepBlock):]
        newBlockLines = kwargs["blockString"].split("\n")
        stepSubBlocks[blockId] = newBlockLines
        dumpStr = "\n".join(headerBlock) + "\n"
        for block in stepSubBlocks:
            dumpStr += "\n".join(block) + "\n"
        dumpStr += "\n".join(pdfOutputBlock) 
        return dumpStr

    @classmethod
    def removeMacroAttributeLines(self,**kwargs): 
        if "configFile" in kwargs.keys():
            with open(kwargs["configFile"]) as fh:
                YamlString = fh.read ()
                fh.close ()
            self.configLines = YamlString.split("\n")
            logging.debug ("removeMacroAttributeLines {} loaded".format(kwargs["configFile"]))
        elif "configString" in kwargs.keys():
            self.configLines = kwargs["configString"].split("\n")
        macroLine = None
        macroEndLine = None
        for i,line in enumerate(self.configLines):
            if macroLine and macroEndLine == None: 
                if line[3] != "-":
                    macroEndLine =  i
                    #print ("macroEndLine: {}".format(macroEndLine))
            if line.startswith("  macroFiles:") :
                macroLine =  i
                #print ("macroLine: {}".format(macroLine))
        if macroLine and macroEndLine:
            #print (self.configLines[macroLine:macroEndLine+1])
            logging.debug ("removeMacroAttributeLines remove lines {}".format(self.configLines[macroLine:macroEndLine+1]))
        if macroLine and macroEndLine:
            return "\n".join(self.configLines[:macroLine]+self.configLines[macroEndLine+1:])
        else:
            return self.configLines


