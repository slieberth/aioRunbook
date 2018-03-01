#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  \author    Stefan Lieberth / Maik Pfeil
#  \version   3.03.05
#  \date      6.12.2017
#  modifications: 
#   3.03.01: added logs for debug issue
#   3.03.03: encoding utf8 for pdf file
#   3.03.04: revert
#   3.03.05: 


import pprint
import logging
import yaml
import datetime
import jinja2
import json
import os
import datetime
import asyncio
import concurrent.futures
from aioRunbook.tools.helperFunctions import _isInDictionary, _addTimeStampsToStepDict
import subprocess

WORKING_WITH_SUBCATEGORY_DEFAULT = True
PREPEND_DATE = True

class aioPdfRender:

    def __init__(self,processedConfigDict,resultDict,keepTexFile,pdfConfigDict={}):
        logging.debug('init aioPdfRender pwd:{} '.format(os.getcwd()))
        self.blockingError = False
        self.processedConfigDict = processedConfigDict
        self.resultDict = resultDict 

        try:
            self.pdfDict = self.processedConfigDict["config"]["pdfOutput"]
            logging.debug('found pdfOutput in configDict')
            self.pdfResultDir = self.processedConfigDict["config"]["pdfOutput"]["pdfResultDir"]
            self.template = self.processedConfigDict["config"]["pdfOutput"]["template"]
            self.keepTexFile = _isInDictionary ("keepTexFile",self.processedConfigDict["config"]["pdfOutput"],keepTexFile)
            self.prependDate = _isInDictionary ("prepend-date-to-working-dir",self.processedConfigDict["config"]["pdfOutput"],PREPEND_DATE)
        except:
            try:
                self.pdfDict = pdfConfigDict
                self.pdfResultDir = pdfConfigDict["pdfResultDir"]
                self.template = pdfConfigDict["template"]
                self.keepTexFile = _isInDictionary ("keepTexFile",pdfConfigDict,keepTexFile)
                self.prependDate = _isInDictionary ("prepend-date-to-working-dir",pdfConfigDict,PREPEND_DATE)
            except:
                self.pdfDict = None
                logging.error('pdfRender cannot set all parameters from pdfOutputDict')
                self.blockingError = True
        if not self.blockingError == True:
            try:
                self.templateDir = os.path.dirname(self.template)
                logging.debug('templateDir: {}'.format(self.templateDir))
            except:
                self.templateDir = None
                logging.error('cannot set templateDir for: {}'.format(self.template))
                self.blockingError = True
            try:
                self.yamlConfigFile = self.processedConfigDict["yamlConfigFile"]
                self.filename = os.path.splitext(os.path.split(self.yamlConfigFile)[1])[0]
                self.texFileName = os.path.splitext(os.path.split(self.yamlConfigFile)[1])[0] + ".tex"
                logging.debug('set tex file to: {}'.format(self.texFileName))
            except:
                self.yamlConfigFile = None
                self.filename = None
                self.texFileName = None
                logging.error('cannot detect tex file name from yml file')
                self.blockingError = True
            if WORKING_WITH_SUBCATEGORY_DEFAULT:
                try:
                    self.subcategory = os.path.abspath(self.yamlConfigFile).split(os.sep)[-2]          ###FIXME###
                    self.subcategory = _isInDictionary ("subcategory",self.processedConfigDict["config"],self.subcategory)
                    logging.debug('set subcategory to: {}'.format(self.subcategory))
                except:
                    self.subcategory = "default"
                    logging.warning('set subcategory to: {}'.format(self.subcategory))
            else:
                self.subcategory = None   
            if self.prependDate:
                dateString = datetime.datetime.now().strftime('%Y-%m-%d')
                if self.subcategory:
                    self.pdfOutputDir = self.pdfResultDir + os.sep + dateString + os.sep  + self.subcategory + os.sep
                else:
                    self.pdfOutputDir = self.pdfResultDir + os.sep + dateString + os.sep
            else:
                if self.subcategory:
                    self.pdfOutputDir = self.pdfResultDir + os.sep  + self.subcategory + os.sep
                else:
                    self.pdfOutputDir = self.pdfResultDir + os.sep
            logging.info('set pdfOutputDir  to: {}'.format(self.pdfOutputDir))
            self.executor = concurrent.futures.ProcessPoolExecutor(max_workers=3,)
            self.event_loop = asyncio.get_event_loop()


    @classmethod 
    def replaceSpecialLatexChars(self,commandObj,ttOption=False):   ##TEMP
        #set ttOption to true to get the replace character for Latex tt True Type Fonds
        #otherwise the Sans Serif replace character is returned 
        latexReplaceDict = {
        '#' :  ['\\#','\\#'],
        '%' :  ['\\%','\\%'],
        '$' :  ['\\$','\\$'],
        '&' :  ['\\&','\\&'],
        '_' :  ['\\_',"\\_"],
        '"' :  ['\\textquotedbl ',"'"],
        '>' :  ['\\textgreater ','>'],
        '<' :  ['\\textless ','<'],
        '|' :  ['\\textbar ','|'],
        '̃' :  ['\\~{} ','\\~{} '],
        '{' :  ['\\{ ',"\\{ "],
        '}' :  ['\\} ',"\\} "],
        '^' :  [' ',' '],
        '\\\\' : ['',""],
        }
        commandString = str(commandObj)
        if not ttOption:
            for replaceChar in latexReplaceDict:
                commandString = commandString.replace(replaceChar,latexReplaceDict[replaceChar][0])
        else:
            for replaceChar in latexReplaceDict:
                commandString = commandString.replace(replaceChar,latexReplaceDict[replaceChar][1])
        return commandString
            

    async def writePdfFile (self,threadExecutor):
        def blocking_task ():
            if not self.blockingError:
                latex_jinja_env = jinja2.Environment(\
                    block_start_string = '\BLOCK{',
                    block_end_string = '}',
                    variable_start_string = '\VAR{',
                    variable_end_string = '}',
                    comment_start_string = '\#{',
                    comment_end_string = '}',
                    line_statement_prefix = '%-',
                    line_comment_prefix = '%#',
                    trim_blocks = True,
                    autoescape = False,
                    loader = jinja2.FileSystemLoader("."))
                logging.debug("try to open template file: {}".format(self.template))
                try:
                    os.path.isfile(self.template)
                except:
                    logging.error('cannot load j2template, please verify location')  
                try:
                    j2template = latex_jinja_env.get_template(self.template)
                    logging.debug('j2template loaded')
                except:
                    logging.error('cannot load j2template, please verify syntax')  
                    raise
                else:
                    # change from self.processedConfigDict["config"] ...
                    # to self.processedConfigDict for diffSnapshots
                    # requires adaptation of all existing temlates!!!!!
                    #latexString = j2template.render( configDict = self.processedConfigDict["config"],
                    #                                 resultDictList = self.resultDict )
                    latexString = j2template.render( configDict = self.processedConfigDict,
                                                     resultDictList = self.resultDict )
            
                    try:
                        fo = open(self.texFileName, "w")
                        fo.write(latexString );
                        fo.close()
                        logging.debug('latexString written: lines:{0} option w'.format(len(latexString)))
                    except:
                        fo = open(self.texFileName, "wb")
                        fo.write(latexString.encode("utf-8") );
                        fo.close()
                        logging.debug('latexString written: lines {0} option wb/utf8'.format(len(latexString)))
                    cmd = ['pdflatex', '-interaction', 'nonstopmode', self.texFileName ]
                    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)   # run for building TOC helper files
                    stdout,stderr = proc.communicate()
                    #logging.debug("pdfLatex run1 stdout: {}".format(stdout.decode()))
                    #logging.debug("pdfLatex run1 stderr: {}".format(stderr.decode()))
                    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)   # build PDF using TOC helper files
                    stdout,stderr = proc.communicate()
                    logging.debug("pdfLatex run2 stdout: {}".format(stdout.decode()))
                    logging.debug("pdfLatex run2 stderr: {}".format(stderr.decode()))
                    delFilename, file_extension = os.path.splitext( self.texFileName )    
                    if self.keepTexFile:
                        for suffix in [ ".aux", ".frm", ".log", ".out"  ]: # remove latex helper files only
                            if os.path.exists(delFilename + suffix):
                                os.remove(delFilename + suffix)
                                logging.debug('delete file {}'.format(delFilename + suffix)) 
                    else:
                        for suffix in [ ".aux", ".frm", ".log", ".out" , ".tex" ]:   # remove latex files
                            if os.path.exists(delFilename + suffix):
                                os.remove(delFilename + suffix)
                                logging.debug('delete file {}'.format(delFilename + suffix)) 
                    #for listFilename in os.listdir("."):
                    #    if listFilename.endswith(".tmp"): os.remove(listFilename)
                    #os.chdir(self.baseDir)
                    if not os.path.isdir(self.pdfOutputDir):
                        logging.debug('creating dir {}'.format(self.pdfOutputDir)) 
                        os.makedirs (self.pdfOutputDir, exist_ok=True)
                    logging.debug('copying file {} to {}'.format(delFilename + ".pdf",self.pdfOutputDir))   
                    os.rename(delFilename + ".pdf", self.pdfOutputDir + os.sep + delFilename + ".pdf")                 
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(threadExecutor,blocking_task, )

 