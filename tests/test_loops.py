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

"""Unit tests for aioRunbookScheduler connection API"""

import asyncio
from copy import copy
import os
import unittest
from unittest.mock import patch
import logging

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from aioRunbook.aioRunbookScheduler import aioRunbookScheduler
from aioRunbook.tools.helperFunctions import _getOutputInformationTag,_decomposeOutputInformationTag
#import aioRunbook
import pprint
import yaml

from six import StringIO


class test_loops(unittest.TestCase):


    def test_1(self):

        ymlConfigString = """config:
  hostfiles:
    - ./host.yml
  steps:
    - sleep:
        name: sleep 100ms
        seconds: 0.1"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        #pprint.pprint (myRunbook.resultDict)
        self.assertEqual(myRunbook.resultDict["loop_1_step_1_command_1"]["name"],"sleep 100ms")


    def test_2(self):

        ymlConfigString = """config:
  hostfiles:
    - ./host.yml
  loops: 2
  steps:
    - sleep:
        name: sleep 100ms
        seconds: 0.1"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        #pprint.pprint (myRunbook.resultDict)
        self.assertEqual(myRunbook.resultDict["loop_1_step_1_command_1"]["name"],"sleep 100ms")
        self.assertEqual(myRunbook.resultDict["loop_2_step_1_command_1"]["name"],"sleep 100ms")

    def test_3(self):
        
        ouptDict = {'checkResult': '',
                             'commandCounter': 2,
                             'loopCounter': 2,
                             'stepCounter': 1,
                             'stepType': 'check'}
        infTag = _getOutputInformationTag(ouptDict)
        self.assertEqual(infTag ,"loop_2_step_1_command_2")
        loopCounter,stepCounter,cmdCounter = _decomposeOutputInformationTag(infTag)
        self.assertEqual(loopCounter ,2)
        self.assertEqual(stepCounter ,1)
        self.assertEqual(cmdCounter ,2)
        #print(loop,step,cmd)



    def test_4(self):
        ymlConfigString = """#
config:
  loops: 2
  steps:
    - check:
        name: check previous step 
        method: local-shell
        commands:
          - 'pip3 freeze | tail -n 1'
          - 'pip3 freeze | tail -n 2'
        checkMethod: diff
        diffSource: previousLoop"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop))
        #pprint.pprint (myRunbook.resultDict)



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
    #myTest = test_loops()
    #myTest.test_schedulerForeground()
    #myTest.test_schedulerBackground()
    #myTest.test_break()
    #myTest.test_record()
    #myTest.test_schedulerBackgroundStepRange()


