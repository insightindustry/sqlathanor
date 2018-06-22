# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member class documentation is automatically incorporated
# there as needed.

class SQLAthanorError(ValueError):
    pass

class SQLAthanorValidationError(SQLAthanorError):
    pass
