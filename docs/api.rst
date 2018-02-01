.. module:: runbook

.. _API:

API Documentation
*****************

Overview
========


aioRunbook
==========


.. currentmodule:: aioRunbook

.. autoclass:: aioRunbook

   ================================== =
   methods
   ================================== =

   .. automethod:: execSteps


Adaptors
========

aioStdin
--------

.. currentmodule:: adaptors.aioStdin

.. autoclass:: aioStdin

aioSshConnect
-------------

.. currentmodule:: adaptors.aioSshConnect

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
------------

.. currentmodule:: analyzers.jsonCheck

.. autoclass:: jsonCheck

   ================================== =
   methods
   ================================== =

   .. automethod:: checkOutputData


