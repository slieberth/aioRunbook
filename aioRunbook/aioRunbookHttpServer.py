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
import os

from .aioRunbookScheduler import aioRunbookScheduler
#from .views import index
import textwrap

from aiohttp.web import Application, Response, StreamResponse, run_app

import aiohttp_jinja2
import jinja2

TEMPLATES_ROOT = "templates"


class aioRunbookHttpServer():
    """ aiohttp


    """


    def __init__(self,configFile):    
        self.errorCounter = 0
        self.configLoaded = self._readYamlFile(configFile)
        self.runbookDirSplitDirs = []

    def init(self,loop):
        app = Application()
        aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('../aioRunbook/templates'))
        #aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('/Users/slieberth/git/aioRunbook/aioRunbook/templates'))
        app.router.add_get('/', self.index)
        app.router.add_get('/listDir', self.listDir)
        if self.configLoaded:
            return app
        else:
            return None

    @aiohttp_jinja2.template('index.html')
    async def index(self,request):
        root="http://"+request.host
        #print (self.runbookDirs)
        self.runbookDirSplitDirs = []
        self.runbookDict = {}
        for runbookDir in self.runbookDirs:
            runbookDirSplitDir = os.path.abspath(runbookDir).split(os.sep)[-1]
            self.runbookDirSplitDirs.append(runbookDirSplitDir)
            self.runbookDict[runbookDirSplitDir] = [f for f in os.listdir(runbookDir) if f.endswith('.yml')]
        #print(self.runbookDict)
        return {"root":root,"runbookDirSplitDirs":self.runbookDirSplitDirs}

#    @aiohttp_jinja2.template('listDir.html')

    @aiohttp_jinja2.template('listDir.html')
    async def listDir(self,request):
        root="http://"+request.host
        all_args = request.query
        if "dir" in all_args.keys():
            yamlDir = all_args["dir"]
        else:
            yamlDir = None  
        fileList = self.runbookDict[yamlDir]
        jsonDateDict = self._upDateJsonDateDict(yamlDir)
        print(jsonDateDict)
        return {"root":root,"runbookDirSplitDirs":self.runbookDirSplitDirs,"yamlDir":yamlDir,"fileList":fileList,
                "jsonDateDict":jsonDateDict}


    def _readYamlFile (self,configFile):
        self.yamlConfigFile = configFile
        self.runbookDict = {}
        logging.info('reading config file: {0}'.format(configFile))
        try:
            with open(configFile) as fh:
                YamlDictString = fh.read ()
                fh.close ()
        except:
            logging.error('cannot open configFile {}'.format(configFile))
            return False   
        try:     
            self.configDict = yaml.load(YamlDictString)
        except:
            logging.error('cannot load YAML File {}'.format(configFile))
            return False
        try:
            self.runbookDirs = self.configDict["runbookDirs"]
        except:
            logging.error('cannot find runbookDirs in File {}'.format(configFile))
            return False
        try:
            self.httpPort = self.configDict["httpPort"]
        except:
            self.httpPort = 8080
        return True

    def _upDateJsonDateDict (self,yamlDir):
        fileList = self.runbookDict[yamlDir]
        jsonDateDict = {}
        dateList  = []
        for x in fileList:
            #print(x)
            #print(os.sep.join([yamlDir,x]))
            try: 
                modTime = time.strftime("%d.%m.%Y %H:%M:%S",time.localtime(os.path.getmtime(x[:-4]+".json")))
            except:
                modTime = "n/a"
            dateList.append(modTime)
        jsonDateDict = dict(zip(self.runbookDict[yamlDir], dateList))
        return jsonDateDict




