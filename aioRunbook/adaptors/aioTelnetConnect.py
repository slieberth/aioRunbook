#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  \author    Stefan Lieberth
#  \version   0.1.3
#  \date      23.01.17

 #  \modification
#  0.1.1 base line for history
#  0.1.2 work for asyncio loop fix
#  0.1.3 clean-up 


import asyncio
import random
import logging
import yaml
from copy import deepcopy
import asyncssh
import pprint
import datetime
import os
import sys
import re
#sys.path.insert(0, os.path.abspath('../tools'))
from tools.helperFunctions import _isInDictionary, _addTimeStampsToStepDict

# ssh parameters
#sys.path.insert(0, os.path.abspath('../adaptors'))
#from adaptors.aioSshConnect import VENDOR_DICT


# Tunable parameters
DEBUGLEVEL = 0

# Telnet protocol defaults
TELNET_PORT = 23

# Telnet protocol characters (don't change)
IAC  = bytes([255]) # "Interpret As Command"
DONT = bytes([254])
DO   = bytes([253])
WONT = bytes([252])
WILL = bytes([251])
theNULL = bytes([0])

SE  = bytes([240])  # Subnegotiation End
NOP = bytes([241])  # No Operation
DM  = bytes([242])  # Data Mark
BRK = bytes([243])  # Break
IP  = bytes([244])  # Interrupt process
AO  = bytes([245])  # Abort output
AYT = bytes([246])  # Are You There
EC  = bytes([247])  # Erase Character
EL  = bytes([248])  # Erase Line
GA  = bytes([249])  # Go Ahead
SB =  bytes([250])  # Subnegotiation Begin


# Telnet protocol options code (don't change)
# These ones all come from arpa/telnet.h
BINARY = bytes([0]) # 8-bit data path
ECHO = bytes([1]) # echo
RCP = bytes([2]) # prepare to reconnect
SGA = bytes([3]) # suppress go ahead
NAMS = bytes([4]) # approximate message size
STATUS = bytes([5]) # give status
TM = bytes([6]) # timing mark
RCTE = bytes([7]) # remote controlled transmission and echo
NAOL = bytes([8]) # negotiate about output line width
NAOP = bytes([9]) # negotiate about output page size
NAOCRD = bytes([10]) # negotiate about CR disposition
NAOHTS = bytes([11]) # negotiate about horizontal tabstops
NAOHTD = bytes([12]) # negotiate about horizontal tab disposition
NAOFFD = bytes([13]) # negotiate about formfeed disposition
NAOVTS = bytes([14]) # negotiate about vertical tab stops
NAOVTD = bytes([15]) # negotiate about vertical tab disposition
NAOLFD = bytes([16]) # negotiate about output LF disposition
XASCII = bytes([17]) # extended ascii character set
LOGOUT = bytes([18]) # force logout
BM = bytes([19]) # byte macro
DET = bytes([20]) # data entry terminal
SUPDUP = bytes([21]) # supdup protocol
SUPDUPOUTPUT = bytes([22]) # supdup output
SNDLOC = bytes([23]) # send location
TTYPE = bytes([24]) # terminal type
EOR = bytes([25]) # end or record
TUID = bytes([26]) # TACACS user identification
OUTMRK = bytes([27]) # output marking
TTYLOC = bytes([28]) # terminal location number
VT3270REGIME = bytes([29]) # 3270 regime
X3PAD = bytes([30]) # X.3 PAD
NAWS = bytes([31]) # window size
TSPEED = bytes([32]) # terminal speed
LFLOW = bytes([33]) # remote flow control
LINEMODE = bytes([34]) # Linemode option
XDISPLOC = bytes([35]) # X Display Location
OLD_ENVIRON = bytes([36]) # Old - Environment variables
AUTHENTICATION = bytes([37]) # Authenticate
ENCRYPT = bytes([38]) # Encryption option
NEW_ENVIRON = bytes([39]) # New - Environment variables
# the following ones come from
# http://www.iana.org/assignments/telnet-options
# Unfortunately, that document does not assign identifiers
# to all of them, so we are making them up
TN3270E = bytes([40]) # TN3270E
XAUTH = bytes([41]) # XAUTH
CHARSET = bytes([42]) # CHARSET
RSP = bytes([43]) # Telnet Remote Serial Port
COM_PORT_OPTION = bytes([44]) # Com Port Control Option
SUPPRESS_LOCAL_ECHO = bytes([45]) # Telnet Suppress Local Echo
TLS = bytes([46]) # Telnet Start TLS
KERMIT = bytes([47]) # KERMIT
SEND_URL = bytes([48]) # SEND-URL
FORWARD_X = bytes([49]) # FORWARD_X
PRAGMA_LOGON = bytes([138]) # TELOPT PRAGMA LOGON
SSPI_LOGON = bytes([139]) # TELOPT SSPI LOGON
PRAGMA_HEARTBEAT = bytes([140]) # TELOPT PRAGMA HEARTBEAT
EXOPL = bytes([255]) # Extended-Options-List
NOOPT = bytes([0])

_GLOBAL_DEFAULT_TIMEOUT = 3

VENDOR_DICT = { "juniper" : { "initPrompt" : ">", 
                            "lambdaCliPrompt" : lambda output : [ output.rstrip().split("\n")[-1][:-1] + "(>|#)" ] ,
                            "stripPrologueLines" : 1,
                            "stripEpilogueLines" : 2,
                            "initCmds" : [ "set cli screen-length 0\n"],
                            "outputCorrections" : [ lambda output : re.sub(r'(\r\n|\r|\n)', '\n',  output) ] } ,
                "cisco" : { "initPrompt" : "#", 
                            "lambdaCliPrompt" : lambda output : [ output.strip(), output.strip()[:-1]+'\\(.*\\)#' ],
                            "stripPrologueLines" : 3,
                            "stripEpilogueLines" : 1,
                            "initCmds" : [ "terminal length 0\n"],
                            "outputCorrections" : [ lambda output : re.sub(r'(\r\n|\r|\n)', '\n',  output) , 
                                                    lambda output : re.sub(r'\x08','', output)                ] } ,   
                "ubuntu" : { "initPrompt" : "$ ", 
                            "lambdaCliPrompt" : lambda output : [ output.rstrip().lstrip()[:-2] + "\S*\$ " ],
                            "stripPrologueLines" : 1,
                            "stripEpilogueLines" : 1,
                            "initCmds" : [],
                            "outputCorrections" : [ lambda output : re.sub(r'(\r\n|\r|\n)', '\n',  output) , 
                                                    lambda output : rre.sub(r'\[\d+(;\d+)*m', '', output)  ] } }

class aioTelnetConnect():
    """asyncio telnet client, ported from the standard telnetlib. Designed for interaction with network devices.

          :param stepDict: the specific test step dictionary. The stepDict includes the attributes for device access and the commands to be executed.
          :param stepDict["device"]: defines the IP address of the device under test. tested with IPv4 only. 
          :param stepDict["port"]: defines the TCP port for the session. Optional, default = 23.
          :param stepDict["vendor"]: defines the vendor type for this telnet connection. currently ubuntu, juniper and cisco are supported 
          :param stepDict["user"]: defines the user for telnet authentication
          :param stepDict["password"]: defines the clear text password for user authentication
          :param stepDict["enc-password"]: defines the encrypted password for user authentication
          :param stepDict["commands"]: defines the list for all commands. \n
          :param stepDict["timeout"]: defines a specific timeout for this step for telnet interactions, default = 60 secs.
          :param stepDict["optionalPrompt"]: is useful to react for confirmation request, for which the usuall prompt does not match
          :param stepDict["optionalPrompts"]: is useful to react for confirmation request, but for more than one optional prompts
          :param configDict: optional, the overall test dictionary.
          :param configDict["config"]["timeout"]: optional, defines the generic timeout for all steps
          :param configDict["config"]["user"]: optional, defines the generic user for all steps. Has lower precedence than the user attribute in stepDict.
          :param configDict["config"]["password"]: optional, defines the generic clear-text password for all steps. Has lower precedence than the user attribute in stepDict.
          :param configDict["config"]["enc-password"]: optional, defines the generic encrypted password for all steps. Has lower precedence than the user attribute in stepDict.
          :type stepDict: dict
          :type stepDict["device"]: string   
          :type stepDict["port"]: int  
          :type stepDict["vendor"]: string   
          :type stepDict["user"]: string   
          :type stepDict["password"]: string   
          :type stepDict["enc-password"]: string   
          :type stepDict["commands"]: list of strings  
          :type stepDict["timeout"]: int
          :type stepDict["optionalPrompt"]: string
          :type stepDict["optionalPrompts"]: list of strings
          :type configDict: dict
          :type configDict["config"]["timeout"]: int
          :type configDict["config"]["user"]: string   
          :type configDict["config"]["password"]: string   
          :type configDict["config"]["enc-password"]: string   

    """

    def __init__(self,stepDict,configDict = {"config":{}},port=23,eventLoop=None):
    #def __init__(self,stepDict,configDict = {"config":{}},port=23,loop=None):
        """Constructor.


        """
        logging.debug("##### eventLoop aioTelnetConnect() {}".format(eventLoop))
        self.hostname = stepDict["device"]
        self.vendor= stepDict["vendor"]
        self.port = _isInDictionary ("port",stepDict,port)
        self.startShellCommand = _isInDictionary ("startShellCommand",stepDict,"")
        if self.vendor in [ "juniper" , "cisco" ] :
            self.stripPrologueLines = _isInDictionary("stripPrologueLines",stepDict,VENDOR_DICT[self.vendor]["stripPrologueLines"])
            self.stripEpilogueLines = _isInDictionary("stripEpilogueLines",stepDict,VENDOR_DICT[self.vendor]["stripEpilogueLines"])
        self.stepDict = stepDict
        self.device = stepDict["device"]
        self.port = _isInDictionary ("port",stepDict,23)
        self.vendor = stepDict["vendor"]

        self.username = _isInDictionary ("user",configDict["config"],None)
        self.username = _isInDictionary ("user",stepDict,self.username)
        self.password = _isInDictionary ("password",configDict["config"],None)     
        if "enc-password" in configDict["config"].keys():
            logging.debug('enc-password: {0}'.format(configDict["config"]["enc-password"]))
            self.password = base64.b64decode(base64.b64decode(configDict["config"]["enc-password"]).decode('utf-8')).decode('utf-8') ##SECURE##
        self.password = _isInDictionary ("password",stepDict,self.password)
        if "enc-password" in stepDict.keys():
            logging.debug('enc-password: {0}'.format(stepDict["enc-password"]))
            self.password = base64.b64decode(base64.b64decode(stepDict["enc-password"]).decode('utf-8')).decode('utf-8') ##SECURE##
            logging.debug('password: {0}'.format(self.password))     
        if self.password == None:
            logging.error('password not set for stepDict: {0}'.format(stepDict)) 
        self.timeout = _isInDictionary ("timeout",configDict["config"],60)
        self.timeout = _isInDictionary ("timeout",stepDict,self.timeout)
        self.optionalPrompt = _isInDictionary("optionalPrompt",stepDict,None)
        if self.optionalPrompt: 
            self.optionalPrompts = [self.optionalPrompt]
        else:
            self.optionalPrompts = []
        self.optionalPrompts = _isInDictionary("optionalPrompts",stepDict,self.optionalPrompts)
        self.eventLoop = eventLoop
        #self.eventLoop.set_debug(True)
        #asyncio.set_event_loop(self.eventLoop)

        self.sock = None
        self.rawq = b''
        self.irawq = 0
        self.cookedq = b''
        self.eof = 0
        self.iacseq = b'' # Buffer for IAC sequence.
        self.sb = 0 # flag for SB and SE sequence.
        self.sbdataq = b''
        self.option_callback = None


    def process_rawq(self):
        """Transfer from raw queue to cooked queue.

        Set self.eof when connection is closed.  Don't block unless in
        the midst of an IAC sequence.

        """
        buf = [b'', b'']
        try:
            while self.rawq:
                c = self.rawq_getchar()
                if not self.iacseq:
                    if c == theNULL:
                        continue
                    if c == b"\021":
                        continue
                    if c != IAC:
                        buf[self.sb] = buf[self.sb] + c
                        continue
                    else:
                        self.iacseq += c
                elif len(self.iacseq) == 1:
                    # 'IAC: IAC CMD [OPTION only for WILL/WONT/DO/DONT]'
                    if c in (DO, DONT, WILL, WONT):
                        self.iacseq += c
                        continue

                    self.iacseq = b''
                    if c == IAC:
                        buf[self.sb] = buf[self.sb] + c
                    else:
                        if c == SB: # SB ... SE start.
                            self.sb = 1
                            self.sbdataq = b''
                        elif c == SE:
                            self.sb = 0
                            self.sbdataq = self.sbdataq + buf[1]
                            buf[1] = b''
                        if self.option_callback:
                            # Callback is supposed to look into
                            # the sbdataq
                            self.option_callback(self.sock, c, NOOPT)
                        else:
                            # We can't offer automatic processing of
                            # suboptions. Alas, we should not get any
                            # unless we did a WILL/DO before.
                            #self.msg('IAC %d not recognized' % ord(c))
                            pass
                elif len(self.iacseq) == 2:
                    cmd = self.iacseq[1:2]
                    self.iacseq = b''
                    opt = c
                    if cmd in (DO, DONT):
                        #self.msg('IAC %s %d',
                        #    cmd == DO and 'DO' or 'DONT', ord(opt))
                        if self.option_callback:
                            self.option_callback(self.sock, cmd, opt)
                        else:
                            self.writer.write(IAC + WONT + opt)
                            #self.sock.sendall(IAC + WONT + opt)                 ###FIXME###
                    elif cmd in (WILL, WONT):
                        #self.msg('IAC %s %d',
                        #    cmd == WILL and 'WILL' or 'WONT', ord(opt))
                        if self.option_callback:
                            self.option_callback(self.sock, cmd, opt)
                        else:
                            self.writer.write(IAC + DONT + opt)
                            #self.sock.sendall(IAC + DONT + opt)                 ###FIXME###
        except EOFError: # raised by self.rawq_getchar()
            self.iacseq = b'' # Reset on EOF
            self.sb = 0
            pass
        self.cookedq = self.cookedq + buf[0]
        self.sbdataq = self.sbdataq + buf[1]

    def rawq_getchar(self):
        """Get next char from raw queue.

        Block if no data is immediately available.  Raise EOFError
        when connection is closed.

        """
        if not self.rawq:
            self.fill_rawq()
            if self.eof:
                raise EOFError
        c = self.rawq[self.irawq:self.irawq+1]
        self.irawq = self.irawq + 1
        if self.irawq >= len(self.rawq):
            self.rawq = b''
            self.irawq = 0
        return c

    def fill_rawq(self):                                            ###FIXME###
        """Fill raw queue from exactly one recv() system call.

        Block if no data is immediately available.  Set self.eof when
        connection is closed.

        """
        if self.irawq >= len(self.rawq):
            self.rawq = b''
            self.irawq = 0
        # The buffer size should be fairly small so as to avoid quadratic
        # behavior in process_rawq() above


        buf = self.sock.recv(50)              ###FIXME###
        #self.msg("recv %r", buf)
        self.eof = (not buf)
        self.rawq = self.rawq + buf

    def sock_avail(self):
        """Test whether data is available on the socket."""
        with _TelnetSelector() as selector:
            selector.register(self, selectors.EVENT_READ)
            return bool(selector.select(0))


    async def connect(self):
        """Connect to a host.

        The optional second argument is the port number, which
        defaults to the standard telnet port (23).

        Don't try to reopen an already connected instance.
        """
        self.reader, self.writer = None, None
        self.eof = 0
        #print(self.device,self.port,self.timeout)

        try:
            self.reader, self.writer = await asyncio.wait_for(asyncio.open_connection(self.device,self.port),self.timeout) 
        except:
            logging.error ("aioTelnetConnect.connect to {} failed".format(self.hostname))  
        else:
            logging.debug ("aioTelnetConnect open_connection succeeded".format(self.hostname)) 
            logging.debug ("self.reader {}".format(self.reader)) 
        foundPrompt = False                
        counter = False  
        attempts = 0
        #while ((not foundPrompt) and (not counter)):
        while (not foundPrompt):
            buf = None
            try:
                buf = await asyncio.wait_for(self.reader.read(50),self.timeout)  
            except:
                logging.error ("aioTelnetConnect.read to {} finally failed".format(self.hostname))  
            if buf:
                self.eof = (not buf)
                self.rawq = self.rawq + buf
                self.process_rawq()
                logging.debug ("cookedq: {}".format(self.cookedq))
                #
                #   FIXME START: use VENDOR_DICT
                #
                if self.vendor in [ "juniper" , "cisco" ] :
                    #if b'login:' in self.cookedq and not b'Password:' in self.cookedq:
                    if b'login:' in self.cookedq or b'Username:' in self.cookedq:
                        self.writer.write(self.username.encode() + b'\n')
                        self.cookedq = b''
                    elif b'Password:' in self.cookedq:
                        self.writer.write(self.password.encode() + b'\n')
                        self.cookedq = b''
                        loginflag = True
                    elif VENDOR_DICT[self.vendor]["initPrompt"].encode() in self.cookedq:
                        foundPrompt = True
                        output = self.cookedq.decode()
                        self.cookedq = b''
                        self.rePromptList = VENDOR_DICT[self.vendor]["lambdaCliPrompt"](output)
                        if self.optionalPrompts != []:
                            self.rePromptList += self.optionalPrompts
                        logging.debug ("set prompts to {}".format(self.rePromptList))
            if foundPrompt:
                try:
                    if self.vendor in [ "juniper" , "cisco" ] :
                        for initCmd in VENDOR_DICT[self.vendor]["initCmds"]:
                            self.writer.write(initCmd.encode())
                            output = b''
                            gotPrompt = False
                            while not gotPrompt:
                                output += await asyncio.wait_for(self.reader.read(64000),timeout=self.timeout)
                                for rePattern in self.rePromptList:
                                    if re.search(rePattern,output.decode()): gotPrompt = True    
                except:
                    raise 
                    logging.warning ("prompt timeout command {}".format(self.stepDict["stepCounter"]))
            attempts += 1
            #logging.debug ("attempts =  {}".format(attempts))
            if attempts >= 100: break    


                #yield from asyncio.sleep (0.0001)         
        #self.sshConnectLoop.run_until_complete(task(self))


    async def runCommands (self,delayTimer=0):
        """sends all commands from the the test step and stores the return CLI values in the stepDict output section

              :param delayTimer: a waiting time (in seconds) periods before the commands are executed. required for await.
              :type delayTimer: int

              :return: the enriched stepDict output dict

        """
        for i,command in enumerate(self.stepDict["commands"]):
            if self.reader and self.writer:
                t1=datetime.datetime.now()
                self.writer.write(command.encode() + "\n".encode())
                output = b''
                gotPrompt = False
                try:
                    while not gotPrompt:
                        output += await asyncio.wait_for(self.reader.read(64000),timeout=self.timeout)
                        for rePattern in self.rePromptList:
                            if re.search(rePattern,output.decode()): gotPrompt = True
                except:
                    logging.warning ("prompt timeout step {} command {}".format(self.stepDict["stepCounter"],i))
                output = output.decode()
                for correctionLambda in VENDOR_DICT[self.vendor]["outputCorrections"]:
                    output = correctionLambda(output)
                output = "\n".join(output.split("\n")[self.stripPrologueLines:-self.stripEpilogueLines])
                _addTimeStampsToStepDict(t1,self.stepDict,i)  
                self.stepDict["output"][i]["output"] = output                   
            else:
                t1=datetime.datetime.now()
                _addTimeStampsToStepDict(t1,self.stepDict,i) 
                self.stepDict["output"][i]["output"] = "ssh connect failed"
        return self.stepDict["output"]

    async def disconnect (self):
        if self.writer:
            logging.debug ("close writer socket {}".format(self.writer))
            self.writer.write_eof() 
            self.writer.close()
            if self.vendor == "cisco":   
                await asyncio.sleep (0.40)   
            logging.debug ("closed writer socket done")
        #self.sshConnectLoop.run_until_complete(task())
        return True





