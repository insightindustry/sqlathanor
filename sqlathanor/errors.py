# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member class documentation is automatically incorporated
# there as needed.

class SQLAthanorError(ValueError):
    pass

class SQLAthanorValidationError(SQLAthanorError):
    pass

class ValueSerializationError(SQLAthanorError):
    """Error raised when an attribute value fails the serialization process."""
    pass

class ValueDeserializationError(SQLAthanorError):
    """Error raised when an attribute value fails the de-serialization process."""
    pass

class InvalidFormatError(SQLAthanorError):
    """Error raised when supplying a format that is not recognized by **SQLAthanor**."""
    pass

class UnsupportedSerializationError(SQLAthanorError):
    """Error raised when attempting to serialize an attribute that does not support
    serialization."""
    pass

class UnsupportedDeserializationError(SQLAthanorError):
    """Error raised when attempting to de-serialize an attribute that does not support
    de-serialization."""
    pass
