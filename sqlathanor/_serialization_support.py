# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

from validator_collection import validators, checkers

from sqlathanor.utilities import bool_to_tuple, callable_to_dict
from sqlathanor.errors import SQLAthanorError


class SerializationMixin(object):
    """Mixin class that adds standard serialization/de-serialiaztion support."""

    def __init__(self, *args, **kwargs):
        self._supports_csv = (False, False)
        self._csv_sequence = None
        self._supports_json = (False, False)
        self._supports_yaml = (False, False)
        self._supports_dict = (False, False)
        self._on_serialize = {
            'csv': None,
            'json': None,
            'yaml': None,
            'dict': None
        }
        self._on_deserialize = {
            'csv': None,
            'json': None,
            'yaml': None,
            'dict': None
        }
        self._display_name = None

        self.supports_csv = kwargs.pop('supports_csv', (False, False))
        self.csv_sequence = kwargs.pop('csv_sequence', None)
        self.supports_json = kwargs.pop('supports_json', (False, False))
        self.supports_yaml = kwargs.pop('supports_yaml', (False, False))
        self.supports_dict = kwargs.pop('supports_dict', (False, False))
        self.on_serialize = kwargs.pop('on_serialize', None)
        self.on_deserialize = kwargs.pop('on_deserialize', None)
        self.display_name = kwargs.pop('display_name', None)

        super(SerializationMixin, self).__init__(*args, **kwargs)

    @property
    def supports_csv(self):
        """Indicates whether the attribute can be serialized / de-serialized to CSV.

        :returns: 2-member :class:`tuple <python:tuple>` (inbound de-serialization /
          outbound serialization)
        :rtype: :class:`tuple <python:tuple>` of form (:class:`bool <python:bool>`,
          :class:`bool <python:bool>`)

        """
        return self._supports_csv

    @supports_csv.setter
    def supports_csv(self, value):
        value = bool_to_tuple(value)
        self._supports_csv = value

    @property
    def csv_sequence(self):
        """Column position when serialized to or de-serialized from CSV.

        .. note::

          If :obj:`None <python:None>`, will default to alphabetical sorting *after* any
          attributes that have an explicit ``csv_sequence`` provided.

        :rtype: :class:`int <python:int>` / :obj:`None <python:None>`.
        """
        return self._csv_sequence

    @csv_sequence.setter
    def csv_sequence(self, value):
        if value is not None:
            value = validators.integer(value)

        self._csv_sequence = value

    @property
    def supports_json(self):
        """Indicates whether the attribute can be serialized / de-serialized to JSON.

        :returns: 2-member :class:`tuple <python:tuple>` (inbound de-serialization /
          outbound serialization)
        :rtype: :class:`tuple <python:tuple>` of form (:class:`bool <python:bool>`,
          :class:`bool <python:bool>`)

        """
        return self._supports_json

    @supports_json.setter
    def supports_json(self, value):
        value = bool_to_tuple(value)
        self._supports_json = value

    @property
    def supports_yaml(self):
        """Indicates whether the attribute can be serialized / de-serialized to YAML.

        :returns: 2-member :class:`tuple <python:tuple>` (inbound de-serialization /
          outbound serialization)
        :rtype: :class:`tuple <python:tuple>` of form (:class:`bool <python:bool>`,
          :class:`bool <python:bool>`)

        """
        return self._supports_yaml

    @supports_yaml.setter
    def supports_yaml(self, value):
        value = bool_to_tuple(value)
        self._supports_yaml = value

    @property
    def supports_dict(self):
        """Indicates whether the attribute can be serialized / de-serialized to
        :class:`dict <python:dict>`.

        :returns: 2-member :class:`tuple <python:tuple>` (inbound de-serialization /
          outbound serialization)
        :rtype: :class:`tuple <python:tuple>` of form (:class:`bool <python:bool>`,
          :class:`bool <python:bool>`)

        """
        return self._supports_dict

    @supports_dict.setter
    def supports_dict(self, value):
        value = bool_to_tuple(value)
        self._supports_dict = value

    @property
    def on_serialize(self):
        """A function that will be called when attempting to serialize a value from
        the attribute.

        If :obj:`None <python:None>`, the data type's default ``on_serialize``  function will be
        called instead.

        .. tip::

          If you need to execute different ``on_serialize`` functions for
          different formats, you can also supply a :class:`dict <python:dict>`:

          .. code-block:: python

            on_serialize = {
                'csv': csv_on_serialize_callable,
                'json': json_on_serialize_callable,
                'yaml': yaml_on_serialize_callable,
                'dict': dict_on_serialize_callable
            }

        Defaults to :obj:`None <python:None>`.

        :rtype: callable / :class:`dict <python:dict>` with formats
          as keys and values as callables
        """
        return self._on_serialize

    @on_serialize.setter
    def on_serialize(self, value):
        value = callable_to_dict(value)

        for key in value:
            item = value[key]
            if item is not None and not checkers.is_callable(item):
                raise SQLAthanorError('on_serialize for %s must be callable' % key)

        self._on_serialize = value

    @property
    def on_deserialize(self):
        """A function that will be called when attempting to assign a de-serialized
        value to the attribute.

        This is intended to either coerce the value being assigned to a form that
        is acceptable by the attribute, or raise an exception if it cannot be coerced.

        If :obj:`None <python:None>`, the data type's default ``on_deserialize`` function will
        be called instead.

        .. tip::

          If you need to execute different ``on_deserialize`` functions for
          different formats, you can also supply a :class:`dict <python:dict>`:

          .. code-block:: python

            on_deserialize = {
                'csv': csv_on_deserialize_callable,
                'json': json_on_deserialize_callable,
                'yaml': yaml_on_deserialize_callable,
                'dict': dict_on_deserialize_callable
            }

          Defaults to :obj:`None <python:None>`.

        :rtype: callable / :class:`dict <python:dict>` with formats
          as keys and values as callables
        """
        return self._on_deserialize

    @on_deserialize.setter
    def on_deserialize(self, value):
        value = callable_to_dict(value)

        for key in value:
            item = value[key]
            if item is not None and not checkers.is_callable(item):
                raise SQLAthanorError('on_deserialize for %s must be callable' % key)

        self._on_deserialize = value

    @property
    def display_name(self):
        """The property name to apply when serializing the attribute or to expect when
        de-serializing.

        .. note::

          If :obj:`None <python:None>`, will default to the attribute name in the Python
          model class.

        :rtype: :class:`str <python:str>` / :obj:`None <python:None>`.
        """
        return self._display_name

    @display_name.setter
    def display_name(self, value):
        value = validators.string(value, allow_empty = True)
        self._display_name = value
