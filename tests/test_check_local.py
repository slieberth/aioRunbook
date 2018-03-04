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

"""Unit tests for testExecutor connection API"""


import asyncio
from copy import copy
import os
import unittest
from unittest.mock import patch

import sys
sys.path.insert(0, os.path.abspath('..'))
from aioRunbook.aioRunbookScheduler import aioRunbookScheduler
from aioRunbook.tools.helperFunctions import _substitudeVarsInString
import logging
import pprint



class test_check_local(unittest.TestCase):

    def test_check1(self):
        ymlConfigString = """#
config:
  description : ""
  expected : ""
  preparation : ""
  workingDir: ./results_tests
  steps:
    - check:
        name: record test local-shell
        method: local-shell
        commands:
          - 'pip3 freeze'
        textFSM: |
          Value P0 (\d\.\d+)

          Start
            ^PyYAML.*${P0} -> Record
    
          End  
        checkResultCount: 1
        storeFirstTextFsMElementToVariable: tempVariable
  pdfOutput:
    template: "./template_v3.tex"
    author: SL """


        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        #print(myRunbook.configDict["config"]["steps"][0]['check'])
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],True)
        self.assertEqual(myRunbook.varDict['tempVariable'],3.12)

    def test_check2(self):
        ymlConfigString = """#
config:
  description : ""
  expected : ""
  preparation : ""
  workingDir: ./results_tests
  steps:
    - check:
        name: record test local-shell
        method: local-shell
        commands:
          - 'pip3 freeze'
        textFSM: |
          Value P0 (PyYAML.*)

          Start
            ^${P0} -> Record
    
          End  
        checkResultCount: 1
        storeFirstTextFsMElementToVariable: tempVariable
  pdfOutput:
    template: "./template_v3.tex"
    author: SL """
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        #print(myRunbook.configDict["config"]["steps"][0]['check'])
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],True)
        self.assertEqual(myRunbook.varDict['tempVariable'],'PyYAML==3.12')

    def test_check3(self):
        ymlConfigString = """#
config:
  description : ""
  expected : ""
  preparation : ""
  workingDir: ./results_tests
  vars:
    testVar: 3.12
  steps:
    - check:
        name: record test local-shell
        method: local-shell
        commands:
          - 'pip3 freeze'
        textFSM: |
          Value P0 (\d\.\d+)

          Start
            ^PyYAML.*${P0} -> Record
    
          End  
        evalListElement: '[0] >= {{testVar}}'
  pdfOutput:
    template: "./template_v3.tex"
    author: SL """
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],True)

    def test_check4(self):
        ymlConfigString = """#
config:
  description : ""
  expected : ""
  preparation : ""
  workingDir: ./results_tests
  vars:
    testVar: 1
  steps:
    - check:
        name: record test local-shell
        method: local-shell
        commands:
          - 'pip3 freeze'
        textFSM: |
          Value P0 (\d\.\d+)

          Start
            ^PyYAML.*${P0} -> Record
    
          End  
        evalResultCount: '[] >= {{testVar}}'
  pdfOutput:
    template: "./template_v3.tex"
    author: SL """


        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        #print(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['checkCriteris'])
        self.assertIn("PyYAML",myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['checkCriteris'])
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],True)

if __name__ == '__main__':
    logLevel = logging.ERROR
    logLevel = logging.DEBUG
    logging.basicConfig(filename="myLog.log", filemode='w', level=logLevel)
    logging.getLogger().setLevel(logLevel)
    console = logging.StreamHandler()
    console.setLevel(logLevel)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)

    unittest.main()



