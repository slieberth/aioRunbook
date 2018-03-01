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


import asyncio
from copy import copy
import os
import unittest
from unittest.mock import patch
import logging

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from aioRunbook.aioRunbookHttpServer import aioRunbookHttpServer
import pprint
import yaml
from aiohttp.web import Application, Response, StreamResponse, run_app


class test_aioRunbookHttpServer(unittest.TestCase):

    def test_app1(self):
        ymlConfigString = """#
templateDir: "../aioRunbook/templates/"
runbookDirs:
  - "./testDir1"
  - "./testDir2"
  - "./testDir3"
httpPort: 4711  
userAuth:
- - username: CharlieBrown
  - password: test
  - permissions: 
    - viewResults
- - username: MissSophie
  - password: test
  - permissions: 
    - viewResults
    - runTests
- - username: MajorTom
  - password: test
  - permissions: 
    - viewResults
    - runTests
    - editTests
pdfOutput:
  author: SL
  pdfResultDir: ./results_pdfTests
  template: templates/template2.tex
"""
        fh = open("aioServerConfig.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myHttpServer = aioRunbookHttpServer("aioServerConfig.yml")
        loop = asyncio.get_event_loop()
        app = myHttpServer.init(loop)
        if app != None:
            loop.run_until_complete(run_app(app,port=myHttpServer.httpPort))
        else:
            logging.error("cannot load app")

if __name__ == '__main__':
    logLevel = logging.ERROR
    logLevel = logging.DEBUG
    logging.basicConfig(filename="myLog.log", filemode='w', level=logLevel)
    logging.getLogger().setLevel(logLevel)
    console = logging.StreamHandler()
    console.setLevel(logLevel)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)
    #unittest.main()
    myTest = test_aioRunbookHttpServer()
    myTest.test_app1()


