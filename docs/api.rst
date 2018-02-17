.. module:: aioRunbook

.. _API:

API Documentation
*****************

Overview
========


aioRunbookHttpServer
====================


.. currentmodule:: aioRunbook.aioRunbookHttpServer

.. autoclass:: aioRunbookHttpServer

   ================================== =
   methods
   ================================== =

   .. automethod:: init


aioRunbookScheduler
===================


.. currentmodule:: aioRunbook.aioRunbookScheduler

.. autoclass:: aioRunbookScheduler

   ================================== =
   methods
   ================================== =

   .. automethod:: execSteps

   .. automethod:: writeDiffSnapshotToFile

   .. automethod:: saveConfigDictToJsonFile

   .. automethod:: updateConfigDictStepInJsonFile

   .. automethod:: loadConfigDictFromJsonFile


adaptors
========

aioStdin
--------

.. currentmodule:: aioRunbook.adaptors.aioStdin

.. autoclass:: aioStdin

aioSshConnect
-------------

.. currentmodule:: aioRunbook.adaptors.aioSshConnect

.. autoclass:: aioSshConnect

   ================================== =
   methods
   ================================== =

   .. automethod:: runCommands

aioTelnetConnect
----------------

.. currentmodule:: adaptors.aioTelnetConnect

.. autoclass:: aioTelnetConnect

   ================================== =
   methods
   ================================== =

   .. automethod:: runCommands

aioRtbRestConnect
-----------------

.. currentmodule:: adaptors.aioRtbRestConnect

.. autoclass:: aioRtbRestConnect

   ================================== =
   methods
   ================================== =

   .. automethod:: runCommands

aioSftp
-------

.. currentmodule:: adaptors.aioSftp

.. autoclass:: aioSftp

   ================================== =
   methods
   ================================== =

   .. automethod:: execCopy

aioSnmpConnect
--------------

.. currentmodule:: adaptors.aioSnmpConnect

.. autoclass:: aioSnmpConnect

   ================================== =
   methods
   ================================== =

   .. automethod:: sendSnmpRequests



analyzers
=========

.. currentmodule:: analyzers.textFsmCheck

textFsmCheck
------------

.. autoclass:: textFsmCheck

   ================================== =
   methods
   ================================== =

   .. automethod:: checkCliOutputString

jsonCheck
---------

.. currentmodule:: analyzers.jsonCheck

.. autoclass:: jsonCheck

   ================================== =
   methods
   ================================== =

   .. automethod:: checkOutputData


diffCheck
---------

.. currentmodule:: analyzers.diffCheck

.. autoclass:: diffCheck

   ================================== =
   methods
   ================================== =

   .. automethod:: checkCliOutputString



postProcessing
==============

.. currentmodule:: postProcessing.aioPdfRender

.. autoclass:: aioPdfRender

   ================================== =
   methods
   ================================== =

   .. automethod:: writePdfFile

cacheCheckResults
=================

.. currentmodule:: caching.cacheCheckResults

.. autoclass:: cacheCheckResults

   ================================== =
   methods
   ================================== =

   .. automethod:: storeCheckResultToVarDict

   .. automethod:: retrieveVarFromVarDict

helperFunctions
===============

.. currentmodule:: tools.helperFunctions

.. autofunction:: _isInDictionary

.. autofunction:: _substitudeVarsInString

.. autofunction:: _addTimeStampsToStepDict

.. autofunction:: _setHostfileAttributes



