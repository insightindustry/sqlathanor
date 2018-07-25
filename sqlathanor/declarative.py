# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

import csv
import inspect as inspect_
import warnings

from sqlalchemy.ext.declarative import declarative_base as SA_declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.state import InstanceState
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.util import symbol, OrderedProperties
from sqlalchemy.ext.hybrid import hybrid_property

import yaml

from validator_collection import checkers, validators
from validator_collection.errors import NotAnIterableError

from sqlathanor._compat import StringIO, json
from sqlathanor.attributes import AttributeConfiguration, validate_serialization_config, \
    BLANK_ON_SERIALIZE
from sqlathanor.utilities import format_to_tuple, iterable__to_dict, parse_yaml, \
    parse_json
from sqlathanor.errors import ValueSerializationError, ValueDeserializationError, \
    UnsupportedSerializationError, UnsupportedDeserializationError, DeserializationError,\
    CSVStructureError, MaximumNestingExceededError, MaximumNestingExceededWarning, \
    SerializableAttributeError, InvalidFormatError, DeserializableAttributeError, \
    ExtraKeyError, YAMLParseError, JSONParseError
from sqlathanor.default_serializers import get_default_serializer
from sqlathanor.default_deserializers import get_default_deserializer

# pylint: disable=no-member

class BaseModel(object):
    """Base class that establishes shared methods, attributes, and properties.

    When constructing your ORM models, inherit from (or mixin) this class to
    add support for :term:`serialization` and :term:`de-serialization`.

    .. note::

      It is this class which adds **SQLAthanor**'s methods and properties to your
      SQLAlchemy model.

      If your SQLAlchemy models do not inherit from this class, then they will
      not actually support :term:`serialization` or :term:`de-serialization`.

    You can construct your declarative models using three approaches:

    .. tabs::

      .. tab:: Using BaseModel Directly

        By inheriting or mixing in :class:`BaseModel` directly as shown in the
        examples below.

        .. code-block:: python

          from sqlathanor import BaseModel

          # EXAMPLE 1: As a direct parent class for your model.
          class MyModel(BaseModel):

              # Standard SQLAlchemy declarative model definition goes here.

          # EXAMPLE 2: As a mixin parent for your model.
          class MyBaseModel(object):

              # An existing base model that you have developed.

          class MyModel(MyBaseModel, BaseModel):

              # Standard SQLAlchemy declarative model definition goes here.

      .. tab:: Using ``declarative_base()``

        By calling the :func:`declarative_base` function from **SQLAthanor**:

        .. code-block:: python

          from sqlathanor import declarative_base

          MyBaseModel = declarative_base()

      .. tab:: Using ``@as_declarative``

        By decorating your base model class with the
        :func:`@as_declarative <as_declarative>` decorator:

        .. code-block:: python

          from sqlathanor import as_declarative

          @as_declarative
          class MyBaseModel(object):

              # Standard SQLAlchemy declarative model definition goes here.

    """

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

        :returns: :class:`list <python:list>` of
          :class:`Column <sqlalchemy:sqlalchemy.schema.Column>` objects corresponding to
          the table's primary key(s).
        :rtype: :class:`list <python:list>` of
          :class:`Column <sqlalchemy:sqlalchemy.schema.Column>`

        """
        return inspect(cls).primary_key

    @classmethod
    def get_primary_key_column_names(cls):
        """Retrieve the column names for the model's primary key columns.

        :rtype: :class:`list <python:list>` of :class:`str <python:str>`
        """
        return [str(x.name) for x in cls.get_primary_key_columns()]

    @property
    def primary_key_value(self):
        """The instance's primary key.

        .. note::

          If not :obj:`None <python:None>`, this value can always be passed to
          :meth:`Query.get() <sqlalchemy:sqlalchemy.orm.query.Query.get>`.

        .. warning::

          Returns :obj:`None <python:None>` if the instance is pending, in a transient state, or
          does not have a primary key.

        :returns: scalar or :class:`tuple <python:tuple>` value representing the
          primary key. For a composite primary key, the order of identifiers
          corresponds to the order with which the model's primary keys were
          defined. If no primary keys are available, will return :obj:`None <python:None>`.
        :rtype: scalar / :class:`tuple <python:tuple>` / :obj:`None <python:None>`

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
        :type include_private: :class:`bool <python:bool>`

        :param exclude_methods: If ``True``, excludes attributes that correspond to
          methods (are callable). Defaults to ``True``.
        :type exclude_methods: :class:`bool <python:bool>`

        .. note::

          This method will return all attributes, properties, and methods supported
          by the model - whether they map to database columns or not.

        :returns: An iterable of attribute names defined for the model.
        :rtype: :class:`list <python:list>` of :class:`str <python:str>`

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
        """Retrieve a list of
        :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
        objects corresponding to attributes whose values can be serialized from/to CSV,
        JSON, YAML, etc.

        .. note::

          This method operates *solely* on attribute configurations that have been
          declared, ignoring any configuration provided in the ``__<format>_support__``
          attribute.

        :param from_csv: If ``True``, includes attribute names that **can** be
          de-serialized from CSV strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from CSV strings. If :obj:`None <python:None>`,
          will not include attributes based on CSV de-serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type from_csv: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param to_csv: If ``True``, includes attribute names that **can** be
          serialized to CSV strings. If ``False``, includes attribute names
          that **cannot** be serialized to CSV strings. If :obj:`None <python:None>`,
          will not include attributes based on CSV serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type to_csv: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param from_json: If ``True``, includes attribute names that **can** be
          de-serialized from JSON strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from JSON strings. If :obj:`None <python:None>`,
          will not include attributes based on JSON de-serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type from_json: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param to_json: If ``True``, includes attribute names that **can** be
          serialized to JSON strings. If ``False``, includes attribute names
          that **cannot** be serialized to JSON strings. If :obj:`None <python:None>`,
          will not include attributes based on JSON serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type to_json: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param from_yaml: If ``True``, includes attribute names that **can** be
          de-serialized from YAML strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from YAML strings. If :obj:`None <python:None>`,
          will not include attributes based on YAML de-serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type from_yaml: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param to_yaml: If ``True``, includes attribute names that **can** be
          serialized to YAML strings. If ``False``, includes attribute names
          that **cannot** be serialized to YAML strings. If :obj:`None <python:None>`,
          will not include attributes based on YAML serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type to_yaml: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param from_dict: If ``True``, includes attribute names that **can** be
          de-serialized from :class:`dict <python:dict>` objects. If ``False``, includes
          attribute names that **cannot** be de-serialized from :class:`dict <python:dict>`
          objects. If :obj:`None <python:None>`, will not include attributes based on
          :class:`dict <python:dict>` de-serialization support (but may include them
          based on other parameters). Defaults to :obj:`None <python:None>`.
        :type from_dict: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param to_dict: If ``True``, includes attribute names that **can** be
          serialized to :class:`dict <python:dict>` objects. If ``False``, includes
          attribute names that **cannot** be serialized to :class:`dict <python:dict>`
          objects. If :obj:`None <python:None>`, will not include attributes based on
          :class:`dict <python:dict>` serialization support (but may include them
          based on other parameters). Defaults to :obj:`None <python:None>`.
        :type from_dict: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param exclude_private: If ``True``, will exclude private attributes whose
          names begin with a single underscore. Defaults to ``True``.
        :type exclude_private: :class:`bool <python:bool>`

        :returns: List of attribute configurations.
        :rtype: :class:`list <python:list>` of
        :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`

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
        """Retrieve a list of :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>` objects corresponding
        to attributes whose values can be serialized from/to CSV, JSON, YAML, etc.

        .. note::

          This method operates *solely* on attribute configurations that have been
          provided in the meta override ``__<format>_support__`` attribute.

        :param from_csv: If ``True``, includes attribute names that **can** be
          de-serialized from CSV strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from CSV strings. If :obj:`None <python:None>`,
          will not include attributes based on CSV de-serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type from_csv: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param to_csv: If ``True``, includes attribute names that **can** be
          serialized to CSV strings. If ``False``, includes attribute names
          that **cannot** be serialized to CSV strings. If :obj:`None <python:None>`,
          will not include attributes based on CSV serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type to_csv: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param from_json: If ``True``, includes attribute names that **can** be
          de-serialized from JSON strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from JSON strings. If :obj:`None <python:None>`,
          will not include attributes based on JSON de-serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type from_json: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param to_json: If ``True``, includes attribute names that **can** be
          serialized to JSON strings. If ``False``, includes attribute names
          that **cannot** be serialized to JSON strings. If :obj:`None <python:None>`,
          will not include attributes based on JSON serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type to_json: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param from_yaml: If ``True``, includes attribute names that **can** be
          de-serialized from YAML strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from YAML strings. If :obj:`None <python:None>`,
          will not include attributes based on YAML de-serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type from_yaml: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param to_yaml: If ``True``, includes attribute names that **can** be
          serialized to YAML strings. If ``False``, includes attribute names
          that **cannot** be serialized to YAML strings. If :obj:`None <python:None>`,
          will not include attributes based on YAML serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type to_yaml: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param from_dict: If ``True``, includes attribute names that **can** be
          de-serialized from :class:`dict <python:dict>` objects. If ``False``, includes
          attribute names that **cannot** be de-serialized from :class:`dict <python:dict>`
          objects. If :obj:`None <python:None>`, will not include attributes based on
          :class:`dict <python:dict>` de-serialization support (but may include them
          based on other parameters). Defaults to :obj:`None <python:None>`.
        :type from_dict: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param to_dict: If ``True``, includes attribute names that **can** be
          serialized to :class:`dict <python:dict>` objects. If ``False``, includes
          attribute names that **cannot** be serialized to :class:`dict <python:dict>`
          objects. If :obj:`None <python:None>`, will not include attributes based on
          :class:`dict <python:dict>` serialization support (but may include them
          based on other parameters). Defaults to :obj:`None <python:None>`.
        :type from_dict: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :returns: List of attribute configurations.
        :rtype: :class:`list <python:list>` of :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`

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
        """Retrieve a list of :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>` applied to the class."""
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
        """Retrieve a list of
        :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
        objects corresponding to attributes whose values can be serialized
        from/to CSV, JSON, YAML, etc.

        :param from_csv: If ``True``, includes attribute names that **can** be
          de-serialized from CSV strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from CSV strings. If :obj:`None <python:None>`,
          will not include attributes based on CSV de-serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type from_csv: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param to_csv: If ``True``, includes attribute names that **can** be
          serialized to CSV strings. If ``False``, includes attribute names
          that **cannot** be serialized to CSV strings. If :obj:`None <python:None>`,
          will not include attributes based on CSV serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type to_csv: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param from_json: If ``True``, includes attribute names that **can** be
          de-serialized from JSON strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from JSON strings. If :obj:`None <python:None>`,
          will not include attributes based on JSON de-serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type from_json: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param to_json: If ``True``, includes attribute names that **can** be
          serialized to JSON strings. If ``False``, includes attribute names
          that **cannot** be serialized to JSON strings. If :obj:`None <python:None>`,
          will not include attributes based on JSON serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type to_json: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param from_yaml: If ``True``, includes attribute names that **can** be
          de-serialized from YAML strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from YAML strings. If :obj:`None <python:None>`,
          will not include attributes based on YAML de-serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type from_yaml: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param to_yaml: If ``True``, includes attribute names that **can** be
          serialized to YAML strings. If ``False``, includes attribute names
          that **cannot** be serialized to YAML strings. If :obj:`None <python:None>`,
          will not include attributes based on YAML serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type to_yaml: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param from_dict: If ``True``, includes attribute names that **can** be
          de-serialized from :class:`dict <python:dict>` objects. If ``False``, includes
          attribute names that **cannot** be de-serialized from :class:`dict <python:dict>`
          objects. If :obj:`None <python:None>`, will not include attributes based on
          :class:`dict <python:dict>` de-serialization support (but may include them
          based on other parameters). Defaults to :obj:`None <python:None>`.
        :type from_dict: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param to_dict: If ``True``, includes attribute names that **can** be
          serialized to :class:`dict <python:dict>` objects. If ``False``, includes
          attribute names that **cannot** be serialized to :class:`dict <python:dict>`
          objects. If :obj:`None <python:None>`, will not include attributes based on
          :class:`dict <python:dict>` serialization support (but may include them
          based on other parameters). Defaults to :obj:`None <python:None>`.
        :type from_dict: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param exclude_private: If ``True``, will exclude private attributes whose
          names begin with a single underscore. Defaults to ``True``.
        :type exclude_private: :class:`bool <python:bool>`

        :returns: List of attribute configurations.
        :rtype: :class:`list <python:list>` of :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`

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
          CSV strings. If :obj:`None <python:None>`, ignores de-serialization
          configuration when determining which attribute configurations to return.
          Defaults to :obj:`None <python:None>`.
        :type deserialize: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param serialize: If ``True``, returns configurations for attributes that
          **can** be serialized to CSV strings. If ``False``,
          returns configurations for attributes that **cannot** be serialized to
          CSV strings. If :obj:`None <python:None>`, ignores serialization
          configuration when determining which attribute configurations to return.
          Defaults to :obj:`None <python:None>`.
        :type serialize: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :returns: Set of attribute serialization configurations that match the
          arguments supplied.
        :rtype: :class:`list <python:list>` of
          :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
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
          JSON strings. If :obj:`None <python:None>`, ignores de-serialization
          configuration when determining which attribute configurations to return.
          Defaults to :obj:`None <python:None>`.
        :type deserialize: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param serialize: If ``True``, returns configurations for attributes that
          **can** be serialized to JSON strings. If ``False``,
          returns configurations for attributes that **cannot** be serialized to
          JSON strings. If :obj:`None <python:None>`, ignores serialization
          configuration when determining which attribute configurations to return.
          Defaults to :obj:`None <python:None>`.
        :type serialize: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :returns: Set of attribute serialization configurations that match the
          arguments supplied.
        :rtype: :class:`list <python:list>` of
          :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
        """
        return [x for x in cls.get_serialization_config(from_json = deserialize,
                                                        to_json = serialize)]

    @classmethod
    def get_yaml_serialization_config(cls, deserialize = True, serialize = True):
        """Retrieve the YAML serialization configurations that apply for this object.

        :param deserialize: If ``True``, returns configurations for attributes that
          **can** be de-serialized from YAML strings. If ``False``,
          returns configurations for attributes that **cannot** be de-serialized from
          YAML strings. If :obj:`None <python:None>`, ignores de-serialization
          configuration when determining which attribute configurations to return.
          Defaults to :obj:`None <python:None>`.
        :type deserialize: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param serialize: If ``True``, returns configurations for attributes that
          **can** be serialized to YAML strings. If ``False``,
          returns configurations for attributes that **cannot** be serialized to
          YAML strings. If :obj:`None <python:None>`, ignores serialization
          configuration when determining which attribute configurations to return.
          Defaults to :obj:`None <python:None>`.
        :type serialize: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :returns: Set of attribute serialization configurations that match the
          arguments supplied.
        :rtype: :class:`list <python:list>` of
          :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`

        """
        return [x for x in cls.get_serialization_config(from_yaml = deserialize,
                                                        to_yaml = serialize)]

    @classmethod
    def get_dict_serialization_config(cls, deserialize = True, serialize = True):
        """Retrieve the :class:`dict <python:dict>` serialization configurations that
        apply for this object.

        :param deserialize: If ``True``, returns configurations for attributes that
          **can** be de-serialized from :class:`dict <python:dict>` objects. If ``False``,
          returns configurations for attributes that **cannot** be de-serialized from
          :class:`dict <python:dict>` objects. If :obj:`None <python:None>`, ignores de-serialization
          configuration when determining which attribute configurations to return.
          Defaults to :obj:`None <python:None>`.
        :type deserialize: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param serialize: If ``True``, returns configurations for attributes that
          **can** be serialized to :class:`dict <python:dict>` objects. If ``False``,
          returns configurations for attributes that **cannot** be serialized to
          :class:`dict <python:dict>` objects. If :obj:`None <python:None>`, ignores serialization
          configuration when determining which attribute configurations to return.
          Defaults to :obj:`None <python:None>`.
        :type serialize: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :returns: Set of attribute serialization configurations that match the
          arguments supplied.
        :rtype: :class:`list <python:list>` of
          :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
        """
        return [x for x in cls.get_serialization_config(from_dict = deserialize,
                                                        to_dict = serialize)]

    @classmethod
    def get_attribute_serialization_config(cls, attribute):
        """Retrieve the
        :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
        for ``attribute``.

        :param attribute: The attribute/column name whose serialization
          configuration should be returned.
        :type attribute: :class:`str <python:str>`

        :returns: The
          :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
          for ``attribute``.
        :rtype: :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`

        """
        attributes = cls._get_attribute_configurations()

        for config in attributes:
            if config.name == attribute:
                return config.copy()

        return None

    @classmethod
    def set_attribute_serialization_config(cls,
                                           attribute,
                                           config = None,
                                           supports_csv = None,
                                           csv_sequence = None,
                                           supports_json = None,
                                           supports_yaml = None,
                                           supports_dict = None,
                                           on_deserialize = None,
                                           on_serialize = None):
        """Set the serialization/de-serialization configuration for ``attribute``.

        .. note::

          Supplying keyword arguments like ``supports_csv`` or ``supports_json``
          will override any configuration set in ``config``.

        :param attribute: The name of the :term:`model attribute` whose
          serialization/de-serialization configuration is to be configured.
        :type attribute: :class:`str <python:str>`

        :param config: The
          :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
          to apply. If :obj:`None <python:None>`, will set particular values based
          on their corresponding keyword arguments.
        :type config: :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
          / :obj:`None <python:None>`

        :param supports_csv: Determines whether the column can be serialized to or
          de-serialized from CSV format.

          If ``True``, can be serialized to CSV and de-serialized from CSV. If
          ``False``, will not be included when serialized to CSV and will be ignored
          if present in a de-serialized CSV.

          Can also accept a 2-member :class:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          If :obj:`None <python:None>`, will retain whatever configuration is currently
          applied. Defaults to :obj:`None <python:None>`

        :type supports_csv: :class:`bool <python:bool>` / :class:`tuple <python:tuple>`
          of form (inbound: :class:`bool <python:bool>`, outbound:
          :class:`bool <python:bool>`) / :obj:`None <python:None>`

        :param supports_json: Determines whether the column can be serialized to or
          de-serialized from JSON format.

          If ``True``, can be serialized to JSON and de-serialized from JSON.
          If ``False``, will not be included when serialized to JSON and will be
          ignored if present in a de-serialized JSON.

          Can also accept a 2-member :class:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          If :obj:`None <python:None>`, will retain whatever configuration is currently
          applied. Defaults to :obj:`None <python:None>`

        :type supports_json: :class:`bool <python:bool>` / :class:`tuple <python:tuple>`
          of form (inbound: :class:`bool <python:bool>`, outbound:
          :class:`bool <python:bool>`) / :obj:`None <python:None>`

        :param supports_yaml: Determines whether the column can be serialized to or
          de-serialized from YAML format.

          If ``True``, can be serialized to YAML and de-serialized from YAML.
          If ``False``, will not be included when serialized to YAML and will be
          ignored if present in a de-serialized YAML.

          Can also accept a 2-member :class:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          If :obj:`None <python:None>`, will retain whatever configuration is currently
          applied. Defaults to :obj:`None <python:None>`

        :type supports_yaml: :class:`bool <python:bool>` / :class:`tuple <python:tuple>`
          of form (inbound: :class:`bool <python:bool>`, outbound:
          :class:`bool <python:bool>`) / :obj:`None <python:None>`

        :param supports_dict: Determines whether the column can be serialized to or
          de-serialized to a Python :class:`dict <python:dict>`.

          If ``True``, can be serialized to :class:`dict <python:dict>` and de-serialized
          from a :class:`dict <python:dict>`. If ``False``, will not be included
          when serialized to :class:`dict <python:dict>` and will be ignored if
          present in a de-serialized :class:`dict <python:dict>`.

          Can also accept a 2-member :class:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          If :obj:`None <python:None>`, will retain whatever configuration is currently
          applied. Defaults to :obj:`None <python:None>`

        :type supports_dict: :class:`bool <python:bool>` / :class:`tuple <python:tuple>`
          of form (inbound: :class:`bool <python:bool>`, outbound:
          :class:`bool <python:bool>`) / :obj:`None <python:None>`

        :param on_deserialize: A function that will be called when attempting to
          assign a de-serialized value to the column. This is intended to either coerce
          the value being assigned to a form that is acceptable by the column, or
          raise an exception if it cannot be coerced.

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

          If ``False``, will clear the current configuration to apply the default.

          If :obj:`None <python:None>`, will retain whatever configuration is currently
          applied. Defaults to :obj:`None <python:None>`

          .. tip::

            To clear the ``on_deserialize`` function, you can either supply a value
            of ``False`` or pass a :class:`dict <python:dict>` with particular formats
            set to :obj:`None <python:None>`:

            .. code-block:: python

              on_deserialize = {
                'csv': None,
                'json': None,
                'yaml': None,
                'dict': None
              }

              # is equivalent to:

              on_deserialize = False

            This will revert the `on_deserialize` function to the attribute's
            default `on_deserialize` function based on its data type.

        :type on_deserialize: callable / :class:`dict <python:dict>` with formats
          as keys and values as callables / :obj:`None <python:None>`

        :param on_serialize: A function that will be called when attempting to
          serialize a value from the column.

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

          If ``False``, will clear the current configuration to apply the default
          configuration.

          If :obj:`None <python:None>`, will retain whatever configuration is currently
          applied. Defaults to :obj:`None <python:None>`

          .. tip::

            To clear the ``on_serialize`` function, you need to pass ``False`` or a
            :class:`dict <python:dict>` with particular formats set to
            :obj:`None <python:None>`:

            .. code-block:: python

              on_serialize = {
                'csv': None,
                'json': None,
                'yaml': None,
                'dict': None
              }

              # is equivalent to

              on_serialize = False

            This will revert the `on_serialize` function to the attribute's
            default `on_serialize` function based on its data type.

        :type on_serialize: callable / :class:`dict <python:dict>` with formats
          as keys and values as callables / :obj:`None <python:None>` / ``False``

        :param csv_sequence: Indicates the numbered position that the column should be in
          in a valid CSV-version of the object.

          .. note::

            If not specified, the column will go after any columns that *do* have a
            ``csv_sequence`` assigned, sorted alphabetically.

            If two columns have the same ``csv_sequence``, they will be sorted
            alphabetically.

          If ``False``, will set the position to :obj:`None` <python:None>` which will
          position the column *after* any explicitly positioned columns in alphabetical
          order.

          If :obj:`None <python:None>`, will retain whatever configuration is currently
          applied. Defaults to :obj:`None <python:None>`

        :type csv_sequence: :class:`int <python:int>` / :obj:`None <python:None>` /
          ``False``

        :raises ValueError: if ``attribute`` does not match ``config.name`` if
          ``config`` is not :obj:`None <python:None>`

        """
        # pylint: disable=too-many-branches
        original_config = cls.get_attribute_serialization_config(attribute)
        if original_config is None:
            original_config = AttributeConfiguration(name = attribute)

        if config is None:
            new_config = AttributeConfiguration(name = attribute)
        else:
            new_config = config

        if attribute != new_config.name:
            raise ValueError(
                'attribute (%s) does not match config.name (%s)' % (attribute,
                                                                    config.name)
            )

        if supports_csv is not None:
            new_config.supports_csv = supports_csv
        elif new_config.get('supports_csv', None) is None:
            new_config.supports_csv = original_config['supports_csv']

        if supports_json is not None:
            new_config.supports_json = supports_json
        elif new_config.get('supports_json', None) is None:
            new_config.supports_json = original_config['supports_json']

        if supports_yaml is not None:
            new_config.supports_yaml = supports_yaml
        elif new_config.get('supports_yaml', None) is None:
            new_config.supports_yaml = original_config['supports_yaml']

        if supports_dict is not None:
            new_config.supports_dict = supports_dict
        elif new_config.get('supports_dict', None) is None:
            new_config.supports_dict = original_config['supports_dict']

        if csv_sequence is not None:
            if csv_sequence is False:
                csv_sequence = None

            new_config.csv_sequence = csv_sequence
        elif new_config.get('csv_sequence', None) is None:
            new_config['csv_sequence'] = original_config['csv_sequence']

        if on_deserialize is not None:
            if on_deserialize is False:
                on_deserialize = BLANK_ON_SERIALIZE

            new_config.on_deserialize = on_deserialize
        elif checkers.are_dicts_equivalent(new_config.on_deserialize,
                                           BLANK_ON_SERIALIZE):
            new_config.on_deserialize = original_config.on_deserialize

        if on_serialize is not None:
            if on_serialize is False:
                on_serialize = BLANK_ON_SERIALIZE

            new_config.on_serialize = on_serialize
        elif checkers.are_dicts_equivalent(new_config.on_serialize,
                                           BLANK_ON_SERIALIZE):
            new_config.on_serialize = original_config.on_serialize

        serialization = [x for x in cls.__serialization__
                         if x.name != attribute]
        serialization.append(new_config)

        cls.__serialization__ = [x for x in serialization]

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
        :type attribute: :class:`str <python:str>`

        :param from_csv: If ``True``, includes attribute names that **can** be
          de-serialized from CSV strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from CSV strings. If :obj:`None <python:None>`,
          will not include attributes based on CSV de-serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type from_csv: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param to_csv: If ``True``, includes attribute names that **can** be
          serialized to CSV strings. If ``False``, includes attribute names
          that **cannot** be serialized to CSV strings. If :obj:`None <python:None>`,
          will not include attributes based on CSV serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type to_csv: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param from_json: If ``True``, includes attribute names that **can** be
          de-serialized from JSON strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from JSON strings. If :obj:`None <python:None>`,
          will not include attributes based on JSON de-serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type from_json: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param to_json: If ``True``, includes attribute names that **can** be
          serialized to JSON strings. If ``False``, includes attribute names
          that **cannot** be serialized to JSON strings. If :obj:`None <python:None>`,
          will not include attributes based on JSON serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type to_json: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param from_yaml: If ``True``, includes attribute names that **can** be
          de-serialized from YAML strings. If ``False``, includes attribute names
          that **cannot** be de-serialized from YAML strings. If :obj:`None <python:None>`,
          will not include attributes based on YAML de-serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type from_yaml: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param to_yaml: If ``True``, includes attribute names that **can** be
          serialized to YAML strings. If ``False``, includes attribute names
          that **cannot** be serialized to YAML strings. If :obj:`None <python:None>`,
          will not include attributes based on YAML serialization support (but
          may include them based on other parameters). Defaults to :obj:`None <python:None>`.
        :type to_yaml: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param from_dict: If ``True``, includes attribute names that **can** be
          de-serialized from :class:`dict <python:dict>` objects. If ``False``, includes
          attribute names that **cannot** be de-serialized from :class:`dict <python:dict>`
          objects. If :obj:`None <python:None>`, will not include attributes based on
          :class:`dict <python:dict>` de-serialization support (but may include them
          based on other parameters). Defaults to :obj:`None <python:None>`.
        :type from_dict: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :param to_dict: If ``True``, includes attribute names that **can** be
          serialized to :class:`dict <python:dict>` objects. If ``False``, includes
          attribute names that **cannot** be serialized to :class:`dict <python:dict>`
          objects. If :obj:`None <python:None>`, will not include attributes based on
          :class:`dict <python:dict>` serialization support (but may include them
          based on other parameters). Defaults to :obj:`None <python:None>`.
        :type from_dict: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :returns: ``True`` if the attribute's serialization support matches,
          ``False`` if not, and :obj:`None <python:None>` if no serialization support was
          specified.
        :rtype: :class:`bool <python:bool>` / :obj:`None <python:None>`

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
        :type format: :class:`str <python:str>`

        :param attribute: The name of the attribute that whose serialized value
          should be returned.
        :type attribute: :class:`str <python:str>`

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
        :type format: :class:`str <python:str>`

        :param attribute: The name of the attribute that whose serialized value
          should be returned.
        :type attribute: :class:`str <python:str>`

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
          :term:`de-serialization`. If ``False``, returns columns that do *not*
          support deserialization. If :obj:`None <python:None>`, does not take
          deserialization into account. Defaults to ``True``.
        :type deserialize: :class:`bool <python:bool>`

        :param serialize: If ``True``, returns columns that support
          :term:`serialization`. If ``False``, returns columns that do *not*
          support serialization. If :obj:`None <python:None>`, does not take
          serialization into account. Defaults to ``True``.
        :type serialize: :class:`bool <python:bool>`

        :returns: List of CSV column names, sorted according to their configuration.
        :rtype: :class:`list <python:list>` of :class:`str <python:str>`
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
        r"""Retrieve a header string for a CSV representation of the model.

        :param delimiter: The character(s) to utilize between columns. Defaults to
          a pipe (``|``).
        :type delimiter: :class:`str <python:str>`

        :param wrap_all_strings: If ``True``, wraps any string data in the
          ``wrapper_character``. If ``None``, only wraps string data if it contains
          the ``delimiter``. Defaults to ``False``.
        :type wrap_all_strings: :class:`bool <python:bool>`

        :param null_text: The text value to use in place of empty values. Only
          applies if ``wrap_empty_values`` is ``True``. Defaults to ``'None'``.
        :type null_text: :class:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is necessary. Defaults to ``'``.
        :type wrapper_character: :class:`str <python:str>`

        :param double_wrapper_character_when_nested: If ``True``, will double the
          ``wrapper_character`` when it is found inside a column value. If ``False``,
          will precede the ``wrapper_character`` by the ``escape_character`` when
          it is found inside a column value. Defaults to ``False``.
        :type double_wrapper_character_when_nested: :class:`bool <python:bool>`

        :param escape_character: The character to use when escaping nested wrapper
          characters. Defaults to ``\``.
        :type escape_character: :class:`str <python:str>`

        :param line_terminator: The character used to mark the end of a line.
          Defaults to ``\r\n``.
        :type line_terminator: :class:`str <python:str>`

        :returns: A string ending in ``line_terminator`` with the model's CSV column names
          listed, separated by the ``delimiter``.
        :rtype: :class:`str <python:str>`
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
        r"""Return the CSV representation of the model instance (record).

        :param delimiter: The delimiter used between columns. Defaults to ``|``.
        :type delimiter: :class:`str <python:str>`

        :param wrap_all_strings: If ``True``, wraps any string data in the
          ``wrapper_character``. If ``None``, only wraps string data if it contains
          the ``delimiter``. Defaults to ``False``.
        :type wrap_all_strings: :class:`bool <python:bool>`

        :param null_text: The text value to use in place of empty values. Only
          applies if ``wrap_empty_values`` is ``True``. Defaults to ``'None'``.
        :type null_text: :class:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is necessary. Defaults to ``'``.
        :type wrapper_character: :class:`str <python:str>`

        :param double_wrapper_character_when_nested: If ``True``, will double the
          ``wrapper_character`` when it is found inside a column value. If ``False``,
          will precede the ``wrapper_character`` by the ``escape_character`` when
          it is found inside a column value. Defaults to ``False``.
        :type double_wrapper_character_when_nested: :class:`bool <python:bool>`

        :param escape_character: The character to use when escaping nested wrapper
          characters. Defaults to ``\``.
        :type escape_character: :class:`str <python:str>`

        :param line_terminator: The character used to mark the end of a line.
          Defaults to ``\r\n``.
        :type line_terminator: :class:`str <python:str>`

        :returns: Data from the object in CSV format ending in ``line_terminator``.
        :rtype: :class:`str <python:str>`
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
        r"""Retrieve a CSV string with the object's data.

        :param include_header: If ``True``, will include a header row with column
          labels. If ``False``, will not include a header row. Defaults to ``True``.
        :type include_header: :class:`bool <python:bool>`

        :param delimiter: The delimiter used between columns. Defaults to ``|``.
        :type delimiter: :class:`str <python:str>`

        :param wrap_all_strings: If ``True``, wraps any string data in the
          ``wrapper_character``. If ``None``, only wraps string data if it contains
          the ``delimiter``. Defaults to ``False``.
        :type wrap_all_strings: :class:`bool <python:bool>`

        :param null_text: The text value to use in place of empty values. Only
          applies if ``wrap_empty_values`` is ``True``. Defaults to ``'None'``.
        :type null_text: :class:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is necessary. Defaults to ``'``.
        :type wrapper_character: :class:`str <python:str>`

        :param double_wrapper_character_when_nested: If ``True``, will double the
          ``wrapper_character`` when it is found inside a column value. If ``False``,
          will precede the ``wrapper_character`` by the ``escape_character`` when
          it is found inside a column value. Defaults to ``False``.
        :type double_wrapper_character_when_nested: :class:`bool <python:bool>`

        :param escape_character: The character to use when escaping nested wrapper
          characters. Defaults to ``\``.
        :type escape_character: :class:`str <python:str>`

        :param line_terminator: The character used to mark the end of a line.
          Defaults to ``\r\n``.
        :type line_terminator: :class:`str <python:str>`

        :returns: Data from the object in CSV format ending in a newline (``\n``).
        :rtype: :class:`str <python:str>`
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
        """Generate a :class:`dict <python:dict>` from a CSV record.

        .. tip::

          Unwrapped empty column values are automatically interpreted as null
          (:obj:`None <python:None>`).

        :param csv_data: The CSV record. Should be a single row and should **not**
          include column headers.
        :type csv_data: :class:`str <python:str>`

        :param delimiter: The delimiter used between columns. Defaults to ``|``.
        :type delimiter: :class:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is applied. Defaults to ``'``.
        :type wrapper_character: :class:`str <python:str>`

        :param null_text: The string used to indicate an empty value if empty
          values are wrapped. Defaults to `None`.
        :type null_text: :class:`str <python:str>`

        :returns: A :class:`dict <python:dict>` representation of the CSV record.
        :rtype: :class:`dict <python:dict>`

        :raises DeserializationError: if ``csv_data`` is not a valid
          :class:`str <python:str>`
        :raises CSVStructureError: if the columns in ``csv_data`` do not match
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
            raise CSVStructureError('expected 1 row of data, received %s' % len(csv_reader))
        elif len(rows) == 0:
            data = {}
            for column_name in csv_column_names:
                data[column_name] = None
        else:
            data = rows[0]

        if data.get(None, None) is not None:
            raise CSVStructureError('expected %s fields, found %s' % (len(csv_column_names),
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
        """Update the model instance from a CSV record.

        .. tip::

          Unwrapped empty column values are automatically interpreted as null
          (:obj:`None <python:None>`).

        :param csv_data: The CSV record. Should be a single row and should **not**
          include column headers.
        :type csv_data: :class:`str <python:str>`

        :param delimiter: The delimiter used between columns. Defaults to ``|``.
        :type delimiter: :class:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is applied. Defaults to ``'``.
        :type wrapper_character: :class:`str <python:str>`

        :param null_text: The string used to indicate an empty value if empty
          values are wrapped. Defaults to `None`.
        :type null_text: :class:`str <python:str>`

        :raises DeserializationError: if ``csv_data`` is not a valid
          :class:`str <python:str>`
        :raises CSVStructureError: if the columns in ``csv_data`` do not match
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
          (:obj:`None <python:None>`).

        :param csv_data: The CSV record. Should be a single row and should **not**
          include column headers.
        :type csv_data: :class:`str <python:str>`

        :param delimiter: The delimiter used between columns. Defaults to ``|``.
        :type delimiter: :class:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is applied. Defaults to ``'``.
        :type wrapper_character: :class:`str <python:str>`

        :param null_text: The string used to indicate an empty value if empty
          values are wrapped. Defaults to `None`.
        :type null_text: :class:`str <python:str>`

        :returns: A :term:`model instance` created from the record.
        :rtype: model instance

        :raises DeserializationError: if ``csv_data`` is not a valid
          :class:`str <python:str>`
        :raises CSVStructureError: if the columns in ``csv_data`` do not match
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
        """Return a :class:`dict <python:dict>` representation of the object.

        .. warning::

          This method is an **intermediate** step that is used to produce the
          contents for certain public JSON, YAML, and :class:`dict <python:dict>`
          serialization methods. It should not be called directly.

        :param format: The format to which the :class:`dict <python:dict>` will
          ultimately be serialized. Accepts: ``'csv'``, ``'json'``, ``'yaml'``, and
          ``'dict'``.
        :type format: :class:`str <python:str>`

        :param max_nesting: The maximum number of levels that the resulting
          :class:`dict <python:dict>` object can be nested. If set to ``0``, will
          not nest other serializable objects. Defaults to ``0``.
        :type max_nesting: :class:`int <python:int>`

        :param current_nesting: The current nesting level at which the
          :class:`dict <python:dict>` representation will reside. Defaults to ``0``.
        :type current_nesting: :class:`int <python:int>`

        :returns: A :class:`dict <python:dict>` representation of the object.
        :rtype: :class:`dict <python:dict>`

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
                    value = item._to_dict(format,                               # pylint: disable=protected-access
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
        :type max_nesting: :class:`int <python:int>`

        :param current_nesting: The current nesting level at which the
          :class:`dict <python:dict>` representation will reside. Defaults to ``0``.
        :type current_nesting: :class:`int <python:int>`

        :param serialize_function: Optionally override the default JSON serializer.
          Defaults to :obj:`None <python:None>`, which applies the default
          :doc:`simplejson <simplejson:index>` JSON serializer.

          .. note::

            Use the ``serialize_function`` parameter to override the default
            JSON serializer.

            A valid ``serialize_function`` is expected to accept a single
            :class:`dict <python:dict>` and return a :class:`str <python:str>`,
            similar to :func:`simplejson.dumps() <simplejson:simplejson.dumps>`.

            If you wish to pass additional arguments to your ``serialize_function``
            pass them as keyword arguments (in ``kwargs``).

        :type serialize_function: callable / :obj:`None <python:None>`

        :param kwargs: Optional keyword parameters that are passed to the
          JSON serializer function. By default, these are options which are passed
          to :func:`simplejson.dumps() <simplejson:simplejson.dumps>`.
        :type kwargs: keyword arguments

        :returns: A :class:`str <python:str>` with the JSON representation of the
          object.
        :rtype: :class:`str <python:str>`

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
        :type max_nesting: :class:`int <python:int>`

        :param current_nesting: The current nesting level at which the
          representation will reside. Defaults to ``0``.
        :type current_nesting: :class:`int <python:int>`

        :param serialize_function: Optionally override the default YAML serializer.
          Defaults to :obj:`None <python:None>`, which calls the default ``yaml.dump()``
          function from the `PyYAML <https://github.com/yaml/pyyaml>`_ library.

          .. note::

            Use the ``serialize_function`` parameter to override the default
            YAML serializer.

            A valid ``serialize_function`` is expected to
            accept a single :class:`dict <python:dict>` and return a
            :class:`str <python:str>`, similar to ``yaml.dump()``.

            If you wish to pass additional arguments to your ``serialize_function``
            pass them as keyword arguments (in ``kwargs``).

        :type serialize_function: callable / :obj:`None <python:None>`

        :param kwargs: Optional keyword parameters that are passed to the
          YAML serializer function. By default, these are options which are passed
          to ``yaml.dump()``.
        :type kwargs: keyword arguments

        :returns: A :class:`str <python:str>` with the JSON representation of the
          object.
        :rtype: :class:`str <python:str>`

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
        """Return a :class:`dict <python:dict>` representation of the object.

        :param max_nesting: The maximum number of levels that the resulting
          :class:`dict <python:dict>` object can be nested. If set to ``0``, will
          not nest other serializable objects. Defaults to ``0``.
        :type max_nesting: :class:`int <python:int>`

        :param current_nesting: The current nesting level at which the
          :class:`dict <python:dict>` representation will reside. Defaults to ``0``.
        :type current_nesting: :class:`int <python:int>`

        :returns: A :class:`dict <python:dict>` representation of the object.
        :rtype: :class:`dict <python:dict>`

        :raises SerializableAttributeError: if attributes is empty
        :raises MaximumNestingExceededError: if ``current_nesting`` is greater
          than ``max_nesting``
        :raises MaximumNestingExceededWarning: if an attribute requires nesting
          beyond ``max_nesting``

        """
        return self._to_dict('dict',
                             max_nesting = max_nesting,
                             current_nesting = current_nesting)

    @classmethod
    def _parse_dict(cls,
                    input_data,
                    format,
                    error_on_extra_keys = True,
                    drop_extra_keys = False):
        """Generate a processed :class:`dict <python:dict>` object from
        in-bound :class:`dict <python:dict>` data.

        :param input_data: An inbound :class:`dict <python:dict>` object which
          can be processed for de-serialization.
        :type input_data: :class:`dict <python:dict>`

        :param format: The format from which ``input_data`` was received. Accepts:
          ``'csv'``, ``'json'``, ``'yaml'``, and ``'dict'``.
        :type format: :class:`str <python:str>`

        :param error_on_extra_keys: If ``True``, will raise an error if an
          unrecognized key is found in ``dict_data``. If ``False``, will
          either drop or include the extra key in the result, as configured in
          the ``drop_extra_keys`` parameter. Defaults to ``True``.
        :type error_on_extra_keys: :class:`bool <python:bool>`

        :param drop_extra_keys: If ``True``, will omit unrecognized top-level keys
          from the resulting :class:`dict <python:dict>`. If ``False``, will
          include unrecognized keys or raise an error based on the configuration of
          the ``error_on_extra_keys`` parameter. Defaults to ``False``.
        :type drop_extra_keys: :class:`bool <python:bool>`

        :returns: A processed :class:`dict <python:dict>` object that has had
          :term:`deserializer functions` applied to it.
        :rtype: :class:`dict <python:dict>`

        :raises ExtraKeyError: if ``error_on_extra_keys`` is ``True`` and
          ``input_data`` contains top-level keys that are not recognized as
          attributes for the instance model.
        :raises DeserializationError: if ``input_data`` is
          not a :class:`dict <python:dict>` or JSON object serializable to a
          :class:`dict <python:dict>` or if ``input_data`` is empty.
        :raises InvalidFormatError: if ``format`` is not a supported value
        """
        if format not in ['csv', 'json', 'yaml', 'dict']:
            raise InvalidFormatError("format '%s' not supported" % format)

        try:
            input_data = validators.dict(input_data,
                                         allow_empty = True,
                                         json_serializer = json)
        except ValueError:
            raise DeserializationError('input_data is not a dict')

        if not input_data or len(input_data.keys()) == 0:
            raise DeserializationError("input_data is empty")

        dict_object = {}

        if format == 'csv':
            attribute_getter = cls.get_csv_serialization_config
        elif format == 'json':
            attribute_getter = cls.get_json_serialization_config
        elif format == 'yaml':
            attribute_getter = cls.get_yaml_serialization_config
        elif format == 'dict':
            attribute_getter = cls.get_dict_serialization_config

        attributes = [x
                      for x in attribute_getter(deserialize = True,
                                                serialize = None)
                      if hasattr(cls, x.name)]

        if not attributes:
            raise DeserializableAttributeError(
                "'%s' has no '%s' de-serializable attributes" % (type(cls.__name__),
                                                                 format)
            )

        attribute_names = [x.name for x in attributes]
        extra_keys = [x for x in input_data.keys()
                      if x not in attribute_names]
        if extra_keys and error_on_extra_keys:
            raise ExtraKeyError("input data had extra keys: %s" % extra_keys)

        for attribute in attributes:
            key = attribute.name
            try:
                value = input_data.pop(key)
            except KeyError:
                continue

            value = cls._get_deserialized_value(value,
                                                format,
                                                attribute.name)

            dict_object[key] = value

        if input_data and not drop_extra_keys:
            for key in input_data:
                dict_object[key] = input_data[key]

        return dict_object

    def update_from_dict(self,
                         input_data,
                         error_on_extra_keys = True,
                         drop_extra_keys = False):
        """Update the model instance from data in a :class:`dict <python:dict>` object.

        :param input_data: The input :class:`dict <python:dict>`
        :type input_data: :class:`dict <python:dict>`

        :param error_on_extra_keys: If ``True``, will raise an error if an
          unrecognized key is found in ``input_data``. If ``False``, will
          either drop or include the extra key in the result, as configured in
          the ``drop_extra_keys`` parameter. Defaults to ``True``.

          .. warning::

            Be careful setting ``error_on_extra_keys`` to ``False``.

            This method's last step attempts to set an attribute on the model
            instance for every top-level key in the parsed/processed input data.

            If there is an extra key that cannot be set as an attribute on your
            model instance, it *will* raise
            :class:`AttributeError <python:AttributeError>`.

        :type error_on_extra_keys: :class:`bool <python:bool>`

        :param drop_extra_keys: If ``True``, will omit unrecognized top-level keys
          from the resulting :class:`dict <python:dict>`. If ``False``, will
          include unrecognized keys or raise an error based on the configuration of
          the ``error_on_extra_keys`` parameter. Defaults to ``False``.
        :type drop_extra_keys: :class:`bool <python:bool>`

        :raises ExtraKeyError: if ``error_on_extra_keys`` is ``True`` and
          ``input_data`` contains top-level keys that are not recognized as
          attributes for the instance model.
        :raises DeserializationError: if ``input_data`` is
          not a :class:`dict <python:dict>` or JSON object serializable to a
          :class:`dict <python:dict>` or if ``input_data`` is empty.

        """
        data = self._parse_dict(input_data,
                                'dict',
                                error_on_extra_keys = error_on_extra_keys,
                                drop_extra_keys = drop_extra_keys)

        for key in data:
            setattr(self, key, data[key])

    @classmethod
    def new_from_dict(cls,
                      input_data,
                      error_on_extra_keys = True,
                      drop_extra_keys = False):
        """Update the model instance from data in a :class:`dict <python:dict>` object.

        :param input_data: The input :class:`dict <python:dict>`
        :type input_data: :class:`dict <python:dict>`

        :param error_on_extra_keys: If ``True``, will raise an error if an
          unrecognized key is found in ``input_data``. If ``False``, will
          either drop or include the extra key in the result, as configured in
          the ``drop_extra_keys`` parameter. Defaults to ``True``.

          .. warning::

            Be careful setting ``error_on_extra_keys`` to ``False``.

            This method's last step passes the keys/values of the processed input
            data to your model's ``__init__()`` method.

            If your instance's ``__init__()`` method does not support your extra keys,
            it will likely raise a :class:`TypeError <python:TypeError>`.

        :type error_on_extra_keys: :class:`bool <python:bool>`

        :param drop_extra_keys: If ``True``, will omit unrecognized top-level keys
          from the resulting :class:`dict <python:dict>`. If ``False``, will
          include unrecognized keys or raise an error based on the configuration of
          the ``error_on_extra_keys`` parameter. Defaults to ``False``.
        :type drop_extra_keys: :class:`bool <python:bool>`

        :raises ExtraKeyError: if ``error_on_extra_keys`` is ``True`` and
          ``input_data`` contains top-level keys that are not recognized as
          attributes for the instance model.
        :raises DeserializationError: if ``input_data`` is
          not a :class:`dict <python:dict>` or JSON object serializable to a
          :class:`dict <python:dict>` or if ``input_data`` is empty.

        """
        data = cls._parse_dict(input_data,
                               'dict',
                               error_on_extra_keys = error_on_extra_keys,
                               drop_extra_keys = drop_extra_keys)

        return cls(**data)

    def update_from_yaml(self,
                         input_data,
                         deserialize_function = None,
                         error_on_extra_keys = True,
                         drop_extra_keys = False,
                         **kwargs):
        """Update the model instance from data in a YAML string.

        :param input_data: The YAML data to de-serialize.
        :type input_data: :class:`str <python:str>`

        :param deserialize_function: Optionally override the default YAML deserializer.
          Defaults to :obj:`None <python:None>`, which calls the default ``yaml.safe_load()``
          function from the `PyYAML <https://github.com/yaml/pyyaml>`_ library.

          .. note::

            Use the ``deserialize_function`` parameter to override the default
            YAML deserializer.

            A valid ``deserialize_function`` is expected to accept a single
            :class:`str <python:str>` and return a :class:`dict <python:dict>`,
            similar to ``yaml.safe_load()``.

            If you wish to pass additional arguments to your ``deserialize_function``
            pass them as keyword arguments (in ``kwargs``).

        :type deserialize_function: callable / :obj:`None <python:None>`

        :param error_on_extra_keys: If ``True``, will raise an error if an
          unrecognized key is found in ``input_data``. If ``False``, will
          either drop or include the extra key in the result, as configured in
          the ``drop_extra_keys`` parameter. Defaults to ``True``.

          .. warning::

            Be careful setting ``error_on_extra_keys`` to ``False``.

            This method's last step attempts to set an attribute on the model
            instance for every top-level key in the parsed/processed input data.

            If there is an extra key that cannot be set as an attribute on your
            model instance, it *will* raise
            :class:`AttributeError <python:AttributeError>`.

        :type error_on_extra_keys: :class:`bool <python:bool>`

        :param drop_extra_keys: If ``True``, will ignore unrecognized keys in the
          input data. If ``False``, will include unrecognized keys or raise an
          error based on the configuration of the ``error_on_extra_keys`` parameter.
          Defaults to ``False``.
        :type drop_extra_keys: :class:`bool <python:bool>`

        :param kwargs: Optional keyword parameters that are passed to the
          YAML deserializer function. By default, these are options which are passed
          to ``yaml.safe_load()``.
        :type kwargs: keyword arguments

        :raises ExtraKeyError: if ``error_on_extra_keys`` is ``True`` and
          ``input_data`` contains top-level keys that are not recognized as
          attributes for the instance model.
        :raises DeserializationError: if ``input_data`` is
          not a :class:`str <python:str>` YAML de-serializable object to a
          :class:`dict <python:dict>` or if ``input_data`` is empty.

        """
        from_yaml = parse_yaml(input_data,
                               deserialize_function = deserialize_function,
                               **kwargs)

        data = self._parse_dict(from_yaml,
                                'yaml',
                                error_on_extra_keys = error_on_extra_keys,
                                drop_extra_keys = drop_extra_keys)

        for key in data:
            setattr(self, key, data[key])

    @classmethod
    def new_from_yaml(cls,
                      input_data,
                      deserialize_function = None,
                      error_on_extra_keys = True,
                      drop_extra_keys = False,
                      **kwargs):
        """Create a new model instance from data in YAML.

        :param input_data: The input YAML data.
        :type input_data: :class:`str <python:str>`

        :param deserialize_function: Optionally override the default YAML deserializer.
          Defaults to :obj:`None <python:None>`, which calls the default ``yaml.safe_load()``
          function from the `PyYAML <https://github.com/yaml/pyyaml>`_ library.

          .. note::

            Use the ``deserialize_function`` parameter to override the default
            YAML deserializer.

            A valid ``deserialize_function`` is expected to accept a single
            :class:`str <python:str>` and return a :class:`dict <python:dict>`,
            similar to ``yaml.safe_load()``.

            If you wish to pass additional arguments to your ``deserialize_function``
            pass them as keyword arguments (in ``kwargs``).

        :type deserialize_function: callable / :obj:`None <python:None>`

        :param error_on_extra_keys: If ``True``, will raise an error if an
          unrecognized key is found in ``input_data``. If ``False``, will
          either drop or include the extra key in the result, as configured in
          the ``drop_extra_keys`` parameter. Defaults to ``True``.

          .. warning::

            Be careful setting ``error_on_extra_keys`` to ``False``.

            This method's last step passes the keys/values of the processed input
            data to your model's ``__init__()`` method.

            If your instance's ``__init__()`` method does not support your extra keys,
            it will likely raise a :class:`TypeError <python:TypeError>`.

        :type error_on_extra_keys: :class:`bool <python:bool>`

        :param drop_extra_keys: If ``True``, will ignore unrecognized top-level
          keys in ``input_data``. If ``False``, will include unrecognized keys
          or raise an error based on the configuration of
          the ``error_on_extra_keys`` parameter. Defaults to ``False``.
        :type drop_extra_keys: :class:`bool <python:bool>`

        :raises ExtraKeyError: if ``error_on_extra_keys`` is ``True`` and
          ``input_data`` contains top-level keys that are not recognized as
          attributes for the instance model.
        :raises DeserializationError: if ``input_data`` is
          not a :class:`dict <python:dict>` or JSON object serializable to a
          :class:`dict <python:dict>` or if ``input_data`` is empty.

        """
        from_yaml = parse_yaml(input_data,
                               deserialize_function = deserialize_function,
                               **kwargs)

        data = cls._parse_dict(from_yaml,
                               'yaml',
                               error_on_extra_keys = error_on_extra_keys,
                               drop_extra_keys = drop_extra_keys)

        return cls(**data)

    def update_from_json(self,
                         input_data,
                         deserialize_function = None,
                         error_on_extra_keys = True,
                         drop_extra_keys = False,
                         **kwargs):
        """Update the model instance from data in a JSON string.

        :param input_data: The JSON data to de-serialize.
        :type input_data: :class:`str <python:str>`

        :param deserialize_function: Optionally override the default JSON deserializer.
          Defaults to :obj:`None <python:None>`, which calls the default
          :func:`simplejson.loads() <simplejson:simplejson.loads>` function from
          the :doc:`simplejson <simplejson:index>` library.

          .. note::

            Use the ``deserialize_function`` parameter to override the default
            JSON deserializer.

            A valid ``deserialize_function`` is expected to
            accept a single :class:`str <python:str>` and return a
            :class:`dict <python:dict>`, similar to
            :func:`simplejson.loads() <simplejson:simplejson.loads>`.

            If you wish to pass additional arguments to your ``deserialize_function``
            pass them as keyword arguments (in ``kwargs``).

        :type deserialize_function: callable / :obj:`None <python:None>`

        :param error_on_extra_keys: If ``True``, will raise an error if an
          unrecognized key is found in ``input_data``. If ``False``, will
          either drop or include the extra key in the result, as configured in
          the ``drop_extra_keys`` parameter. Defaults to ``True``.

          .. warning::

            Be careful setting ``error_on_extra_keys`` to ``False``.

            This method's last step attempts to set an attribute on the model
            instance for every top-level key in the parsed/processed input data.

            If there is an extra key that cannot be set as an attribute on your
            model instance, it *will* raise
            :class:`AttributeError <python:AttributeError>`.

        :type error_on_extra_keys: :class:`bool <python:bool>`

        :param drop_extra_keys: If ``True``, will ignore unrecognized keys in the
          input data. If ``False``, will include unrecognized keys or raise an
          error based on the configuration of the ``error_on_extra_keys`` parameter.
          Defaults to ``False``.
        :type drop_extra_keys: :class:`bool <python:bool>`

        :param kwargs: Optional keyword parameters that are passed to the
          JSON deserializer function.By default, these are options which are passed
          to :func:`simplejson.loads() <simplejson:simplejson.loads>`.
        :type kwargs: keyword arguments

        :raises ExtraKeyError: if ``error_on_extra_keys`` is ``True`` and
          ``input_data`` contains top-level keys that are not recognized as
          attributes for the instance model.
        :raises DeserializationError: if ``input_data`` is
          not a :class:`str <python:str>` JSON de-serializable object to a
          :class:`dict <python:dict>` or if ``input_data`` is empty.

        """
        from_json = parse_json(input_data,
                               deserialize_function = deserialize_function,
                               **kwargs)

        data = self._parse_dict(from_json,
                                'json',
                                error_on_extra_keys = error_on_extra_keys,
                                drop_extra_keys = drop_extra_keys)

        for key in data:
            setattr(self, key, data[key])

    @classmethod
    def new_from_json(cls,
                      input_data,
                      deserialize_function = None,
                      error_on_extra_keys = True,
                      drop_extra_keys = False,
                      **kwargs):
        """Create a new model instance from data in JSON.

        :param input_data: The input JSON data.
        :type input_data: :class:`str <python:str>`

        :param deserialize_function: Optionally override the default JSON deserializer.
          Defaults to :obj:`None <python:None>`, which calls the default
          :func:`simplejson.loads() <simplejson:simplejson.loads>`
          function from the doc:`simplejson <simplejson:index>` library.

          .. note::

            Use the ``deserialize_function`` parameter to override the default
            JSON deserializer.

            A valid ``deserialize_function`` is expected to accept a single
            :class:`str <python:str>` and return a :class:`dict <python:dict>`,
            similar to :func:`simplejson.loads() <simplejson:simplejson.loads>`.

            If you wish to pass additional arguments to your ``deserialize_function``
            pass them as keyword arguments (in ``kwargs``).

        :type deserialize_function: callable / :obj:`None <python:None>`

        :param error_on_extra_keys: If ``True``, will raise an error if an
          unrecognized key is found in ``input_data``. If ``False``, will
          either drop or include the extra key in the result, as configured in
          the ``drop_extra_keys`` parameter. Defaults to ``True``.

          .. warning::

            Be careful setting ``error_on_extra_keys`` to ``False``.

            This method's last step passes the keys/values of the processed input
            data to your model's ``__init__()`` method.

            If your instance's ``__init__()`` method does not support your extra keys,
            it will likely raise a :class:`TypeError <python:TypeError>`.

        :type error_on_extra_keys: :class:`bool <python:bool>`

        :param drop_extra_keys: If ``True``, will ignore unrecognized top-level
          keys in ``input_data``. If ``False``, will include unrecognized keys
          or raise an error based on the configuration of
          the ``error_on_extra_keys`` parameter. Defaults to ``False``.
        :type drop_extra_keys: :class:`bool <python:bool>`

        :param kwargs: Optional keyword parameters that are passed to the
          JSON deserializer function. By default, these are options which are passed
          to :func:`simplejson.loads() <simplejson:simplejson.loads>`.
        :type kwargs: keyword arguments

        :raises ExtraKeyError: if ``error_on_extra_keys`` is ``True`` and
          ``input_data`` contains top-level keys that are not recognized as
          attributes for the instance model.
        :raises DeserializationError: if ``input_data`` is
          not a :class:`dict <python:dict>` or JSON object serializable to a
          :class:`dict <python:dict>` or if ``input_data`` is empty.

        """
        from_json = parse_json(input_data,
                               deserialize_function = deserialize_function,
                               **kwargs)

        data = cls._parse_dict(from_json,
                               'json',
                               error_on_extra_keys = error_on_extra_keys,
                               drop_extra_keys = drop_extra_keys)

        return cls(**data)

def declarative_base(cls, **kwargs):
    """Construct a base class for declarative class definitions.

    The new base class will be given a metaclass that produces appropriate
    :class:`Table <sqlalchemy:sqlalchemy.schema.Table>` objects and makes the
    appropriate :func:`mapper <sqlalchemy:sqlalchemy.orm.mapper>` calls based on the
    information provided declaratively in the class and any subclasses of the class.

    :param cls: Defaults to :class:`BaseModel` to provide  serialization/de-serialization
      support.

      If a :class:`tuple <python:tuple>` of classes, will include :class:`BaseModel`
      in that list of classes to mixin serialization/de-serialization support.

      If not :obj:`None <python:None>` and not a :class:`tuple <python:tuple>`, will mixin
      :class:`BaseModel` with the value passed to provide
      serialization/de-serialization support.
    :type cls: :obj:`None <python:None>` / :class:`tuple <python:tuple>` of classes / class object

    :param kwargs: Additional keyword arguments supported by the original
      :func:`sqlalchemy.ext.declarative.declarative_base() <sqlalchemy:sqlalchemy.ext.declarative.declarative_base>`
      function
    :type kwargs: keyword arguments

    :returns: Base class for declarative class definitions with support for
      serialization and de-serialization.

    """
    cls = kwargs.pop('cls', None)
    if cls is None:
        cls = BaseModel
    elif isinstance(cls, tuple):
        class_list = [x for x in cls]
        class_list.insert(0, BaseModel)
        cls = (x for x in class_list)
    elif checkers.is_iterable(cls):
        class_list = [BaseModel]
        class_list.extend(cls)
        cls = (x for x in class_list)

    return SA_declarative_base(cls = cls, **kwargs)

def as_declarative(**kw):
    """Class decorator for :func:`declarative_base`.

    Provides a syntactical shortcut to the ``cls`` argument
    sent to :func:`declarative_base`, allowing the base class
    to be converted in-place to a "declarative" base:

    .. code-block:: python

        from sqlathanor import as_declarative

        @as_declarative()
        class Base(object):
            @declared_attr
            def __tablename__(cls):
                return cls.__name__.lower()

            id = Column(Integer,
                        primary_key = True,
                        supports_csv = True)

        class MyMappedClass(Base):
            # ...

    .. tip::

      All keyword arguments passed to :func:`as_declarative` are passed
      along to :func:`declarative_base`.

    .. seealso::

      * :func:`declarative_base() <declarative_base>`
    """
    def decorate(cls):
        kw['cls'] = cls
        kw['name'] = cls.__name__
        return declarative_base(**kw)

    return decorate
