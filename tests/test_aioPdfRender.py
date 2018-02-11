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
import concurrent.futures
from copy import copy
import os
import unittest
from unittest.mock import patch
import logging
import pprint
import yaml

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from aioRunbook.aioRunbook import aioRunbook
sys.path.insert(0, os.path.abspath('../aioRunbook/postProcessing/'))
from aioPdfRender import aioPdfRender


import time

class test_aioPdfRender(unittest.TestCase):

    def test_pdfRender1(self):
        ymlConfigString = """#
config:
  pdfOutput:
    author: SL
    pdfResultDir: ./results_pdfTests
    template: ./templates/template.tex
  steps:
  - record:
      commands:
      - pip3 freeze
      hostname: ''
      loopCounter: 1
      method: local-shell
      name: record test local-shell
      output:
      - commandCounter: 1
        commandOrig: pip3 freeze
        elapsed: '0:00:00.556753'
        elapsedRaw: 0.556753
        endTS: '2018-02-11 04:17:52.935360'
        loopCounter: 1
        output: 'aiohttp==2.3.10'
        pass: true
        skip: false
        startTS: '2018-02-11 04:17:52.378607'
        stepCounter: 1
        stepType: record
      stepCounter: 1
      stepIndex: 0
yamlConfigFile: test.yml"""
        processedConfigDict = yaml.load(ymlConfigString)
        myAioPdfRender = aioPdfRender(processedConfigDict,{},"...",False)

    def test_pdfRender2(self):
        ymlConfigString = """#
config:
  steps:
  - record:
      commands:
      - pip3 freeze
      hostname: ''
      loopCounter: 1
      method: local-shell
      name: record test local-shell
      output:
      - commandCounter: 1
        commandOrig: pip3 freeze
        elapsed: '0:00:00.556753'
        elapsedRaw: 0.556753
        endTS: '2018-02-11 04:17:52.935360'
        loopCounter: 1
        output: 'aiohttp==2.3.10'
        pass: true
        skip: false
        startTS: '2018-02-11 04:17:52.378607'
        stepCounter: 1
        stepType: record
      stepCounter: 1
      stepIndex: 0"""
        processedConfigDict = yaml.load(ymlConfigString)
        myAioPdfRender = aioPdfRender(processedConfigDict,{},"...",False)

    def test_pdfRender3(self):
        ymlConfigString = """#
config:
  pdfOutput:
    author: SL
    pdfResultDir: ./results_pdfTests
    template: templates/template.tex
  steps:
  - record:
      commands:
      - pip3 freeze
      hostname: ''
      loopCounter: 1
      method: local-shell
      name: record test local-shell
      output:
      - commandCounter: 1
        commandOrig: pip3 freeze
        elapsed: '0:00:00.556753'
        elapsedRaw: 0.556753
        endTS: '2018-02-11 04:17:52.935360'
        loopCounter: 1
        output: 'aiohttp==2.3.10'
        pass: true
        skip: false
        startTS: '2018-02-11 04:17:52.378607'
        stepCounter: 1
        stepType: record
      stepCounter: 1
      stepIndex: 0
yamlConfigFile: test.yml"""
        processedConfigDict = yaml.load(ymlConfigString)
        myAioPdfRender = aioPdfRender(processedConfigDict,{},"...",False)
        threadExecutor = concurrent.futures.ThreadPoolExecutor(max_workers=3,)
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete( myAioPdfRender.writePdfFile(threadExecutor)) 
        except Exception:
            print("exception consumed")
            raise


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
    #myTest = test_aioSftp()
    #myTest.test_juniper1()


