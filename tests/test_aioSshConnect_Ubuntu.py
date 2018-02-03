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

from six import StringIO


class test_aioRunbook(unittest.TestCase):

    def test_ubuntu1(self):

        ymlHostString = "DUT:  {'device': '192.168.122.151','method':'ssh','vendor':'ubuntu',\
            'password': 'rtbrick', 'user': 'rtbrick'}"
        fh = open("host.yml",'w')
        fh.write(ymlHostString)
        fh.close()
        ymlConfigString = """config:
  hostfiles:
    - ./host.yml
  steps:
    - record:
        name: "DUT - uname -a"
        commands: 
          - uname -a
          - uname -a
          - uname -a"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbook("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['record']['output'][0]['output'],
            "Linux rtbrick-VirtualBox 4.2.0-27-generic #32~14.04.1-Ubuntu SMP Fri Jan 22 15:32:26 UTC 2016 x86_64 x86_64 x86_64 GNU/Linux")




if __name__ == '__main__':
    logLevel = logging.DEBUG
    logLevel = logging.ERROR
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
    #myTest.test_schedulerForeground()
    #myTest.test_schedulerBackground()


