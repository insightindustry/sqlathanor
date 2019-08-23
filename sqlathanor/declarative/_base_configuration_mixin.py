# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

import inspect as inspect_
from collections import OrderedDict

from sqlalchemy.inspection import inspect
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.associationproxy import AssociationProxy
from validator_collection import checkers

from sqlathanor._compat import dict as dict_
from sqlathanor.attributes import AttributeConfiguration, validate_serialization_config, \
    BLANK_ON_SERIALIZE
from sqlathanor.errors import ConfigurationError, UnsupportedSerializationError


class ConfigurationMixin(object):
    """Mixin that provides base serialization configuration support."""

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

            try:
                item = getattr(cls, key)
            except InvalidRequestError as error:
                is_AssociationProxy = isinstance(inspect(cls).all_orm_descriptors[key], AssociationProxy)
                if not is_AssociationProxy:
                    raise error

                item = None

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
            try:
                value = getattr(cls, key)
            except InvalidRequestError as error:
                value = inspect(cls).all_orm_descriptors[key]
                is_AssociationProxy = isinstance(value, AssociationProxy)
                if not is_AssociationProxy:
                    raise error

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
                                          to_dict = None,
                                          config_set = None):
        """Retrieve a list of
        :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
        objects corresponding to attributes whose values can be serialized from/to CSV,
        JSON, YAML, etc.

        .. note::

          This method operates *solely* on attribute configurations that have been
          provided in the meta override ``__serialization__`` attribute.

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

        :param config_set: If not :obj:`None <python:None>`, will return those
          :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
          objects that are contained within the named set. Defaults to
          :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :returns: List of attribute configurations.
        :rtype: :class:`list <python:list>` of :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`

        :raises ConfigurationError: if ``config_set`` is not empty and there are no
          configuration sets defined on ``cls`` or if there are configuration sets defined
          but no ``config_set`` is specified
        :raises ValueError: if ``config_set`` is not defined within ``__serialization__``

        """
        if config_set and not isinstance(cls.__serialization__, (dict, OrderedDict)):
            raise ConfigurationError('__serialization__ is not a dict and therefore no '
                                     'config_set can be found')
        elif not config_set and isinstance(cls.__serialization__, (dict, OrderedDict)):
            raise ConfigurationError('configuration sets defined but no config_set '
                                     ' specified')

        if config_set and config_set not in cls.__serialization__:
            raise ValueError('config set (%s) not found in __serialization__ '
                             ' configuration' % config_set)

        attributes = []

        if not config_set:
            __serialization__ = [x for x in cls.__serialization__]
        else:
            __serialization__ = [x for x in cls.__serialization__[config_set]]

        if from_csv is not None and to_csv is None:
            attributes.extend([x for x in __serialization__
                               if x.supports_csv[0] == bool(from_csv) and \
                                  x not in attributes
                              ])
        if to_csv is not None and from_csv is None:
            attributes.extend([x for x in __serialization__
                               if x.supports_csv[1] == bool(to_csv) and \
                                  x not in attributes
                              ])

        if from_csv is not None and to_csv is not None:
            attributes.extend([x for x in __serialization__
                               if x.supports_csv[0] == bool(from_csv) and \
                                  x.supports_csv[1] == bool(to_csv) and \
                                  x not in attributes
                              ])

        if from_json is not None and to_json is None:
            attributes.extend([x for x in __serialization__
                               if x.supports_json[0] == bool(from_json) and \
                                  x not in attributes
                              ])
        if to_json is not None and from_json is None:
            attributes.extend([x for x in __serialization__
                               if x.supports_json[1] == bool(to_json) and \
                                  x not in attributes
                              ])

        if from_json is not None and to_json is not None:
            attributes.extend([x for x in __serialization__
                               if x.supports_json[0] == bool(from_json) and \
                                  x.supports_json[1] == bool(to_json) and \
                                  x not in attributes
                              ])

        if from_yaml is not None and to_yaml is None:
            attributes.extend([x for x in __serialization__
                               if x.supports_yaml[0] == bool(from_yaml) and \
                                  x not in attributes
                              ])
        if to_yaml is not None and from_yaml is None:
            attributes.extend([x for x in __serialization__
                               if x.supports_yaml[1] == bool(to_yaml) and \
                                  x not in attributes
                              ])

        if from_yaml is not None and to_yaml is not None:
            attributes.extend([x for x in __serialization__
                               if x.supports_yaml[0] == bool(from_yaml) and \
                                  x.supports_yaml[1] == bool(to_yaml) and \
                                  x not in attributes
                              ])

        if from_dict is not None and to_dict is None:
            attributes.extend([x for x in __serialization__
                               if x.supports_dict[0] == bool(from_dict) and \
                                  x not in attributes
                              ])
        if to_dict is not None and from_dict is None:
            attributes.extend([x for x in __serialization__
                               if x.supports_dict[1] == bool(to_dict) and \
                                  x not in attributes
                              ])

        if from_dict is not None and to_dict is not None:
            attributes.extend([x for x in __serialization__
                               if x.supports_dict[0] == bool(from_dict) and \
                                  x.supports_dict[1] == bool(to_dict) and \
                                  x not in attributes
                              ])

        return attributes

    @classmethod
    def _get_attribute_configurations(cls, config_set = None):
        """Retrieve a list of
        :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
        applied to the class.

        :param config_set: If not :obj:`None <python:None>`, will return those
          :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
          objects that are contained within the named set. Defaults to
          :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :raises ConfigurationError: if ``config_set`` is not empty and there are no
          configuration sets defined on ``cls`` or if there are configuration sets defined
          but no ``config_set`` is specified
        :raises ValueError: if ``config_set`` is not defined within ``__serialization__``

        """
        if config_set and not isinstance(cls.__serialization__, (dict, OrderedDict)):
            raise ConfigurationError('__serialization__ is not a dict and therefore no '
                                     'config_set can be found')
        elif not config_set and isinstance(cls.__serialization__, (dict, OrderedDict)):
            raise ConfigurationError('configuration sets defined but no config_set '
                                     ' specified')

        if config_set and config_set not in cls.__serialization__:
            raise ValueError('config set (%s) not found in __serialization__ '
                             ' configuration' % config_set)

        if not config_set:
            attributes = [x for x in cls.__serialization__]
        else:
            attributes = [x for x in cls.__serialization__[config_set]]

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
                                 exclude_private = True,
                                 config_set = None):
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

        :param config_set: If not :obj:`None <python:None>`, will return those
          :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
          objects that are contained within the named set. Defaults to
          :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :returns: List of attribute configurations.
        :rtype: :class:`list <python:list>` of
          :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`

        :raises ConfigurationError: if ``cls`` does not use named configuration sets but
          ``config_set`` is not :obj:`None <python:None>`
        :raises ConfigurationError: if ``cls`` uses named configuration sets but
          ``config_set`` is empty
        :raises ValueError: if ``config_set`` is not defined within ``__serialization__``

        """
        if config_set and not isinstance(cls.__serialization__, (dict, OrderedDict)):
            raise ConfigurationError('object does not use named configuration sets, '
                                     'but config_set is not None')
        elif not config_set and isinstance(cls.__serialization__, (dict, OrderedDict)):
            raise ConfigurationError('configuration sets defined but config_set is empty')

        if config_set and config_set not in cls.__serialization__:
            raise ValueError('config set (%s) not found in __serialization__ '
                             ' configuration' % config_set)

        if config_set:
            __serialization__ = [x for x in cls.__serialization__[config_set]]
        else:
            __serialization__ = [x for x in cls.__serialization__]

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
            config_set = config_set
        )

        attributes = [x for x in meta_attributes]
        attributes.extend([x for x in declarative_attributes
                           if x not in attributes and x not in __serialization__])

        return attributes

    @classmethod
    def get_attribute_serialization_config(cls,
                                           attribute,
                                           config_set = None):
        """Retrieve the
        :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
        for ``attribute``.

        :param attribute: The attribute/column name whose serialization
          configuration should be returned.
        :type attribute: :class:`str <python:str>`

        :param config_set: If not :obj:`None <python:None>`, will return the
          :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
          object for ``attribute`` that is contained within the named set. Defaults to
          :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :returns: The
          :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
          for ``attribute``.
        :rtype: :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`

        :raises ConfigurationError: if ``config_set`` is not empty and there are no
          configuration sets defined on ``cls`` or if there are configuration sets defined
          but no ``config_set`` is specified
        :raises ValueError: if ``config_set`` is not defined within ``__serialization__``

        """
        attributes = cls._get_attribute_configurations(config_set = config_set)

        for config in attributes:
            if config.name == attribute:
                return config.copy()
            if config.display_name == attribute:
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
                                           on_serialize = None,
                                           config_set = None):
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

        :raises ConfigurationError: if ``config_set`` is not empty and there are no
          configuration sets defined on ``cls`` or if there are configuration sets defined
          but no ``config_set`` is specified
        :raises ValueError: if ``config_set`` is not defined within ``__serialization__``
        :raises ValueError: if ``attribute`` does not match ``config.name`` if
          ``config`` is not :obj:`None <python:None>`

        """
        # pylint: disable=too-many-branches
        if config_set and not isinstance(cls.__serialization__, (dict, OrderedDict)):
            raise ConfigurationError('__serialization__ is not a dict and therefore no '
                                     'config_set can be found')
        elif not config_set and isinstance(cls.__serialization__, (dict, OrderedDict)):
            raise ConfigurationError('configuration sets defined but no config_set '
                                     ' specified')

        if config_set and config_set not in cls.__serialization__:
            raise ValueError('config set (%s) not found in __serialization__ '
                             ' configuration' % config_set)

        if config_set:
            __serialization__ = [x for x in cls.__serialization__[config_set]]
        else:
            __serialization__ = [x for x in cls.__serialization__]

        original_config = cls.get_attribute_serialization_config(attribute,
                                                                 config_set = config_set)
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

        serialization = [x for x in __serialization__
                         if x.name != attribute]
        serialization.append(new_config)

        if config_set:
            cls.__serialization__[config_set] = [x for x in serialization]
        else:
            cls.__serialization__ = [x for x in serialization]

    @classmethod
    def configure_serialization(cls,
                                configs = None,
                                attributes = None,
                                supports_csv = False,
                                supports_json = False,
                                supports_yaml = False,
                                supports_dict = False,
                                on_serialize = None,
                                on_deserialize = None,
                                config_set = None):
        """Apply configuration settings to the :term:`model class` (overwrites
        entire configuration).

        .. tip::

          For this method, the configuration settings applied in ``configs`` receive
          priority over a configuration specified in keyword arguments.

          This means that if an attribute is configured in both ``configs`` and
          ``attributes``, the configuration in ``configs`` will apply.

        :param configs: Collection of
          :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
          objects to apply to the class. Defaults to :obj:`None <python:None>`.
        :type configs: iterable of
          :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>` /
          :obj:`None <python:None>`

        :param attributes: Collection of :term:`model attribute` names to which
          a configuration will be applied. Defaults to :obj:`None <python:None>`.
        :type attributes: iterable of :class:`str <python:str>` /
          :obj:`None <python:None>`

        :param supports_csv: Determines whether the column can be serialized to or
          de-serialized from CSV format.

          If ``True``, can be serialized to CSV and de-serialized from CSV. If
          ``False``, will not be included when serialized to CSV and will be ignored
          if present in a de-serialized CSV.

          Can also accept a 2-member :class:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``.

        :type supports_csv: :class:`bool <python:bool>` / :class:`tuple <python:tuple>`
          of form (inbound: :class:`bool <python:bool>`, outbound:
          :class:`bool <python:bool>`)

        :param supports_json: Determines whether the column can be serialized to or
          de-serialized from JSON format.

          If ``True``, can be serialized to JSON and de-serialized from JSON.
          If ``False``, will not be included when serialized to JSON and will be
          ignored if present in a de-serialized JSON.

          Can also accept a 2-member :class:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``.

        :type supports_json: :class:`bool <python:bool>` / :class:`tuple <python:tuple>`
          of form (inbound: :class:`bool <python:bool>`, outbound:
          :class:`bool <python:bool>`)

        :param supports_yaml: Determines whether the column can be serialized to or
          de-serialized from YAML format.

          If ``True``, can be serialized to YAML and de-serialized from YAML.
          If ``False``, will not be included when serialized to YAML and will be
          ignored if present in a de-serialized YAML.

          Can also accept a 2-member :class:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``.

        :type supports_yaml: :class:`bool <python:bool>` / :class:`tuple <python:tuple>`
          of form (inbound: :class:`bool <python:bool>`, outbound:
          :class:`bool <python:bool>`)

        :param supports_dict: Determines whether the column can be serialized to or
          de-serialized to a Python :class:`dict <python:dict>`.

          If ``True``, can be serialized to :class:`dict <python:dict>` and de-serialized
          from a :class:`dict <python:dict>`. If ``False``, will not be included
          when serialized to :class:`dict <python:dict>` and will be ignored if
          present in a de-serialized :class:`dict <python:dict>`.

          Can also accept a 2-member :class:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``.

        :type supports_dict: :class:`bool <python:bool>` / :class:`tuple <python:tuple>`
          of form (inbound: :class:`bool <python:bool>`, outbound:
          :class:`bool <python:bool>`)

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

        :param config_set: If not :obj:`None <python:None>`, will apply ``configs`` to the
          configuration set named. If the class does not use pre-existing configuration sets,
          will switch the class' meta configuration to use configuration sets, with any
          pre-existing configuration set assigned to a set named ``_original``. Defaults
          to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        """
        config = validate_serialization_config(configs)
        config_attributes = [x.name for x in config]

        if not attributes:
            attributes = []

        attributes = [AttributeConfiguration(name = x,
                                             supports_csv = supports_csv,
                                             supports_json = supports_json,
                                             supports_yaml = supports_yaml,
                                             supports_dict = supports_dict,
                                             on_serialize = on_serialize,
                                             on_deserialize = on_deserialize)
                      for x in attributes
                      if x not in config_attributes]

        config.extend(attributes)

        if not config_set and not isinstance(cls.__serialization__, (dict, OrderedDict)):
            cls.__serialization__ = [x for x in config]
        elif config_set and isinstance(cls.__serialization__, (dict, OrderedDict)):
            cls.__serialization__[config_set] = [x for x in config]
        elif config_set:
            config_dict = dict_()
            config_dict['_original'] = [x for x in cls.__serialization__]
            config_dict[config_set] = [x for x in config]
            cls.__serialization__ = config_dict

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
                                   to_dict = None,
                                   config_set = None):
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

        :param config_set: If not :obj:`None <python:None>`, will determine serialization
          support within the indicated configuration set. Defaults to
          :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :returns: ``True`` if the attribute's serialization support matches,
          ``False`` if not, and :obj:`None <python:None>` if no serialization support was
          specified.
        :rtype: :class:`bool <python:bool>` / :obj:`None <python:None>`

        :raises UnsupportedSerializationError: if ``attribute`` is not present
          on the object
        :raises ValueError: if ``config_set`` is not :obj:`None <python:None>` and
          its value does not match a named configuration set
        :raises ConfigurationError: if ``config_set`` is :obj:`None <python:None>` and the
          object uses named configuration sets
        :raises ConfigurationError: if the object does not use configuration sets but
          ``config_set`` is not None

        """
        # pylint: disable=too-many-boolean-expressions,too-many-branches
        if config_set and not isinstance(cls.__serialization__, (dict, OrderedDict)):
            raise ConfigurationError('object does not use configuration sets, but '
                                     'config_set was not None')
        elif not config_set and isinstance(cls.__serialization__, (dict, OrderedDict)):
            raise ConfigurationError('configuration sets defined but no config_set '
                                     ' specified')

        if config_set and config_set not in cls.__serialization__:
            raise ValueError('config set (%s) not found in __serialization__ '
                             ' configuration' % config_set)

        if from_csv is None and to_csv is None and \
           from_json is None and to_json is None and \
           from_yaml is None and to_yaml is None and \
           from_dict is None and to_dict is None:
            return None

        config = cls.get_attribute_serialization_config(attribute,
                                                        config_set = config_set)
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

    @classmethod
    def get_csv_serialization_config(cls,
                                     deserialize = True,
                                     serialize = True,
                                     config_set = None):
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

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          whose CSV serialization configuration should be returned. Defaults to
          :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :returns: Set of attribute serialization configurations that match the
          arguments supplied.
        :rtype: :class:`list <python:list>` of
          :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`

        :raises ConfigurationError: if ``cls`` does not use named configuration sets but
          ``config_set`` is not :obj:`None <python:None>`
        :raises ConfigurationError: if ``cls`` uses named configuration sets but
          ``config_set`` is empty
        :raises ValueError: if ``config_set`` is not defined within ``__serialization__``

        """
        attributes = [x.copy()
                      for x in cls.get_serialization_config(from_csv = deserialize,
                                                            to_csv = serialize,
                                                            config_set = config_set)]
        for config in attributes:
            if config.csv_sequence is None:
                config.csv_sequence = len(attributes) + 1

        return sorted(attributes, key = lambda x: (x.csv_sequence, x.name))

    @classmethod
    def get_json_serialization_config(cls,
                                      deserialize = True,
                                      serialize = True,
                                      config_set = None):
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

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          whose serialization configuration should be returned. Defaults to
          :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :returns: Set of attribute serialization configurations that match the
          arguments supplied.
        :rtype: :class:`list <python:list>` of
          :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
        """
        return [x for x in cls.get_serialization_config(from_json = deserialize,
                                                        to_json = serialize,
                                                        config_set = config_set)]

    @classmethod
    def get_yaml_serialization_config(cls,
                                      deserialize = True,
                                      serialize = True,
                                      config_set = None):
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

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          whose serialization configuration should be returned. Defaults to
          :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :returns: Set of attribute serialization configurations that match the
          arguments supplied.
        :rtype: :class:`list <python:list>` of
          :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`

        """
        return [x for x in cls.get_serialization_config(from_yaml = deserialize,
                                                        to_yaml = serialize,
                                                        config_set = config_set)]

    @classmethod
    def get_dict_serialization_config(cls,
                                      deserialize = True,
                                      serialize = True,
                                      config_set = None):
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

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          whose serialization configuration should be returned. Defaults to
          :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :returns: Set of attribute serialization configurations that match the
          arguments supplied.
        :rtype: :class:`list <python:list>` of
          :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
        """
        return [x for x in cls.get_serialization_config(from_dict = deserialize,
                                                        to_dict = serialize,
                                                        config_set = config_set)]
