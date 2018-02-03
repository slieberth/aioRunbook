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
import functools
import asyncio


class aioStdin:
    """asyncio reader from stdin. Used for non-blocking gathering of user input (step type break)

    stdinPrompt = aioStdin()

    myInput = await stdinPrompt("prompt text:")

    """

    def __init__(self, eventLoop=None):
        self.loop = eventLoop or asyncio.get_event_loop()
        self.q = asyncio.Queue(loop=self.loop)
        self.loop.add_reader(sys.stdin, self.got_input)

    def got_input(self):
        asyncio.ensure_future(self.q.put(sys.stdin.readline()), loop=self.loop)

    async def __call__(self, msg, end='\n', flush=False):
        print(msg, end=end, flush=flush)
        return (await self.q.get()).rstrip('\n')

