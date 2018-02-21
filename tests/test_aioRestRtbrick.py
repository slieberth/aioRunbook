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
#import aioRunbook
import pprint
import yaml

from six import StringIO


class test_aioRestRtbrick(unittest.TestCase):

    def test_1(self):

        ymlConfigString = """config:
  steps:
    - record:
        name: "test conversation to JSON"
        method: rest
        vendor: rtbrick 
        device: 127.0.0.1
        port: 8080
        includeRequestInOutput: true
        commands: 
          - get default.bgp.peer peer_ipv4_address 1.1.1.1
          - set global.interface.logical.config interface_name ifl-0/0/1/1/100 interface_description "Interface 0000:24:00.0" admin_status up
          - setTable default.bgp.1.peer-group.iBGP_1.ipv4.unicast table_type bgp.pg type 1
          - '[ "set default.bgp.1.peer-group.iBGP_1.ipv4.unicast prefix4 {}.{}.{}.0/24".format(P1,P2,P3) for P1 in range(89,90) for P2 in range(0,1) for P3 in range(0,2)]'
"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        print(yaml.load(myRunbook.configDict["config"]["steps"][0]['record']['output'][0]['output'])['request'])
        print(yaml.load(myRunbook.configDict["config"]["steps"][0]['record']['output'][1]['output'])['request'])
        print(yaml.load(myRunbook.configDict["config"]["steps"][0]['record']['output'][2]['output'])['request'])
        print(yaml.load(myRunbook.configDict["config"]["steps"][0]['record']['output'][3]['output'])['request'])




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
    myTest = test_aioRunbookScheduler()
    #myTest.test_schedulerForeground()
    #myTest.test_schedulerBackground()
    #myTest.test_break()
    #myTest.test_record()
    #myTest.test_schedulerBackgroundStepRange()


