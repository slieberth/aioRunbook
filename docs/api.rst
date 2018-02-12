.. module:: aioRunbook

.. _API:

API Documentation
*****************

Overview
========


aioRunbook
==========


.. currentmodule:: aioRunbook.aioRunbookScheduler

.. autoclass:: aioRunbookScheduler

   ================================== =
   methods
   ================================== =

   .. automethod:: execSteps

   .. automethod:: writeDiffSnapshotToFile

Adaptors
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



Analyzers
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




