Overview
========

Current SW status is alpha! - ETA for beta is March 2018

Documentation is under development:
http://aiorunbook.readthedocs.io/en/latest/index.html

Installation
============

.. code-block:: bash

    pip3 install git+https://github.com/slieberth/aioRunbook.git


Hello-World aioRunbookScheduler
===============================

.. code-block:: python

    import asyncio
    from aioRunbook.aioRunbookScheduler import aioRunbookScheduler

    ymlConfigString = """#hello world yml
    config:
      steps:
        - record:
            name: record test local-shell
            method: local-shell
            commands:
              - echo "Hello World" """
    fh = open("test.yml",'w')
    fh.write(ymlConfigString)
    fh.close()
    myRunbook = aioRunbookScheduler("test.yml")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(myRunbook.execSteps(loop))
    print(myRunbook.configDict["config"]["steps"][0]['record']['output'])

Hello-World aioRunbookHttpServer
================================

.. code-block:: python

    from aioRunbook.aioRunbookHttpServer import aioRunbookHttpServer
    from aiohttp.web import Application, Response, StreamResponse, run_app
    import asyncio

    ymlConfigString = """#
    runbookDirs:
      - "./testDir1"
      - "./testDir2"
      - "./testDir3"
    httpPort: 4711  
    userAuth:
    - - username: CharlieBrown
      - password: test
      - permissions: 
        - viewResults
    - - username: MissSophie
      - password: test
      - permissions: 
        - viewResults
        - runTests
    - - username: MajorTom
      - password: test
      - permissions: 
        - viewResults
        - runTests
        - editTests"""
    fh = open("aioServerConfig.yml",'w')
    fh.write(ymlConfigString)
    fh.close()
    myHttpServer = aioRunbookHttpServer("aioServerConfig.yml")
    loop = asyncio.get_event_loop()
    app = myHttpServer.init(loop)
    if app != None:
        loop.run_until_complete(run_app(app,port=myHttpServer.httpPort))


