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
import os
import logging
from aioRunbook.aioRunbookHttpServer import aioRunbookHttpServer
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

myHttpServer = aioRunbookHttpServer("/aioRunbook/aioServerConfig.yml")
loop = asyncio.get_event_loop()
app = myHttpServer.init(loop)
if app != None:
    loop.run_until_complete(run_app(app,port=myHttpServer.httpPort))
else:
    logging.error("cannot load app")