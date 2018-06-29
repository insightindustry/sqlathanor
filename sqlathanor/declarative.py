# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

import csv
import inspect as inspect_
import warnings

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.state import InstanceState
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.util import symbol, OrderedProperties
from sqlalchemy.ext.hybrid import hybrid_property

import yaml

from validator_collection import checkers, validators
from validator_collection.errors import NotAnIterableError

from sqlathanor._compat import StringIO, json
from sqlathanor.attributes import AttributeConfiguration, validate_serialization_config
from sqlathanor.utilities import format_to_tuple, iterable__to_dict
from sqlathanor.errors import ValueSerializationError, ValueDeserializationError, \
    UnsupportedSerializationError, UnsupportedDeserializationError, DeserializationError,\
    CSVColumnError, MaximumNestingExceededError, MaximumNestingExceededWarning, \
    SerializableAttributeError, InvalidFormatError
from sqlathanor.default_serializers import get_default_serializer
from sqlathanor.default_deserializers import get_default_deserializer

# pylint: disable=no-member

class BaseModel(object):
    """Base class that establishes shared methods, attributes,and properties."""

    __serialization__ = []

    def __init__(self, *args, **kwargs):
        if self.__serialization__:
            self.__serialization__ = validate_serialization_config(self.__serialization__)
        else:
            self.__serialization__ = []

        super(BaseModel, self).__init__(*args, **kwargs)

    def _check_is_model_instance(self):
        return True

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
                                 include_private = False,
                                 exclude_methods = True):
        """Retrieve the names of the model's attributes and methods.

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
            if key.startswith('__'):
                continue

            if key.startswith('_') and not key.startswith('__') and not include_private:
                continue

            item = getattr(cls, key)
            if checkers.is_callable(item) and exclude_methods:
                continue

            instance_attributes.append(key)

        return instance_attributes

    @classmethod
    def _get_declarative_serializable_attributes(cls,
                                                 from_csv = None,
                                                 to_csv = None,
                                                 from_json = None,
                                                 to_json = None,
                                                 from_yaml = None,
                                                 to_yaml = None,
                                                 from_dict = None,
                                                 to_dict = None,
                                                 exclude_private = True):
        """Retrieve a list of :class:`AttributeConfiguration` objects corresponding
        to attributes whose values can be serialized from/to CSV, JSON, YAML, etc.

        .. note::

          This method operates *solely* on attribute configurations that have been
          declared, ignoring any configuration provided in the ``__<format>_support__``
          attribute.

        :param from_csv: If ``True``, includes attribute names that **can** be
          de-serialized from CSV strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from CSV strings. If :class:`None`,
          will not include attributes based on CSV de-serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type from_csv: :ref:`bool <python:bool>` / :class:`None`

        :param to_csv: If ``True``, includes attribute names that **can** be
          serialized to CSV strings. If ``False``, includes attribute names
          that **cannot** be serialized to CSV strings. If :class:`None`,
          will not include attributes based on CSV serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type to_csv: :ref:`bool <python:bool>` / :class:`None`

        :param from_json: If ``True``, includes attribute names that **can** be
          de-serialized from JSON strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from JSON strings. If :class:`None`,
          will not include attributes based on JSON de-serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type from_json: :ref:`bool <python:bool>` / :class:`None`

        :param to_json: If ``True``, includes attribute names that **can** be
          serialized to JSON strings. If ``False``, includes attribute names
          that **cannot** be serialized to JSON strings. If :class:`None`,
          will not include attributes based on JSON serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type to_json: :ref:`bool <python:bool>` / :class:`None`

        :param from_yaml: If ``True``, includes attribute names that **can** be
          de-serialized from YAML strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from YAML strings. If :class:`None`,
          will not include attributes based on YAML de-serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type from_yaml: :ref:`bool <python:bool>` / :class:`None`

        :param to_yaml: If ``True``, includes attribute names that **can** be
          serialized to YAML strings. If ``False``, includes attribute names
          that **cannot** be serialized to YAML strings. If :class:`None`,
          will not include attributes based on YAML serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type to_yaml: :ref:`bool <python:bool>` / :class:`None`

        :param from_dict: If ``True``, includes attribute names that **can** be
          de-serialized from :ref:`dict <python:dict>` objects. If ``False``, includes
          attribute names that **cannot** be de-serialized from :ref:`dict <python:dict>`
          objects. If :class:`None`, will not include attributes based on
          :ref:`dict <python:dict> de-serialization support (but may include them
          based on other parameters). Defaults to :class:`None`.
        :type from_dict: :ref:`bool <python:bool>` / :class:`None`

        :param to_dict: If ``True``, includes attribute names that **can** be
          serialized to :ref:`dict <python:dict>` objects. If ``False``, includes
          attribute names that **cannot** be serialized to :ref:`dict <python:dict>`
          objects. If :class:`None`, will not include attributes based on
          :ref:`dict <python:dict> serialization support (but may include them
          based on other parameters). Defaults to :class:`None`.
        :type from_dict: :ref:`bool <python:bool>` / :class:`None`

        :param exclude_private: If ``True``, will exclude private attributes whose
          names begin with a single underscore. Defaults to ``True``.
        :type exclude_private: :ref:`bool <python:bool>`

        :returns: List of attribute configurations.
        :rtype: :ref:`list <python:list>` of :class:`AttributeConfiguration`

        """
        # pylint: disable=too-many-branches

        include_private = not exclude_private

        instance_attributes = cls._get_instance_attributes(
            include_private = include_private,
            exclude_methods = True
        )

        attributes = []
        for key in instance_attributes:
            value = getattr(cls, key)
            config = AttributeConfiguration(attribute = value)
            config.name = key

            if from_csv is not None and to_csv is None:
                if config not in attributes and config.supports_csv[0] == bool(from_csv):
                    attributes.append(config)
                    continue

            if to_csv is not None and from_csv is None:
                if config not in attributes and config.supports_csv[1] == bool(to_csv):
                    attributes.append(config)
                    continue

            if from_csv is not None and to_csv is not None:
                if config not in attributes and config.supports_csv == (bool(from_csv),
                                                                        bool(to_csv)):
                    attributes.append(config)
                    continue

            if from_json is not None and to_json is None:
                if config not in attributes and config.supports_json[0] == bool(from_json):   # pylint: disable=line-too-long
                    attributes.append(config)
                    continue

            if to_json is not None and from_json is None:
                if config not in attributes and config.supports_json[1] == bool(to_json):
                    attributes.append(config)
                    continue

            if from_json is not None and to_json is not None:
                if config not in attributes and config.supports_json == (bool(from_json),
                                                                         bool(to_json)):
                    attributes.append(config)
                    continue

            if from_yaml is not None and to_yaml is None:
                if config not in attributes and config.supports_yaml[0] == bool(from_yaml):   # pylint: disable=line-too-long
                    attributes.append(config)
                    continue

            if to_yaml is not None and from_yaml is None:
                if config not in attributes and config.supports_yaml[1] == bool(to_yaml):
                    attributes.append(config)
                    continue

            if from_yaml is not None and to_yaml is not None:
                if config not in attributes and config.supports_yaml == (bool(from_yaml),
                                                                         bool(to_yaml)):
                    attributes.append(config)
                    continue

            if from_dict is not None and to_dict is None:
                if config not in attributes and config.supports_dict[0] == bool(from_dict):   # pylint: disable=line-too-long
                    attributes.append(config)
                    continue

            if to_dict is not None and from_dict is None:
                if config not in attributes and config.supports_dict[1] == bool(to_dict):
                    attributes.append(config)
                    continue

            if from_dict is not None and to_dict is not None:
                if config not in attributes and config.supports_dict == (bool(from_dict),
                                                                         bool(to_dict)):
                    attributes.append(config)
                    continue

        return attributes

    @classmethod
    def _get_meta_serializable_attributes(cls,
                                          from_csv = None,
                                          to_csv = None,
                                          from_json = None,
                                          to_json = None,
                                          from_yaml = None,
                                          to_yaml = None,
                                          from_dict = None,
                                          to_dict = None):
        """Retrieve a list of :class:`AttributeConfiguration` objects corresponding
        to attributes whose values can be serialized from/to CSV, JSON, YAML, etc.

        .. note::

          This method operates *solely* on attribute configurations that have been
          provided in the meta override ``__<format>_support__`` attribute.

        :param from_csv: If ``True``, includes attribute names that **can** be
          de-serialized from CSV strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from CSV strings. If :class:`None`,
          will not include attributes based on CSV de-serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type from_csv: :ref:`bool <python:bool>` / :class:`None`

        :param to_csv: If ``True``, includes attribute names that **can** be
          serialized to CSV strings. If ``False``, includes attribute names
          that **cannot** be serialized to CSV strings. If :class:`None`,
          will not include attributes based on CSV serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type to_csv: :ref:`bool <python:bool>` / :class:`None`

        :param from_json: If ``True``, includes attribute names that **can** be
          de-serialized from JSON strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from JSON strings. If :class:`None`,
          will not include attributes based on JSON de-serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type from_json: :ref:`bool <python:bool>` / :class:`None`

        :param to_json: If ``True``, includes attribute names that **can** be
          serialized to JSON strings. If ``False``, includes attribute names
          that **cannot** be serialized to JSON strings. If :class:`None`,
          will not include attributes based on JSON serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type to_json: :ref:`bool <python:bool>` / :class:`None`

        :param from_yaml: If ``True``, includes attribute names that **can** be
          de-serialized from YAML strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from YAML strings. If :class:`None`,
          will not include attributes based on YAML de-serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type from_yaml: :ref:`bool <python:bool>` / :class:`None`

        :param to_yaml: If ``True``, includes attribute names that **can** be
          serialized to YAML strings. If ``False``, includes attribute names
          that **cannot** be serialized to YAML strings. If :class:`None`,
          will not include attributes based on YAML serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type to_yaml: :ref:`bool <python:bool>` / :class:`None`

        :param from_dict: If ``True``, includes attribute names that **can** be
          de-serialized from :ref:`dict <python:dict>` objects. If ``False``, includes
          attribute names that **cannot** be de-serialized from :ref:`dict <python:dict>`
          objects. If :class:`None`, will not include attributes based on
          :ref:`dict <python:dict> de-serialization support (but may include them
          based on other parameters). Defaults to :class:`None`.
        :type from_dict: :ref:`bool <python:bool>` / :class:`None`

        :param to_dict: If ``True``, includes attribute names that **can** be
          serialized to :ref:`dict <python:dict>` objects. If ``False``, includes
          attribute names that **cannot** be serialized to :ref:`dict <python:dict>`
          objects. If :class:`None`, will not include attributes based on
          :ref:`dict <python:dict> serialization support (but may include them
          based on other parameters). Defaults to :class:`None`.
        :type from_dict: :ref:`bool <python:bool>` / :class:`None`

        :returns: List of attribute configurations.
        :rtype: :ref:`list <python:list>` of :class:`AttributeConfiguration`

        """
        attributes = []

        if from_csv is not None and to_csv is None:
            attributes.extend([x for x in cls.__serialization__
                               if x.supports_csv[0] == bool(from_csv) and \
                                  x not in attributes
                              ])
        if to_csv is not None and from_csv is None:
            attributes.extend([x for x in cls.__serialization__
                               if x.supports_csv[1] == bool(to_csv) and \
                                  x not in attributes
                              ])

        if from_csv is not None and to_csv is not None:
            attributes.extend([x for x in cls.__serialization__
                               if x.supports_csv[0] == bool(from_csv) and \
                                  x.supports_csv[1] == bool(to_csv) and \
                                  x not in attributes
                              ])

        if from_json is not None and to_json is None:
            attributes.extend([x for x in cls.__serialization__
                               if x.supports_json[0] == bool(from_json) and \
                                  x not in attributes
                              ])
        if to_json is not None and from_json is None:
            attributes.extend([x for x in cls.__serialization__
                               if x.supports_json[1] == bool(to_json) and \
                                  x not in attributes
                              ])

        if from_json is not None and to_json is not None:
            attributes.extend([x for x in cls.__serialization__
                               if x.supports_json[0] == bool(from_json) and \
                                  x.supports_json[1] == bool(to_json) and \
                                  x not in attributes
                              ])

        if from_yaml is not None and to_yaml is None:
            attributes.extend([x for x in cls.__serialization__
                               if x.supports_yaml[0] == bool(from_yaml) and \
                                  x not in attributes
                              ])
        if to_yaml is not None and from_yaml is None:
            attributes.extend([x for x in cls.__serialization__
                               if x.supports_yaml[1] == bool(to_yaml) and \
                                  x not in attributes
                              ])

        if from_yaml is not None and to_yaml is not None:
            attributes.extend([x for x in cls.__serialization__
                               if x.supports_yaml[0] == bool(from_yaml) and \
                                  x.supports_yaml[1] == bool(to_yaml) and \
                                  x not in attributes
                              ])

        if from_dict is not None and to_dict is None:
            attributes.extend([x for x in cls.__serialization__
                               if x.supports_dict[0] == bool(from_dict) and \
                                  x not in attributes
                              ])
        if to_dict is not None and from_dict is None:
            attributes.extend([x for x in cls.__serialization__
                               if x.supports_dict[1] == bool(to_dict) and \
                                  x not in attributes
                              ])

        if from_dict is not None and to_dict is not None:
            attributes.extend([x for x in cls.__serialization__
                               if x.supports_dict[0] == bool(from_dict) and \
                                  x.supports_dict[1] == bool(to_dict) and \
                                  x not in attributes
                              ])

        return attributes

    @classmethod
    def _get_attribute_configurations(cls):
        """Retrieve a list of :class:`AttributeConfiguration` applied to the class."""
        attributes = [x for x in cls.__serialization__]
        attributes.extend([x
                           for x in cls._get_declarative_serializable_attributes(
                               from_csv = True,
                               from_json = True,
                               from_yaml = True,
                               from_dict = True
                           )
                           if x not in attributes])

        attributes.extend([x
                           for x in cls._get_declarative_serializable_attributes(
                               to_csv = True,
                               to_json = True,
                               to_yaml = True,
                               to_dict = True
                           )
                           if x not in attributes])

        return attributes

    @classmethod
    def get_serialization_config(cls,
                                 from_csv = None,
                                 to_csv = None,
                                 from_json = None,
                                 to_json = None,
                                 from_yaml = None,
                                 to_yaml = None,
                                 from_dict = None,
                                 to_dict = None,
                                 exclude_private = True):
        """Retrieve a list of :class:`AttributeConfiguration` objects corresponding
        to attributes whose values can be serialized from/to CSV, JSON, YAML, etc.

        :param from_csv: If ``True``, includes attribute names that **can** be
          de-serialized from CSV strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from CSV strings. If :class:`None`,
          will not include attributes based on CSV de-serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type from_csv: :ref:`bool <python:bool>` / :class:`None`

        :param to_csv: If ``True``, includes attribute names that **can** be
          serialized to CSV strings. If ``False``, includes attribute names
          that **cannot** be serialized to CSV strings. If :class:`None`,
          will not include attributes based on CSV serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type to_csv: :ref:`bool <python:bool>` / :class:`None`

        :param from_json: If ``True``, includes attribute names that **can** be
          de-serialized from JSON strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from JSON strings. If :class:`None`,
          will not include attributes based on JSON de-serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type from_json: :ref:`bool <python:bool>` / :class:`None`

        :param to_json: If ``True``, includes attribute names that **can** be
          serialized to JSON strings. If ``False``, includes attribute names
          that **cannot** be serialized to JSON strings. If :class:`None`,
          will not include attributes based on JSON serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type to_json: :ref:`bool <python:bool>` / :class:`None`

        :param from_yaml: If ``True``, includes attribute names that **can** be
          de-serialized from YAML strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from YAML strings. If :class:`None`,
          will not include attributes based on YAML de-serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type from_yaml: :ref:`bool <python:bool>` / :class:`None`

        :param to_yaml: If ``True``, includes attribute names that **can** be
          serialized to YAML strings. If ``False``, includes attribute names
          that **cannot** be serialized to YAML strings. If :class:`None`,
          will not include attributes based on YAML serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type to_yaml: :ref:`bool <python:bool>` / :class:`None`

        :param from_dict: If ``True``, includes attribute names that **can** be
          de-serialized from :ref:`dict <python:dict>` objects. If ``False``, includes
          attribute names that **cannot** be de-serialized from :ref:`dict <python:dict>`
          objects. If :class:`None`, will not include attributes based on
          :ref:`dict <python:dict> de-serialization support (but may include them
          based on other parameters). Defaults to :class:`None`.
        :type from_dict: :ref:`bool <python:bool>` / :class:`None`

        :param to_dict: If ``True``, includes attribute names that **can** be
          serialized to :ref:`dict <python:dict>` objects. If ``False``, includes
          attribute names that **cannot** be serialized to :ref:`dict <python:dict>`
          objects. If :class:`None`, will not include attributes based on
          :ref:`dict <python:dict> serialization support (but may include them
          based on other parameters). Defaults to :class:`None`.
        :type from_dict: :ref:`bool <python:bool>` / :class:`None`

        :param exclude_private: If ``True``, will exclude private attributes whose
          names begin with a single underscore. Defaults to ``True``.
        :type exclude_private: :ref:`bool <python:bool>`

        :returns: List of attribute configurations.
        :rtype: :ref:`list <python:list>` of :class:`AttributeConfiguration`

        """
        declarative_attributes = cls._get_declarative_serializable_attributes(
            from_csv = from_csv,
            to_csv = to_csv,
            from_json = from_json,
            to_json = to_json,
            from_yaml = from_yaml,
            to_yaml = to_yaml,
            from_dict = from_dict,
            to_dict = to_dict,
            exclude_private = exclude_private
        )
        meta_attributes = cls._get_meta_serializable_attributes(
            from_csv = from_csv,
            to_csv = to_csv,
            from_json = from_json,
            to_json = to_json,
            from_yaml = from_yaml,
            to_yaml = to_yaml,
            from_dict = from_dict,
            to_dict = to_dict,
        )

        attributes = [x for x in meta_attributes]
        attributes.extend([x for x in declarative_attributes
                           if x not in attributes and x not in cls.__serialization__])

        return attributes

    @classmethod
    def get_csv_serialization_config(cls, deserialize = True, serialize = True):
        """Retrieve the CSV serialization configurations that apply for this object.

        :param deserialize: If ``True``, returns configurations for attributes that
          **can** be de-serialized from CSV strings. If ``False``,
          returns configurations for attributes that **cannot** be de-serialized from
          CSV strings. If :class:`None`, ignores de-serialization
          configuration when determining which attribute configurations to return.
          Defaults to :class:`None`.
        :type deserialize: :ref:`bool <python:bool>` / :class:`None`

        :param serialize: If ``True``, returns configurations for attributes that
          **can** be serialized to CSV strings. If ``False``,
          returns configurations for attributes that **cannot** be serialized to
          CSV strings. If :class:`None`, ignores serialization
          configuration when determining which attribute configurations to return.
          Defaults to :class:`None`.
        :type serialize: :ref:`bool <python:bool>` / :class:`None`

        :returns: Set of attribute serialization configurations that match the
          arguments supplied.
        :rtype: :ref:`list <python:list>` of :class:`AttributeConfiguration`
        """
        attributes = [x.copy()
                      for x in cls.get_serialization_config(from_csv = deserialize,
                                                            to_csv = serialize)]
        for config in attributes:
            if config.csv_sequence is None:
                config.csv_sequence = len(attributes) + 1

        return sorted(attributes, key = lambda x: (x.csv_sequence, x.name))

    @classmethod
    def get_json_serialization_config(cls, deserialize = True, serialize = True):
        """Retrieve the JSON serialization configurations that apply for this object.

        :param deserialize: If ``True``, returns configurations for attributes that
          **can** be de-serialized from JSON strings. If ``False``,
          returns configurations for attributes that **cannot** be de-serialized from
          JSON strings. If :class:`None`, ignores de-serialization
          configuration when determining which attribute configurations to return.
          Defaults to :class:`None`.
        :type deserialize: :ref:`bool <python:bool>` / :class:`None`

        :param serialize: If ``True``, returns configurations for attributes that
          **can** be serialized to JSON strings. If ``False``,
          returns configurations for attributes that **cannot** be serialized to
          JSON strings. If :class:`None`, ignores serialization
          configuration when determining which attribute configurations to return.
          Defaults to :class:`None`.
        :type serialize: :ref:`bool <python:bool>` / :class:`None`

        :returns: Set of attribute serialization configurations that match the
          arguments supplied.
        :rtype: :ref:`list <python:list>` of :class:`AttributeConfiguration`
        """
        return [x for x in cls.get_serialization_config(from_json = deserialize,
                                                        to_json = serialize)]

    @classmethod
    def get_yaml_serialization_config(cls, deserialize = True, serialize = True):
        """Retrieve the YAML serialization configurations that apply for this object.

        :param deserialize: If ``True``, returns configurations for attributes that
          **can** be de-serialized from YAML strings. If ``False``,
          returns configurations for attributes that **cannot** be de-serialized from
          YAML strings. If :class:`None`, ignores de-serialization
          configuration when determining which attribute configurations to return.
          Defaults to :class:`None`.
        :type deserialize: :ref:`bool <python:bool>` / :class:`None`

        :param serialize: If ``True``, returns configurations for attributes that
          **can** be serialized to YAML strings. If ``False``,
          returns configurations for attributes that **cannot** be serialized to
          YAML strings. If :class:`None`, ignores serialization
          configuration when determining which attribute configurations to return.
          Defaults to :class:`None`.
        :type serialize: :ref:`bool <python:bool>` / :class:`None`

        :returns: Set of attribute serialization configurations that match the
          arguments supplied.
        :rtype: :ref:`list <python:list>` of :class:`AttributeConfiguration`

        """
        return [x for x in cls.get_serialization_config(from_yaml = deserialize,
                                                        to_yaml = serialize)]

    @classmethod
    def get_dict_serialization_config(cls, deserialize = True, serialize = True):
        """Retrieve the :ref:`dict <python:dict>` serialization configurations that
        apply for this object.

        :param deserialize: If ``True``, returns configurations for attributes that
          **can** be de-serialized from :ref:`dict <python:dict>` objects. If ``False``,
          returns configurations for attributes that **cannot** be de-serialized from
          :ref:`dict <python:dict>` objects. If :class:`None`, ignores de-serialization
          configuration when determining which attribute configurations to return.
          Defaults to :class:`None`.
        :type deserialize: :ref:`bool <python:bool>` / :class:`None`

        :param serialize: If ``True``, returns configurations for attributes that
          **can** be serialized to :ref:`dict <python:dict>` objects. If ``False``,
          returns configurations for attributes that **cannot** be serialized to
          :ref:`dict <python:dict>` objects. If :class:`None`, ignores serialization
          configuration when determining which attribute configurations to return.
          Defaults to :class:`None`.
        :type serialize: :ref:`bool <python:bool>` / :class:`None`

        :returns: Set of attribute serialization configurations that match the
          arguments supplied.
        :rtype: :ref:`list <python:list>` of :class:`AttributeConfiguration`
        """
        return [x for x in cls.get_serialization_config(from_dict = deserialize,
                                                        to_dict = serialize)]

    @classmethod
    def get_attribute_serialization_config(cls, attribute):
        """Retrieve the :class:`AttributeConfiguration` for ``attribute``.

        :param attribute: The attribute/column name whose serialization
          configuration should be returned.
        :type attribute: :ref:`str <python:str>`

        """
        attributes = cls._get_attribute_configurations()

        for config in attributes:
            if config.name == attribute:
                return config.copy()

        return None

    @classmethod
    def does_support_serialization(cls,
                                   attribute,
                                   from_csv = None,
                                   to_csv = None,
                                   from_json = None,
                                   to_json = None,
                                   from_yaml = None,
                                   to_yaml = None,
                                   from_dict = None,
                                   to_dict = None):
        """Indicate whether ``attribute`` supports serialization/deserializtion.

        :param attribute: The name of the attribute whose serialization support
          should be confirmed.
        :type attribute: :ref:`str <python:str>`

        :param from_csv: If ``True``, includes attribute names that **can** be
          de-serialized from CSV strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from CSV strings. If :class:`None`,
          will not include attributes based on CSV de-serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type from_csv: :ref:`bool <python:bool>` / :class:`None`

        :param to_csv: If ``True``, includes attribute names that **can** be
          serialized to CSV strings. If ``False``, includes attribute names
          that **cannot** be serialized to CSV strings. If :class:`None`,
          will not include attributes based on CSV serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type to_csv: :ref:`bool <python:bool>` / :class:`None`

        :param from_json: If ``True``, includes attribute names that **can** be
          de-serialized from JSON strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from JSON strings. If :class:`None`,
          will not include attributes based on JSON de-serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type from_json: :ref:`bool <python:bool>` / :class:`None`

        :param to_json: If ``True``, includes attribute names that **can** be
          serialized to JSON strings. If ``False``, includes attribute names
          that **cannot** be serialized to JSON strings. If :class:`None`,
          will not include attributes based on JSON serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type to_json: :ref:`bool <python:bool>` / :class:`None`

        :param from_yaml: If ``True``, includes attribute names that **can** be
          de-serialized from YAML strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from YAML strings. If :class:`None`,
          will not include attributes based on YAML de-serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type from_yaml: :ref:`bool <python:bool>` / :class:`None`

        :param to_yaml: If ``True``, includes attribute names that **can** be
          serialized to YAML strings. If ``False``, includes attribute names
          that **cannot** be serialized to YAML strings. If :class:`None`,
          will not include attributes based on YAML serialization support (but
          may include them based on other parameters). Defaults to :class:`None`.
        :type to_yaml: :ref:`bool <python:bool>` / :class:`None`

        :param from_dict: If ``True``, includes attribute names that **can** be
          de-serialized from :ref:`dict <python:dict>` objects. If ``False``, includes
          attribute names that **cannot** be de-serialized from :ref:`dict <python:dict>`
          objects. If :class:`None`, will not include attributes based on
          :ref:`dict <python:dict> de-serialization support (but may include them
          based on other parameters). Defaults to :class:`None`.
        :type from_dict: :ref:`bool <python:bool>` / :class:`None`

        :param to_dict: If ``True``, includes attribute names that **can** be
          serialized to :ref:`dict <python:dict>` objects. If ``False``, includes
          attribute names that **cannot** be serialized to :ref:`dict <python:dict>`
          objects. If :class:`None`, will not include attributes based on
          :ref:`dict <python:dict> serialization support (but may include them
          based on other parameters). Defaults to :class:`None`.
        :type from_dict: :ref:`bool <python:bool>` / :class:`None`

        :returns: ``True`` if the attribute's serialization support matches,
          ``False`` if not, and :class:`None` if no serialization support was
          specified.
        :rtype: :ref:`bool <python:bool>` / :class:`None`

        :raises AttributeError: if ``attribute`` is not present on the object
        """
        # pylint: disable=too-many-boolean-expressions

        if from_csv is None and to_csv is None and \
           from_json is None and to_json is None and \
           from_yaml is None and to_yaml is None and \
           from_dict is None and to_dict is None:
            return None

        config = cls.get_attribute_serialization_config(attribute)
        if config is None:
            if inspect_.isclass(cls):
                class_name = cls.__name__
            else:
                class_name = type(cls).__name__

            raise UnsupportedSerializationError(
                "'%s' has no serializable attribute '%s'" % (class_name,
                                                             attribute)
            )

        csv_check = False
        json_check = False
        yaml_check = False
        dict_check = False

        if from_csv is not None and to_csv is not None:
            csv_check = config.supports_csv == (bool(from_csv), bool(to_csv))
        elif from_csv is not None:
            csv_check = config.supports_csv[0] == bool(from_csv)
        elif to_csv is not None:
            csv_check = config.supports_csv[1] == bool(to_csv)
        else:
            csv_check = True

        if from_json is not None and to_json is not None:
            json_check = config.supports_json == (bool(from_json), bool(to_json))
        elif from_json is not None:
            json_check = config.supports_json[0] == bool(from_json)
        elif to_json is not None:
            json_check = config.supports_json[1] == bool(to_json)
        else:
            json_check = True

        if from_yaml is not None and to_yaml is not None:
            yaml_check = config.supports_yaml == (bool(from_yaml), bool(to_yaml))
        elif from_yaml is not None:
            yaml_check = config.supports_yaml[0] == bool(from_yaml)
        elif to_yaml is not None:
            yaml_check = config.supports_yaml[1] == bool(to_yaml)
        else:
            yaml_check = True

        if from_dict is not None and to_dict is not None:
            dict_check = config.supports_dict == (bool(from_dict), bool(to_dict))
        elif from_dict is not None:
            dict_check = config.supports_dict[0] == bool(from_dict)
        elif to_dict is not None:
            dict_check = config.supports_dict[1] == bool(to_dict)
        else:
            dict_check = True

        return csv_check and json_check and yaml_check and dict_check

    def _get_serialized_value(self,
                              format,
                              attribute):
        """Retrieve the value of ``attribute`` after applying the attribute's
        ``on_serialize`` function for the format indicated by ``format``.

        :param format: The format to which the value should be serialized. Accepts
          either: ``csv``, ``json``, ``yaml``, or ``dict``.
        :type format: :ref:`str <python:str>`

        :param attribute: The name of the attribute that whose serialized value
          should be returned.
        :type attribute: :ref:`str <python:str>`

        :returns: The value returned by the attribute's ``on_serialize`` function
          for the indicated ``format``.

        :raises InvalidFormatError: if ``format`` is not ``csv``, ``json``, ``yaml``,
          or ``dict``.
        :raises ValueSerializationError: if the ``on_serialize`` function raises
          an exception
        """
        # pylint: disable=line-too-long

        to_csv, to_json, to_yaml, to_dict = format_to_tuple(format)

        supports_serialization = self.does_support_serialization(attribute,
                                                                 to_csv = to_csv,
                                                                 to_json = to_json,
                                                                 to_yaml = to_yaml,
                                                                 to_dict = to_dict)
        if not supports_serialization:
            raise UnsupportedSerializationError(
                "%s attribute '%s' does not support serialization to '%s'" % (self.__class__,
                                                                              attribute,
                                                                              format)
            )

        config = self.get_attribute_serialization_config(attribute)

        on_serialize = config.on_serialize[format]
        if on_serialize is None:
            on_serialize = get_default_serializer(getattr(self.__class__,
                                                          attribute),
                                                  format = format,
                                                  value = getattr(self,
                                                                  attribute,
                                                                  None))

        if on_serialize is None:
            if format == 'csv':
                return getattr(self, attribute, '')
            else:
                return getattr(self, attribute, None)

        try:
            return_value = on_serialize(getattr(self, attribute, None))
        except Exception:
            raise ValueSerializationError(
                "attribute '%s' failed serialization to format '%s'" % (attribute,
                                                                        format)
            )

        return return_value

    @classmethod
    def _get_deserialized_value(cls,
                                value,
                                format,
                                attribute):
        """Retrieve the value of ``attribute`` after applying the attribute's
        ``on_deserialize`` function for the format indicated by ``format``.

        :param value: The input value that was received when de-serializing.

        :param format: The format to which the value should be serialized. Accepts
          either: ``csv``, ``json``, ``yaml``, or ``dict``.
        :type format: :ref:`str <python:str>`

        :param attribute: The name of the attribute that whose serialized value
          should be returned.
        :type attribute: :ref:`str <python:str>`

        :returns: The value returned by the attribute's ``on_serialize`` function
          for the indicated ``format``.

        :raises InvalidFormatError: if ``format`` is not ``csv``, ``json``, ``yaml``,
          or ``dict``.
        :raises ValueDeserializationError: if the ``on_deserialize`` function raises
          an exception
        """
        # pylint: disable=line-too-long

        from_csv, from_json, from_yaml, from_dict = format_to_tuple(format)

        try:
            supports_deserialization = cls.does_support_serialization(attribute,
                                                                      from_csv = from_csv,
                                                                      from_json = from_json,
                                                                      from_yaml = from_yaml,
                                                                      from_dict = from_dict)
        except UnsupportedSerializationError:
            supports_deserialization = False

        if inspect_.isclass(cls):
            class_name = str(cls)
            class_obj = cls
        else:
            class_name = str(type(cls))
            class_obj = cls.__class__

        if not supports_deserialization:
            raise UnsupportedDeserializationError(
                "%s attribute '%s' does not support de-serialization from '%s'" % \
                (class_name,
                 attribute,
                 format)
            )

        config = cls.get_attribute_serialization_config(attribute)

        on_deserialize = config.on_deserialize[format]
        if on_deserialize is None:
            on_deserialize = get_default_deserializer(getattr(class_obj,
                                                              attribute),
                                                      format = format)

        if on_deserialize is None:
            return value

        try:
            return_value = on_deserialize(value)
        except Exception:
            raise ValueDeserializationError(
                "attribute '%s' failed de-serialization to format '%s'" % (attribute,
                                                                           format)
            )

        return return_value

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
                       deserialize = None,
                       serialize = True,
                       delimiter = '|',
                       wrap_all_strings = False,
                       null_text = 'None',
                       wrapper_character = "'",
                       double_wrapper_character_when_nested = False,
                       escape_character = "\\",
                       line_terminator = '\r\n'):
        """Retrieve a header string for a CSV representation of the model.

        :param delimiter: The character(s) to utilize between columns. Defaults to
          a pipe (``|``).
        :type delimiter: :ref:`str <python:str>`

        :param wrap_all_strings: If ``True``, wraps any string data in the
          ``wrapper_character``. If ``None``, only wraps string data if it contains
          the ``delimiter``. Defaults to ``False``.
        :type wrap_all_strings: :ref:`bool <python:bool>`

        :param null_text: The text value to use in place of empty values. Only
          applies if ``wrap_empty_values`` is ``True``. Defaults to ``'None'``.
        :type null_text: :ref:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is necessary. Defaults to ``'``.
        :type wrapper_character: :ref:`str <python:str>`

        :param double_wrapper_character_when_nested: If ``True``, will double the
          ``wrapper_character`` when it is found inside a column value. If ``False``,
          will precede the ``wrapper_character`` by the ``escape_character`` when
          it is found inside a column value. Defaults to ``False``.
        :type :ref:`bool <python:bool>`

        :param escape_character: The character to use when escaping nested wrapper
          characters. Defaults to ``\``.
        :type escape_character: :ref:`str <python:str>`

        :param line_terminator: The character used to mark the end of a line.
          Defaults to ``\r\n``.
        :type line_terminator: :ref:`str <python:str>`

        :returns: A string ending in ``\n`` with the model's CSV column names
          listed, separated by the ``delimiter``.
        :rtype: :ref:`str <python:str>`
        """
        if not wrapper_character:
            wrapper_character = '\''

        if wrap_all_strings:
            quoting = csv.QUOTE_NONNUMERIC
        else:
            quoting = csv.QUOTE_MINIMAL

        column_names = cls.get_csv_column_names(deserialize = deserialize,
                                                serialize = serialize)
        if 'sqlathanor' in csv.list_dialects():
            csv.unregister_dialect('sqlathanor')

        csv.register_dialect('sqlathanor',
                             delimiter = delimiter,
                             doublequote = double_wrapper_character_when_nested,
                             escapechar = escape_character,
                             quotechar = wrapper_character,
                             quoting = quoting,
                             lineterminator = line_terminator)

        output = StringIO()
        csv_writer = csv.DictWriter(output,
                                    fieldnames = column_names,
                                    dialect = 'sqlathanor')

        csv_writer.writeheader()

        header_string = output.getvalue()
        output.close()

        csv.unregister_dialect('sqlathanor')

        return header_string

    def get_csv_data(self,
                     delimiter = '|',
                     wrap_all_strings = False,
                     null_text = 'None',
                     wrapper_character = "'",
                     double_wrapper_character_when_nested = False,
                     escape_character = "\\",
                     line_terminator = '\r\n'):
        """Return the CSV representation of the model instance (record).

        :param delimiter: The delimiter used between columns. Defaults to ``|``.
        :type delimiter: :ref:`str <python:str>`

        :param wrap_all_strings: If ``True``, wraps any string data in the
          ``wrapper_character``. If ``None``, only wraps string data if it contains
          the ``delimiter``. Defaults to ``False``.
        :type wrap_all_strings: :ref:`bool <python:bool>`

        :param null_text: The text value to use in place of empty values. Only
          applies if ``wrap_empty_values`` is ``True``. Defaults to ``'None'``.
        :type null_text: :ref:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is necessary. Defaults to ``'``.
        :type wrapper_character: :ref:`str <python:str>`

        :param double_wrapper_character_when_nested: If ``True``, will double the
          ``wrapper_character`` when it is found inside a column value. If ``False``,
          will precede the ``wrapper_character`` by the ``escape_character`` when
          it is found inside a column value. Defaults to ``False``.
        :type :ref:`bool <python:bool>`

        :param escape_character: The character to use when escaping nested wrapper
          characters. Defaults to ``\``.
        :type escape_character: :ref:`str <python:str>`

        :param line_terminator: The character used to mark the end of a line.
          Defaults to ``\r\n``.
        :type line_terminator: :ref:`str <python:str>`

        :returns: Data from the object in CSV format ending in ``line_terminator``.
        :rtype: :ref:`str <python: str>`
        """
        if not wrapper_character:
            wrapper_character = '\''

        csv_column_names = [x
                            for x in self.get_csv_column_names(deserialize = None,
                                                               serialize = True)
                            if hasattr(self, x)]

        if not csv_column_names:
            raise SerializableAttributeError("no 'csv' serializable attributes found")

        if wrap_all_strings:
            quoting = csv.QUOTE_NONNUMERIC
        else:
            quoting = csv.QUOTE_MINIMAL

        if 'sqlathanor' in csv.list_dialects():
            csv.unregister_dialect('sqlathanor')

        csv.register_dialect('sqlathanor',
                             delimiter = delimiter,
                             doublequote = double_wrapper_character_when_nested,
                             escapechar = escape_character,
                             quotechar = wrapper_character,
                             quoting = quoting,
                             lineterminator = line_terminator)

        data = [self._get_serialized_value(format = 'csv',
                                           attribute = x)
                for x in csv_column_names]

        for index, item in enumerate(data):
            if item == '' or item is None or item == 'None':
                data[index] = null_text
            elif not checkers.is_string(item) and not checkers.is_numeric(item):
                data[index] = str(item)

        data_dict = {}
        for index, column_name in enumerate(csv_column_names):
            data_dict[column_name] = data[index]

        output = StringIO()
        csv_writer = csv.DictWriter(output,
                                    fieldnames = csv_column_names,
                                    dialect = 'sqlathanor')


        csv_writer.writerow(data_dict)

        data_row = output.getvalue()
        output.close()

        csv.unregister_dialect('sqlathanor')

        return data_row

    def to_csv(self,
               include_header = False,
               delimiter = '|',
               wrap_all_strings = False,
               null_text = 'None',
               wrapper_character = "'",
               double_wrapper_character_when_nested = False,
               escape_character = "\\",
               line_terminator = '\r\n'):
        """Retrieve a CSV string with the object's data.

        :param include_header: If ``True``, will include a header row with column
          labels. If ``False``, will not include a header row. Defaults to ``True``.
        :type include_header: :ref:`bool <python:bool>`

        :param delimiter: The delimiter used between columns. Defaults to ``|``.
        :type delimiter: :ref:`str <python:str>`

        :param wrap_all_strings: If ``True``, wraps any string data in the
          ``wrapper_character``. If ``None``, only wraps string data if it contains
          the ``delimiter``. Defaults to ``False``.
        :type wrap_all_strings: :ref:`bool <python:bool>`

        :param null_text: The text value to use in place of empty values. Only
          applies if ``wrap_empty_values`` is ``True``. Defaults to ``'None'``.
        :type null_text: :ref:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is necessary. Defaults to ``'``.
        :type wrapper_character: :ref:`str <python:str>`

        :param double_wrapper_character_when_nested: If ``True``, will double the
          ``wrapper_character`` when it is found inside a column value. If ``False``,
          will precede the ``wrapper_character`` by the ``escape_character`` when
          it is found inside a column value. Defaults to ``False``.
        :type :ref:`bool <python:bool>`

        :param escape_character: The character to use when escaping nested wrapper
          characters. Defaults to ``\``.
        :type escape_character: :ref:`str <python:str>`

        :param line_terminator: The character used to mark the end of a line.
          Defaults to ``\r\n``.
        :type line_terminator: :ref:`str <python:str>`

        :returns: Data from the object in CSV format ending in a newline (``\n``).
        :rtype: :ref:`str <python:str>`
        """
        if include_header:
            return self.get_csv_header(delimiter = delimiter) + \
                   self.get_csv_data(delimiter = delimiter,
                                     wrap_all_strings = wrap_all_strings,
                                     null_text = null_text,
                                     wrapper_character = wrapper_character,
                                     double_wrapper_character_when_nested = double_wrapper_character_when_nested,     # pylint: disable=line-too-long
                                     escape_character = escape_character,
                                     line_terminator = line_terminator)


        return self.get_csv_data(delimiter = delimiter,
                                 wrap_all_strings = wrap_all_strings,
                                 null_text = null_text,
                                 wrapper_character = wrapper_character,
                                 double_wrapper_character_when_nested = double_wrapper_character_when_nested,     # pylint: disable=line-too-long
                                 escape_character = escape_character,
                                 line_terminator = line_terminator)

    @classmethod
    def _parse_csv(cls,
                   csv_data,
                   delimiter = '|',
                   wrap_all_strings = False,
                   null_text = 'None',
                   wrapper_character = "'",
                   double_wrapper_character_when_nested = False,
                   escape_character = "\\",
                   line_terminator = '\r\n'):
        """Generate a :ref:`dict <python:dict>` from a CSV record.

        .. tip::

          Unwrapped empty column values are automatically interpreted as null
          (:class:`None`).

        :param csv_data: The CSV record. Should be a single row and should **not**
          include column headers.
        :type csv_data: :ref:`str <python:str>`

        :param delimiter: The delimiter used between columns. Defaults to ``|``.
        :type delimiter: :ref:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is applied. Defaults to ``'``.
        :type wrapper_character: :ref:`str <python:str>`

        :param null_text: The string used to indicate an empty value if empty
          values are wrapped. Defaults to `None`.
        :type null_text: :ref:`str <python:str>`

        :returns: A :ref:`dict <python:dict>` representation of the CSV record.
        :rtype: :ref:`dict <python:dict>`

        :raises DeserializationError: if ``csv_data`` is not a valid
          :ref:`str <python:str>`
        :raises CSVColumnError: if the columns in ``csv_data`` do not match
          the expected columns returned by
          :func:`get_csv_column_names() <BaseModel.get_csv_column_names>`
        :raises ValueDeserializationError: if a value extracted from the CSV
          failed when executing its :term:`de-serialization function`.

        """
        try:
            csv_data = validators.string(csv_data, allow_empty = False)
        except (ValueError, TypeError):
            raise DeserializationError("csv_data expects a 'str', received '%s'" \
                                       % type(csv_data))

        if not wrapper_character:
            wrapper_character = '\''

        if wrap_all_strings:
            quoting = csv.QUOTE_NONNUMERIC
        else:
            quoting = csv.QUOTE_MINIMAL

        if 'sqlathanor' in csv.list_dialects():
            csv.unregister_dialect('sqlathanor')

        csv.register_dialect('sqlathanor',
                             delimiter = delimiter,
                             doublequote = double_wrapper_character_when_nested,
                             escapechar = escape_character,
                             quotechar = wrapper_character,
                             quoting = quoting,
                             lineterminator = line_terminator)

        csv_column_names = [x
                            for x in cls.get_csv_column_names(deserialize = True,
                                                              serialize = None)
                            if hasattr(cls, x)]

        csv_reader = csv.DictReader([csv_data],
                                    fieldnames = csv_column_names,
                                    dialect = 'sqlathanor',
                                    restkey = None,
                                    restval = None)

        rows = [x for x in csv_reader]

        if len(rows) > 1:
            raise CSVColumnError('expected 1 row of data, received %s' % len(csv_reader))
        elif len(rows) == 0:
            data = {}
            for column_name in csv_column_names:
                data[column_name] = None
        else:
            data = rows[0]

        if data.get(None, None) is not None:
            raise CSVColumnError('expected %s fields, found %s' % (len(csv_column_names),
                                                                   len(data.keys())))
        for key in data:
            if data[key] == null_text:
                data[key] = None
                continue

            deserialized_value = cls._get_deserialized_value(data[key],
                                                             'csv',
                                                             key)

            data[key] = deserialized_value

        csv.unregister_dialect('sqlathanor')

        return data

    def update_from_csv(self,
                        csv_data,
                        delimiter = '|',
                        wrap_all_strings = False,
                        null_text = 'None',
                        wrapper_character = "'",
                        double_wrapper_character_when_nested = False,
                        escape_character = "\\",
                        line_terminator = '\r\n'):
        """Update a new model instance from a CSV record.

        .. tip::

          Unwrapped empty column values are automatically interpreted as null
          (:class:`None`).

        :param csv_data: The CSV record. Should be a single row and should **not**
          include column headers.
        :type csv_data: :ref:`str <python:str>`

        :param delimiter: The delimiter used between columns. Defaults to ``|``.
        :type delimiter: :ref:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is applied. Defaults to ``'``.
        :type wrapper_character: :ref:`str <python:str>`

        :param null_text: The string used to indicate an empty value if empty
          values are wrapped. Defaults to `None`.
        :type null_text: :ref:`str <python:str>`

        :returns: A :term:`model instance` created from the record.
        :rtype: model instance

        :raises DeserializationError: if ``csv_data`` is not a valid
          :ref:`str <python:str>`
        :raises CSVColumnError: if the columns in ``csv_data`` do not match
          the expected columns returned by
          :func:`get_csv_column_names() <BaseModel.get_csv_column_names>`
        :raises ValueDeserializationError: if a value extracted from the CSV
          failed when executing its :term:`de-serialization function`.

        """
        data = self._parse_csv(csv_data,
                               delimiter = delimiter,
                               wrap_all_strings = wrap_all_strings,
                               null_text = null_text,
                               wrapper_character = wrapper_character,
                               double_wrapper_character_when_nested = double_wrapper_character_when_nested,
                               escape_character = escape_character,
                               line_terminator = line_terminator)

        for key in data:
            setattr(self, key, data[key])

    @classmethod
    def new_from_csv(cls,
                     csv_data,
                     delimiter = '|',
                     wrap_all_strings = False,
                     null_text = 'None',
                     wrapper_character = "'",
                     double_wrapper_character_when_nested = False,
                     escape_character = "\\",
                     line_terminator = '\r\n'):
        """Create a new model instance from a CSV record.

        .. tip::

          Unwrapped empty column values are automatically interpreted as null
          (:class:`None`).

        :param csv_data: The CSV record. Should be a single row and should **not**
          include column headers.
        :type csv_data: :ref:`str <python:str>`

        :param delimiter: The delimiter used between columns. Defaults to ``|``.
        :type delimiter: :ref:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is applied. Defaults to ``'``.
        :type wrapper_character: :ref:`str <python:str>`

        :param null_text: The string used to indicate an empty value if empty
          values are wrapped. Defaults to `None`.
        :type null_text: :ref:`str <python:str>`

        :returns: A :term:`model instance` created from the record.
        :rtype: model instance

        :raises DeserializationError: if ``csv_data`` is not a valid
          :ref:`str <python:str>`
        :raises CSVColumnError: if the columns in ``csv_data`` do not match
          the expected columns returned by
          :func:`get_csv_column_names() <BaseModel.get_csv_column_names>`
        :raises ValueDeserializationError: if a value extracted from the CSV
          failed when executing its :term:`de-serialization function`.

        """
        data = cls._parse_csv(csv_data,
                              delimiter = delimiter,
                              wrap_all_strings = wrap_all_strings,
                              null_text = null_text,
                              wrapper_character = wrapper_character,
                              double_wrapper_character_when_nested = double_wrapper_character_when_nested,
                              escape_character = escape_character,
                              line_terminator = line_terminator)

        return cls(**data)

    def _to_dict(self,
                 format,
                 max_nesting = 0,
                 current_nesting = 0):
        """Return a :ref:`dict <python:dict>` representation of the object.

        .. warning::

          This method is an **intermediate** step that is used to produce the
          contents for certain public JSON, YAML, and :ref:`dict <python:dict>`
          serialization methods. It should not be called directly.

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

        :returns: A :ref:`dict <python:dict>` representation of the object.
        :rtype: :ref:`dict <python:dict>`

        :raises InvalidFormatError: if ``format`` is not recognized
        :raises SerializableAttributeError: if attributes is empty
        :raises MaximumNestingExceededError: if ``current_nesting`` is greater
          than ``max_nesting``
        :raises MaximumNestingExceededWarning: if an attribute requires nesting
          beyond ``max_nesting``
        """
        next_nesting = current_nesting + 1

        if format not in ['csv', 'json', 'yaml', 'dict']:
            raise InvalidFormatError("format '%s' not supported" % format)

        if current_nesting > max_nesting:
            raise MaximumNestingExceededError(
                'current nesting level (%s) exceeds maximum %s' % (current_nesting,
                                                                   max_nesting)
            )

        dict_object = {}

        if format == 'csv':
            attribute_getter = self.get_csv_serialization_config
        elif format == 'json':
            attribute_getter = self.get_json_serialization_config
        elif format == 'yaml':
            attribute_getter = self.get_yaml_serialization_config
        elif format == 'dict':
            attribute_getter = self.get_dict_serialization_config

        attributes = [x
                      for x in attribute_getter(deserialize = None,
                                                serialize = True)
                      if hasattr(self, x.name)]

        if not attributes:
            raise SerializableAttributeError(
                "'%s' has no '%s' serializable attributes" % (type(self.__class__),
                                                              format)
            )

        for attribute in attributes:
            item = getattr(self, attribute.name, None)
            try:
                try:
                    value = item._to_dict(format,
                                          max_nesting = max_nesting,
                                          current_nesting = next_nesting)
                except MaximumNestingExceededError:
                    warnings.warn(
                        "skipping key '%s' because maximum nesting has been exceeded" \
                            % attribute.name,
                        MaximumNestingExceededWarning
                    )
                    continue
            except AttributeError:
                try:
                    value = iterable__to_dict(item,
                                              format,
                                              max_nesting = max_nesting,
                                              current_nesting = next_nesting)
                except MaximumNestingExceededError:
                    warnings.warn(
                        "skipping key '%s' because maximum nesting has been exceeded" \
                            % attribute.name,
                        MaximumNestingExceededWarning
                    )
                    continue
                except NotAnIterableError:
                    value = self._get_serialized_value(format,
                                                       attribute.name)

            dict_object[attribute.name] = value

        return dict_object

    def to_json(self,
                max_nesting = 0,
                current_nesting = 0,
                serialize_function = None,
                **kwargs):
        """Return a JSON representation of the object.

        :param max_nesting: The maximum number of levels that the resulting
          JSON object can be nested. If set to ``0``, will
          not nest other serializable objects. Defaults to ``0``.
        :type max_nesting: :ref:`int <python:int>`

        :param current_nesting: The current nesting level at which the
          :ref:`dict <python:dict>` representation will reside. Defaults to ``0``.
        :type current_nesting: :ref:`int <python:int>`

        :param serialize_function: Optionally override the default JSON serializer.
          Defaults to :class:`None`, which applies the default :ref:`simplejson`
          JSON serializer.

          .. note::

            Use the ``serialize_function`` parameter to override the default
            JSON serializer. A valid ``serialize_function`` is expected to
            accept a single :ref:`dict <python:dict>` and return a
            :ref:`str <python:str>`, similar to
            :ref:`simplejson.dumps() <simplejson:simplejson.dumps>`.

            If you wish to pass additional arguments to your ``serialize_function``
            pass them as keyword arguments (in ``kwargs``).
        :type serialize_function: callable / :class:`None`

        :param **kwargs: Optional keyword parameters that are passed to the
          JSON serializer function. By default, these are options which are passed
          to :ref:`simplejson.dumps() <simplejson:simplejson.dumps>`.
        :type **kwargs: keyword arguments

        :returns: A :ref:`str <python:str>` with the JSON representation of the
          object.
        :rtype: :ref:`str <python:str>`

        :raises SerializableAttributeError: if attributes is empty
        :raises MaximumNestingExceededError: if ``current_nesting`` is greater
          than ``max_nesting``
        :raises MaximumNestingExceededWarning: if an attribute requires nesting
          beyond ``max_nesting``

        """
        if serialize_function is None:
            serialize_function = json.dumps
        else:
            if checkers.is_callable(serialize_function) is False:
                raise ValueError(
                    'serialize_function (%s) is not callable' % serialize_function
                )

        as_dict = self._to_dict('json',
                                max_nesting = max_nesting,
                                current_nesting = current_nesting)

        as_json = serialize_function(as_dict, **kwargs)

        return as_json

    def to_yaml(self,
                max_nesting = 0,
                current_nesting = 0,
                serialize_function = None,
                **kwargs):
        """Return a YAML representation of the object.

        :param max_nesting: The maximum number of levels that the resulting
          object can be nested. If set to ``0``, will not nest other serializable
          objects. Defaults to ``0``.
        :type max_nesting: :ref:`int <python:int>`

        :param current_nesting: The current nesting level at which the
          representation will reside. Defaults to ``0``.
        :type current_nesting: :ref:`int <python:int>`

        :param serialize_function: Optionally override the default YAML serializer.
          Defaults to :class:`None`, which calls the default ``yaml.dump()``
          function from the `PyYAML <https://github.com/yaml/pyyaml>`_ library.

          .. note::

            Use the ``serialize_function`` parameter to override the default
            YAML serializer. A valid ``serialize_function`` is expected to
            accept a single :ref:`dict <python:dict>` and return a
            :ref:`str <python:str>`, similar to
            ``yaml.dump()``.

            If you wish to pass additional arguments to your ``serialize_function``
            pass them as keyword arguments (in ``kwargs``).

        :type serialize_function: callable / :class:`None`

        :param **kwargs: Optional keyword parameters that are passed to the
          YAML serializer function. By default, these are options which are passed
          to ``yaml.dump()``.
        :type **kwargs: keyword arguments

        :returns: A :ref:`str <python:str>` with the JSON representation of the
          object.
        :rtype: :ref:`str <python:str>`

        :raises SerializableAttributeError: if attributes is empty
        :raises MaximumNestingExceededError: if ``current_nesting`` is greater
          than ``max_nesting``
        :raises MaximumNestingExceededWarning: if an attribute requires nesting
          beyond ``max_nesting``

        """
        if serialize_function is None:
            serialize_function = yaml.dump
        else:
            if checkers.is_callable(serialize_function) is False:
                raise ValueError(
                    'serialize_function (%s) is not callable' % serialize_function
                )

        as_dict = self._to_dict('yaml',
                                max_nesting = max_nesting,
                                current_nesting = current_nesting)

        as_yaml = serialize_function(as_dict, **kwargs)

        return as_yaml

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

        :raises SerializableAttributeError: if attributes is empty
        :raises MaximumNestingExceededError: if ``current_nesting`` is greater
          than ``max_nesting``
        :raises MaximumNestingExceededWarning: if an attribute requires nesting
          beyond ``max_nesting``

        """
        return self._to_dict('dict',
                             max_nesting = max_nesting,
                             current_nesting = current_nesting)


BaseModel = declarative_base(cls = BaseModel)
