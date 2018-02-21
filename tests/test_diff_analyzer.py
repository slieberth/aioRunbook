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

"""Unit tests for diffCheck analyzer"""

import asyncio
from copy import copy
import os
import unittest
from unittest.mock import patch

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from aioRunbook.aioRunbookScheduler import aioRunbookScheduler
import logging
import pprint
import time



class test_diff_analyzer(unittest.TestCase):

    def test_diff1(self):

        """setting the diffSnapshot"""

        ymlConfigString = """#
config:
  steps:
    - check:
        name: record test local-shell
        method: local-shell
        device: local-shell
        vendor: local-shell
        commands:
          - 'pip3 freeze'
        checkMethod: diff
    - check:
        name: record test local-shell
        method: local-shell
        device: local-shell
        vendor: local-shell
        commands:
          - 'pip3 freeze | tail -n 2'
        checkMethod: diff"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop,setDiffSnapshot = True)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],True)
        self.assertEqual(myRunbook.configDict["config"]["steps"][1]['check']['output'][0]['pass'],True)
        myRunbook.writeDiffSnapshotToFile()


    def test_diff2(self):
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],True)
        self.assertEqual(myRunbook.configDict["config"]["steps"][1]['check']['output'][0]['pass'],True)

    def test_diff3(self):

        """setting the diffSnapshot"""

        ymlConfigString = """#
config:
  steps:
    - check:
        name: record test local-shell
        method: local-shell
        device: local-shell
        vendor: local-shell
        commands:
          - 'pip3 freeze'
        checkMethod: diff
        diffZip: true
    - check:
        name: record test local-shell
        method: local-shell
        device: local-shell
        vendor: local-shell
        commands:
          - 'pip3 freeze | tail -n 2'
        checkMethod: diff
        diffZip: true"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop,setDiffSnapshot = True)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],True)
        self.assertEqual(myRunbook.configDict["config"]["steps"][1]['check']['output'][0]['pass'],True)
        myRunbook.writeDiffSnapshotToFile()

    def test_diff4(self):
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],True)
        self.assertEqual(myRunbook.configDict["config"]["steps"][1]['check']['output'][0]['pass'],True)

    def test_diff5(self):

        """setting the diffSnapshot"""

        ymlConfigString = """#
config:
  steps:
    - check:
        name: record test local-shell
        method: local-shell
        device: local-shell
        vendor: local-shell
        commands:
          - 'pip3 freeze'
        checkMethod: diff
        diffTextFSMFilter: | 
          Value P0 (.*y.*)
  
          Start
            ^${P0} -> Record
        
          End"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop,setDiffSnapshot = True)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],True)
        myRunbook.writeDiffSnapshotToFile()

    def test_diff6(self):
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],True)


    def test_diff7(self):

        """setting the diffSnapshot"""

        ymlConfigString = """#
config:
  steps:
    - record:
        name: record test local-shell
        method: local-shell
        commands:
          - 'pip3 freeze'
    - check:
        name: comapre againt previous step 
        method: local-shell
        commands:
          - 'pip3 freeze'
        checkMethod: diff
        diffSource: outputFromStep 1 """
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['record']['output'][0]['pass'],True)
        self.assertEqual(myRunbook.configDict["config"]["steps"][1]['check']['output'][0]['pass'],True)

    def test_diff8(self):

        """setting the diffSnapshot"""

        ymlConfigString = """#
config:
  steps:
    - record:
        name: record test local-shell
        method: local-shell
        commands:
          - 'pip3 freeze'
    - check:
        name: check previous step 
        method: local-shell
        commands:
          - 'pip3 freeze'
        checkMethod: diff
        diffSource: outputFromStep 1
        diffTextFSMFilter: | 
          Value P0 (.*y.*)
  
          Start
            ^${P0} -> Record
        
          End"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['record']['output'][0]['pass'],True)
        self.assertEqual(myRunbook.configDict["config"]["steps"][1]['check']['output'][0]['pass'],True)

    def test_diff9(self):

        """setting the diffSnapshot"""

        ymlConfigString = """#
config:
  loops: 2
  steps:
    - check:
        name: check previous step 
        method: local-shell
        commands:
          - 'pip3 freeze'
        checkMethod: diff
        diffSource: previousLoop"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop))

    def test_diff10(self):

        """setting the diffSnapshot"""

        ymlConfigString = """#
config:
  loops: 2
  steps:
    - check:
        name: check previous step 
        method: local-shell
        commands:
          - 'pip3 freeze'
        checkMethod: diff
        diffSource: previousLoop
        diffTextFSMFilter: | 
          Value P0 (.*y.*)
  
          Start
            ^${P0} -> Record
        
          End"""
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
    myTester = test_diff_analyzer()
    myTester.test_diff9()



