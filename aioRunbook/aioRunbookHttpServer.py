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
from textwrap import dedent

import base64
from cryptography import fernet
from aiohttp import web
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_security import setup as setup_security
from aiohttp_security import SessionIdentityPolicy

from aiohttp_security import (
    remember, forget, authorized_userid,
    has_permission, login_required,
)

from .auth.authz import DictionaryAuthorizationPolicy, check_credentials
from .auth.handlers import configure_handlers
#from demo.dictionary_auth.users import user_map

import os
import time
from collections import namedtuple


from .aioRunbookScheduler import aioRunbookScheduler
from aioRunbook.tools.helperFunctions import _getOutputInformationTag,_decomposeOutputInformationTag
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
        app.router.add_get('/login', self.login)
        app.router.add_get('/logout', self.logout)
        app.router.add_get('/home', self.home)
        app.router.add_get('/listDir', self.listDir)
        app.router.add_get('/viewYamlFile', self.viewYamlFile)
        app.router.add_get('/execYamlFile', self.execYamlFile)
        app.router.add_get('/viewResultFile', self.viewResultFile)
        app.user_map = self.user_map
        configure_handlers(app)

        # secret_key must be 32 url-safe base64-encoded bytes
        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)

        storage = EncryptedCookieStorage(secret_key, cookie_name='API_SESSION')
        setup_session(app, storage)

        policy = SessionIdentityPolicy()
        setup_security(app, policy, DictionaryAuthorizationPolicy(self.user_map))

        if self.configLoaded:
            return app
        else:
            return None

    @has_permission('protected')
    @aiohttp_jinja2.template('index.html')
    async def home(self,request):
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

    #@has_permission('protected')
    @aiohttp_jinja2.template('index.html')
    async def index(self,request):
        username = await authorized_userid(request)
        root="http://"+request.host
        if username:
            #print (self.runbookDirs)
            self.runbookDirSplitDirs = []
            self.runbookDict = {}
            for runbookDir in self.runbookDirs:
                runbookDirSplitDir = os.path.abspath(runbookDir).split(os.sep)[-1]
                self.runbookDirSplitDirs.append(runbookDirSplitDir)
                self.runbookDict[runbookDirSplitDir] = [f for f in os.listdir(runbookDir) if f.endswith('.yml')]
                #template = index_template.format(
                #message='Hello, {username}!'.format(username=username))
            return {"root":root,"runbookDirSplitDirs":self.runbookDirSplitDirs,"username":username}
        else:
            index_template = dedent("""
                <!doctype html>
                    <head></head>
                    <body>
                        <form action="/login" method="post">
                            <input type="text" name="username">
                            <input type="password" name="password">
                            <input type="submit" value="Login">
                        </form>
                    </body>
            """)
            template = index_template.format()
            return {"root":root,"username":None}
            #return web.Response(text=template,content_type='text/html',)


    async def login(self,request):
        response = web.HTTPFound('/')
        form = await request.post()
        username = form.get('username')
        password = form.get('password')
        verified = await check_credentials(
            request.app.user_map, username, password)
        if verified:
            await remember(request, response, username)
            return response
        return web.HTTPUnauthorized(body='Invalid username / password combination')

    @aiohttp_jinja2.template('index.html')
    async def logout(self,request):
        root="http://"+request.host
        response = web.Response(
            text='You have been logged out',
            content_type='text/html',
        )
        await forget(request, response)
        #template = index_template.format()
        #return web.Response(text=template,content_type='text/html',)
        return {"root":root,"username":None}

    @has_permission('protected')
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

    @has_permission('protected')
    @aiohttp_jinja2.template('listDir.html')
    async def execYamlFile(self,request):
        root="http://"+request.host
        all_args = request.query
        print(all_args)
        if "dir" in all_args.keys():
            yamlDir = all_args["dir"]
        else:
            yamlDir = None 
        yamFileName  = None
        if "file" in all_args.keys():
            yamFileName = all_args["file"]
        if yamlDir != None and yamFileName  != None:
            yamlFilePath = os.sep.join([yamlDir,yamFileName])
            print (yamlFilePath)
            fileList = self.runbookDict[yamlDir]
            jsonDateDict = self._upDateJsonDateDict(yamlDir)
            try:
                with open(yamlFilePath) as fh:
                    YamlDictString = fh.read ()
                    fh.close ()
            except:
                logging.error('cannot open configFile {}'.format(yamlFilePath))
                return 'cannot open configFile {}'.format(yamlFilePath)
            else:
                try:
                    myRunbook = aioRunbookScheduler(yamlFilePath)
                    loop = asyncio.get_event_loop()
                    threadExecutor = concurrent.futures.ThreadPoolExecutor(max_workers=10,) 
                    #loop.run_until_complete(myRunbook.execSteps(loop,threadExecutor)) 
                    #await myRunbook.execSteps(loop,threadExecutor)
                    #logging.debug("adding background tasks myRunbook.execSteps(loop,threadExecutor)")  
                    threadExecutor = concurrent.futures.ThreadPoolExecutor(max_workers=10,)                      
                    bgTask = loop.create_task(myRunbook.execStepsAndSaveDicts(loop))

                except Exception as e:
                    logging.error('cannot run  aioRunbookScheduler {} {}'.format(yamlFilePath,e))
                    errorMessage =  'cannot run  aioRunbookScheduler {}: {}'.format(yamlFilePath,e)
                    return {"root":root,"runbookDirSplitDirs":self.runbookDirSplitDirs,"yamlDir":yamlDir,"fileList":fileList,
                        "jsonDateDict":jsonDateDict,"errorMessage":errorMessage}
                else:
                    #await myRunbook.saveConfigDictToJsonFile()
                    #await myRunbook.saveResultDictToJsonFile()
                    return web.HTTPFound('{}/listDir?dir={}'.format(root,yamlDir))
        #print(jsonDateDict)
        return {"root":root,"runbookDirSplitDirs":self.runbookDirSplitDirs,"yamlDir":yamlDir,"fileList":fileList,
                "jsonDateDict":jsonDateDict}

    @has_permission('protected')
    @aiohttp_jinja2.template('viewResultFile.html')
    async def viewResultFile(self,request):
        root="http://"+request.host
        all_args = request.query
        #print(all_args)
        if "dir" in all_args.keys():
            yamlDir = all_args["dir"]
        else:
            yamlDir = None 
        yamFileName  = None
        if "file" in all_args.keys():
            yamFileName = all_args["file"]
        if yamlDir != None and yamFileName  != None:
            yamlFilePath = os.sep.join([yamlDir,yamFileName])
            #print (yamlFilePath)
            try:
                with open(yamlFilePath) as fh:
                    YamlDictString = fh.read ()
                    fh.close ()
            except:
                logging.error('cannot open configFile {}'.format(yamlFilePath))
                return 'cannot open configFile {}'.format(yamlFilePath)
            else:
                try:
                    myRunbook = aioRunbookScheduler(yamlFilePath)
                    loop = asyncio.get_event_loop()
                    resultDict = await myRunbook.getResultFileContent(loop)
                except:
                    resultDict = None
                    logging.error('cannot load resultDict aioRunbookScheduler {}'.format(yamlFilePath))
                    return 'cannot load resultDict aioRunbookScheduler {}'.format(yamlFilePath)
        #pprint.pprint(resultDict)
        fileList = self.runbookDict[yamlDir]
        jsonDateDict = self._upDateJsonDateDict(yamlDir)
        stepCommandOutputs = []
        stepCommandOutputIds = []
        for cmdOutputId in resultDict.keys():
            loopCounter,stepCounter,cmdCounter = _decomposeOutputInformationTag(cmdOutputId)
            stepCommandOutputId =  loopCounter*1000000+stepCounter*1000+cmdCounter
            stepCommandOutputIds.append(stepCommandOutputId)
            resultDict[cmdOutputId]["Id"] = stepCommandOutputId
        stepCommandOutputIds.sort()
        #print(stepCommandOutputIds)
        #pprint.pprint(resultDict)
        for Id in stepCommandOutputIds:
            stepCommandOutputs.append([ resultDict[x] for x in resultDict.keys() if resultDict[x]["Id"] == Id ][0])
        #print(jsonDateDict)
        return {"root":root,"runbookDirSplitDirs":self.runbookDirSplitDirs,"yamlDir":yamlDir,"fileList":fileList,
                "jsonDateDict":jsonDateDict, "stepCommandOutputs":stepCommandOutputs,"filename":yamFileName}


    @has_permission('protected')
    @aiohttp_jinja2.template('viewYamlFile.html')
    async def viewYamlFile(self,request):
        root="http://"+request.host
        all_args = request.query
        #print(all_args)
        if "dir" in all_args.keys():
            yamlDir = all_args["dir"]
        else:
            yamlDir = None 
        yamFileName  = None
        if "file" in all_args.keys():
            yamFileName = all_args["file"]
        if yamlDir != None and yamFileName  != None:
            yamlFilePath = os.sep.join([yamlDir,yamFileName])
            #print (yamlFilePath)
            try:
                with open(yamlFilePath) as fh:
                    yamlLines = [ x.rstrip().replace(" ","&nbsp;") for x in fh.readlines() ]
                    fh.close ()
            except Exception as e:
                logging.error('cannot open configFile {} {}'.format(yamlFilePath,e))
                return {"errorMessage":'cannot open configFile {} {}'.format(yamlFilePath,e)}
        fileList = self.runbookDict[yamlDir]
        return {"root":root,"runbookDirSplitDirs":self.runbookDirSplitDirs,"yamlDir":yamlDir,"yamlLines":yamlLines}


#    def saveConfigDictToJsonFile(self,future):
#         configDict = future.result()
#         await myRunbook.saveConfigDictToJsonFile()
#         await myRunbook.saveResultDictToJsonFile()
#         stepCount = resultBackgroundStepDict["output"][0]["stepCount"]
#         stepId = resultBackgroundStepDict["output"][0]["stepType"]
#         self.configDict["config"]["steps"][stepCount][stepId] = resultBackgroundStepDict
#         pass


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
        userNamedTuple = namedtuple('User', ['username', 'password', 'permissions'])
        self.user_map = {user.username: user for user in [userNamedTuple(self.configDict["user"],self.configDict["password"], ('protected'))]}
        pprint.pprint(self.user_map)
        #{'test': User(username='test', password='test', permissions=('protected',))}
        return True

    def _upDateJsonDateDict (self,yamlDir):
        fileList = self.runbookDict[yamlDir]
        jsonDateDict = {}
        dateList  = []
        for yamFileName in fileList:
            yamlFilePath = os.sep.join([yamlDir,yamFileName])
            #print(yamlFilePath)
            #print(os.path.getmtime(yamlFilePath[:-4]+".json"))
            try: 
                modTime = time.strftime("%d.%m.%Y %H:%M:%S",time.localtime(os.path.getmtime(yamlFilePath[:-4]+".json")))
            except:
                modTime = "n/a"
            dateList.append(modTime)
        jsonDateDict = dict(zip(self.runbookDict[yamlDir], dateList))
        return jsonDateDict




