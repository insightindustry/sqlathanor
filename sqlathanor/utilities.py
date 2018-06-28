# -*- coding: utf-8 -*-

"""
************************
sqlathanor.utilities
************************

This module defines a variety of utility functions which are used throughout
**SQLAthanor**.

"""
from validator_collection import validators

from sqlathanor.errors import InvalidFormatError

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
