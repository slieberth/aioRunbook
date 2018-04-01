# Copyright (c) 2017-2018 by Stefan Lieberth <stefan@lieberth.net>.
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

"""Unit tests for aioSshConnect connection API"""

import asyncio
from copy import copy
import os
import unittest
from unittest.mock import patch

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from aioRunbook.aioRunbookScheduler import aioRunbookScheduler
from aioRunbook.tools.helperFunctions import _substitudeVarsInString
from aioRunbook.caching.cacheCheckResults import cacheCheckResults
import logging
import pprint



class test_aioRunbook_variables(unittest.TestCase):

    def test_var1(self):
        ymlConfigString = """#varTest
config:
  vars:
    testVar: helloWorld
    testSeconds: 1
    valueMatrix:
    - - var11
      - var12
    - - var21
      - var22
  steps:
    - break:
        name: "just a hit return test" """

        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        varDict =  myRunbook.configDict["config"]["vars"]
        self.assertEqual(_substitudeVarsInString("test",varDict=varDict),"test")
        self.assertEqual( _substitudeVarsInString(".VAR.testVar.",varDict=varDict),"helloWorld")
        self.assertEqual( _substitudeVarsInString(".VAR.testSeconds.",varDict=varDict),"1")
        self.assertEqual( _substitudeVarsInString(".VAR.valueMatrix[0][0].",varDict=varDict),"var11")
        self.assertEqual( _substitudeVarsInString(".VAR.valueMatrix[loopIndex][0].",varDict=varDict,loopIndex=0),"var11")
        self.assertEqual( _substitudeVarsInString(".VAR.valueMatrix[loopIndex][1].",varDict=varDict,loopIndex=1),"var22")
        #pprint.pprint(myRunbook.configDict)

    def test_var2(self):
        ymlConfigString = """#varTest
config:
  vars:
    testVar1: helloWorld1
  varFiles:
    - 'testParamaterFile.yml'
  steps:
    - break:
        name: "just a hit return test" """

        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        varDict =  myRunbook.configDict["config"]["vars"]
        self.assertEqual( _substitudeVarsInString(".VAR.testVar1.",varDict=varDict),"helloWorld1")
        #pprint.pprint(myRunbook.configDict)

    def test_var3(self):
        ymlVariableString = """#vars
testVar2: helloWorld2
"""
        fh = open("testParamaterFile.yml",'w')
        fh.write(ymlVariableString)
        fh.close()
        ymlConfigString = """#varTest
config:
  vars:
    testVar1: helloWorld1
  varFiles:
    - 'testParamaterFile.yml'
  steps:
    - break:
        name: "just a hit return test" """

        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        self.assertEqual( _substitudeVarsInString(".VAR.testVar1.",varDict=myRunbook.varDict),"helloWorld1")
        self.assertEqual( _substitudeVarsInString(".VAR.testVar2.",varDict=myRunbook.varDict),"helloWorld2")
        #pprint.pprint(myRunbook.configDict)


    def test_var4(self):
        ymlVariableString = """#vars
testVar2: helloWorld2
"""
        fh = open("testParamaterFile.yml",'w')
        fh.write(ymlVariableString)
        fh.close()
        ymlConfigString = """#varTest
config:
  vars:
    testVar1: helloWorld1
  varFiles:
    - 'testParamaterFile.yml'
  steps:
    - break:
        name: "just a hit return test" """

        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        self.assertEqual( _substitudeVarsInString(".VAR.testVar1.",varDict=myRunbook.varDict),"helloWorld1")
        self.assertEqual( _substitudeVarsInString(".VAR.testVar2.",varDict=myRunbook.varDict),"helloWorld2")
        #pprint.pprint(myRunbook.configDict)



    def test_var5(self):
        ymlConfigString = """#
config:
  description : ""
  expected : ""
  preparation : ""
  workingDir: ./results_tests
  vars:
    text1: "test for substituion in the name attribute"
    text2: freeze
  steps:
    - record:
        name: '.VAR.text1.'
        method: local-shell
        commands:
          - 'pip3 .VAR.text2.'
  pdfOutput:
    template: "./template_v3.tex"
    author: SL """

        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['record']['name'],'test for substituion in the name attribute')
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['record']['output'][0]['commandOrig'],'pip3 freeze')
        #pprint.pprint(myRunbook.configDict)


    def test_var6(self):

        ymlVariableString = """#vars
text1: "test for substitution in the name attribute"
text2: freeze
"""
        fh = open("testVarDefFile.yml",'w')
        fh.write(ymlVariableString)
        fh.close()

        ymlConfigString = """#
config:
  description : ""
  expected : ""
  preparation : ""
  varFiles:
    - testVarDefFile.yml
  steps:
    - record:
        name: '.VAR.text1.'
        method: local-shell
        commands:
          - 'pip3 .VAR.text2.'
  pdfOutput:
    template: "./template_v3.tex"
    author: SL """

        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['record']['name'],'test for substitution in the name attribute')
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['record']['output'][0]['commandOrig'],'pip3 freeze')
        pprint.pprint(myRunbook.configDict)

    def test_var7(self):

        ymlConfigString = """#
config:
  description : ""
  expected : ""
  preparation : ""
  steps:
    - check:
        name: 'record echo 2'
        method: local-shell
        device: local-shell
        vendor: local-shell
        commands:
          - 'echo 2'
        textFSM: |
          Value P0 (\d+)

          Start
            ^${P0} -> Record
    
          End 
        checkResultCount: 1
        storeFirstTextFsMElementToVariable: RESULT2
    - check:
        name: 'record echo 3'
        method: local-shell
        device: local-shell
        vendor: local-shell
        commands:
          - 'echo 3'
        textFSM: |
          Value P0 (\d+)

          Start
            ^${P0} -> Record
    
          End 
        evalListElement: '[0] > .VAR.RESULT2.'
"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 


if __name__ == '__main__':
    logLevel = logging.DEBUG
    #logLevel = logging.ERROR
    logging.basicConfig(filename="myLog.log", filemode='w', level=logLevel)
    logging.getLogger().setLevel(logLevel)
    console = logging.StreamHandler()
    console.setLevel(logLevel)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)

    #unittest.main()
    myTest = test_aioRunbook_variables()
    myTest.test_var7()




