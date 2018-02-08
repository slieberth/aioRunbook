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
import subprocess


def _isInDictionary (searchKey,inDictionary,defaultValue):
    if searchKey in inDictionary.keys():
        return inDictionary[searchKey]
    else:
        return defaultValue 


class pdfRender:

    def __init__(self,args,processedConfigDict,loopCheckResult,pdfOutputDir,keepTexFile):
        logging.debug('init pdfRender pwd:{} yaml: {}'.format(os.getcwd(),args[-1]))
        #print (os.path.splitext(os.path.split(args[-1])[1])[0])
        self.texFileName = os.path.splitext(os.path.split(args[-1])[1])[0] + ".tex" 
        logging.debug('init pdfRender texfile: {}'.format(self.texFileName))
        with open(args[-1]) as fh:
            YamlDictString = fh.read ()
            fh.close ()
        #self.configDictOrig = yaml.load(YamlDictString)
        #self.configDictOrig["config"]["configFile"] = os.path.normpath("../../"+str(args[-1]))
        self.processedConfigDict = processedConfigDict
        self.loopCheckResult = loopCheckResult 
        self.pdfOutputDir = pdfOutputDir
        self.baseDir = os.path.abspath(".")
        self.keepTexFile = keepTexFile

    @classmethod
    def replaceSpecialLatexCharsToBeFixed (self,commandObj,ttOption=False):
        #set ttOption to true to get the replace character for Latex tt True Type Fonds
        #otherwise the Sans Serif replace character is returned 
        latexReplaceDict = {
        '%' :  ['\%','\%'],
        '$' :  ['\$','\$'],
        '&' :  ['\&','\&'],
        '_' :  ['\_',"\char‘\_"],
        '"' :  ['\\textquotedbl ',"'"],
        '>' :  ['\\textgreater ','>'],
        '<' :  ['\\textless ','>'],
        '|' :  ['\\textbar ','|'],
        '̃' :  ['\\~{} ','\\~{}'],
        '{' :  ['\\{ ',"\\char‘\\{ "],
        '}' :  ['\\} ',"\\char‘\\} "],
        '^' :  ['\\^{} ','\\^{} '],
        '\\\\' : ['\\textbackslash',"\\char‘\\\\"],
        }

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
            

    def writePdfFile (self):
        if "pdfOutput" in self.processedConfigDict["config"].keys():
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
                loader = jinja2.FileSystemLoader(self.baseDir + '/template'))
            j2templateFilename = self.processedConfigDict["config"]["pdfOutput"]["template"]
            #if j2templateFilename in [ "./template.tex" , "template.tex" ]:
            #    j2templateFilename = "./template_v3.tex"
            j2template = latex_jinja_env.get_template(j2templateFilename)
            latexString = j2template.render( configDict = self.processedConfigDict["config"],
                                             loopCheckResultList = self.loopCheckResult )
            #logging.debug('latexString:\n {0}'.format(latexString))
            self.baseDir = os.getcwd()
            os.makedirs (self.pdfOutputDir + "/", exist_ok=True)
            os.chdir(self.pdfOutputDir)
            try:
                fo = open(self.texFileName, "w")
                fo.write(latexString );
                fo.close()
            except:
                fo = open(self.texFileName, "wb")
                fo.write(latexString.encode("utf-8") );
                fo.close()
            cmd = ['pdflatex', '-interaction', 'nonstopmode', self.texFileName ]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)   # run for building TOC helper files
            proc.communicate()
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)   # build PDF using TOC helper files
            proc.communicate()
            delFilename, file_extension = os.path.splitext( self.texFileName )    
            if self.keepTexFile:
                for suffix in [ ".aux", ".frm", ".log", ".out"  ]: # remove latex helper files only
                    if os.path.exists(delFilename + suffix):
                        os.remove(delFilename + suffix)
                for listFilename in os.listdir("."):
                    if listFilename.endswith(".tmp"): os.remove(listFilename)
            else:
                for suffix in [ ".aux", ".frm", ".log", ".out" , ".tex" ]:   # remove latex files
                    if os.path.exists(delFilename + suffix):
                        os.remove(delFilename + suffix)
                for listFilename in os.listdir("."):
                    if listFilename.endswith(".tmp"): os.remove(listFilename)
            os.chdir(self.baseDir)

if __name__ == '__main__':
    testStr = """set config.interface.ifl interface_name ifl-0/0/1/1/0 interface_description "Interface 0000:21:00.1" ipv4_status up ipv4_mtu 576"""
    print (pdfRender.replaceSpecialLatexChars(testStr))
 