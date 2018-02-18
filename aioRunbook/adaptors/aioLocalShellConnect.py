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

#  \version   0.1.2
#  \date      23.01.17

 #  \modification
#  0.1.1 base line for history
#  0.1.2 work for asyncio loop fix


import sys
import functools
import asyncio
import datetime
import logging
import os
#sys.path.insert(0, os.path.abspath('../tools'))
from aioRunbook.tools.helperFunctions import _isInDictionary


class aioLocalShellConnect:
    """asyncio reader from stdin. Used for non-blocking gathering of user input (step type break)

              :param delayTimer: a waiting time (in seconds) periods before the commands are executed. required for await.
              :type delayTimer: int

              :return: the enriched stepDict output dict

    """

    def __init__(self,stepDict,configDict = {"config":{}},eventLoop=None,**kwargs): 
        self.stepDict = stepDict
        self.timeout = _isInDictionary ("timeout",configDict["config"],60)
        self.timeout = _isInDictionary ("timeout",stepDict,self.timeout)

    async def runCommands (self,delayTimer=0):
        """

        """
        time = await asyncio.sleep(delayTimer)
        for i,command in enumerate(self.stepDict["commands"]):
            t1=datetime.datetime.now()
            self.stepDict["output"][i]["startTS"] = t1.strftime('%Y-%m-%d %H:%M:%S.%f')  
            process = await asyncio.create_subprocess_shell(command,stdout=asyncio.subprocess.PIPE) 
            stdout, stderr = await asyncio.wait_for(process.communicate(),timeout=self.timeout)
            t2=datetime.datetime.now()
            self.stepDict["output"][i]["endTS"] = t2.strftime('%Y-%m-%d %H:%M:%S.%f')   
            self.stepDict["output"][i]["elapsed"] = str((t2-t1))
            self.stepDict["output"][i]["elapsedRaw"] = (t2-t1).total_seconds()
            self.stepDict["output"][i]["output"] = stdout.decode().strip()
        return self.stepDict["output"]


