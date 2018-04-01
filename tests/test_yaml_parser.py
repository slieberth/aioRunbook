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

"""Unit tests for testExecutor connection API"""


import asyncio
from copy import copy
import os
import unittest
from unittest.mock import patch

import sys
sys.path.insert(0, os.path.abspath('..'))
from aioRunbook.aioRunbookScheduler import aioRunbookScheduler
from aioRunbook.tools.helperFunctions import _substitudeVarsInString
import logging
import pprint



class test_yaml_parser(unittest.TestCase):

    def remove_macorattribute (self):
        ymlConfigString = """#
#macroTest
config:
  macroFiles:
    - 'testMacroFile.yml'
  steps:
    - record:
        name: record test local-shell
        method: local-shell
        commands:
          - 'echo 10'
    - record:
        name: record test local-shell
        method: local-shell
        commands:
          - 'echo 11'
"""


        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        #print(myRunbook.configDict["config"]["steps"][0]['check'])
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],True)
        self.assertEqual(myRunbook.varDict['tempVariable'],3.12)


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



