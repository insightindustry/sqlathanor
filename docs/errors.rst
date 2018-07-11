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

Errors During Serialization
-----------------------------

.. include:: _error_handling_serialization.rst

Errors During De-Serialization
--------------------------------

.. include:: _error_handling_deserialization.rst

------------------

SQLAthanor Errors
===================

SQLAthanorError (from :class:`ValueError <python:ValueError>`)
--------------------------------------------------------------------

.. autoclass:: SQLAthanorError

----------------

InvalidFormatError (from :class:`SQLAthanorError`)
-------------------------------------------------------

.. autoclass:: InvalidFormatError

----------------

SerializationError (from :class:`SQLAthanorError`)
-----------------------------------------------------

.. autoclass:: SerializationError

----------------

ValueSerializationError (from :class:`SerializationError`)
---------------------------------------------------------------

.. autoclass:: ValueSerializationError

----------------

SerializableAttributeError (from :class:`SerializationError`)
--------------------------------------------------------------

.. autoclass:: SerializableAttributeError

----------------

MaximumNestingExceededError (from :class:`SerializationError`)
-----------------------------------------------------------------

.. autoclass:: MaximumNestingExceededError

----------------

UnsupportedSerializationError (from :class:`SerializationError`)
-------------------------------------------------------------------

.. autoclass:: UnsupportedSerializationError

----------------

DeserializationError (from :class:`SQLAthanorError`)
-----------------------------------------------------

.. autoclass:: DeserializationError

----------------

CSVStructureError (from :class:`DeserializationError`)
-------------------------------------------------------

.. autoclass:: CSVStructureError

----------------

JSONParseError (from :class:`DeserializationError`)
-------------------------------------------------------

.. autoclass:: JSONParseError

----------------

YAMLParseError (from :class:`DeserializationError`)
-------------------------------------------------------

.. autoclass:: YAMLParseError

----------------

DeserializableAttributeError (from :class:`DeserializationError`)
---------------------------------------------------------------------

.. autoclass:: DeserializableAttributeError

----------------

ValueDeserializationError (from :class:`DeserializationError`)
--------------------------------------------------------------------

.. autoclass:: ValueDeserializationError

----------------

UnsupportedDeserializationError (from :class:`DeserializationError`)
-----------------------------------------------------------------------

.. autoclass:: UnsupportedDeserializationError

----------------

ExtraKeyError (from :class:`DeserializationError`)
-------------------------------------------------------

.. autoclass:: ExtraKeyError

----------------

SQLAthanor Warnings
======================

SQLAthanorWarning (from :class:`UserWarning <python:UserWarning>`)
------------------------------------------------------------------------

.. autoclass:: SQLAthanorWarning

----------------

MaximumNestingExceededWarning (from :class:`SQLAthanorWarning`)
------------------------------------------------------------------

.. autoclass:: MaximumNestingExceededWarning
