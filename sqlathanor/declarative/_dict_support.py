# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

import warnings

from validator_collection import validators, checkers
from validator_collection.errors import NotAnIterableError

from sqlathanor._compat import json, dict as dict_
from sqlathanor.attributes import AttributeConfiguration
from sqlathanor.utilities import iterable__to_dict, get_attribute_names
from sqlathanor.errors import DeserializableAttributeError, DeserializationError, \
    InvalidFormatError, ExtraKeyError, MaximumNestingExceededError, \
    MaximumNestingExceededWarning, SerializableAttributeError, \
    UnsupportedSerializationError

class DictSupportMixin(object):
    """Mixin that provides :class:`dict <python:dict>` serialization/de-serialization
    support.
    """

    @classmethod
    def _parse_dict(cls,
                    input_data,
                    format,
                    error_on_extra_keys = True,
                    drop_extra_keys = False,
                    config_set = None):
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

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          to use when processing the input. Defaults to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

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

        dict_object = dict_()

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
                                                serialize = None,
                                                config_set = config_set)
                      if hasattr(cls, x.name)]

        if not attributes:
            raise DeserializableAttributeError(
                "'%s' has no '%s' de-serializable attributes" % (type(cls.__name__),
                                                                 format)
            )

        attribute_names = [x.display_name or x.name for x in attributes]
        extra_keys = [x for x in input_data.keys()
                      if x not in attribute_names]
        if extra_keys and error_on_extra_keys:
            raise ExtraKeyError("input data had extra keys: %s" % extra_keys)

        for attribute in attributes:
            key = attribute.display_name or attribute.name
            try:
                value = input_data.pop(key)
            except KeyError:
                continue

            value = cls._get_deserialized_value(value,
                                                format,
                                                key,
                                                error_on_extra_keys = error_on_extra_keys,
                                                drop_extra_keys = drop_extra_keys,
                                                config_set = config_set)

            dict_object[attribute.name] = value

        if input_data and not drop_extra_keys:
            for key in input_data:
                dict_object[key] = input_data[key]

        return dict_object


    def _to_dict(self,
                 format,
                 max_nesting = 0,
                 current_nesting = 0,
                 is_dumping = False,
                 config_set = None):
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

        :param is_dumping: If ``True``, retrieves all attributes except callables,
          utilities, and specials (``__<name>``). If ``False``, only retrieves
          those that have JSON serialization enabled. Defaults to ``False``.
        :type is_dumping: :class:`bool <python:bool>`

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          to use when processing the input. Defaults to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :returns: A :class:`dict <python:dict>` representation of the object.
        :rtype: :class:`dict <python:dict>`

        :raises InvalidFormatError: if ``format`` is not recognized
        :raises SerializableAttributeError: if attributes is empty
        :raises UnsupportedSerializationError: if unable to serialize a value
        :raises MaximumNestingExceededError: if ``current_nesting`` is greater
          than ``max_nesting``
        :raises MaximumNestingExceededWarning: if an attribute requires nesting
          beyond ``max_nesting``
        """
        # pylint: disable=too-many-branches

        next_nesting = current_nesting + 1

        if format not in ['csv', 'json', 'yaml', 'dict']:
            raise InvalidFormatError("format '%s' not supported" % format)

        if current_nesting > max_nesting:
            raise MaximumNestingExceededError(
                'current nesting level (%s) exceeds maximum %s' % (current_nesting,
                                                                   max_nesting)
            )

        dict_object = dict_()

        if format == 'csv':
            attribute_getter = self.get_csv_serialization_config
        elif format == 'json':
            attribute_getter = self.get_json_serialization_config
        elif format == 'yaml':
            attribute_getter = self.get_yaml_serialization_config
        elif format == 'dict':
            attribute_getter = self.get_dict_serialization_config

        if not is_dumping:
            attributes = [x
                          for x in attribute_getter(deserialize = None,
                                                    serialize = True,
                                                    config_set = config_set)
                          if hasattr(self, x.name)]
        else:
            attribute_names = [x
                               for x in get_attribute_names(self,
                                                            include_callable = False,
                                                            include_nested = False,
                                                            include_private = True,
                                                            include_special = False,
                                                            include_utilities = False)]
            attributes = []
            for item in attribute_names:
                attribute_config = self.get_attribute_serialization_config(item,
                                                                           config_set = config_set)
                if attribute_config is not None:
                    on_serialize_function = attribute_config.on_serialize.get(format,
                                                                              None)
                else:
                    on_serialize_function = None

                attribute = AttributeConfiguration(name = item,
                                                   supports_json = True,
                                                   supports_yaml = True,
                                                   supports_dict = True,
                                                   on_serialize = on_serialize_function)
                attributes.append(attribute)

        if not attributes:
            raise SerializableAttributeError(
                "'%s' has no '%s' serializable attributes" % (type(self.__class__),
                                                              format)
            )

        for attribute in attributes:
            item = getattr(self, attribute.name, None)
            if hasattr(item, '_to_dict'):
                try:
                    value = item._to_dict(format,                               # pylint: disable=protected-access
                                          max_nesting = max_nesting,
                                          current_nesting = next_nesting,
                                          is_dumping = is_dumping,
                                          config_set = config_set)
                except MaximumNestingExceededError:
                    warnings.warn(
                        "skipping key '%s' because maximum nesting has been exceeded" \
                            % attribute.name,
                        MaximumNestingExceededWarning
                    )
                    continue
            else:
                if attribute.on_serialize[format]:
                    on_serialize_function = attribute.on_serialize[format]
                    item = on_serialize_function(item)

                if checkers.is_iterable(item,
                                        forbid_literals = (str, bytes, dict)):
                    try:
                        value = iterable__to_dict(item,
                                                  format,
                                                  max_nesting = max_nesting,
                                                  current_nesting = next_nesting,
                                                  is_dumping = is_dumping,
                                                  config_set = config_set)
                    except MaximumNestingExceededError:
                        warnings.warn(
                            "skipping key '%s' because maximum nesting has been exceeded" \
                                % attribute.name,
                            MaximumNestingExceededWarning
                        )
                        continue
                    except NotAnIterableError:
                        try:
                            value = self._get_serialized_value(format,
                                                               attribute.name,
                                                               config_set = config_set)
                        except UnsupportedSerializationError as error:
                            if is_dumping:
                                value = getattr(self, attribute.name)
                            else:
                                raise error
                else:
                    try:
                        value = self._get_serialized_value(format,
                                                           attribute.name,
                                                           config_set = config_set)
                    except UnsupportedSerializationError as error:
                        if is_dumping:
                            value = getattr(self, attribute.name)
                        else:
                            raise error

            serialized_key = attribute.display_name or attribute.name

            dict_object[str(serialized_key)] = value

        return dict_object

    def to_dict(self,
                max_nesting = 0,
                current_nesting = 0,
                config_set = None):
        """Return a :class:`OrderedDict <python:collections.OrderedDict>` representation
        of the object.

        :param max_nesting: The maximum number of levels that the resulting
          :class:`dict <python:dict>` object can be nested. If set to ``0``, will
          not nest other serializable objects. Defaults to ``0``.
        :type max_nesting: :class:`int <python:int>`

        :param current_nesting: The current nesting level at which the
          :class:`dict <python:dict>` representation will reside. Defaults to ``0``.
        :type current_nesting: :class:`int <python:int>`

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          to use when processing the input. Defaults to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :returns: A :class:`OrderedDict <python:collections.OrderedDict>` representation
          of the object.
        :rtype: :class:`OrderedDict <python:collections.OrderedDict>`

        :raises SerializableAttributeError: if attributes is empty
        :raises MaximumNestingExceededError: if ``current_nesting`` is greater
          than ``max_nesting``
        :raises MaximumNestingExceededWarning: if an attribute requires nesting
          beyond ``max_nesting``

        """
        return self._to_dict('dict',
                             max_nesting = max_nesting,
                             current_nesting = current_nesting,
                             config_set = config_set)

    def dump_to_dict(self,
                     max_nesting = 0,
                     current_nesting = 0,
                     config_set = None):
        """Return a :class:`OrderedDict <python:collections.OrderedDict>` representation
        of the object, *with all attributes* regardless of configuration.

        .. caution::

          Nested objects (such as :term:`relationships <relationship>` or
          :term:`association proxies <association proxy>`) will **not**
          be serialized.

        :param max_nesting: The maximum number of levels that the resulting
          :class:`OrderedDict <python:collections.OrderedDict>` object can be nested. If
          set to ``0``, will not nest other serializable objects. Defaults to ``0``.
        :type max_nesting: :class:`int <python:int>`

        :param current_nesting: The current nesting level at which the
          :class:`dict <python:dict>` representation will reside. Defaults to ``0``.
        :type current_nesting: :class:`int <python:int>`

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          to use when processing the input. Defaults to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :returns: A :class:`OrderedDict <python:collections.OrderedDict>` representation
          of the object.
        :rtype: :class:`OrderedDict <python:collections.OrderedDict>`

        :raises SerializableAttributeError: if attributes is empty
        :raises MaximumNestingExceededError: if ``current_nesting`` is greater
          than ``max_nesting``
        :raises MaximumNestingExceededWarning: if an attribute requires nesting
          beyond ``max_nesting``

        """
        return self._to_dict('dict',
                             max_nesting = max_nesting,
                             current_nesting = current_nesting,
                             is_dumping = True,
                             config_set = config_set)

    def update_from_dict(self,
                         input_data,
                         error_on_extra_keys = True,
                         drop_extra_keys = False,
                         config_set = None):
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

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          to use when processing the input. Defaults to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

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
                                drop_extra_keys = drop_extra_keys,
                                config_set = config_set)

        for key in data:
            setattr(self, key, data[key])

    @classmethod
    def new_from_dict(cls,
                      input_data,
                      error_on_extra_keys = True,
                      drop_extra_keys = False,
                      config_set = None):
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

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          to use when processing the input. Defaults to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

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
                               drop_extra_keys = drop_extra_keys,
                               config_set = config_set)

        return cls(**data)
