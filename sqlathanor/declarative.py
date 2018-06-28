# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

import inspect as inspect_

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.state import InstanceState
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.util import symbol, OrderedProperties
from sqlalchemy.ext.hybrid import hybrid_property

from validator_collection import checkers, validators

from sqlathanor.attributes import AttributeConfiguration, validate_serialization_config
from sqlathanor.utilities import format_to_tuple
from sqlathanor.errors import ValueSerializationError, ValueDeserializationError, \
    UnsupportedSerializationError, UnsupportedDeserializationError
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
        attributes = [x
                      for x in cls.get_serialization_config(from_csv = deserialize,
                                                            to_csv = serialize)]
        for config in attributes:
            if config.csv_sequence is None:
                config.csv_sequence = len(attributes)

        return sorted(attributes, key = lambda x: x.csv_sequence)

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
                return config

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

    def _get_deserialized_value(self,
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
            supports_deserialization = self.does_support_serialization(attribute,
                                                                       from_csv = from_csv,
                                                                       from_json = from_json,
                                                                       from_yaml = from_yaml,
                                                                       from_dict = from_dict)
        except UnsupportedSerializationError:
            supports_deserialization = False

        if not supports_deserialization:
            raise UnsupportedDeserializationError(
                "%s attribute '%s' does not support de-serialization from '%s'" % \
                (self.__class__,
                 attribute,
                 format)
            )

        config = self.get_attribute_serialization_config(attribute)

        on_deserialize = config.on_deserialize[format]
        if on_deserialize is None:
            on_deserialize = get_default_deserializer(getattr(self.__class__,
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

        data = [self._get_serialized_value(format = 'csv',
                                           attribute = x)
                for x in csv_column_names if hasattr(self, x)]

        for index, item in enumerate(data):
            if item == '' and wrap_empty_values:
                item = None
            if item == 'None' or item is None:
                if wrap_empty_values:
                    data[index] = wrapper_character + str(item) + wrapper_character
                else:
                    data[index] = ''
            elif checkers.is_string(item) and wrap_all_strings:
                data[index] = wrapper_character + item + wrapper_character
            elif not checkers.is_string(item):
                data[index] = str(item)

            if delimiter in data[index]:
                data[index] = wrapper_character + data[index] + wrapper_character

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
        if include_header:
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
