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

#  \version   0.1.1
#  \date      01.02.2018
#  \modification:
#  0.1.1 - get started

import sys
import datetime


class aioError:
    """

    """

    def __init__(self,stepDict,configDict = {"config":{}},port=22,loop=None,**kwargs): 
        self.stepDict = stepDict

    async def runCommands (self):
        """

        """
        t1=datetime.datetime.now()
        self.stepDict["output"][0]["startTS"] = t1.strftime('%Y-%m-%d %H:%M:%S.%f')  
        self.stepDict["output"][0]["endTS"] = t1.strftime('%Y-%m-%d %H:%M:%S.%f')   
        self.stepDict["output"][0]["elapsed"] = str((t1-t1))
        self.stepDict["output"][0]["elapsedRaw"] = 0
        self.stepDict["output"][0]["output"] = "### adapter selection failed ###"
        return self.stepDict["output"]

