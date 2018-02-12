Overview
========

Current SW status is alpha! - ETA for beta is March 2018

Documentation is under development:
http://aiorunbook.readthedocs.io/en/latest/index.html

Installation
============

.. code-block:: bash

    pip3 install git+https://github.com/slieberth/aioRunbook.git


Hello-World
===========

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


