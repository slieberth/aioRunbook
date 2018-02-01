Overview
========

aioRunbook (`asyncio <https://docs.python.org/3/library/asyncio.html>`_ runbook) is a 
Python package providing a framework for automated 
network tests and network migrations. 

.. warning::

    SW status is pre-alpha, alpha code will be available end of Feb. 2018


aioRunbook is designed to be controlled by either shell execution respectively an 
aihttp web microservice. 

.. note::

    the aiohttp based web control app is not yet included.

Use cases for aioRunbook are:

* automated lab tests for recurring test scenarios
* automated network migrations based on sequencial test steps with the option of a rollback functionality

In comparison to other atomization tools (e.g. Ansible), aioRunbook is explicitly designed for 
customizable inspection of the results of each test steps in a sequence of 
test steps. Each test step interacts with just one device. 
Another design differentiation is the documentation of the test results in customizable 
PDF outputs, respectively the flexibility to export the test results via an API.

All characteristics of the test sequence and the behaviour of the io-adapters to the network 
devices is controlled by a single config file.

The results of the aioRunbook steps are stored intermediately in an internal python data 
structures and stored at the end of the execution in a JSON file, for further processing:

* rendering to PDF documents
* dispatching the results in a web app

Concept of a YAML config
========================

The aioRunbook configuration is defined in a YAML file, which is a human friedly way
of documenting data-structures.
For details on the YAML format, please refer to `YAML spec/1.21 <http://yaml.org/spec/1.2/spec.html>`_

This concept allows that the data structure can be imported with the default YAML parser.

Also it allows the flexibility that additional attributes of any kind can added on demand 
without changing any logic in the input file parsing. Consumers of the input configuration
(adapters, analyzers, or rendering)  of attributes can access those attributes as those have
access to the complete data structure.

.. code-block:: yaml
    
    config:
      <global variables in the valueMatrix>
      <global attribute for host-file>
      <global attributes for the test/migration>
      steps:
        - <step-type 1>
            <step-type 1 attributes>
           commands:
              - <step-type 1 commands>
        - <step-type n>
            <step-type n attributes>
            commands:
              - <step-type n commands>
      pdfOutput:
          <attributes for PDF output>

.. note::

    In the future a web based editor for aioRunbook YAML config files might be available.

Concept of Test Steps
=====================

A test step comprehends an execution step on a single device. During a test step one or 
more commands be executed on the specific device. The commands are provided with a list of
strings, respectively with a list of objects for specific adaptors. In general the device 
parameters are referenced by the first word of the step attribute name. Optionally the 
the output (text, json, xml or API data) can be validated with customizable 
verification criteria. Based on experience is a good habit to verify the test step output
if possible.

.. _stepTypes:
.. figure::  images/overview1.pdf
   :align:   center

Following Step Types are implemented:

* **record**: executes a list (with one ore more list-elements) of commands and records the output of CLI commands
* **config**: similar to record, executes a list CLI commands. Was used to differentiate in PDF post processing, might be deprecated in the future.
* **check**: executes a list commands and checks the result of one command by an appropriate analyzer. By default the output of the last command is checked.
* **await**: performs periodical checks and performs an output check until the result is ''pass'', respectively the give-up-timer has expired.
* **copy**: sFTP file transfer to/from the network elements
* **sleep**: waits a configurable period of time before continuing with the next step.
* **break**: waits for a user input (return) before continuing with the next step
* **comment**: includes text-comments, text-segments, pre-recorded screenshots and file attachments. The later is a handy tool to document
    complete router configurations in the PDF output.

.. warning::

    follwoing step types still need to be ported to asyncio:

    * comment


This an example of the aioRunbook steps:

.. code-block:: yaml
    
    config:
      steps:
        - record:
            name: "<DUT> - <test step summary line>"
            commands: 
              - <command #1>
              - <command #n>
        - check:
            name: "<DUT> - <test step summary line>"
            commands: 
              - <command #1>
              - <command #n>
            # option for CLI output verification
            textFSMOneLine: '(.*Hostname\: MX1.*) 1'
            # option for JSON output verification
            jsonOneLine: '[some] == "data"'
        - await:
            name: "<DUT> - <test step summary line>"
            give-up-timer: 10
            commands: 
              - <command #1>
              - <command #n>
            # option for CLI output verification
            textFSMOneLine: '(.*Hostname\: MX1.*) 1'
            # option for JSON output verification
            jsonOneLine: '[some] == "data"'


Step Scheduler
==============

Two modes of scheduling for test steps are supported:

* **foreground / blocking mode**: the scheduler waits until the test-step is finshed, before the next step is started.
* **background / non blocking mode**: the scheduler starts the test-step in the background and continues to the nest test-step. 
    Once the test step is finished in the background, then the results are collected.

It is possible to loop the list of test steps by configuring a loop counter.:

.. _stepScheduler:
.. figure::  images/scheduler1.pdf
   :align:   center

This example lists the config options for aioRunbook step concurrency:

.. code-block:: yaml
    
    config:
      loops: <n>  #optional default := 1
      steps:
        - record:
            name: "<DUT> - <foreground test step summary line>"
            commands: 
              - <command #1>
        - record:
            name: "<DUT> - <background test step summary line>"
            startInBackground: true  #optional default := false
            randomStartDelay: 1  #optional default := 0 (seconds)
            commands: 
              - <command #1>





