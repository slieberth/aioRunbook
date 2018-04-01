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
import logging

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from aioRunbook.aioRunbookScheduler import aioRunbookScheduler

from six import StringIO
import time
import pprint


class test_aioRunbook(unittest.TestCase):

    def test_juniper1(self):

        ymlHostString = "DUT:  {'device': '192.168.56.11','method':'ssh','vendor':'juniper',\
            'password': 'admin1', 'user': 'admin'}"
        fh = open("host.yml",'w')
        fh.write(ymlHostString)
        fh.close()
        ymlConfigString = """config:
  hostfiles:
    - ./host.yml
  sshKnownHostsCheck: true
  steps:
    - record:
        name: "DUT - show version"
        commands: 
          - show version"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        #print(myRunbook.configDict["config"]["steps"][0]['record']['output'][0]['output'])


    def test_juniper2(self):

        ymlHostString = "DUT:  {'device': '192.168.56.11','method':'ssh','vendor':'juniper',\
            'password': 'admin1', 'user': 'admin'}"
        fh = open("host.yml",'w')
        fh.write(ymlHostString)
        fh.close()
        ymlConfigString = """config:
  hostfiles:
    - ./host.yml
  steps:
    - record:
        name: "DUT - configure hostname"
        commands: 
          - config
          - set system host-name myMX
          - commit and-quit"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['record']['output'][2]['output'],"commit complete\nExiting configuration mode")

    def test_juniper3(self):
        #test optional prompt
        ymlHostString = "DUT:  {'device': '192.168.56.11','method':'ssh','vendor':'juniper',\
            'password': 'admin1', 'user': 'admin'}"
        fh = open("host.yml",'w')
        fh.write(ymlHostString)
        fh.close()
        ymlConfigString = """config:
  hostfiles:
    - ./host.yml
  steps:
    - record:
        name: "DUT - abort configure"
        optionalPrompt: '\\(yes\\)'
        commands: 
          - config
          - set system host-name NOTGOOD
          - exit
          - 'yes'"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['record']['output'][2]['output'],"")

    def test_juniper4(self):
        #test timeout
        ymlHostString = "DUT:  {'device': '192.168.56.11','method':'ssh','vendor':'juniper',\
            'password': 'admin1', 'user': 'admin'}"
        fh = open("host.yml",'w')
        fh.write(ymlHostString)
        fh.close()
        ymlConfigString = """config:
  hostfiles:
    - ./host.yml
  steps:
    - record:
        name: "DUT - abort configure by timout closing ssh"
        timeout: 3
        commands: 
          - config
          - set system host-name NOTGOOD
          - exit"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['record']['output'][2]['output'],"")

    def test_juniper5(self):
        #test timeout
        ymlHostString = "DUT:  {'device': '192.168.56.11','method':'ssh','vendor':'juniper',\
            'password': 'admin1', 'user': 'admin'}"
        fh = open("host.yml",'w')
        fh.write(ymlHostString)
        fh.close()
        ymlConfigString = """config:
  hostfiles:
    - ./host.yml
  steps:
    - record:
        name: "DUT - test persistant ssh"
        timeout: 3
        commands: 
          - show version
    - record:
        name: "DUT - test persistant ssh"
        timeout: 3
        commands: 
          - show version
    - record:
        name: "DUT - background"
        timeout: 3
        commands: 
          - show version
    - record:
        name: "DUT - test persistant ssh"
        timeout: 3
        commands: 
          - show version
    - record:
        name: "DUT - test persistant ssh"
        timeout: 3
        commands: 
          - show version"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][1]['record']['output'][0]['pass'],True)
        pprint.pprint(myRunbook.configDict["config"]["steps"][0]['record']['output'][0]['elapsedRaw'])
        #pprint.pprint(myRunbook.configDict["config"]["steps"][0]['record']['output'][0]['output'])
        pprint.pprint(myRunbook.configDict["config"]["steps"][1]['record']['output'][0]['elapsedRaw'])
        pprint.pprint(myRunbook.configDict["config"]["steps"][2]['record']['output'][0]['elapsedRaw'])
        pprint.pprint(myRunbook.configDict["config"]["steps"][3]['record']['output'][0]['elapsedRaw'])
        pprint.pprint(myRunbook.configDict["config"]["steps"][4]['record']['output'][0]['elapsedRaw'])
        #pprint.pprint(myRunbook.configDict["config"]["steps"][4]['record']['output'][0]['output'])



    def test_juniper6(self):
        #test timeout
        ymlHostString = "DUT:  {'device': '192.168.56.11','method':'ssh','vendor':'juniper',\
            'password': 'admin1', 'user': 'admin'}"
        fh = open("host.yml",'w')
        fh.write(ymlHostString)
        fh.close()
        ymlConfigString = """config:
  hostfiles:
    - ./host.yml
  steps:
    - record:
        name: "DUT - bg"
        startInBackground: true
        timeout: 3
        commands: 
          - show system users
    - record:
        name: "DUT - fg1"
        #startInBackground: true
        timeout: 3
        commands: 
          - show system users
    - record:
        name: "DUT - fg2"
        #startInBackground: true
        timeout: 3
        commands: 
          - show system users"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['record']['output'][0]['pass'],True)
        #pprint.pprint(myRunbook.configDict["config"]["steps"][0]['record']['output'])
        #pprint.pprint(myRunbook.configDict["config"]["steps"][1]['record']['output'])
        #pprint.pprint(myRunbook.configDict["config"]["steps"][2]['record']['output'])
        pprint.pprint(myRunbook.configDict["config"]["steps"][0]['record']['output'][0]['elapsedRaw'])
        pprint.pprint(myRunbook.configDict["config"]["steps"][1]['record']['output'][0]['endTS'])
        pprint.pprint(myRunbook.configDict["config"]["steps"][1]['record']['output'][0]['elapsedRaw'])


if __name__ == '__main__':
    #logLevel = logging.ERROR
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
    #myTest = test_aioRunbook()
    #myTest.test_juniper5()


