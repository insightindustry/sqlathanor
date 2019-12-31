# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

from sqlalchemy.orm.attributes import QueryableAttribute as SA_QueryableAttribute
from sqlalchemy import util

from validator_collection import validators, checkers

from sqlathanor._serialization_support import SerializationMixin
from sqlathanor.utilities import bool_to_tuple, callable_to_dict


BLANK_ON_SERIALIZE = {
    'csv': None,
    'json': None,
    'yaml': None,
    'dict': None
}


class AttributeConfiguration(SerializationMixin):
    """Serialization/de-serialization configuration of a :term:`model attribute`.
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self,
                 *args,
                 **kwargs):
        """Construct an :class:`AttributeConfiguration` object.

        :param name: The name of the attribute. Defaults to ``None``.
        :type name: :class:`str <python:str>`

        :param supports_csv: Determines whether the column can be serialized to or
          de-serialized from CSV format.

          If ``True``, can be serialized to CSV and de-serialized from CSV. If
          ``False``, will not be included when serialized to CSV and will be ignored
          if present in a de-serialized CSV.

          Can also accept a 2-member :class:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``, which means the column will not be serialized to CSV
          or de-serialized from CSV.

        :type supports_csv: :class:`bool <python:bool>` / :class:`tuple <python:tuple>` of
          form (inbound: :class:`bool <python:bool>`, outbound: :class:`bool <python:bool>`)

        :param supports_json: Determines whether the column can be serialized to or
          de-serialized from JSON format.

          If ``True``, can be serialized to JSON and de-serialized from JSON.
          If ``False``, will not be included when serialized to JSON and will be
          ignored if present in a de-serialized JSON.

          Can also accept a 2-member :class:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``, which means the column will not be serialized to JSON
          or de-serialized from JSON.

        :type supports_json: :class:`bool <python:bool>` / :class:`tuple <python:tuple>` of
          form (inbound: :class:`bool <python:bool>`, outbound: :class:`bool <python:bool>`)

        :param supports_yaml: Determines whether the column can be serialized to or
          de-serialized from YAML format.

          If ``True``, can be serialized to YAML and de-serialized from YAML.
          If ``False``, will not be included when serialized to YAML and will be
          ignored if present in a de-serialized YAML.

          Can also accept a 2-member :class:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``, which means the column will not be serialized to YAML
          or de-serialized from YAML.

        :type supports_yaml: :class:`bool <python:bool>` / :class:`tuple <python:tuple>` of
          form (inbound: :class:`bool <python:bool>`, outbound: :class:`bool <python:bool>`)

        :param supports_dict: Determines whether the column can be serialized to or
          de-serialized to a Python :class:`dict <python:dict>`.

          If ``True``, can be serialized to :class:`dict <python:dict>` and de-serialized
          from a :class:`dict <python:dict>`. If ``False``, will not be included
          when serialized to :class:`dict <python:dict>` and will be ignored if
          present in a de-serialized :class:`dict <python:dict>`.

          Can also accept a 2-member :class:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``, which means the column will not be serialized to a
          :class:`dict <python:dict>` or de-serialized from a :class:`dict <python:dict>`.

        :type supports_dict: :class:`bool <python:bool>` / :class:`tuple <python:tuple>` of
          form (inbound: :class:`bool <python:bool>`, outbound: :class:`bool <python:bool>`)

        :param on_deserialize: A function that will be called when attempting to
          assign a de-serialized value to the column. This is intended to either coerce
          the value being assigned to a form that is acceptable by the column, or
          raise an exception if it cannot be coerced. If :obj:`None <python:None>`, the data
          type's default ``on_deserialize`` function will be called instead.

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

        :type on_deserialize: callable / :class:`dict <python:dict>` with formats
          as keys and values as callables

        :param on_serialize: A function that will be called when attempting to
          serialize a value from the column. If :obj:`None <python:None>`, the data
          type's default ``on_serialize`` function will be called instead.

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

        :type on_serialize: callable / :class:`dict <python:dict>` with formats
          as keys and values as callables

        :param csv_sequence: Indicates the numbered position that the column should be in
          in a valid CSV-version of the object. Defaults to :obj:`None <python:None>`.

          .. note::

            If not specified, the column will go after any columns that *do* have a
            ``csv_sequence`` assigned, sorted alphabetically.

            If two columns have the same ``csv_sequence``, they will be sorted
            alphabetically.

        :type csv_sequence: :class:`int <python:int>` / :obj:`None <python:None>`

        :param attribute: The object representation of an attribute. Supplying this
          value overrides any other configuration options supplied. Defaults to
          :obj:`None <python:None>`.
        :type attribute: class attribute

        :param display_name: An optional name to use or expect in place of `name` when
          serializing or de-serializing the attribute. If :obj:`None <python:None>`, the
          attribute will default to the same name as in its Python model class and as
          provided in ``name``. Defaults to :obj:`None <python:None>`
        :type display_name: :class:`str <python:str>` / :obj:`None <python:None>`

        """
        object.__setattr__(self, '_dict_proxy', {})
        self._current = -1
        self._name = None
        self.name = kwargs.pop('name', None)
        attribute = kwargs.pop('attribute', None)

        super(AttributeConfiguration, self).__init__(*args, **kwargs)

        if attribute is not None:
            try:
                self.name = attribute.__name__
            except AttributeError:
                self.name = None
            try:
                self.supports_csv = attribute.supports_csv
                self.csv_sequence = attribute.csv_sequence
                self.supports_json = attribute.supports_json
                self.supports_yaml = attribute.supports_yaml
                self.supports_dict = attribute.supports_dict
                self.on_serialize = attribute.on_serialize
                self.on_deserialize = attribute.on_deserialize
                self.display_name = attribute.display_name
            except AttributeError:
                pass

        self._dict_proxy = dict(**kwargs)

    def __repr__(self):
        repr_string = 'AttributeConfiguration('
        repr_string += 'name = %s, ' % str(self.name)
        repr_string += 'supports_csv = %s, ' % str(self.supports_csv)
        repr_string += 'supports_json = %s, ' % str(self.supports_json)
        repr_string += 'supports_yaml = %s, ' % str(self.supports_yaml)
        repr_string += 'supports_dict = %s, ' % str(self.supports_dict)
        repr_string += 'csv_sequence = %s, ' % str(self.csv_sequence)
        repr_string += 'on_serialize = %s, ' % str(self.on_serialize)
        repr_string += 'on_deserialize = %s, ' % str(self.on_deserialize)
        repr_string += 'display_name = %s)' % str(self.display_name)

        return repr_string

    def __str__(self):
        return 'AttributeConfiguration(name = %s)' % self.name

    def __bool__(self):
        return True

    def __nonzero__(self):
        return self.__bool__()

    def __eq__(self, other):
        return isinstance(self, type(other)) and self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getitem__(self, key):
        if key in ['name',
                   'supports_csv',
                   'supports_json',
                   'supports_yaml',
                   'supports_dict',
                   'csv_sequence',
                   'on_serialize',
                   'on_deserialize',
                   'display_name']:
            return getattr(self, key)

        return self._dict_proxy[key]

    def __missing__(self, key):
        raise KeyError(key)

    def __setitem__(self, key, value):
        if key in ['name',
                   'supports_csv',
                   'supports_json',
                   'supports_yaml',
                   'supports_dict',
                   'csv_sequence',
                   'on_serialize',
                   'on_deserialize',
                   'display_name']:
            setattr(self, key, value)
        else:
            self._dict_proxy[key] = value

    def __delitem__(self, key):
        if key in ['name',
                   'csv_sequence',
                   'on_serialize',
                   'on_deserialize',
                   'display_name']:
            setattr(self, key, None)
        elif key in ['supports_csv',
                     'supports_json',
                     'supports_yaml',
                     'supports_dict']:
            setattr(self, key, (False, False))
        else:
            self._dict_proxy.__delitem__(key)

    def __getattr__(self, name):
        try:
            return self._dict_proxy[name]
        except KeyError as error:
            try:
                return self._dict_proxy.get(name)
            except AttributeError:
                raise error

    def __contains__(self, item):
        if item in ['name',
                    'supports_csv',
                    'supports_json',
                    'supports_yaml',
                    'supports_dict',
                    'csv_sequence',
                    'on_serialize',
                    'on_deserialize',
                    'display_name']:
            return True

        return item in self._dict_proxy

    def __len__(self):
        return 9 + len(self._dict_proxy)

    def __iter__(self):
        return self

    def next(self):
        if self._current >= (len(self) - 1):
            self._current = -1
            raise StopIteration()

        self._current += 1
        return self.keys()[self._current]

    def __next__(self):
        return self.next()

    def clear(self):
        self._current = 0
        self.name = None
        self.supports_csv = (False, False)
        self.csv_sequence = None
        self.supports_json = (False, False)
        self.supports_yaml = (False, False)
        self.supports_dict = (False, False)
        self.on_serialize = BLANK_ON_SERIALIZE
        self.on_deserialize = BLANK_ON_SERIALIZE
        self.display_name = None
        self._dict_proxy = {}

    @classmethod
    def fromkeys(cls, seq, value = None):
        """Create a new :class:`AttributeConfiguration` with keys in ``seq`` and
        values in ``value``.

        :param seq: Iterable of keys
        :type seq: iterable

        :param value: Iterable of values
        :type value: iterable

        :rtype: :class:`AttributeConfiguration`

        """
        return cls(zip(seq, value))

    def get(self, key, default = None):
        return self[key] or default

    def keys(self):
        return_value = ['name',
                        'supports_csv',
                        'supports_json',
                        'supports_yaml',
                        'supports_dict',
                        'csv_sequence',
                        'on_serialize',
                        'on_deserialize',
                        'display_name']
        return_value.extend(sorted(self._dict_proxy.keys()))
        return return_value

    def pop(self, key, default = None):
        if key not in self:
            raise KeyError(key)

        return_value = self[key] or default
        if key in ['name',
                   'csv_sequence',
                   'display_name']:
            self[key] = None
        elif key in ['on_serialize',
                     'on_deserialize']:
            self[key] = BLANK_ON_SERIALIZE
        elif key in ['supports_csv',
                     'supports_json',
                     'supports_yaml',
                     'supports_dict']:
            self[key] = (False, False)
        else:
            return_value = self._dict_proxy.pop(key, default = default)

        return return_value

    def values(self):
        return [self[x] for x in self.keys()]

    def items(self):
        return [(x, self[x]) for x in self.keys()]

    @property
    def name(self):
        """The name of the attribute.

        :rtype: :class:`str <python:str>` / :obj:`None <python:None>`
        """
        return self._name

    @name.setter
    def name(self, value):
        value = validators.string(value, allow_empty = True)
        self._name = value

    @classmethod
    def from_attribute(cls, attribute):
        """Return an instance of :class:`AttributeConfiguration` configured for a
        given attribute.

        """
        return cls(attribute = attribute)

    def copy(self):
        new_instance = self.__class__()
        new_instance.name = self.name
        new_instance.supports_csv = self.supports_csv
        new_instance.csv_sequence = self.csv_sequence
        new_instance.supports_json = self.supports_json
        new_instance.supports_yaml = self.supports_yaml
        new_instance.supports_dict = self.supports_dict
        new_instance.on_serialize = self.on_serialize
        new_instance.on_deserialize = self.on_deserialize
        new_instance.display_name = self.display_name

        return new_instance


def validate_serialization_config(config):
    """Validate that ``config`` contains :class:`AttributeConfiguration` objects.

    :param config: Object or iterable of objects that represent
      :class:`AttributeConfigurations <AttributeConfiguration>`
    :type config: iterable of :class:`AttributeConfiguration` objects / iterable of
      :class:`dict <python:dict>` objects corresponding to a
      :class:`AttributeConfiguration` / :class:`AttributeConfiguration` /
      :class:`dict <python:dict>` object corresponding to a :class:`AttributeConfiguration`

    :rtype: :class:`list <python:list>` of :class:`AttributeConfiguration` objects
    """
    if config and not checkers.is_iterable(config,
                                           forbid_literals = (str,
                                                              bytes,
                                                              dict,
                                                              AttributeConfiguration)):
        config = [config]

    if not config:
        return []

    return_value = []
    for item in config:
        if isinstance(item, AttributeConfiguration) and item not in return_value:
            return_value.append(item)
        elif isinstance(item, dict):
            item = AttributeConfiguration(**item)
            if item not in return_value:
                return_value.append(item)

    return return_value
