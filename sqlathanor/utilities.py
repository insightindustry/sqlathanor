# -*- coding: utf-8 -*-

"""
************************
sqlathanor.utilities
************************

This module defines a variety of utility functions which are used throughout
**SQLAthanor**.

"""
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.state import InstanceState

from validator_collection import validators

from sqlathanor.errors import InvalidFormatError, UnsupportedSerializationError, \
    UnsupportedDeserializationError

def bool_to_tuple(input):
    """Converts a single :ref:`bool <python:bool>` value to a
    :ref:`tuple <python:tuple>` of form ``(bool, bool)``.

    :param input: Value that should be converted.
    :type input: :ref:`bool <python:bool>` / 2-member :ref:`tuple <python:tuple>`

    :returns: :ref:`tuple <python:tuple>` of form (:ref:`bool <python:bool>`,
      :ref:`bool <python:bool>`)
    :rtype: :ref:`tuple <python:tuple>`

    :raises ValueError: if ``input`` is not a :ref:`bool <python:bool>` or
      2-member :ref:`tuple <python:tuple>`
    """

    if input is True:
        input = (True, True)
    elif not input:
        input = (False, False)
    elif not isinstance(input, tuple) or len(input) > 2:
        raise ValueError('input was neither a bool nor a 2-member tuple')

    return input


def callable_to_dict(input):
    """Coerce the ``input`` into a :ref:`dict <python:dict>` with callable
    keys for each supported serialization format.

    :param input: The callable function that should correspond to one or more
      formats.
    :type input: callable / :ref:`dict <python:dict>` with formats
      as keys and callables as values

    :returns: :ref:`dict <python:dict>` with formats as keys and callables as values
    :rtype: :ref:`dict <python:dict>`

    """
    if input is not None and not isinstance(input, dict):
        input = {
            'csv': input,
            'json': input,
            'yaml': input,
            'dict': input
        }
    elif input is not None:
        if 'csv' not in input:
            input['csv'] = None
        if 'json' not in input:
            input['json'] = None
        if 'yaml' not in input:
            input['yaml'] = None
        if 'dict' not in input:
            input['dict'] = None
    else:
        input = {
            'csv': None,
            'json': None,
            'yaml': None,
            'dict': None
        }

    return input


def format_to_tuple(format):
    """Retrieve a serialization/de-serialization tuple based on ``format``.

    :param format: The format to which the value should be serialized. Accepts
      either: ``csv``, ``json``, ``yaml``, or ``dict``.
    :type format: :ref:`str <python:str>`

    :returns: A 4-member :ref:`tuple <python:tuple>` corresponding to
      ``<direction>_csv``, ``<direction>_json``, ``<direction>_yaml``,
      ``<direction>_dict``
    :rtype: :ref:`tuple <python:tuple>` of :ref:`bool <python:bool>` / :class:`None`

    :raises InvalidFormatError: if ``format`` is not ``csv``, ``json``, ``yaml``,
      or ``dict``.

    """
    csv = None
    json = None
    yaml = None
    dict = None

    try:
        format = validators.string(format,
                                   allow_empty = False)
    except ValueError:
        raise InvalidFormatError('%s is not a valid format string' % format)

    format = format.lower()

    if format == 'csv':
        csv = True
    elif format == 'json':
        json = True
    elif format == 'yaml':
        yaml = True
    elif format == 'dict':
        dict = True
    else:
        raise InvalidFormatError('%s is not a valid format string' % format)

    return csv, json, yaml, dict


def get_class_type_key(class_attribute, value = None):
    """Retrieve the class type for ``class_attribute.

    .. note::

      If ``class_attribute`` does not have a SQLAlchemy data type, then
      determines the data type based on ``value``.

    :param class_attribute: The class attribute whose default serializer will be
      returned. Defaults to :class:`None`.

    :param format: The format to which the value should be serialized. Accepts
      either: ``csv``, ``json``, ``yaml``, or ``dict``. Defaults to :class:`None`.
    :type format: :ref:`str <python:str>`

    :param value: The class attribute's value.

    :returns: The key to use to find a default serializer or de-serializer.
    :rtype: :ref:`str <python:str>`

    """
    if class_attribute is not None:
        try:
            class_type = class_attribute.type
        except AttributeError:
            if value is not None:
                class_type = type(value)
            else:
                class_type = None
    elif value is not None:
        class_type = type(value)
    else:
        class_type = None

    if class_type is not None:
        try:
            class_type_key = class_type.__name__
        except AttributeError:
            class_type_key = str(class_type)
    else:
        class_type_key = 'NONE'

    return class_type_key


def raise_UnsupportedSerializationError(value):
    raise UnsupportedSerializationError("value '%s' cannot be serialized" % value)

def raise_UnsupportedDeserializationError(value):
    raise UnsupportedDeserializationError("value '%s' cannot be de-serialized" % value)

def is_model_instance(obj):
    """Indicate whether ``obj`` is a :term:`model instance`.

    :returns: ``True`` if ``obj`` is a model instance. ``False`` if not.
    :rtype: :ref:`bool <python:bool>`
    """
    try:
        property_type = type(obj.__is_model_instance)
    except AttributeError:
        return False

    print(property_type)

    return property_type == bool
