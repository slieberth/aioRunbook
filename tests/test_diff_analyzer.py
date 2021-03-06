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
        kwargs = {"file":"test.yml"}
        myRunbook = aioRunbookScheduler(**kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop,setDiffSnapshot = True)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],True)
        self.assertEqual(myRunbook.configDict["config"]["steps"][1]['check']['output'][0]['pass'],True)
        myRunbook.writeDiffSnapshotToFile()


    def test_diff2(self):
        kwargs = {"file":"test.yml"}
        myRunbook = aioRunbookScheduler(**kwargs)
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
        kwargs = {"file":"test.yml"}
        myRunbook = aioRunbookScheduler(**kwargs)
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
        kwargs = {"file":"test.yml"}
        myRunbook = aioRunbookScheduler(**kwargs)
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
        kwargs = {"file":"test.yml"}
        myRunbook = aioRunbookScheduler(**kwargs)
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
        kwargs = {"file":"test.yml"}
        myRunbook = aioRunbookScheduler(**kwargs)
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
        kwargs = {"file":"test.yml"}
        myRunbook = aioRunbookScheduler(**kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop))
        self.assertIn("PyYAML",myRunbook.resultDict["loop_2_step_1_command_1"]['checkCriteria'])
        #pprint.pprint(myRunbook.resultDict)

    def test_diff10(self):

        """setting the diffSnapshot"""

        ymlConfigString = """#
config:
  loops: 2
  steps:
    - check:
        name: check previous loop
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
        kwargs = {"file":"test.yml"}
        myRunbook = aioRunbookScheduler(**kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        print(myRunbook.resultDict)

    def test_diff11(self):

        ymlString = """json:
  objects:
  - attribute:
      as_path:
      - 3320
      - 3320
      - 4911
      bgp_nh4: 49.100.1.1
      community:
      - 3320:1276
      - 3320:2010
      - 3320:9010
      origin: EGP
      peer4: 49.100.1.1
      prefix4: 49.11.8.0/24
      received_time: Thu Apr 19 13:40:12 2018
      recv_path_id: 0
      send_path_id: 3282071806
      source: bgp
      source_ip4: 49.100.1.2
      sub_src: Local Peer
    sequence: 285
    update: true"""

        fh = open("testOutput.yml",'w')
        fh.write(ymlString)
        fh.close()

        ymlConfigString = """#
config:
  steps:
    - check:
        name: record test local-shell
        method: local-shell
        commands:
          - cat testOutput.yml
        checkMethod: diff
        diffSource: diffSnapshot
        diffJsonFilter: 
          - '["json"]["objects"][0]["attribute"]["as_path"]'
          - '["json"]["objects"][0]["attribute"]["bgp_nh4"]'
          - '["json"]["objects"][0]["attribute"]["community"]'
          - '["json"]["objects"][0]["attribute"]["origin"]'
          - '["json"]["objects"][0]["attribute"]["med"]'
  pdfOutput:
    template: "./template_v3.tex"
    author: SL """
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        kwargs = {"file":"test.yml","setDiffSnapshot":True}
        myRunbook = aioRunbookScheduler(**kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],True)
        #print (myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['checkCriteria'])
        kwargs = {"file":"test.yml"}
        myRunbook = aioRunbookScheduler(**kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],True)
        #print (myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['checkCriteria'])

    def test_diff12(self):

        jsonString = '{"Result":42,"parfume":4711}'
        fh = open("test.json",'w')
        fh.write(jsonString)
        fh.close()

        ymlConfigString = """#
config:
  steps:
    - check:
        name: record test local-shell
        method: local-shell
        commands:
          - cat test.json
        checkMethod: diff
        diffSource: diffSnapshot
        diffJsonFilter: 
          - ["Result"]
          - ["parfume"]
  pdfOutput:
    template: "./template_v3.tex"
    author: SL """
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        kwargs = {"file":"test.yml","setDiffSnapshot":True}
        myRunbook = aioRunbookScheduler(**kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],True)

        jsonString = '{"Result":43,"parfume":4711}'
        fh = open("test.json",'w')
        fh.write(jsonString)
        fh.close()
        kwargs = {"file":"test.yml"}
        myRunbook = aioRunbookScheduler(**kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        #print (myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['checkResult'])
        print (myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['checkCriteria'])
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],False)

    def test_diff13(self):

        jsonString = 'string to produce json loaderror'
        fh = open("test.json",'w')
        fh.write(jsonString)
        fh.close()

        ymlConfigString = """#
config:
  steps:
    - check:
        name: record test local-shell
        method: local-shell
        commands:
          - cat test.json
        checkMethod: diff
        diffSource: diffSnapshot
        diffJsonFilter: 
          - ["Result"]
          - ["parfume"]
  pdfOutput:
    template: "./template_v3.tex"
    author: SL """
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        kwargs = {"file":"test.yml","setDiffSnapshot":True}
        myRunbook = aioRunbookScheduler(**kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],True)

        jsonString = '{"Result":43,"parfume":4711}'
        fh = open("test.json",'w')
        fh.write(jsonString)
        fh.close()
        kwargs = {"file":"test.yml"}
        myRunbook = aioRunbookScheduler(**kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        #print (myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['checkResult'])
        print (myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['checkCriteria'])
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],False)



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
    myTester.test_diff13()



