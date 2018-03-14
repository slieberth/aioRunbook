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

"""Unit tests for Macro Tests"""

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



class test_aioRunbook_macros(unittest.TestCase):


    def test_macro1(self):
        ymlMacroString = """#macros
ECHO5:
  - echo cmdString line1
  - echo cmdString line2
  - echo cmdString line3
  - echo cmdString line4
  - echo cmdString line5
"""
        fh = open("testMacroFile.yml",'w')
        fh.write(ymlMacroString)
        fh.close()
        ymlConfigString = """#macroTest
config:
  macroFiles:
    - 'testMacroFile.yml'
  steps:
    - record:
        name: a flock of echo commands 
        method: local-shell
        commands: #-MACRO-ECHO5-#
"""

        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['record']['output'][4]['output'],'cmdString line5')
        #pprint.pprint(myRunbook.configDict)

    def test_macro2(self):
        ymlMacroString = """#macros
MACRO1:
  - '          - echo cmdString line1'
  - '          - echo cmdString line2'
  - '          - echo cmdString line3'
  - '          - echo cmdString line4'
  - '          - echo cmdString line5'
"""
        fh = open("testMacroFile.yml",'w')
        fh.write(ymlMacroString)
        fh.close()
        ymlConfigString = """#macroTest
config:
  macroFiles:
    - 'testMacroFile.yml'
  steps:
    - record:
        name: a flock of echo commands 
        method: local-shell
        commands:
#-MACRO-BLOCK for ELEMENT in MACRO1 -#
#-MACRO-ELEMENT-#
#-MACRO-BLOCK endfor -#
"""

        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['record']['output'][4]['output'],'cmdString line5')
        #pprint.pprint(myRunbook.configDict)



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
    #myTest = test_aioRunbook_break()
    #myTest.test_break1()

    unittest.main()



