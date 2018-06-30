# -*- coding: utf-8 -*-

"""
************************
sqlathanor.utilities
************************

This module defines a variety of utility functions which are used throughout
**SQLAthanor**.

"""
import warnings
import yaml

from sqlalchemy.orm.collections import InstrumentedList

from validator_collection import validators, checkers
from validator_collection.errors import NotAnIterableError

from sqlathanor._compat import json
from sqlathanor.errors import InvalidFormatError, UnsupportedSerializationError, \
    UnsupportedDeserializationError, MaximumNestingExceededError, \
    MaximumNestingExceededWarning, DeserializationError

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
    """Retrieve the class type for ``class_attribute``.

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


def iterable__to_dict(iterable,
                      format,
                      max_nesting = 0,
                      current_nesting = 0):
    """Given an iterable, traverse it and execute ``_to_dict()`` if present.

    :param iterable: An iterable to traverse.
    :type iterable: iterable

    :param format: The format to which the :ref:`dict <python:dict>` will
      ultimately be serialized. Accepts: ``'csv'``, ``'json'``, ``'yaml'``, and
      ``'dict'``.
    :type format: :ref:`str <python:str>`


    :param max_nesting: The maximum number of levels that the resulting
      :ref:`dict <python:dict>` object can be nested. If set to ``0``, will
      not nest other serializable objects. Defaults to ``0``.
    :type max_nesting: :ref:`int <python:int>`

    :param current_nesting: The current nesting level at which the
      :ref:`dict <python:dict>` representation will reside. Defaults to ``0``.
    :type current_nesting: :ref:`int <python:int>`

    :returns: Collection of values, possibly converted to :ref:`dict <python:dict>`
      objects.
    :rtype: :ref:`list <python:list>` of objects

    :raises InvalidFormatError: if ``format`` is not an acceptable value
    :raises ValueError: if ``iterable`` is not an iterable

    """
    next_nesting = current_nesting + 1

    if format not in ['csv', 'json', 'yaml', 'dict']:
        raise InvalidFormatError("format '%s' not supported" % format)

    iterable = validators.iterable(iterable,
                                   allow_empty = True,
                                   forbid_literals = (str, bytes, dict))

    if iterable is None:
        return []

    if current_nesting > max_nesting:
        raise MaximumNestingExceededError(
            'current nesting level (%s) exceeds maximum %s' % (current_nesting,
                                                               max_nesting)
        )

    items = []

    for item in iterable:
        try:
            new_item = item._to_dict(format,
                                     max_nesting = max_nesting,
                                     current_nesting = next_nesting)
        except AttributeError:
            try:
                new_item = iterable__to_dict(item,
                                             format,
                                             max_nesting = max_nesting,
                                             current_nesting = next_nesting)
            except NotAnIterableError:
                new_item = item

        items.append(new_item)

    return items

def raise_UnsupportedSerializationError(value):
    raise UnsupportedSerializationError("value '%s' cannot be serialized" % value)

def raise_UnsupportedDeserializationError(value):
    raise UnsupportedDeserializationError("value '%s' cannot be de-serialized" % value)


def are_equivalent(*args, **kwargs):
    """Indicate if arguments passed to this function are equivalent.

    .. hint::

      This checker operates recursively on the members contained within iterables
      and :class:`dict <python:dict>` objects.

    .. caution::

      If you only pass one argument to this checker - even if it is an iterable -
      the checker will *always* return ``True``.

      To evaluate members of an iterable for equivalence, you should instead
      unpack the iterable into the function like so:

      .. code-block:: python

        obj = [1, 1, 1, 2]

        result = are_equivalent(*obj)
        # Will return ``False`` by unpacking and evaluating the iterable's members

        result = are_equivalent(obj)
        # Will always return True

    :param args: One or more values, passed as positional arguments.

    :returns: ``True`` if ``args`` are equivalent, and ``False`` if not.
    :rtype: :class:`bool <python:bool>`
    """
    if len(args) == 1:
        return True

    first_item = args[0]
    for item in args[1:]:
        if not all(isinstance(x, (list, InstrumentedList)) for x in args) and \
           type(item) != type(first_item):                                      # pylint: disable=C0123
            return False

        if isinstance(item, dict):
            if not are_dicts_equivalent(item, first_item):
                return False
        elif hasattr(item, '__iter__') and not isinstance(item, (str, bytes, dict)):
            if len(item) != len(first_item):
                return False
            for value in item:
                if value not in first_item:
                    return False
            for value in first_item:
                if value not in item:
                    return False
        else:
            if item != first_item:
                return False

    return True


def are_dicts_equivalent(*args, **kwargs):
    """Indicate if :ref:`dicts <python:dict>` passed to this function have identical
    keys and values.

    :param args: One or more values, passed as positional arguments.

    :returns: ``True`` if ``args`` have identical keys/values, and ``False`` if not.
    :rtype: :class:`bool <python:bool>`
    """
    # pylint: disable=too-many-return-statements
    if not args:
        return False

    if len(args) == 1:
        return True

    if not all(checkers.is_dict(x) for x in args):
        return False

    first_item = args[0]
    for item in args[1:]:
        if len(item) != len(first_item):
            return False

        for key in item:
            if key not in first_item:
                return False

            if not are_equivalent(item[key], first_item[key]):
                return False

        for key in first_item:
            if key not in item:
                return False

            if not are_equivalent(first_item[key], item[key]):
                return False

    return True


def parse_yaml(input_data,
               deserialize_function = None,
               **kwargs):
    """De-serialize YAML data into a Python :ref:`dict <python:dict>` object.

    :param input_data: The YAML data to de-serialize.
    :type input_data: :ref:`str <python:str>`

    :param deserialize_function: Optionally override the default YAML deserializer.
      Defaults to :class:`None`, which calls the default ``yaml.safe_load()``
      function from the `PyYAML <https://github.com/yaml/pyyaml>`_ library.

      .. note::

        Use the ``deserialize_function`` parameter to override the default
        YAML deserializer. A valid ``deserialize_function`` is expected to
        accept a single :ref:`str <python:str>` and return a
        :ref:`dict <python:dict>`, similar to ``yaml.safe_load()``.

        If you wish to pass additional arguments to your ``deserialize_function``
        pass them as keyword arguments (in ``kwargs``).

    :type deserialize_function: callable / :class:`None`

    :param **kwargs: Optional keyword parameters that are passed to the
      YAML deserializer function. By default, these are options which are passed
      to ``yaml.safe_load()``.
    :type **kwargs: keyword arguments

    :returns: A :ref:`dict <python:dict>` representation of ``input_data``.
    :rtype: :ref:`dict <python:dict>`
    """
    if deserialize_function is None:
        deserialize_function = yaml.safe_load
    else:
        if checkers.is_callable(deserialize_function) is False:
            raise ValueError(
                'deserialize_function (%s) is not callable' % deserialize_function
            )

    if not input_data:
        raise DeserializationError('input_data is empty')

    try:
        input_data = validators.string(input_data,
                                       allow_empty = False)
    except ValueError:
        raise DeserializationError('input_data is not a valid string')

    from_yaml = yaml.safe_load(input_data, **kwargs)

    return from_yaml


def parse_json(input_data,
               deserialize_function = None,
               **kwargs):
    """De-serialize JSON data into a Python :ref:`dict <python:dict>` object.

    :param input_data: The JSON data to de-serialize.
    :type input_data: :ref:`str <python:str>`

    :param deserialize_function: Optionally override the default JSON deserializer.
      Defaults to :class:`None`, which calls the default
      :ref:`simplejson.loads() <simplejson:simplejson.loads>`
      function from the `simplejson <https://github.com/simplejson/simplejson>`_ library.

      .. note::

        Use the ``deserialize_function`` parameter to override the default
        YAML deserializer. A valid ``deserialize_function`` is expected to
        accept a single :ref:`str <python:str>` and return a
        :ref:`dict <python:dict>`, similar to
        :ref:`simplejson.loads() <simplejson:simplejson.loads>`

        If you wish to pass additional arguments to your ``deserialize_function``
        pass them as keyword arguments (in ``kwargs``).

    :type deserialize_function: callable / :class:`None`

    :param **kwargs: Optional keyword parameters that are passed to the
      JSON deserializer function. By default, these are options which are passed
      to :ref:`simplejson.loads() <simplejson:simplejson.loads>`.
    :type **kwargs: keyword arguments

    :returns: A :ref:`dict <python:dict>` representation of ``input_data``.
    :rtype: :ref:`dict <python:dict>`
    """
    if deserialize_function is None:
        deserialize_function = json.loads
    else:
        if checkers.is_callable(deserialize_function) is False:
            raise ValueError(
                'deserialize_function (%s) is not callable' % deserialize_function
            )

    if not input_data:
        raise DeserializationError('input_data is empty')

    try:
        input_data = validators.string(input_data,
                                       allow_empty = False)
    except ValueError:
        raise DeserializationError('input_data is not a valid string')

    from_json = json.loads(input_data, **kwargs)

    return from_json
