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
from aioRunbook.tools.aioRunbookYmlBlockParser import aioRunbookYmlBlockParser
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
        pprint.pprint(myRunbook.configDict)

    def test_macro2(self):
        ymlMacroString = """#macros
MACRO1:
  - '          - echo .VAR.myVar. line1'
  - '          - echo .VAR.myVar. line2'
  - '          - echo .VAR.myVar. line3'
  - '          - echo .VAR.myVar. line4'
  - '          - echo .VAR.myVar. line5'
"""
        fh = open("testMacroFile.yml",'w')
        fh.write(ymlMacroString)
        fh.close()
        ymlConfigString = """#macroTest
config:
  macroFiles:
    - 'testMacroFile.yml'
  vars:
    myVar: mySubstitudeString
  steps:
#-MACRO-BLOCK for ELEMENT in MACRO1 -#
    - record:
        name: a flock of echo commands 
        method: local-shell
        commands:
#-MACRO-ELEMENT-#
#-MACRO-BLOCK endfor -#
"""

        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][4]['record']['output'][0]['output'],'mySubstitudeString line5')
        #pprint.pprint(myRunbook.configDict)

    def test_macro3(self):
        ymlMacroString = """#macros
saveMacroPreprocessorResultToFile: test1.pre
stopAfterMacroPreprocessor: true
"""
        fh = open("testMacroFile.yml",'w')
        fh.write(ymlMacroString)
        fh.close()
        ymlConfigString = """#macroTest
config:
  macroFiles:
    - 'testMacroFile.yml'
  steps:
#-MACRO-BLOCK set SOURCEIP = "source 49.10.5.254 instance C1_CRS count 1" -#
#-MACRO-BLOCK set DEST_DUTS = [ "20", "21", "22", "30" , "31" , "32" ,\
                                "120", "121", "122", "130" , "131" , "132" ] -#\
#-MACRO-BLOCK for P1 in DEST_DUTS -#\
#-MACRO-BLOCK set DESTIPS = [\
['49.',P1,'.1.254']|join(''),\
['49.',P1,'.2.254']|join(''),\
['49.',P1,'.3.254']|join(''),\
['49.',P1,'.4.254']|join(''),\
['49.',P1,'.5.254']|join(''),\
['49.',P1,'.6.254']|join(''),\
['49.',P1,'.7.254']|join(''),\
['49.',P1,'.8.254']|join(''),\
['49.',P1,'.9.254']|join(''),\
['49.',P1,'.10.254']|join(''),\
['49.',P1,'.11.254']|join(''),\
['49.',P1,'.12.254']|join(''),\
['49.',P1,'.13.254']|join(''),\
['49.',P1,'.14.254']|join(''),\
['49.',P1,'.15.254']|join(''),\
['49.',P1,'.16.254']|join(''),\
['49.',P1,'.17.254']|join(''),\
['49.',P1,'.18.254']|join(''),\
['49.',P1,'.19.254']|join(''),\
['49.',P1,'.20.254']|join(''),\
['49.',P1,'.21.254']|join(''),\
['49.',P1,'.22.254']|join(''),\
['49.',P1,'.23.254']|join(''),\
['49.',P1,'.24.254']|join(''),\
['49.',P1,'.25.254']|join(''),\
['49.',P1,'.26.254']|join(''),\
['49.',P1,'.27.254']|join(''),\
['49.',P1,'.28.254']|join(''),\
['192.168.',P1,'.254']|join('') ] -#
#-MACRO-BLOCK set RESULTS = [\
".*100.00% packet loss.*",\
".*100.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*100.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*100.00% packet loss.*",\
".*100.00% packet loss.*",\
".*100.00% packet loss.*",\
".*100.00% packet loss.*",\
".*100.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*\s0.00% packet loss.*",\
".*100.00% packet loss.*" ] -#
#-MACRO-BLOCK for DESTIP in DESTIPS -#\
    - check:
        name: test macro with echo commands 
        device: local-shell
        vendor: local-shell
        method: local-shell
        commands:
          - echo ping #-MACRO-DESTIP-# #-MACRO-SOURCEIP-#
        textFSMOneLine: '(#-MACRO-RESULTS[loop.index]-#) 1'
#-MACRO-BLOCK endfor -#
#-MACRO-BLOCK endfor -#
"""

        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        #self.assertEqual(myRunbook.configDict["config"]["steps"][0]['record']['output'][0]['output'],'ping 49.10.5.254')
        #pprint.pprint(myRunbook.configDict)


    def test_macro4(self):
        ymlMacroString = """#macros
saveMacroPreprocessorResultToFile: test1.pre
TEXTFSM_PYAML: |2
            Value P0 (\d\.\d+)
  
            Start
              ^PyYAML.*${P0} -> Record
      
            End
"""
        fh = open("testMacroFile.yml",'w')
        fh.write(ymlMacroString)
        fh.close()
        ymlConfigString = """#macroTest
config:
  macroFiles:
    - 'testMacroFile.yml'
  steps:
    - check:
        name: record test local-shell
        method: local-shell
        commands:
          - 'pip3 freeze'
        textFSM: |
#-MACRO- TEXTFSM_PYAML -#
        checkResultCount: 1
"""

        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 


    def test_macro5(self):
        ymlMacroString = """#macros
saveMacroPreprocessorResultToFile: test1.pre
stopAfterMacroPreprocessor: true
"""
        fh = open("testMacroFile.yml",'w')
        fh.write(ymlMacroString)
        fh.close()
        ymlConfigString = """#macroTest
config:
  macroFiles:
    - 'testMacroFile.yml'
  steps:
#-MACRO-BLOCK set ECHO_STRINGS = [ "10", "11" ] -#\
#-MACRO-BLOCK for ECHO_STRING in ECHO_STRINGS -#\
    - record:
        name: record test local-shell
        method: local-shell
        commands:
          - 'echo #-MACRO- ECHO_STRING -#'
#-MACRO-BLOCK endfor -#
"""

        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")





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
    myTest = test_aioRunbook_macros()
    myTest.test_macro5()





