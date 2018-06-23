# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.state import InstanceState
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.util import symbol, OrderedProperties

from validator_collection import checkers

from sqlathanor.attributes import AttributeConfiguration, validate_serialization_config
from sqlathanor.utilities import bool_to_tuple

# pylint: disable=no-member

class BaseModel(object):
    """Base class that establishes shared methods, attributes,and properties."""

    __csv_support__ = []
    __json_support__ = []
    __yaml_support__ = []
    __dict_support__ = []

    def __init__(self, *args, **kwargs):
        if self.__csv_support__:
            self.__csv_support__ = validate_serialization_config(self.__csv_support__)
        else:
            self.__csv_support__ = []

        if self.__json_support__:
            self.__json_support__ = validate_serialization_config(self.__json_support__)
        else:
            self.__json_support__ = []

        if self.__yaml_support__:
            self.__yaml_support__ = validate_serialization_config(self.__yaml_support__)
        else:
            self.__yaml_support__ = []

        if self.__dict_support__:
            self.__dict_support__ = validate_serialization_config(self.__dict_support__)
        else:
            self.__dict_support__ = []

        super(BaseModel, self).__init__(*args, **kwargs)

    @classmethod
    def get_primary_key_columns(cls):
        """Retrieve the model's primary key columns.

        :returns: :ref:`list <python:list>` of
          :ref:`Column <sqlalchemy:sqlalchemy.Column>` objects corresponding to
          the table's primary key(s).
        :rtype: :ref:`list <python:list>` of :ref:`Column <sqlalchemy:sqlalchemy.Column>`

        """
        return inspect(cls).primary_key

    @classmethod
    def get_primary_key_column_names(cls):
        """Retrieve the column names for the model's primary key columns.

        :rtype: :ref:`list <python:list>` of :ref:`str <python:str>`
        """
        return [x.name for x in cls.get_primary_key_columns()]

    @property
    def primary_key_value(self):
        """The instance's primary key.

        .. note::

          If not :class:`None`, this value can always be passed to
          :ref:`Query.get() <sqlalchemy:sqlalchemy.orm.query.Query.get>`.

        .. warning::

          Returns :class:`None` if the instance is pending, in a transient state, or
          does not have a primary key.

        :returns: scalar or :ref:`tuple <python:tuple>` value representing the
          primary key. For a composite primary key, the order of identifiers
          corresponds to the order with which the model's primary keys were
          defined.

          If no primary keys are available, will return :class:`None`.
        :rtype: scalar / :ref:`tuple <python:tuple>` / :class:`None`

        """
        if not inspect(self).has_identity or not inspect(self).identity:
            return None

        primary_keys = inspect(self).identity

        if len(primary_keys) == 1:
            return primary_keys[0]

        return primary_keys

    @classmethod
    def _get_instance_attributes(cls,
                                 read_only = None,
                                 include_private = False,
                                 exclude_methods = True):
        """Retrieve the names of the model's attributes and methods.

        :param read_only: If :class:`None`, returns all attributes. If ``True``,
          returns only read-only properties. If ``False``, does not return any read-only
          properties. Defaults to :class:`None`.
        :type read_only: :ref:`bool <python:bool>` / :class:`None`

        :param include_private: If ``True``, includes properties whose names start
          with an underscore. Defaults to ``False``.
        :type include_private: :ref:`bool <python:bool>`

        :param exclude_methods: If ``True``, excludes attributes that correspond to
          methods (are callable). Defaults to ``True``.
        :type exclude_methods: :ref:`bool <python:bool>`

        .. note::

          This method will return all attributes, properties, and methods supported
          by the model - whether they map to database columns or not.

        :returns: An iterable of attribute names defined for the model.
        :rtype: :ref:`list <python:list>` of :ref:`str <python:str>`

        """
        base_attributes = dir(cls)
        instance_attributes = []
        for key in base_attributes:
            if key.startswith('_') and not key.startswith('__') and not include_private:
                continue

            item = getattr(cls, key)
            if checkers.is_callable(item) and exclude_methods:
                continue

            if isinstance(item, property):
                if read_only and item.fset is not None:
                    continue

                if read_only is False and item.fset is None:
                    continue

            elif read_only is not None:
                continue

            instance_attributes.append(key)

        return instance_attributes

    @classmethod
    def _get_declarative_serializable_attributes(cls,
                                                 supports_dict = True,
                                                 supports_json = True,
                                                 supports_csv = True,
                                                 supports_yaml = True,
                                                 exclude_private = True):
        """Retrieve a list of model attribute names (Python attributes) whose values
        can be serialized to a database, to JSON, CSV, etc. based on their attribute
        declarations.

        .. note::

          This method operates *solely* on attributes that have been delcared,
          ignoring any configuration provided in the ``__<format>_support__``
          attribute.

        :param supports_dict: If ``True``, includes attribute names that can be
          serialized to a :ref:`dict <python:dict>`. Defaults to ``True``.
        :type supports_dict: :ref:`bool <python:bool>`

        :param supports_json: If ``True``, includes attribute names that can be
          serialized to :term:`JSON`. Defaults to ``True``.
        :type supports_json: :ref:`bool <python:bool>`

        :param supports_csv: If ``True``, includes attribute names that can be
          serialized to :term:`CSV`. Defaults to ``True``.
        :type supports_csv: :ref:`bool <python:bool>`

        :param supports_yaml: If ``True``, includes attribute names that can be
          serialized to :term:`YAML`. Defaults to ``True``.
        :type supports_yaml: :ref:`bool <python:bool>`

        :param exclude_private: If ``True``, will exclude private attributes whose
          names begin with a single underscore. Defaults to ``True``.
        :type exclude_private: :ref:`bool <python:bool>`

        :returns: List of model attribute names that can be serialized.
        :rtype: :ref:`list <python:list>` of :ref:`str <python:str>`
        """
        include_private = not exclude_private

        instance_attributes = cls._get_instance_attributes(
            include_private = include_private,
            exclude_methods = True
        )

        if supports_csv is not None:
            supports_csv = bool_to_tuple(supports_csv)
        if supports_json is not None:
            supports_json = bool_to_tuple(supports_json)
        if supports_yaml is not None:
            supports_yaml = bool_to_tuple(supports_yaml)
        if supports_dict is not None:
            supports_dict = bool_to_tuple(supports_dict)

        attributes = []
        for key in instance_attributes:
            value = getattr(cls, key)
            config = AttributeConfiguration(attribute = value)
            config.name = key
            if supports_csv is not None and config.supports_csv == supports_csv:
                attributes.append(config)
                continue

            if supports_json is not None and config.supports_json == supports_json:
                attributes.append(config)
                continue

            if supports_yaml is not None and config.supports_yaml == supports_yaml:
                attributes.append(config)
                continue

            if supports_dict is not None and config.supports_dict == supports_dict:
                attributes.append(config)
                continue

        return attributes

    @classmethod
    def _get_meta_serializable_attributes(cls,
                                          supports_dict = None,
                                          supports_json = None,
                                          supports_csv = None,
                                          supports_yaml = None):
        """Retrieve a list of model attribute names (Python attributes) whose values
        can be serialized to a database, to JSON, CSV, etc. based on the contents
        of the meta declaration in ``__<format>_support__``.

        .. note::

          This method operates *solely* on attributes that have been provided in
          the ``__<format>_support__`` meta attribute.

        :param supports_dict: If ``True``, includes attribute names that can be
          serialized to a :ref:`dict <python:dict>`. Defaults to :class:`None`
        :type supports_dict: :ref:`bool <python:bool>` / 2-member
          :ref:`tuple <python:tuple>` of form (:ref:`bool <python:bool>`,
          :ref:`bool <python:bool>`) / :class:`None`

        :param supports_json: If ``True``, includes attribute names that can be
          serialized to :term:`JSON`. Defaults to ``True``.
        :type supports_json: :ref:`bool <python:bool>`

        :param supports_csv: If ``True``, includes attribute names that can be
          serialized to :term:`CSV`. Defaults to ``True``.
        :type supports_csv: :ref:`bool <python:bool>`

        :param supports_yaml: If ``True``, includes attribute names that can be
          serialized to :term:`YAML`. Defaults to ``True``.
        :type supports_yaml: :ref:`bool <python:bool>`

        :returns: List of model attribute names that can be serialized.
        :rtype: :ref:`list <python:list>` of :ref:`str <python:str>`
        """
        if supports_csv is not None:
            supports_csv = bool_to_tuple(supports_csv)
        if supports_json is not None:
            supports_json = bool_to_tuple(supports_json)
        if supports_yaml is not None:
            supports_yaml = bool_to_tuple(supports_yaml)
        if supports_dict is not None:
            supports_dict = bool_to_tuple(supports_dict)

        attributes = []
        if supports_csv is not None:
            attributes.extend([x for x in cls.__csv_support__
                               if x.supports_csv == supports_csv
                              ])
        if supports_json is not None:
            attributes.extend([x for x in cls.__json_support__
                               if x.supports_json == supports_json
                              ])
        if supports_yaml is not None:
            attributes.extend([x for x in cls.__yaml_support__
                               if x.supports_yaml == supports_yaml
                              ])
        if supports_dict is not None:
            attributes.extend([x for x in cls.__dict_support__
                               if x.supports_dict == supports_dict
                              ])

        return attributes

    @classmethod
    def get_serialization_config(cls,
                                 supports_csv = True,
                                 supports_json = True,
                                 supports_yaml = True,
                                 supports_dict = True,
                                 exclude_private = True):
        """Retrieve attributes for a given serialization/de-serialization configuration.

        :rtype: :ref:`list <python:list>` of :class:`AttributeConfiguration` objects

        """
        declarative_attributes = cls._get_declarative_serializable_attributes(
            supports_csv = supports_csv,
            supports_json = supports_json,
            supports_yaml = supports_yaml,
            supports_dict = supports_dict,
            exclude_private = exclude_private
        )
        meta_attributes = cls._get_meta_serializable_attributes(
            supports_csv = supports_csv,
            supports_json = supports_json,
            supports_yaml = supports_yaml,
            supports_dict = supports_dict
        )
        attributes = [x for x in declarative_attributes]
        attributes.extend([x for x in meta_attributes
                           if x not in attributes])

        return attributes

    @classmethod
    def get_csv_serialization_config(cls, deserialize = True, serialize = True):
        """Retrieve the CSV column names that apply for this object.

        :returns: Ordered list of CSV column names that apply for this object.
        :rtype: :ref:`list <python:list>` of :ref:`str <python:str>`
        """
        supports_csv = bool_to_tuple((deserialize, serialize))
        return sorted([x
                       for x in cls.get_serialization_config(supports_csv = supports_csv,
                                                             supports_json = None,
                                                             supports_yaml = None,
                                                             supports_dict = None)],
                      key = lambda x: x.csv_sequence)

    @classmethod
    def get_json_serialization_config(cls, deserialize = True, serialize = True):
        """Retrieve the JSON serialization configurations that apply for this object.

        :returns: Ordered list of JSON keys that apply for this object.
        :rtype: :ref:`list <python:list>` of :class:`AttributeConfiguration`
        """
        supports_json = bool_to_tuple((deserialize, serialize))
        return [x for x in cls.get_serialization_config(supports_csv = None,
                                                        supports_json = supports_json,
                                                        supports_yaml = None,
                                                        supports_dict = None)]

    @classmethod
    def get_yaml_serialization_config(cls, deserialize = True, serialize = True):
        """Retrieve the JSON serialization configurations that apply for this object.

        :returns: Ordered list of YAML keys that apply for this object.
        :rtype: :ref:`list <python:list>` of :class:`AttributeConfiguration`
        """
        supports_yaml = bool_to_tuple((deserialize, serialize))
        return [x for x in cls.get_serialization_config(supports_csv = None,
                                                        supports_json = None,
                                                        supports_yaml = supports_yaml,
                                                        supports_dict = None)]

    @classmethod
    def get_dict_serialization_config(cls, deserialize = True, serialize = True):
        """Retrieve the :ref:`dict <python:dict>` serialization configurations that
        apply for this object.

        :returns: Ordered list of :ref:`dict <python:dict>` keys that apply for
          this object.
        :rtype: :ref:`list <python:list>` of :class:`AttributeConfiguration`
        """
        supports_dict = bool_to_tuple((deserialize, serialize))
        return [x for x in cls.get_serialization_config(supports_csv = None,
                                                        supports_json = None,
                                                        supports_yaml = None,
                                                        supports_dict = supports_dict)]

    @classmethod
    def attribute_serialization_config(cls,
                                       attribute,
                                       supports_csv = None,
                                       supports_json = None,
                                       supports_yaml = None,
                                       supports_dict = None):
        """Retrieve the :class:`AttributeConfiguration` for ``attribute``.

        :param attribute: The attribute/column name whose serialization
          configuration should be returned.
        :type attribute: :ref:`str <python:str>`

        """
        config = cls.get_serialization_config(supports_csv = supports_csv,
                                              supports_json = supports_json,
                                              supports_yaml = supports_yaml,
                                              supports_dict = supports_dict)
        for item in config:
            if item.name == attribute:
                return item

        return None

    @classmethod
    def does_support_serialization(cls,
                                   attribute,
                                   supports_csv = None,
                                   supports_json = None,
                                   supports_yaml = None,
                                   supports_dict = None):
        """Indicate whether ``attribute`` supports serialization/deserializtion.

        :returns: ``True`` if the serialization support matches. ``False`` if not.
        :rtype: :ref:`bool <python:bool>`
        """
        config = cls.attribute_serialization_config(attribute,
                                                    supports_csv = supports_csv,
                                                    supports_json = supports_json,
                                                    supports_yaml = supports_yaml,
                                                    supports_dict = supports_dict)
        return config is not None

    @classmethod
    def get_csv_column_names(cls, deserialize = True, serialize = True):
        """Retrieve a list of CSV column names.

        :param deserialize: If ``True``, returns columns that support
          :term:`deserialization`. If ``False``, returns columns that do *not*
          support deserialization. If :class:`None`, does not take
          deserialization into account. Defaults to ``True``.
        :type deserialize: :ref:`bool <python:bool>`

        :param serialize: If ``True``, returns columns that support
          :term:`serialization`. If ``False``, returns columns that do *not*
          support serialization. If :class:`None`, does not take
          serialization into account. Defaults to ``True``.
        :type serialize: :ref:`bool <python:bool>`

        :returns: List of CSV column names, sorted according to their configuration.
        :rtype: :ref:`list <python:list>` of :ref:`str <python:str>`
        """
        config = cls.get_csv_serialization_config(deserialize = deserialize,
                                                  serialize = serialize)
        return [x.name for x in config]

    @classmethod
    def get_csv_header(cls,
                       deserialize = True,
                       serialize = True,
                       delimiter = '|'):
        """Retrieve a header string for a CSV representation of the model.

        :param delimiter: The character(s) to utilize between columns. Defaults to
          a pipe (``|``).
        :type delimiter: :ref:`str <python:str>`

        :returns: A string ending in ``\n`` with the model's CSV column names
          listed, separated by the ``delimiter``.
        :rtype: :ref:`str <python:str>`
        """
        column_names = cls.get_csv_column_names(deserialize = deserialize,
                                                serialize = serialize)
        header_string = delimiter.join(column_names) + '\n'

        return header_string

    def get_csv_data(self,
                     delimiter = '|',
                     wrap_all_strings = False,
                     wrap_empty_values = True,
                     wrapper_character = "'"):
        """Return the CSV representation of the model instance (record).

        :param delimiter: The character(s) to place between columns. Defaults to
          a pipe ('|').
        :type delimiter: :ref:`str <python:str>`

        :param wrap_all_strings: If ``True``, will wrap all string values in the
          ``wrapper_character``. Defaults to ``False``.
        :type wrap_all_strings: :ref:`bool <python:bool>`

        :param wrap_empty_values: If ``True``, will wrap empty values with the
          ``wrapper_character``. Defaults to ``True``.

          .. note::

            This solves an issue in Microsoft Excel where an empty value in the
            last column of a CSV record will now be recognized as a valid value.

        :type wrap_empty_values: :ref:`bool <python:bool>`

        :param wrapper_character: The character to use as a wrapper if a column
          value needs to be wrapped. Defaults to a single quote (``'``).
        :type wrapper_character: :ref:`str <python:str>`

        :returns: The CSV representation of the model instance (record).
        :rtype: :ref:`str <python: str>`
        """
        if not wrapper_character:
            wrapper_character = '\''

        csv_column_names = self.get_csv_column_names(deserialize = None,
                                                     serialize = True)

        data = [getattr(self, x, '') for x in csv_column_names if hasattr(self, x)]

        for index, item in enumerate(data):
            if item == 'None' or item is None:
                if wrap_empty_values:
                    data[index] = wrapper_character + str(item) + wrapper_character
                else:
                    data[index] = ''
            elif checkers.is_string(item) and wrap_all_strings:
                data[index] = wrapper_character + item + wrapper_character

        data_row = delimiter.join(data) + '\n'

        return data_row

    def to_csv(self,
               include_header = False,
               delimiter = '|',
               wrap_all_strings = False,
               wrap_empty_values = True,
               wrapper_character = "'"):
        """Retrieve a CSv string with the object's data.

        :param include_header: If ``True``, will include a header row with column
          labels. If ``False``, will not include a header row. Defaults to ``True``.
        :type include_header: :ref:`bool <python:bool>`

        :returns: Data from the object in CSV (pipe-delimited) format.
        :rtype: :ref:`str <python:str>`
        """
        if include_header is True:
            return self.get_csv_header(delimiter = delimiter) + \
                   self.get_csv_data(delimiter = delimiter,
                                     wrap_all_strings = wrap_all_strings,
                                     wrap_empty_values = wrap_empty_values,
                                     wrapper_character = wrapper_character)

        return self.get_csv_data(delimiter = delimiter,
                                 wrap_all_strings = wrap_all_strings,
                                 wrap_empty_values = wrap_empty_values,
                                 wrapper_character = wrapper_character)

    def to_dict(self,
                max_nesting = 0,
                current_nesting = 0):
        """Return a :ref:`dict <python:dict>` representation of the object.

        :param max_nesting: The maximum number of levels that the resulting
          :ref:`dict <python:dict>` object can be nested. If set to ``0``, will
          not nest other serializable objects. Defaults to ``0``.
        :type max_nesting: :ref:`int <python:int>`

        :param current_nesting: The current nesting level at which the
          :ref:`dict <python:dict>` representation will reside. Defaults to ``0``.
        :type current_nesting: :ref:`int <python:int>`

        :returns: A :ref:`dict <python:dict>` representation of the object.
        :rtype: :ref:`dict <python:dict>`
        """
        dict_object = {}

        dict_attributes = self.get_dict_attribute_names()

        for key in dict_attributes:
            item = getattr(self, key, None)

            try:
                getattr(item, 'to_dict')
                has_attribute = True
            except AttributeError:
                has_attribute = False

            if has_attribute and current_nesting < max_nesting:
                item = item.to_dict(max_nesting = max_nesting,
                                    current_nesting = current_nesting + 1)

            dict_object[key] = item

        return dict_object

BaseModel = declarative_base(cls = BaseModel)
