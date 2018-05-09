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
import json

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
from aioRunbook.postProcessing.aioPdfRender import aioPdfRender
import textwrap

from aiohttp.web import Application, Response, StreamResponse, run_app

import aiohttp_jinja2
import jinja2

TEMPLATES_ROOT = "templates"

SCHEDULER_DEFAULT_KWARGS = {'macrofile' :None,
             'logfile': 'testExecutor3.log',
             'logging': 'info',
             'pdflatex': False,
             'keepTexFile': False,
             'setDiffSnapshot': False,
             'tester': None,
             'verbose': True
             }


class aioRunbookHttpServer():
    """ aiohttp


    """


    def __init__(self,configFile):    
        self.errorCounter = 0
        self.configLoaded = self._readYamlFile(configFile)
        self.runbookDirSplitDirs = []
        self.bgList = []
        self.bgYamlDict = {}
        self.fifoFileList = []

    def init(self,loop):
        app = Application()
        aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(self.templateDir))
        #aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('/Users/slieberth/git/aioRunbook/aioRunbook/templates'))
        app.router.add_get('/', self.index)
        app.router.add_get('/login', self.login)
        app.router.add_get('/logout', self.logout)
        app.router.add_get('/listDir', self.listDir)
        app.router.add_get('/viewYamlFile', self.viewYamlFile)
        app.router.add_get('/execYamlFile', self.execYamlFile)
        app.router.add_get('/execAllFilesFromDir', self.execYamlFile)
        app.router.add_get('/viewResultFile', self.viewResultFile)
        app.router.add_get('/createPDF', self.createPDF)
        app.router.add_route('*','/settings',self.settings)
        app.router.add_get('/saveConfig',self.saveConfig)
        app.router.add_get('/confirmSetDiffSnapshot',self.confirmSetDiffSnapshot) 
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

#     @has_permission('viewResults')
#     @aiohttp_jinja2.template('index.html')
#     async def home(self,request):
#         root="http://"+request.host
#         #print (self.runbookDirs)
#         self.runbookDirSplitDirs = []
#         self.runbookDict = {}
#         for runbookDir in self.runbookDirs:
#             runbookDirSplitDir = os.path.abspath(runbookDir).split(os.sep)[-1]
#             self.runbookDirSplitDirs.append(runbookDirSplitDir)
#             self.runbookDict[runbookDirSplitDir] = [f for f in os.listdir(runbookDir) if f.endswith('.yml')]
#         #print(self.runbookDict)
#         return {"root":root,"runbookDirSplitDirs":self.runbookDirSplitDirs}

    #@has_permission('protected')
    @aiohttp_jinja2.template('index.html')
    async def index(self,request):
        username = await authorized_userid(request)
        root="http://"+request.host
        if username:
            #print (self.runbookDirs)
            self.runbookDirSplitDirs = []
            self.runbookDict = {}
            #
            if self.autoRunbookDirs == True:
                self.runbookDirs = self._findDirsWithYamlFilesInPwd(self.runbookParentDir)
            #
            self.runbookDirSplitDirs = []
            self.runbookExecAllDict = {}
            for runbookDirObj in self.runbookDirs:
                if type(runbookDirObj) is dict:  #execAll   ###FIXME### 
                    runbookDir = list(runbookDirObj.keys())[0]
                    if "execAll" in  runbookDirObj[runbookDir].keys():
                        self.runbookExecAllDict[runbookDir] = runbookDirObj[runbookDir]
                else:
                    runbookDir = runbookDirObj
                runbookDirSplitDir = runbookDir
                self.runbookDirSplitDirs.append(runbookDir)
                self.runbookDict[runbookDirSplitDir] = [f for f in os.listdir(runbookDir) if f.endswith('.yml')]
            print(self.runbookExecAllDict)
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

    #@has_permission('viewResults')
    @aiohttp_jinja2.template('listDir.html')
    async def listDir(self,request):
        root="http://"+request.host
        all_args = request.query
        execAllFlag = False
        if "dir" in all_args.keys():
            yamlDir = all_args["dir"]
            if yamlDir in self.runbookExecAllDict.keys():
                if "execAll" in self.runbookExecAllDict[yamlDir].keys():
                    if self.runbookExecAllDict[yamlDir]["execAll"] == True:
                        execAllFlag = True
        else:
            yamlDir = None  
        #print ("execAllFlag = {}".format(execAllFlag))
        fileList = self.runbookDict[yamlDir]
        jsonDateDict = self._upDateJsonDateDict(yamlDir)
        jsonErrorDict = self._upDateJsonErrorDict(yamlDir)
        #print(jsonDateDict)
        if len([task for task in self.bgList if not task.done()]) > 0:
            bgFileList = []
            for task in self.bgList:
                if not task.done():
                    bgFileList.append(self.bgYamlDict[task])
            errorMessage = "background tasks to be done {}".format(bgFileList)
        else:
            errorMessage = None
        if len(self.fifoFileList) > 0:
            files = [ x[0] for x in self.fifoFileList ]
            if errorMessage == None:
                errorMessage = "background files to be done {}".format(files)
            else:
                errorMessage += "background files to be done {}".format(files)
        return {"root":root,"runbookDirSplitDirs":self.runbookDirSplitDirs,"yamlDir":yamlDir,"fileList":fileList,
                "jsonDateDict":jsonDateDict,"errorMessage":errorMessage,"jsonErrorDict":jsonErrorDict,"execAllFlag":execAllFlag}

    @has_permission('runTests')
    @aiohttp_jinja2.template('listDir.html')
    async def execYamlFile(self,request):
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
                print (yamlFilePath)
                fileList = self.runbookDict[yamlDir]
                jsonDateDict = self._upDateJsonDateDict(yamlDir)
                jsonErrorDict = self._upDateJsonErrorDict(yamlDir)
                if self.scheduler_settingsDict["setDiffSnapshot"] == True:
                    if "confirmSetDiffSnapshot" not in all_args.keys():
                        logging.warning('will redirect to confim page {}/confirmSetDiffSnapshot?yamlDir={}&file={}'.format(root,yamlDir,all_args["file"]))
                        return web.HTTPFound('{}/confirmSetDiffSnapshot?yamlDir={}&file={}'.format(root,yamlDir,all_args["file"]))
                try:
                    with open(yamlFilePath) as fh:
                        YamlDictString = fh.read ()
                        fh.close ()
                except:
                    errorMessage = 'cannot open configFile {}'.format(yamlFilePath)
                    logging.error(errorMessage)
                    #return web.HTTPFound('{}/listDir?dir={}'.format(root,yamlDir))          ###FIXME###
                    return {"root":root,"runbookDirSplitDirs":self.runbookDirSplitDirs,"yamlDir":yamlDir,"errorMessage":errorMessage}
                else:
                    try:
                        self.scheduler_settingsDict["file"] = yamlFilePath
                        myRunbook = aioRunbookScheduler(**self.scheduler_settingsDict)
                        logging.debug('aioRunbookScheduler initialized {}'.format(myRunbook))
                        loop = asyncio.get_event_loop()
                        threadExecutor = concurrent.futures.ThreadPoolExecutor(max_workers=10,) 
                        #loop.run_until_complete(myRunbook.execSteps(loop,threadExecutor)) 
                        #await myRunbook.execSteps(loop,threadExecutor)
                        #logging.debug("adding background tasks myRunbook.execSteps(loop,threadExecutor)")  
                        threadExecutor = concurrent.futures.ThreadPoolExecutor(max_workers=10,)                      
                        bgTask = loop.create_task(myRunbook.execStepsAndSaveDicts(loop))
                        logging.debug('aioRunbookScheduler bgTask added {}'.format(bgTask))
                        self.bgList.append(bgTask)
                        NewBgYamlDict = {}
                        NewBgYamlDict[bgTask] = yamlFilePath
                        #cleanup existing list
                        for existingBgTask in self.bgYamlDict.keys():
                            if not existingBgTask.done():
                                NewBgYamlDict[existingBgTask] = self.bgYamlDict[existingBgTask]
                        self.bgYamlDict = NewBgYamlDict
                    except Exception as e:
                        logging.error('cannot run  aioRunbookScheduler {} {}'.format(yamlFilePath,e))
                        errorMessage =  'cannot run  aioRunbookScheduler {}: {}'.format(yamlFilePath,e)
                        return {"root":root,"runbookDirSplitDirs":self.runbookDirSplitDirs,"yamlDir":yamlDir,"fileList":fileList,
                            "jsonDateDict":jsonDateDict,"errorMessage":errorMessage,"jsonErrorDict":jsonErrorDict}
                    else:
                        return web.HTTPFound('{}/listDir?dir={}'.format(root,yamlDir))
        elif "execAllFilesFromDir" in all_args.keys():
            fileList = self.runbookDict[yamlDir]
            if len(self.fifoFileList) > 0:
                logging.error('still processing last fifo list {}'.format(self.fifoFileList))
                errorMessage =  'still processing last fifo list {}'.format(self.fifoFileList)
                fileList = self.runbookDict[yamlDir]
                jsonDateDict = self._upDateJsonDateDict(yamlDir)
                jsonErrorDict = self._upDateJsonErrorDict(yamlDir)
                return {"root":root,"runbookDirSplitDirs":self.runbookDirSplitDirs,"yamlDir":yamlDir,"fileList":fileList,
                    "jsonDateDict":jsonDateDict,"errorMessage":errorMessage}
            else:
                if self.scheduler_settingsDict["setDiffSnapshot"] == True:
                    if "confirmSetDiffSnapshot" not in all_args.keys():
                        logging.warning('will redirect to confim page {}/confirmSetDiffSnapshot?yamlDir={}&execAllFilesFromDir=true'.format(root,yamlDir))
                        return web.HTTPFound('{}/confirmSetDiffSnapshot?yamlDir={}&execAllFilesFromDir=true'.format(root,yamlDir))

                sortedList = self.runbookDict[yamlDir]                      ###FIXME### sort list already on self.runbookDict
                sortedList.sort()
                self.fifoFileList = [ [os.sep.join([yamlDir,x]),self.scheduler_settingsDict] for x in sortedList]
                loop = asyncio.get_event_loop()
                fifoBgTask = loop.create_task(self._fifoSchedulerForRunbookList())
            jsonDateDict = self._upDateJsonDateDict(yamlDir)
            jsonErrorDict = self._upDateJsonErrorDict(yamlDir)
            return web.HTTPFound('{}/listDir?dir={}'.format(root,yamlDir))
        return {"root":root,"runbookDirSplitDirs":self.runbookDirSplitDirs,"yamlDir":yamlDir,"fileList":fileList,
                "jsonDateDict":jsonDateDict}

    @has_permission('viewResults')
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
                    self.scheduler_settingsDict["file"] = yamlFilePath
                    myRunbook = aioRunbookScheduler(**self.scheduler_settingsDict)  #this is required to get the YAMLfilename 
                    loop = asyncio.get_event_loop()
                    resultDict = await myRunbook.getResultFileContent(loop)
                except:
                    resultDict = None
                    logging.error('cannot load resultDict aioRunbookScheduler {}'.format(yamlFilePath))
                    return 'cannot load resultDict aioRunbookScheduler {}'.format(yamlFilePath)     ###FIXME###
        #pprint.pprint(resultDict)
        fileList = self.runbookDict[yamlDir]
        jsonDateDict = self._upDateJsonDateDict(yamlDir)
        jsonErrorDict = self._upDateJsonErrorDict(yamlDir)
        stepCommandOutputs = []
        stepCommandOutputIds = []
        for cmdOutputId in resultDict.keys():
            loopCounter,stepCounter,cmdCounter = _decomposeOutputInformationTag(cmdOutputId)
            stepCommandOutputId =  loopCounter*1000000+stepCounter*1000+cmdCounter
            stepCommandOutputIds.append(stepCommandOutputId)
            resultDict[cmdOutputId]["Id"] = stepCommandOutputId
        stepCommandOutputIds.sort()

        prettyJsonString = json.dumps(resultDict,indent=4,sort_keys=True)
        prettyJsonLines = [ x.rstrip().replace(" ","&nbsp;") for x in prettyJsonString.split("\n") ]

        for Id in stepCommandOutputIds:
            stepCommandOutputs.append([ resultDict[x] for x in resultDict.keys() if resultDict[x]["Id"] == Id ][0])
        #print(jsonDateDict)
        return {"root":root,"runbookDirSplitDirs":self.runbookDirSplitDirs,"yamlDir":yamlDir,"fileList":fileList,
                "jsonDateDict":jsonDateDict, "stepCommandOutputs":stepCommandOutputs,"filename":yamFileName,
                "prettyJsonLines":prettyJsonLines }


    @has_permission('viewResults')
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
        return {"root":root,"runbookDirSplitDirs":self.runbookDirSplitDirs,"yamlDir":yamlDir,"yamlLines":yamlLines,"file":yamFileName}


    @has_permission('viewResults')
    @aiohttp_jinja2.template('listDir.html')
    async def createPDF(self,request):
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
            self.scheduler_settingsDict["file"] = yamlFilePath
            myRunbook = aioRunbookScheduler(**self.scheduler_settingsDict)
            loop = asyncio.get_event_loop()
            threadExecutor = concurrent.futures.ThreadPoolExecutor(max_workers=3,)
            myAioPdfRender = aioPdfRender(myRunbook.configDict,myRunbook.resultDict,True,self.configDict["pdfOutput"])
            await myAioPdfRender.writePdfFile(threadExecutor)
        return web.HTTPFound('{}/listDir?dir={}'.format(root,yamlDir))


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
        self.autoRunbookDirs = False
        if isinstance(self.runbookDirs,str):
            self.autoRunbookDirs = True
            self.runbookParentDir = self.runbookDirs
            self.runbookDirs = self._findDirsWithYamlFilesInPwd(self.runbookParentDir)
        #print ("self.runbookDirs: {}".format(self.runbookDirs))
        try:
            self.httpPort = self.configDict["httpPort"]
        except:
            self.httpPort = 8080
        userNamedTuple = namedtuple('User', ['username', 'password', 'permissions'])
        authUserDict = {}
        self.user_map = {}
        for authUser in self.configDict["userAuth"]:
            user = userNamedTuple(authUser[0]["username"],authUser[1]["password"],authUser[2]["permissions"])
            self.user_map[authUser[0]["username"]] = userNamedTuple(authUser[0]["username"],authUser[1]["password"],authUser[2]["permissions"])
            pass
        try:
            self.templateDir = self.configDict["templateDir"]
        except:
            logging.error('missing attribute templateDir in File {}'.format(configFile))
            return False
        if not os.path.isdir(self.templateDir):
            logging.error('troubles access templateDir {}'.format(self.templateDir))
            return False
        try:
            self.scheduler_settingsDict = self.configDict["scheduler"]
        except:
            logging.error('cannot set config paramters for tE {}'.format(configFile))
            self.scheduler_settingsDict = SCHEDULER_DEFAULT_KWARGS
        return True

    @has_permission('viewResults')
    @aiohttp_jinja2.template('settings.html')
    async def saveConfig(self,request):
        root="http://"+request.host
        all_args = request.query
        #print ("GET args:",all_args)
        self.configDict["scheduler"] = self.scheduler_settingsDict
        yamlConfig = yaml.dump(self.configDict,default_flow_style=False)
        #print(yamlConfig)
        errorMessage = None
        try:
            with open(self.yamlConfigFile, 'w') as outfile:  
                outfile.write(yamlConfig)
                outfile.close ()
        except Exception as e:
            logging.error('cannot write configFile {}'.format(self.yamlConfigFile))
            errorMessage = 'cannot write configFile {} {}'.format(self.yamlConfigFile,e) 
        return {"root":root,"errorMessage":errorMessage,"settingsDict":self.scheduler_settingsDict}


    @has_permission('viewResults')
    @aiohttp_jinja2.template('settings.html')
    async def settings(self,request):
        root="http://"+request.host
        if request.method == "POST":
            all_args = await request.post()
            #print ("POST args:",all_args)
            self.scheduler_settingsDict["tester"] = all_args["tester"]
            self.scheduler_settingsDict["logging"] = all_args["loggingSelect"]  
            if  "setDiffSnapshot" in all_args.keys():
                self.scheduler_settingsDict["setDiffSnapshot"] = True       
            else:
                self.scheduler_settingsDict["setDiffSnapshot"] = False    
            if  "pdflatex" in all_args.keys():
                self.scheduler_settingsDict["pdflatex"] = True       
            else:
                self.scheduler_settingsDict["pdflatex"] = False              
            #pprint.pprint(self.scheduler_settingsDict)
            self._change_logging(**self.scheduler_settingsDict)
        else:
            all_args = request.query
            #print ("GET args:",all_args)
        errorMessage = None
        return {"root":root,"errorMessage":errorMessage,"settingsDict":self.scheduler_settingsDict}

    @has_permission('viewResults')
    @aiohttp_jinja2.template('confirmSetDiffSnapshot.html')
    async def confirmSetDiffSnapshot(self,request):
        root="http://"+request.host
        all_args = request.query
        #print(all_args)
        yamlDir = all_args["yamlDir"]
        if "file" in all_args:
            yamFileName = all_args["file"]
        else:
            yamFileName = None
        if "execAllFilesFromDir" in all_args:
            execAllFilesFromDir = True
        else:
            execAllFilesFromDir = False
        errorMessage = None
        logging.debug ("confirmSetDiffSnapshot @End root:{} filename{} yamlDir:{} errorMessage:{}".format (root,yamFileName,yamlDir,errorMessage))
        return {"root":root,"filename":yamFileName,"yamlDir":yamlDir,"errorMessage":errorMessage,"execAllFilesFromDir":execAllFilesFromDir}


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

    def _upDateJsonErrorDict (self,yamlDir):
        fileList = self.runbookDict[yamlDir]
        jsonErrorCountDict = {}
        for yamlFile in fileList:
            yamlFilePath = os.sep.join([yamlDir,yamlFile])
            jsonFile = yamlFilePath[:-4]+".json"
            try: 
                with open(jsonFile) as infile:            
                    processedConfigDict = json.load(infile)
                    jsonErrorCountDict[yamlFile] = {"errorCounter": processedConfigDict["errorCounter"]}
            except:
                jsonErrorCountDict[yamlFile] = {"errorCounter": 0}                    
        return jsonErrorCountDict

    def _findDirsWithYamlFilesInPwd (self,parentDir):
        parentDirAbs = os.path.abspath(parentDir)     
        #dirList = [f for f in os.listdir(parentDirAbs) if os.path.isdir(f)]
        dirList = [f.path for f in os.scandir(parentDirAbs) if f.is_dir() ]
        ymlDirList = []
        for thisDir in dirList:
            ymlFilesInThisDir = [f for f in os.listdir(thisDir) if f.endswith('.yml')]
            if len( ymlFilesInThisDir ) > 0:
                ymlDirList.append(thisDir)
        #print ("_findDirsWithYamlFilesInPwd ymlDirList: {}".format(ymlDirList))
        return ymlDirList

    def _change_logging(self,**kwargs):
        if kwargs['logging'] is not None:
            self.loggingLevel = kwargs['logging']
            if self.loggingLevel in ["debug", "info", "warning"]:
                if self.loggingLevel == "debug": logging.getLogger().setLevel(logging.DEBUG)
                if self.loggingLevel == "info": logging.getLogger().setLevel(logging.INFO)
                if self.loggingLevel == "warning": logging.getLogger().setLevel(logging.WARNING)

    async def _fifoSchedulerForRunbookList(self):
        """tbd

        """
        loop = asyncio.get_event_loop()
        #threadExecutor = concurrent.futures.ThreadPoolExecutor(max_workers=10,)   
        while len(self.fifoFileList) > 0:
            configFile,scheduler_settingsDict = self.fifoFileList.pop(0)
            scheduler_settingsDict["file"] = configFile
            myRunbook = aioRunbookScheduler(**scheduler_settingsDict)                   
            await myRunbook.execStepsAndSaveDicts(loop)





