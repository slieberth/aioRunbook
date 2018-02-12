# Copyright (c) 2017-2018 by Stefan Lieberth <stefan@lieberth.net>.
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

"""Unit tests for diffCheck analyzer"""

import asyncio
from copy import copy
import os
import unittest
from unittest.mock import patch

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from aioRunbook.aioRunbookScheduler import aioRunbookScheduler
import logging
import pprint
import time



class test_diff_analyzer(unittest.TestCase):

    def test_diff1(self):

        """setting the diffSnapshot"""

        ymlConfigString = """# diff test 1 runbook
config:
  steps:
    - check:
        name: record test local-shell
        method: local-shell
        commands:
          - 'pip3 freeze'
        checkMethod: diff
    - check:
        name: record test local-shell
        method: local-shell
        commands:
          - 'pip3 freeze | tail -n 2'
        checkMethod: diff """
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],False)
        self.assertEqual(myRunbook.configDict["config"]["steps"][1]['check']['output'][0]['pass'],False)
        #pprint.pprint(myRunbook.configDict)
        myRunbook.writeDiffSnapshotToFile()
        time.sleep(1)

    def test_diff2(self):

        """using the diffSnapshot, must match"""

        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        #pprint.pprint(myRunbook.configDict)
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],True)
        self.assertEqual(myRunbook.configDict["config"]["steps"][1]['check']['output'][0]['pass'],True)

    def test_diff3(self):

        """setting the diffSnapshot, different command in step 2, -> missmatch"""

        ymlConfigString = """# diff test 1 runbook
config:
  steps:
    - check:
        name: record test local-shell
        method: local-shell
        commands:
          - 'pip3 freeze'
        checkMethod: diff
    - check:
        name: record test local-shell
        method: local-shell
        commands:
          - 'pip3 freeze | tail -n 3'
        checkMethod: diff 
diffSnapshot:
  created: '2018-02-10 06:46:07.495384'
  loop_1_step_1: !!binary |
    Nzg5YzM1NTFjYjhlZGIzMDBjYmNlYjVmNjIzODhlYjc0ZDBlM2UxNGJkMTVkZGEyNjg0ZjNkMmEz
    MjlkNzBhZGQ3OGEzNDZhZmQ3ZDQ1YmE4YmY4OTBhMTY2ODZhMzkxYzVmNDY0Y2VkMzM0NzQ5N2Vl
    ZGMxYjdiZTAxMzgxZGIwYTcyOWRhNmJlMWIzYTlkZmZkYWUyM2RhNTU1MjY2N2E1NTIzY2JiNTIz
    MzI3MjU4ZGMyYTIxYWRkODkzMTQwZGE1ODNjZmI4ZjIxZDE3MzlhOWFhYzdkZTZhZWFhNjk2YTBi
    YmJkMTM4Mjg4YzBiMzY3NjdmYmU4YWYzZDViODQ1YjBiMmRiZjlkMzk2MTk5NGRlMGJkNDhkOGY2
    MmYzYjNjYTA2YTEyYzk2MTgyMjE0ZDI2YzYzNWI4MTczYjQ3MmZhNDlmZjlkODhiY2Y4NDk5YTZm
    MThkZmVjYTBjYWRlYmMzMWVjYmM1MDEwNWQ0YjYzNTZhODA1ZTNhMzcxMGZiMmRmNDMxMzhlOTJj
    YWJjZGFiMjZlZjliNzVkNDBhZDRjNDgzMTcxOGFlODA0OGUyNjZjOWU3MTQ2YzdjMjE3NmQ3NGNl
    MjM0NDE2ZWY5N2VlNjJiMjJkMzZlMDlhNjRiNTc0OTU2MWNmNzBkMDY1NzU1ZTFmMTg5N2E0NjYw
    MjdkZDU4MjFhOGY2YjJlYzkwMWQxZTEzNDk4NWNhNTdhNDFhMzIyZDdhYzA5OGFkZWU5MmE1ODJi
    OWE1MzgwNWQzY2M2ZWViM2Y5NTk3ZmQ4YWZkYWMxMjBlNjk1MTY3OTczNzlkYTliYTA4MDA3MTAz
    NzhhMjE0YmE4ZjY2YmIyM2Y1ZjVlYmY2YjkwYzExNDc4ZGY4MDk4OGUzZGVkZjQ2MzcwZTI5NGZj
    MWRiYzVlZjVkYWFlNDZiOGZmN2ZiZWRlZjBmYjFjYjRjMjViZjc2MmY4MmY0NmFkZWZkNjUyNmNj
    NTdiYmM1ZjM0ZDQ2MGFhMmQ5YWFmNjlmZTAxMjA1N2MzZjU=
  loop_1_step_2: !!binary |
    Nzg5YzJiMmRjYWM5Yzk0YzMyYjZiNTM1ZDQzMzMyZTJhYTRjMmNjYTAxMzEwZGY1MGMwMDY3NWIw
    NzI1'"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop)) 
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],True)
        self.assertEqual(myRunbook.configDict["config"]["steps"][1]['check']['output'][0]['pass'],False)

    def test_diff4(self):

        """setting the diffSnapshot with errenaous zip/binary data"""

        ymlConfigString = """# diff test 4 runbook
config:
  steps:
    - check:
        name: record test local-shell
        method: local-shell
        commands:
          - 'pip3 freeze'
        checkMethod: diff
    - check:
        name: record test local-shell
        method: local-shell
        commands:
          - 'pip3 freeze | tail -n 3'
        checkMethod: diff 
diffSnapshot:
  created: '2018-02-10 06:46:07.495384'
  loop_1_step_1: !!binary |
    Nzg5YzM1NTFjYjhlZGIzMDBjYmNlYjVmNjIzODhlYjc0ZDBlM2UxNGJkMTVkZGEyNjg0ZjNkMmEz
    MjlkNzBhZGQ3OGEzNDZhZmQ3ZDQ1YmE4YmY4OTBhMTY2ODZhMzkxYzVmNDY0Y2VkMzM0NzQ5N2Vl
    ZGMxYjdiZTAxMzgxZGIwYTcyOWRhNmJlMWIzYTlkZmZkYWUyM2RhNTU1MjY2N2E1NTIzY2JiNTIz
    MzI3MjU4ZGMyYTIxYWRkODkzMTQwZGE1ODNjZmI4ZjIxZDE3MzlhOWFhYzdkZTZhZWFhNjk2YTBi
    YmJkMTM4Mjg4YzBiMzY3NjdmYmU4YWYzZDViODQ1YjBiMmRiZjlkMzk2MTk5NGRlMGJkNDhkOGY2
    MmYzYjNjYTA2YTEyYzk2MTgyMjE0ZDI2YzYzNWI4MTczYjQ3MmZhNDlmZjlkODhiY2Y4NDk5YTZm
    MThkZmVjYTBjYWRlYmMzMWVjYmM1MDEwNWQ0YjYzNTZhODA1ZTNhMzcxMGZiMmRmNDMxMzhlOTJj
    YWJjZGFiMjZlZjliNzVkNDBhZDRjNDgzMTcxOGFlODA0OGUyNjZjOWU3MTQ2YzdjMjE3NmQ3NGNl
    MjM0NDE2ZWY5N2VlNjJiMjJkMzZlMDlhNjRiNTc0OTU2MWNmNzBkMDY1NzU1ZTFmMTg5N2E0NjYw
    MjdkZDU4MjFhOGY2YjJlYzkwMWQxZTEzNDk4NWNhNTdhNDFhMzIyZDdhYzA5OGFkZWU5MmE1ODJi
    OWE1MzgwNWQzY2M2ZWViM2Y5NTk3ZmQ4YWZkYWMxMjBlNjk1MTY3OTczNzlkYTliYTA4MDA3MTAz
    NzhhMjE0YmE4ZjY2YmIyM2Y1ZjVlYmY2YjkwYzExNDc4ZGY4MDk4OGUzZGVkZjQ2MzcwZTI5NGZj
    MWRiYzVlZjVkYWFlNDZiOGZmN2ZiZWRlZjBmYjFjYjRjMjViZjc2MmY4MmY0NmFkZWZkNjUyNmNj
    NTdiYmM1ZjM0ZDQ2MGFhMmQ5YWFmNjlmZTAxMjA1N2MzZjU=
  loop_1_step_2: !!binary |
    Nzg5YzJiMmRjYWM5Yzk0YzMyYjZiNTM1ZDQzMzMyZTJhYTRjMmNjYTAxMzEwZGY1MGMwMDY3NWIx
    NzI1'"""
        fh = open("test.yml",'w')
        fh.write(ymlConfigString)
        fh.close()
        myRunbook = aioRunbookScheduler("test.yml")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myRunbook.execSteps(loop))
        self.assertEqual(myRunbook.configDict["config"]["steps"][0]['check']['output'][0]['pass'],True)
        self.assertEqual(myRunbook.configDict["config"]["steps"][1]['check']['output'][0]['pass'],False)


if __name__ == '__main__':
    #logLevel = logging.DEBUG
    logLevel = logging.ERROR
    logging.basicConfig(filename="myLog.log", filemode='w', level=logLevel)
    logging.getLogger().setLevel(logLevel)
    console = logging.StreamHandler()
    console.setLevel(logLevel)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)

    unittest.main()



