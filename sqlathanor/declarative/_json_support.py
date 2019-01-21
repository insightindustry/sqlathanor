# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

from validator_collection import checkers

from sqlathanor._compat import json
from sqlathanor.utilities import parse_json

class JSONSupportMixin(object):
    """Mixin that provides JSON serialization/de-serialization support."""

    def to_json(self,
                max_nesting = 0,
                current_nesting = 0,
                serialize_function = None,
                config_set = None,
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

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          to use. Defaults to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

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
                                current_nesting = current_nesting,
                                is_dumping = False,
                                config_set = config_set)

        as_json = serialize_function(as_dict, **kwargs)

        return as_json

    def dump_to_json(self,
                     max_nesting = 0,
                     current_nesting = 0,
                     serialize_function = None,
                     config_set = None,
                     **kwargs):
        """Return a :term:`JSON <JavaScript Object Notation (JSON)>`
        representation of the object, *with all attributes* regardless of
        configuration.

        .. caution::

          Nested objects (such as :term:`relationships <relationship>` or
          :term:`association proxies <association proxy>`) will **not**
          be serialized.

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

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          to use. Defaults to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

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
                                current_nesting = current_nesting,
                                is_dumping = True,
                                config_set = config_set)

        as_json = serialize_function(as_dict, **kwargs)

        return as_json

    def update_from_json(self,
                         input_data,
                         deserialize_function = None,
                         error_on_extra_keys = True,
                         drop_extra_keys = False,
                         config_set = None,
                         **kwargs):
        """Update the model instance from data in a JSON string.

        :param input_data: The JSON data to de-serialize.

          .. note::

            If ``input_data`` points to a file, and the file contains a list of
            JSON objects, the first JSON object will be considered.

        :type input_data: :class:`str <python:str>` or Path-like object

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

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          to use. Defaults to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

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

        if isinstance(from_json, list):
            from_json = from_json[0]

        data = self._parse_dict(from_json,
                                'json',
                                error_on_extra_keys = error_on_extra_keys,
                                drop_extra_keys = drop_extra_keys,
                                config_set = config_set)

        for key in data:
            setattr(self, key, data[key])

    @classmethod
    def new_from_json(cls,
                      input_data,
                      deserialize_function = None,
                      error_on_extra_keys = True,
                      drop_extra_keys = False,
                      config_set = None,
                      **kwargs):
        """Create a new model instance from data in JSON.

        :param input_data: The JSON data to de-serialize.

          .. note::

            If ``input_data`` points to a file, and the file contains a list of
            JSON objects, the first JSON object will be considered.

        :type input_data: :class:`str <python:str>` or Path-like object

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

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          to use. Defaults to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

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

        if isinstance(from_json, list):
            from_json = from_json[0]

        data = cls._parse_dict(from_json,
                               'json',
                               error_on_extra_keys = error_on_extra_keys,
                               drop_extra_keys = drop_extra_keys,
                               config_set = config_set)

        return cls(**data)
