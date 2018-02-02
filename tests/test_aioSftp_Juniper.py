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
from aioRunbook import aioRunbook

import time


class test_aioSftp(unittest.TestCase):

    def test_juniper1(self):

        ymlHostString = "DUT:  {'device': '192.168.56.11','method':'ssh','vendor':'juniper',\
            'password': 'admin1', 'user': 'admin'}"
        fh = open("host.yml",'w')
        fh.write(ymlHostString)
        fh.flush()
        fh.close()
        ymlConfigString = """config:
  hostfiles:
    - ./host.yml
  steps:
    - copy:
        name: "DUT - get config"
        direction: get
        remote: vMX1Base"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.flush()
        fh.close()
        myRunbook = aioRunbook("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        #print(myRunbook.configDict["config"]["steps"][0]['record']['output'][0]['output'])

    def test_juniper2(self):

        ymlHostString = "DUT:  {'device': '192.168.56.11','method':'ssh','vendor':'juniper',\
            'password': 'admin1', 'user': 'admin'}"
        fh = open("host.yml",'w')
        fh.write(ymlHostString)
        fh.flush()
        fh.close()
        ymlConfigString = """config:
  hostfiles:
    - ./host.yml
  steps:
    - copy:
        name: "DUT - put config"
        direction: put
        local: vMX1BaseCopy"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.flush()
        fh.close()
        myRunbook = aioRunbook("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        #print(myRunbook.configDict["config"]["steps"][0]['record']['output'][0]['output'])

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
    #myTest = test_aioSftp()
    #myTest.test_juniper1()


