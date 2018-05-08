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



#logLevel = logging.ERROR
logLevel = logging.DEBUG
logging.basicConfig(filename="myServerLog.log", filemode='w', level=logLevel)
logging.getLogger().setLevel(logLevel)
console = logging.StreamHandler()
console.setLevel(logLevel)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)


myHttpServer = aioRunbookHttpServer("httpServerConfig.yml")
loop = asyncio.get_event_loop()
app = myHttpServer.init(loop)
if app != None:
    loop.run_until_complete(run_app(app,port=myHttpServer.httpPort))
else:
    logging.error("cannot load app")
