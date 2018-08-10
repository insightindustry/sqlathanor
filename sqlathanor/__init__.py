# -*- coding: utf-8 -*-
"""Extension to the SQLAlchemy ORM with useful methods.

While this entry point to the library exposes all classes and functions for
convenience, those items themselves are actually implemented and documented in
child modules.

"""

import os

# Get the version number from the _version.py file
version_dict = {}
with open(os.path.join(os.path.dirname(__file__), '__version__.py')) as version_file:
    exec(version_file.read(), version_dict)                                     # pylint: disable=W0122

__version__ = version_dict.get('__version__')

from sqlathanor.declarative import BaseModel, declarative_base, as_declarative, \
    generate_model_from_csv, generate_model_from_json, generate_model_from_yaml, \
    generate_model_from_dict
from sqlathanor.flask_sqlathanor import FlaskBaseModel, initialize_flask_sqlathanor
from sqlathanor.schema import Column, relationship, Table
from sqlathanor.attributes import AttributeConfiguration

BaseModel = declarative_base(cls = BaseModel)

__all__ = [
    'BaseModel',
    'Column',
    'relationship',
    'Table',
    'AttributeConfiguration',
    'declarative_base',
    'as_declarative',
    'generate_model_from_csv',
    'generate_model_from_json',
    'generate_model_from_yaml',
    'generate_model_from_dict',
    'FlaskBaseModel',
    'initialize_flask_sqlathanor',
]
