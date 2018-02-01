# aioRunbook
automation tool for network tests and migrations

.. warning::

    currently in pre-alpha status. Do not use this code in current version.

Overview
========

aioRunbook (`asyncio <https://docs.python.org/3/library/asyncio.html>`_ runbook) is a 
Python package providing a framework for automated 
network tests and network migrations. 

aioRunbook is designed to be controlled by either shell execution respectively an 
aihttp web microservice. 

.. warning::

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
