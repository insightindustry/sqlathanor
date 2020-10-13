# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

import inspect as inspect_
import yaml

from sqlathanor._compat import json
from sqlathanor.attributes import validate_serialization_config
from sqlathanor.utilities import format_to_tuple
from sqlathanor.default_serializers import get_default_serializer
from sqlathanor.default_deserializers import get_default_deserializer

from sqlathanor.declarative._primary_key_mixin import PrimaryKeyMixin
from sqlathanor.declarative._base_configuration_mixin import ConfigurationMixin
from sqlathanor.declarative._csv_support import CSVSupportMixin
from sqlathanor.declarative._json_support import JSONSupportMixin
from sqlathanor.declarative._yaml_support import YAMLSupportMixin
from sqlathanor.declarative._dict_support import DictSupportMixin

from sqlathanor.errors import UnsupportedSerializationError, ValueSerializationError, \
    UnsupportedDeserializationError, ValueDeserializationError


class BaseModel(PrimaryKeyMixin,
                ConfigurationMixin,
                CSVSupportMixin,
                JSONSupportMixin,
                YAMLSupportMixin,
                DictSupportMixin):
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
        if self.__serialization__ and isinstance(self.__serialization__, dict):
            for key in self.__serialization__:
                self.__serialization__[key] = validate_serialization_config(self.__serialization__[key])
        elif self.__serialization__:
            self.__serialization__ = validate_serialization_config(self.__serialization__)
        else:
            self.__serialization__ = []

        super(BaseModel, self).__init__(*args, **kwargs)

    def _get_serialized_value(self,
                              format,
                              attribute,
                              config_set = None):
        """Retrieve the value of ``attribute`` after applying the attribute's
        ``on_serialize`` function for the format indicated by ``format``.

        :param format: The format to which the value should be serialized. Accepts
          either: ``csv``, ``json``, ``yaml``, or ``dict``.
        :type format: :class:`str <python:str>`

        :param attribute: The name of the attribute that whose serialized value
          should be returned.
        :type attribute: :class:`str <python:str>`

        :param config_set: The name of the named configuration set whose configuration
          should be used to retrieve the serialized value. Defaults to
          :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

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
                                                                 to_dict = to_dict,
                                                                 config_set = config_set)
        if not supports_serialization:
            raise UnsupportedSerializationError(
                "%s attribute '%s' does not support serialization to '%s'" % (self.__class__,
                                                                              attribute,
                                                                              format)
            )

        config = self.get_attribute_serialization_config(attribute,
                                                         config_set = config_set)

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
                                attribute,
                                config_set = None,
                                **kwargs):
        """Retrieve the value of ``attribute`` after applying the attribute's
        ``on_deserialize`` function for the format indicated by ``format``.

        :param value: The input value that was received when de-serializing.

        :param format: The format to which the value should be serialized. Accepts
          either: ``csv``, ``json``, ``yaml``, or ``dict``.
        :type format: :class:`str <python:str>`

        :param attribute: The name of the attribute that whose serialized value
          should be returned.
        :type attribute: :class:`str <python:str>`

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          whose configuration should be used to determine the deserialized value. Defaults
          to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

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
                                                                      from_dict = from_dict,
                                                                      config_set = config_set)
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

        config = cls.get_attribute_serialization_config(attribute,
                                                        config_set = config_set)

        on_deserialize = config.on_deserialize[format]
        if on_deserialize is None:
            on_deserialize = get_default_deserializer(getattr(class_obj,
                                                              config.name),
                                                      format = format)

        if on_deserialize is None:
            item = getattr(class_obj, config.name)
            class_resolver = getattr(getattr(item, 'property', None), 'argument', None)
            if class_resolver:
                resolved_class = class_resolver()
            else:
                resolved_class = None
            if resolved_class:
                # pylint: disable=W0212
                if hasattr(resolved_class, 'new_from_json') and format == 'json' and isinstance(value, dict):
                    as_json = json.dumps(value)
                    return_value = resolved_class.new_from_json(as_json, **kwargs)
                elif hasattr(resolved_class, 'new_from_yaml') and format == 'yaml' and isinstance(value, dict):
                    as_yaml = yaml.dump(value)
                    return_value = resolved_class.new_from_yaml(value, **kwargs)
                elif hasattr(resolved_class, 'new_from_dict') and format == 'dict' and isinstance(value, dict):
                    return_value = resolved_class.new_from_dict(value, **kwargs)
                else:
                    return_value = [resolved_class(
                        **resolved_class._parse_dict(x,
                                                     format,
                                                     **kwargs)) for x in value]
                #pylint: enable=W0212
            else:
                return_value = value
        else:
            try:
                return_value = on_deserialize(value)
            except Exception:
                raise ValueDeserializationError(
                    "attribute '%s' failed de-serialization to format '%s'" % (attribute,
                                                                               format)
                )


        return return_value

    @classmethod
    def _get_attribute_name(cls, display_name):
        """Retrieve the model class attribute name that corresponds to ``display_name``.

        :param display_name: The purported attribute name (or the ``display_name``) to check
          against.
        :type display_name: :class:`str <python:str>`

        .. note::

          Will return :obj:`None <python:None>` if ``display_name`` is not found.

        :returns: The model class attribute name that corresponds to ``display_name``.
        :rtype: :class:`str <python:str>` / :obj:`None <python:None>`

        """
        if hasattr(cls, display_name):
            return display_name

        config = cls.get_attribute_serialization_config(display_name)
        if config.display_name == display_name:
            return config.name

        return None
