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
from aioRunbook.aioRunbook import aioRunbook
import logging
import pprint



class test_diff_analyzer(unittest.TestCase):

    def test_diff1(self):
        ymlConfigString = """# diff test 1 runbook
config:
  steps:
    - check:
        name: record test local-shell
        method: local-shell
        commands:
          - echo "Hello World" 
        checkMethod: diff """
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbook("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        pprint.pprint(myRunbook.configDict)


    def test_diff2(self):
        myRunbook = aioRunbook("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        pprint.pprint(myRunbook.configDict)

    def test_diff3(self):
        ymlConfigString = """# diff test 1 runbook
config:
  steps:
    - check:
        name: record test local-shell
        method: local-shell
        commands:
          - echo "This is an Error" 
        checkMethod: diff
diffStrings:
  loop_1_step_1: Hello World """
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbook("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        pprint.pprint(myRunbook.configDict)

    def test_diff4(self):
        ymlConfigString = """# diff test 1 runbook
config:
  steps:
    - check:
        name: record test local-shell
        method: local-shell
        commands:
          - 'pip3 freeze | tail -n 2'
        checkMethod: diff
    - check:
        name: record test local-shell
        method: local-shell
        commands:
          - 'pip3 freeze | tail -n 2'
        checkMethod: diff """
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbook("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        pprint.pprint(myRunbook.configDict)

    def test_diff5(self):
        myRunbook = aioRunbook("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        pprint.pprint(myRunbook.configDict)

    def test_diff6(self):
        ymlConfigString = """# diff test 1 runbook
config:
  steps:
    - check:
        name: record test local-shell
        method: local-shell
        commands:
          - 'pip3 freeze | tail -n 2'
        checkMethod: diff
    - check:
        name: record test local-shell
        method: local-shell
        commands:
          - 'pip3 freeze | tail -n 2'
        checkMethod: diff 
diffStrings:
  loop_1_step_1: 'urllib3==1.22

    yarl==1.1.0'
  loop_1_step_2: 'urllib3==1.22

    yarl==1.1.1'"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbook("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        pprint.pprint(myRunbook.configDict)


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
    myTest = test_diff_analyzer()
    myTest.test_diff1()
    myTest.test_diff2()
    myTest.test_diff3()
    myTest.test_diff4()
    myTest.test_diff5()
    myTest.test_diff6()


