import asyncio
from aioRunbook.aioRunbook import aioRunbook

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
myRunbook = aioRunbook("test.yml")
loop = asyncio.get_event_loop()
loop.run_until_complete(myRunbook.execSteps(loop))
print(myRunbook.configDict["config"]["steps"][0]['record']['output'])
