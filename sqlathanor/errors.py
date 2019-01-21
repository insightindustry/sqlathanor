# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member class documentation is automatically incorporated
# there as needed.

import warnings

class SQLAthanorError(ValueError):
    """Base error raised by **SQLAthanor**. Inherits from
    :class:`ValueError <python:ValueError>`.
    """
    pass

class SQLAthanorWarning(UserWarning):
    """Base warning raised by **SQLAthanor**. Inherits from
    :class:`UserWarning <python:warnings.UserWarning>`."""
    pass

class SQLAlchemySupportError(SQLAthanorError):
    """Error raised when attempting to leverage a SQLAlchemy functionality that
    is not supported in your environment's version of SQLAlchemy."""
    pass

class ConfigurationError(SQLAthanorError):
    """Error raised when the serialization confirmation does not match expectations."""
    pass

class SerializationError(SQLAthanorError):
    """Error raised when something went wrong during serialization."""
    pass

class SerializableAttributeError(SerializationError):
    """Error raised when there are no serializable attributes on a model instance."""
    pass

class DeserializationError(SQLAthanorError):
    """Error raised when something went wrong during de-serialization."""
    pass

class YAMLParseError(DeserializationError):
    """Error raised when something went wrong parsing input YAML data."""
    pass

class JSONParseError(DeserializationError):
    """Error raised when something went wrong parsing input JSON data."""
    pass

class ValueSerializationError(SerializationError):
    """Error raised when an attribute value fails the serialization process."""
    pass

class DeserializableAttributeError(DeserializationError):
    """Error raised when there are no de-serializable attributes on a model instance
    or an inbound data source is empty."""
    pass

class MaximumNestingExceededError(ValueSerializationError):
    """Error raised when the maximum permitted nesting is exceeded during
    serialization."""
    pass

class MaximumNestingExceededWarning(SQLAthanorWarning):
    """Warning raised when the maximum permitted nesting is exceeded during
    serialization."""
    pass

class ValueDeserializationError(DeserializationError):
    """Error raised when an attribute value fails the de-serialization process."""
    pass

class InvalidFormatError(SQLAthanorError):
    """Error raised when supplying a format that is not recognized by **SQLAthanor**."""
    pass

class UnsupportedSerializationError(SerializationError):
    """Error raised when attempting to serialize an attribute that does not support
    serialization."""
    pass

class UnsupportedDeserializationError(DeserializationError):
    """Error raised when attempting to de-serialize an attribute that does not support
    de-serialization."""
    pass

class CSVStructureError(DeserializationError):
    """Error raised when there is a mismatch between expected columns and found columns
    in CSV data."""
    pass

class ExtraKeyError(DeserializationError):
    """Error raised when an inbound object being de-serialized has extra (unrecognized)
    keys."""
    pass

class UnsupportedValueTypeError(DeserializationError):
    """Error raised when a value type found in a serialized string is not supported."""
    pass
