# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member class documentation is automatically incorporated
# there as needed.

class SQLAthanorError(ValueError):
    pass

class SQLAthanorValidationError(SQLAthanorError):
    pass

class SerializationError(SQLAthanorError):
    """Error raised when something went wrong during serialization."""
    pass

class DeserializationError(SQLAthanorError):
    """Error raised when something went wrong during de-serialization."""
    pass

class ValueSerializationError(SerializationError):
    """Error raised when an attribute value fails the serialization process."""
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

class CSVColumnError(DeserializationError):
    """Error raised when there is a mismatch between expected columns and found columns
    in CSV data."""
    pass
