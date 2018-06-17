**********************************
Error Reference
**********************************

.. module:: sqlathanor.errors

.. contents::
  :local:
  :depth: 3
  :backlinks: entry

----------

Handling Errors
=================

Stack Traces
--------------

Because **SQLAthanor** produces exceptions which inherit from the
standard library, it leverages the same API for handling stack trace information.
This means that it will be handled just like a normal exception in unit test
frameworks, logging solutions, and other tools that might need that information.

---------

SQLAthanor Errors
===================

ValidationError (from :class:`ValueError <python:ValueError>`)
--------------------------------------------------------------------

.. autoclass:: ValidationError
