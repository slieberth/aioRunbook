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

"""Unit tests for aioRunbook connection API"""

import asyncio
from copy import copy
import os
import unittest
from unittest.mock import patch
import logging

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from aioRunbook import aioRunbook
import pprint
import yaml

from six import StringIO


class test_aioRunbook(unittest.TestCase):

    def test_loadRunbook(self):

        ymlConfigString = """config:
  steps:
    - record:
        name: "DUT - show version"
        commands: 
          - show version
          - show system users"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbook("test.yml")
        self.assertEqual(myRunbook.configDict, 
             {'config': {'steps': [{'record': {'commands': ['show version', 'show system users'], 
             'name': 'DUT - show version'}}]}})

    def test_hostfile(self):

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
        name: "DUT - show version"
        commands: 
          - show version
          - show system users"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbook("test.yml")
        self.assertEqual(myRunbook.hostfiles,['./host.yml'])
        self.assertEqual(myRunbook.hostDict["DUT"],{'device': '192.168.56.11','method':'ssh',
                                   'vendor':'juniper','password': 'admin1', 'user': 'admin'})

    def test_sleep1Sec(self):

        ymlConfigString = """config:
  hostfiles:
    - ./host.yml
  steps:
    - sleep:
        name: test sleep 1 sec"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbook("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertGreater(myRunbook.configDict["config"]["steps"][0]['sleep']['output'][0]['elapsedRaw'],1)

    def test_sleep0_5Sec(self):

        ymlConfigString = """config:
  hostfiles:
    - ./host.yml
  steps:
    - sleep:
        name: test sleep
        seconds: 0.5"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbook("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertGreater(myRunbook.configDict["config"]["steps"][0]['sleep']['output'][0]['elapsedRaw'],0.5)

    def test_schedulerForeground(self):

        ymlConfigString = """config:
  hostfiles:
    - ./host.yml
  steps:
    - sleep:
        name: test sleep 1 sec
    - sleep:
        name: test sleep 2 sec"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbook("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertGreater(myRunbook.configDict["config"]["steps"][0]['sleep']['output'][0]['elapsedRaw'],1)
        self.assertGreater(myRunbook.configDict["config"]["steps"][1]['sleep']['output'][0]['elapsedRaw'],2)
        pprint.pprint (myRunbook.configDict)

    def test_schedulerBackground(self):

        ymlConfigString = """config:
  hostfiles:
    - ./host.yml
  steps:
    - sleep:
        name: test sleep 1 sec
        startInBackground: true
    - sleep:
        name: test sleep 2 sec
        startInBackground: true"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbook("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertGreater(myRunbook.configDict["config"]["steps"][0]['sleep']['output'][0]['elapsedRaw'],1)
        self.assertGreater(myRunbook.configDict["config"]["steps"][1]['sleep']['output'][0]['elapsedRaw'],2)
        pprint.pprint (myRunbook.configDict)

    def test_record_localShell(self):
        ymlHostString = "mySystem: {'device': 'local-shell','vendor':'local-shell', 'method':'local-shell' }"
        fh = open("host.yml",'w')
        fh.write(ymlHostString)
        fh.flush()
        fh.close()
        ymlConfigString = """config:
  hostfiles:
    - ./host.yml
  valueMatrix: [[""]]
  steps:
    - record: 
        name: mySystem - test command concatenation
        commands: 
          - "ls"
          - "cd ..; ls" """
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbook("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        print (yaml.dump (myRunbook.configDict, default_flow_style=False))

    def test_break(self):
        ymlHostString = "mySystem: {'device': 'local-shell','vendor':'local-shell', 'method':'local-shell' }"
        fh = open("host.yml",'w')
        fh.write(ymlHostString)
        fh.flush()
        fh.close()
        ymlConfigString = """config:
  hostfiles:
    - ./host.yml
  valueMatrix: [[""]]
  steps:
    - break: 
        name: break test"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbook("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        print (yaml.dump (myRunbook.configDict, default_flow_style=False))

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

    #unittest.main()
    myTest = test_aioRunbook()
    myTest.test_schedulerForeground()
    myTest.test_schedulerBackground()
    myTest.test_break()
    #myTest.test_record()


