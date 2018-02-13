#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 by Stefan Lieberth <stefan@lieberth.net>.
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

#  \version   0.2.1
#  \date      09.02.2018

#  0.2.1 get started

import asyncio
import concurrent.futures
#import random
import logging
import yaml
from copy import deepcopy
import pprint
import re
import datetime
from aiohttp import web

from .aioRunbookScheduler import aioRunbookScheduler
import textwrap

from aiohttp.web import Application, Response, StreamResponse, run_app


class aioRunbookHttpServer():
    """ aiohttp


    """

    def __init__(self):    
        self.errorCounter = 0

    async def _intro(self,request):
        txt = textwrap.dedent("""\
            Type {url}/simple or {url}/ in browser url bar
        """).format(url='127.0.0.1:8080')
        binary = txt.encode('utf8')
        resp = StreamResponse()
        resp.content_length = len(binary)
        resp.content_type = 'text/plain'
        await resp.prepare(request)
        resp.write(binary)
        return resp


    async def _simple(self,request):
        return Response(text="Simple answer")


    async def init(self,loop):
        app = Application()
        app.router.add_get('/', self._intro)
        app.router.add_get('/simple', self._simple)

        return app

