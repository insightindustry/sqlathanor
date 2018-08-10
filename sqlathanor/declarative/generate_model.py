# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

from validator_collection import checkers

from sqlathanor.declarative.base_model import BaseModel
from sqlathanor.declarative.declarative_base import declarative_base
from sqlathanor.attributes import AttributeConfiguration, validate_serialization_config
from sqlathanor.utilities import parse_yaml, parse_json, parse_csv, read_csv_data
from sqlathanor.default_deserializers import get_type_mapping
from sqlathanor.schema import Column

def generate_model_from_dict(serialized_dict,
                             tablename,
                             primary_key,
                             cls = BaseModel,
                             serialization_config = None,
                             skip_nested = True,
                             default_to_str = False,
                             type_mapping = None,
                             base_model_attrs = None,
                             **kwargs):
    """Generate a :term:`model class` from a serialized :class:`dict <python:dict>`.

    .. versionadded: 0.3.0

    .. note::

      This function *cannot* programmatically create
      :term:`relationships <relationship>`, :term:`hybrid properties <hybrid property>`,
      or :term:`association proxies <association proxy>`.

    :param serialized_dict: The :class:`dict <python:dict>` that has been de-serialized
      from a given string. Keys will be treated as column names, while value data
      types will determine :term:`model attribute` data types.
    :type serialized_dict: :class:`dict <python:dict>`

    :param tablename: The name of the SQL table to which the model corresponds.
    :type tablename: :class:`str <python:str>`

    :param primary_key: The name of the column/key that should be used as the table's
      primary key.
    :type primary_key: :class:`str <python:str>`

    :param cls: The base class to use when generating a new :term:`model class`.
      Defaults to :class:`BaseModel` to provide serialization/de-serialization
      support.

      If a :class:`tuple <python:tuple>` of classes, will include :class:`BaseModel`
      in that list of classes to mixin serialization/de-serialization support.

      If not :obj:`None <python:None>` and not a :class:`tuple <python:tuple>`, will mixin
      :class:`BaseModel` with the value passed to provide
      serialization/de-serialization support.
    :type cls: :obj:`None <python:None>` / :class:`tuple <python:tuple>` of classes / class object

    :param serialization_config: Collection of
      :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
      that determine the generated model's
      :term:`serialization`/:term:`de-serialization`
      :ref:`configuration <configuration>`. If :obj:`None <python:None>`, will
      support serialization and de-serialization across all keys in
      ``serialized_dict``. Defaults to :obj:`None <python:None>`.
    :type serialization_config: Iterable of
      :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
      or coercable :class:`dict <python:dict>` objects / :obj:`None <python:None>`

    :param skip_nested: If ``True`` then any keys in ``serialized_dict`` that
      feature nested items (e.g. iterables, :class:`dict <python:dict>` objects,
      etc.) will be ignored. If ``False``, will treat serialized items as
      :class:`str <python:str>`. Defaults to ``True``.
    :type skip_nested: :class:`bool <python:bool>`

    :param default_to_str: If ``True``, will automatically set a key/column whose
      value type cannot be determined to ``str``
      (:class:`Text <sqlalchemy:sqlalchemy.types.Text>`). If ``False``, will
      use the value type's ``__name__`` attribute and attempt to find a mapping.
      Defaults to ``False``.
    :type default_to_str: :class:`bool <python:bool>`

    :param type_mapping: Determines how value types in ``serialized_dict`` map to
      SQL column data types. To add a new mapping or override a default, set a
      key to the name of the value type in Python, and set the value to a
      :doc:`SQLAlchemy Data Type <sqlalchemy:core/types>`. The following are the
      default mappings applied:

      .. list-table::
         :widths: 30 30
         :header-rows: 1

         * - Python Literal
           - SQL Column Type
         * - ``bool``
           - :class:`Boolean <sqlalchemy:sqlalchemy.types.Boolean>`
         * - ``str``
           - :class:`Text <sqlalchemy:sqlalchemy.types.Text>`
         * - ``int``
           - :class:`Integer <sqlalchemy:sqlalchemy.types.Integer>`
         * - ``float``
           - :class:`Float <sqlalchemy:sqlalchemy.types.Float>`
         * - ``date``
           - :class:`Date <sqlalchemy:sqlalchemy.types.Date>`
         * - ``datetime``
           - :class:`DateTime <sqlalchemy:sqlalchemy.types.DateTime>`
         * - ``time``
           - :class:`Time <sqlalchemy:sqlalchemy.types.Time>`

    :type type_mapping: :class:`dict <python:dict>` with type names as keys and
      column data types as values.

    :param base_model_attrs: Optional :class:`dict <python:dict>` of special
      attributes that will be applied to the generated
      :class:`BaseModel <sqlathanor.declarative.BaseModel>` (e.g.
      ``__table_args__``). Keys will correspond to the attribute name, while the
      value is the value that will be applied. Defaults to :obj:`None <python:None>`.
    :type base_model_attrs: :class:`dict <python:dict>` / :obj:`None <python:None>`

    :param kwargs: Any additional keyword arguments will be passed to
      :func:`declarative_base() <sqlathanor.declarative.declarative_base>` when
      generating the programmatic :class:`BaseModel <sqlathanor.declarative.BaseModel>`.

    :returns: :term:`Model class` whose structure matches ``serialized_dict``.
    :rtype: :class:`BaseModel`

    :raises UnsupportedValueTypeError: when a value in ``serialized_dict`` does not
      have a corresponding key in ``type_mapping``
    :raises ValueError: if ``serialized_dict`` is not a :class:`dict <python:dict>`
      or is empty
    :raises ValueError: if ``tablename`` is empty
    :raises ValueError: if ``primary_key`` is empty

    """
    # pylint: disable=too-many-branches

    if not isinstance(serialized_dict, dict):
        raise ValueError('serialized_dict must be a dict')

    if not serialized_dict:
        raise ValueError('serialized_dict cannot be empty')

    if not tablename:
        raise ValueError('tablename cannot be empty')

    if not primary_key:
        raise ValueError('primary_key cannot be empty')

    serialization_config = validate_serialization_config(serialization_config)

    GeneratedBaseModel = declarative_base(cls = cls, **kwargs)

    class InterimGeneratedModel(object):
        # pylint: disable=too-few-public-methods,missing-docstring,invalid-variable-name
        __tablename__ = tablename

    prospective_serialization_config = []

    for key in serialized_dict:
        value = serialized_dict[key]
        column_type = get_type_mapping(value,
                                       type_mapping = type_mapping,
                                       skip_nested = skip_nested,
                                       default_to_str = default_to_str)
        if column_type is None:
            continue

        if key == primary_key:
            column = Column(name = key, type_ = column_type, primary_key = True)
        else:
            column = Column(name = key, type_ = column_type)

        setattr(InterimGeneratedModel, key, column)

        attribute_config = AttributeConfiguration(name = key,
                                                  supports_csv = True,
                                                  supports_json = True,
                                                  supports_yaml = True,
                                                  supports_dict = True,
                                                  on_serialize = None,
                                                  on_deserialize = None)
        prospective_serialization_config.append(attribute_config)

    if not serialization_config:
        serialization_config = prospective_serialization_config

    if base_model_attrs:
        for key in base_model_attrs:
            setattr(InterimGeneratedModel, key, base_model_attrs[key])

    class GeneratedModel(GeneratedBaseModel, InterimGeneratedModel):
        # pylint: disable=missing-docstring,too-few-public-methods
        pass

    GeneratedModel.configure_serialization(configs = serialization_config)

    return GeneratedModel


def generate_model_from_json(serialized,
                             tablename,
                             primary_key,
                             deserialize_function = None,
                             cls = BaseModel,
                             serialization_config = None,
                             skip_nested = True,
                             default_to_str = False,
                             type_mapping = None,
                             base_model_attrs = None,
                             deserialize_kwargs = None,
                             **kwargs):
    """Generate a :term:`model class` from a serialized
    :term:`JSON <JavaScript Object Notation (JSON)>` string.

    .. versionadded: 0.3.0

    .. note::

      This function *cannot* programmatically create
      :term:`relationships <relationship>`, :term:`hybrid properties <hybrid property>`,
      or :term:`association proxies <association proxy>`.

    :param serialized: The JSON data whose keys will be treated as column
      names, while value data types will determine :term:`model attribute` data
      types, or the path to a file whose contents will be the JSON object in
      question.

      .. note::

        If providing a path to a file, and if the file contains more than one JSON
        object, will only use the first JSON object listed.

    :type serialized: :class:`str <python:str>` / Path-like object

    :param tablename: The name of the SQL table to which the model corresponds.
    :type tablename: :class:`str <python:str>`

    :param primary_key: The name of the column/key that should be used as the table's
      primary key.
    :type primary_key: :class:`str <python:str>`

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
        pass them as keyword arguments (in ``deserialize_kwargs``).

    :type deserialize_function: callable / :obj:`None <python:None>`

    :param cls: The base class to use when generating a new :term:`model class`.
      Defaults to :class:`BaseModel` to provide serialization/de-serialization
      support.

      If a :class:`tuple <python:tuple>` of classes, will include :class:`BaseModel`
      in that list of classes to mixin serialization/de-serialization support.

      If not :obj:`None <python:None>` and not a :class:`tuple <python:tuple>`, will mixin
      :class:`BaseModel` with the value passed to provide
      serialization/de-serialization support.
    :type cls: :obj:`None <python:None>` / :class:`tuple <python:tuple>` of
      classes / class object

    :param serialization_config: Collection of
      :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
      that determine the generated model's
      :term:`serialization`/:term:`de-serialization`
      :ref:`configuration <configuration>`. If :obj:`None <python:None>`, will
      support serialization and de-serialization across all keys in
      ``serialized_dict``. Defaults to :obj:`None <python:None>`.
    :type serialization_config: Iterable of
      :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
      or coercable :class:`dict <python:dict>` objects / :obj:`None <python:None>`

    :param skip_nested: If ``True`` then any keys in ``serialized_json`` that
      feature nested items (e.g. iterables, JSON objects, etc.) will be ignored.
      If ``False``, will treat serialized items as :class:`str <python:str>`.
      Defaults to ``True``.
    :type skip_nested: :class:`bool <python:bool>`

    :param default_to_str: If ``True``, will automatically set a key/column whose
      value type cannot be determined to ``str``
      (:class:`Text <sqlalchemy:sqlalchemy.types.Text>`). If ``False``, will
      use the value type's ``__name__`` attribute and attempt to find a mapping.
      Defaults to ``False``.
    :type default_to_str: :class:`bool <python:bool>`

    :param type_mapping: Determines how value types in ``serialized`` map to
      SQL column data types. To add a new mapping or override a default, set a
      key to the name of the value type in Python, and set the value to a
      :doc:`SQLAlchemy Data Type <sqlalchemy:core/types>`. The following are the
      default mappings applied:

      .. list-table::
         :widths: 30 30
         :header-rows: 1

         * - Python Literal
           - SQL Column Type
         * - ``bool``
           - :class:`Boolean <sqlalchemy:sqlalchemy.types.Boolean>`
         * - ``str``
           - :class:`Text <sqlalchemy:sqlalchemy.types.Text>`
         * - ``int``
           - :class:`Integer <sqlalchemy:sqlalchemy.types.Integer>`
         * - ``float``
           - :class:`Float <sqlalchemy:sqlalchemy.types.Float>`
         * - ``date``
           - :class:`Date <sqlalchemy:sqlalchemy.types.Date>`
         * - ``datetime``
           - :class:`DateTime <sqlalchemy:sqlalchemy.types.DateTime>`
         * - ``time``
           - :class:`Time <sqlalchemy:sqlalchemy.types.Time>`

    :type type_mapping: :class:`dict <python:dict>` with type names as keys and
      column data types as values.

    :param base_model_attrs: Optional :class:`dict <python:dict>` of special
      attributes that will be applied to the generated
      :class:`BaseModel <sqlathanor.declarative.BaseModel>` (e.g.
      ``__table_args__``). Keys will correspond to the attribute name, while the
      value is the value that will be applied. Defaults to :obj:`None <python:None>`.
    :type base_model_attrs: :class:`dict <python:dict>` / :obj:`None <python:None>`

    :param deserialize_kwargs: Optional additional keyword arguments that will be
      passed to the deserialize function. Defaults to :obj:`None <python:None>`.
    :type deserialize_kwargs: :class:`dict <python:dict>` / :obj:`None <python:None>`

    :param kwargs: Any additional keyword arguments will be passed to
      :func:`declarative_base() <sqlathanor.declarative.declarative_base>` when
      generating the programmatic :class:`BaseModel <sqlathanor.declarative.BaseModel>`.

    :returns: :term:`Model class` whose structure matches ``serialized``.
    :rtype: :class:`BaseModel`

    :raises UnsupportedValueTypeError: when a value in ``serialized`` does not
      have a corresponding key in ``type_mapping``
    :raises ValueError: if ``tablename`` is empty

    """
    # pylint: disable=line-too-long
    if deserialize_kwargs:
        from_json = parse_json(serialized,
                               deserialize_function = deserialize_function,
                               **deserialize_kwargs)
    else:
        from_json = parse_json(serialized,
                               deserialize_function = deserialize_function)

    if isinstance(from_json, list):
        from_json = from_json[0]

    generated_model = generate_model_from_dict(from_json,
                                               tablename,
                                               primary_key,
                                               cls = cls,
                                               serialization_config = serialization_config,
                                               skip_nested = skip_nested,
                                               default_to_str = default_to_str,
                                               type_mapping = type_mapping,
                                               base_model_attrs = base_model_attrs,
                                               **kwargs)

    return generated_model


def generate_model_from_yaml(serialized,
                             tablename,
                             primary_key,
                             deserialize_function = None,
                             cls = BaseModel,
                             serialization_config = None,
                             skip_nested = True,
                             default_to_str = False,
                             type_mapping = None,
                             base_model_attrs = None,
                             deserialize_kwargs = None,
                             **kwargs):
    """Generate a :term:`model class` from a serialized
    :term:`YAML <YAML Ain't a Markup Language (YAML)>` string.

    .. versionadded: 0.3.0

    .. note::

      This function *cannot* programmatically create
      :term:`relationships <relationship>`, :term:`hybrid properties <hybrid property>`,
      or :term:`association proxies <association proxy>`.

    :param serialized: The YAML data whose keys will be treated as column
      names, while value data types will determine :term:`model attribute` data
      types, or the path to a file whose contents will be the YAML object in
      question.
    :type serialized: :class:`str <python:str>` / Path-like object

    :param tablename: The name of the SQL table to which the model corresponds.
    :type tablename: :class:`str <python:str>`

    :param primary_key: The name of the column/key that should be used as the table's
      primary key.
    :type primary_key: :class:`str <python:str>`

    :param deserialize_function: Optionally override the default YAML deserializer.
      Defaults to :obj:`None <python:None>`, which calls the default
      ``yaml.safe_load()`` function from the
      `PyYAML <https://github.com/yaml/pyyaml>`_ library.

      .. note::

        Use the ``deserialize_function`` parameter to override the default
        YAML deserializer.

        A valid ``deserialize_function`` is expected to accept a single
        :class:`str <python:str>` and return a :class:`dict <python:dict>`,
        similar to ``yaml.safe_load()``.

        If you wish to pass additional arguments to your ``deserialize_function``
        pass them as keyword arguments (in ``kwargs``).

    :type deserialize_function: callable / :obj:`None <python:None>`

    :param cls: The base class to use when generating a new :term:`model class`.
      Defaults to :class:`BaseModel` to provide serialization/de-serialization
      support.

      If a :class:`tuple <python:tuple>` of classes, will include :class:`BaseModel`
      in that list of classes to mixin serialization/de-serialization support.

      If not :obj:`None <python:None>` and not a :class:`tuple <python:tuple>`, will mixin
      :class:`BaseModel` with the value passed to provide
      serialization/de-serialization support.
    :type cls: :obj:`None <python:None>` / :class:`tuple <python:tuple>` of
      classes / class object

    :param serialization_config: Collection of
      :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
      that determine the generated model's
      :term:`serialization`/:term:`de-serialization`
      :ref:`configuration <configuration>`. If :obj:`None <python:None>`, will
      support serialization and de-serialization across all keys in
      ``serialized_dict``. Defaults to :obj:`None <python:None>`.
    :type serialization_config: Iterable of
      :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
      or coercable :class:`dict <python:dict>` objects / :obj:`None <python:None>`

    :param skip_nested: If ``True`` then any keys in ``serialized_json`` that
      feature nested items (e.g. iterables, JSON objects, etc.) will be ignored.
      If ``False``, will treat serialized items as :class:`str <python:str>`.
      Defaults to ``True``.
    :type skip_nested: :class:`bool <python:bool>`

    :param default_to_str: If ``True``, will automatically set a key/column whose
      value type cannot be determined to ``str``
      (:class:`Text <sqlalchemy:sqlalchemy.types.Text>`). If ``False``, will
      use the value type's ``__name__`` attribute and attempt to find a mapping.
      Defaults to ``False``.
    :type default_to_str: :class:`bool <python:bool>`

    :param type_mapping: Determines how value types in ``serialized`` map to
      SQL column data types. To add a new mapping or override a default, set a
      key to the name of the value type in Python, and set the value to a
      :doc:`SQLAlchemy Data Type <sqlalchemy:core/types>`. The following are the
      default mappings applied:

      .. list-table::
         :widths: 30 30
         :header-rows: 1

         * - Python Literal
           - SQL Column Type
         * - ``bool``
           - :class:`Boolean <sqlalchemy:sqlalchemy.types.Boolean>`
         * - ``str``
           - :class:`Text <sqlalchemy:sqlalchemy.types.Text>`
         * - ``int``
           - :class:`Integer <sqlalchemy:sqlalchemy.types.Integer>`
         * - ``float``
           - :class:`Float <sqlalchemy:sqlalchemy.types.Float>`
         * - ``date``
           - :class:`Date <sqlalchemy:sqlalchemy.types.Date>`
         * - ``datetime``
           - :class:`DateTime <sqlalchemy:sqlalchemy.types.DateTime>`
         * - ``time``
           - :class:`Time <sqlalchemy:sqlalchemy.types.Time>`

    :type type_mapping: :class:`dict <python:dict>` with type names as keys and
      column data types as values.

    :param base_model_attrs: Optional :class:`dict <python:dict>` of special
      attributes that will be applied to the generated
      :class:`BaseModel <sqlathanor.declarative.BaseModel>` (e.g.
      ``__table_args__``). Keys will correspond to the attribute name, while the
      value is the value that will be applied. Defaults to :obj:`None <python:None>`.
    :type base_model_attrs: :class:`dict <python:dict>` / :obj:`None <python:None>`

    :param deserialize_kwargs: Optional additional keyword arguments that will be
      passed to the deserialize function. Defaults to :obj:`None <python:None>`.
    :type deserialize_kwargs: :class:`dict <python:dict>` / :obj:`None <python:None>`

    :param kwargs: Any additional keyword arguments will be passed to
      :func:`declarative_base() <sqlathanor.declarative.declarative_base>` when
      generating the programmatic :class:`BaseModel <sqlathanor.declarative.BaseModel>`.

    :returns: :term:`Model class` whose structure matches ``serialized``.
    :rtype: :class:`BaseModel`

    :raises UnsupportedValueTypeError: when a value in ``serialized`` does not
      have a corresponding key in ``type_mapping``
    :raises ValueError: if ``tablename`` is empty

    """
    # pylint: disable=line-too-long
    if deserialize_kwargs:
        from_yaml = parse_yaml(serialized,
                               deserialize_function = deserialize_function,
                               **deserialize_kwargs)
    else:
        from_yaml = parse_yaml(serialized,
                               deserialize_function = deserialize_function)

    if isinstance(from_yaml, list):
        from_yaml = from_yaml[0]

    generated_model = generate_model_from_dict(from_yaml,
                                               tablename,
                                               primary_key,
                                               cls = cls,
                                               serialization_config = serialization_config,
                                               skip_nested = skip_nested,
                                               default_to_str = default_to_str,
                                               type_mapping = type_mapping,
                                               base_model_attrs = base_model_attrs,
                                               **kwargs)

    return generated_model


def generate_model_from_csv(serialized,
                            tablename,
                            primary_key,
                            cls = BaseModel,
                            serialization_config = None,
                            skip_nested = True,
                            default_to_str = False,
                            type_mapping = None,
                            base_model_attrs = None,
                            delimiter = '|',
                            wrap_all_strings = False,
                            null_text = 'None',
                            wrapper_character = "'",
                            double_wrapper_character_when_nested = False,
                            escape_character = "\\",
                            line_terminator = '\r\n',
                            **kwargs):
    """Generate a :term:`model class` from a serialized
    :term:`CSV <Comma-Separated Value (CSV)>` string.

    .. versionadded: 0.3.0

    .. note::

      This function *cannot* programmatically create
      :term:`relationships <relationship>`, :term:`hybrid properties <hybrid property>`,
      or :term:`association proxies <association proxy>`.

    :param serialized: The CSV data whose column headers will be treated as column
      names, while value data types will determine :term:`model attribute` data
      types.

      .. note::

        If a Path-like object, will read the file contents from a file that is assumed
        to include a header row. If a :class:`str <python:str>` and has more than
        one record (line), will assume the first line is a header row. If a
        :class:`list <python:list>`, will assume the first item is the header row.

    :type serialized: :class:`str <python:str>` / Path-like object /
      :class:`list <python:list>`

    :param tablename: The name of the SQL table to which the model corresponds.
    :type tablename: :class:`str <python:str>`

    :param primary_key: The name of the column/key that should be used as the table's
      primary key.
    :type primary_key: :class:`str <python:str>`

    :param cls: The base class to use when generating a new :term:`model class`.
      Defaults to :class:`BaseModel` to provide serialization/de-serialization
      support.

      If a :class:`tuple <python:tuple>` of classes, will include :class:`BaseModel`
      in that list of classes to mixin serialization/de-serialization support.

      If not :obj:`None <python:None>` and not a :class:`tuple <python:tuple>`, will mixin
      :class:`BaseModel` with the value passed to provide
      serialization/de-serialization support.
    :type cls: :obj:`None <python:None>` / :class:`tuple <python:tuple>` of
      classes / class object

    :param serialization_config: Collection of
      :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
      that determine the generated model's
      :term:`serialization`/:term:`de-serialization`
      :ref:`configuration <configuration>`. If :obj:`None <python:None>`, will
      support serialization and de-serialization across all keys in
      ``serialized_dict``. Defaults to :obj:`None <python:None>`.
    :type serialization_config: Iterable of
      :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
      or coercable :class:`dict <python:dict>` objects / :obj:`None <python:None>`

    :param skip_nested: If ``True`` then any keys in ``serialized_json`` that
      feature nested items (e.g. iterables, JSON objects, etc.) will be ignored.
      If ``False``, will treat serialized items as :class:`str <python:str>`.
      Defaults to ``True``.
    :type skip_nested: :class:`bool <python:bool>`

    :param default_to_str: If ``True``, will automatically set a key/column whose
      value type cannot be determined to ``str``
      (:class:`Text <sqlalchemy:sqlalchemy.types.Text>`). If ``False``, will
      use the value type's ``__name__`` attribute and attempt to find a mapping.
      Defaults to ``False``.
    :type default_to_str: :class:`bool <python:bool>`

    :param type_mapping: Determines how value types in ``serialized`` map to
      SQL column data types. To add a new mapping or override a default, set a
      key to the name of the value type in Python, and set the value to a
      :doc:`SQLAlchemy Data Type <sqlalchemy:core/types>`. The following are the
      default mappings applied:

      .. list-table::
         :widths: 30 30
         :header-rows: 1

         * - Python Literal
           - SQL Column Type
         * - ``bool``
           - :class:`Boolean <sqlalchemy:sqlalchemy.types.Boolean>`
         * - ``str``
           - :class:`Text <sqlalchemy:sqlalchemy.types.Text>`
         * - ``int``
           - :class:`Integer <sqlalchemy:sqlalchemy.types.Integer>`
         * - ``float``
           - :class:`Float <sqlalchemy:sqlalchemy.types.Float>`
         * - ``date``
           - :class:`Date <sqlalchemy:sqlalchemy.types.Date>`
         * - ``datetime``
           - :class:`DateTime <sqlalchemy:sqlalchemy.types.DateTime>`
         * - ``time``
           - :class:`Time <sqlalchemy:sqlalchemy.types.Time>`

    :type type_mapping: :class:`dict <python:dict>` with type names as keys and
      column data types as values.

    :param base_model_attrs: Optional :class:`dict <python:dict>` of special
      attributes that will be applied to the generated
      :class:`BaseModel <sqlathanor.declarative.BaseModel>` (e.g.
      ``__table_args__``). Keys will correspond to the attribute name, while the
      value is the value that will be applied. Defaults to :obj:`None <python:None>`.
    :type base_model_attrs: :class:`dict <python:dict>` / :obj:`None <python:None>`

    :param delimiter: The delimiter used between columns. Defaults to ``|``.
    :type delimiter: :class:`str <python:str>`

    :param wrapper_character: The string used to wrap string values when
      wrapping is applied. Defaults to ``'``.
    :type wrapper_character: :class:`str <python:str>`

    :param null_text: The string used to indicate an empty value if empty
      values are wrapped. Defaults to `None`.
    :type null_text: :class:`str <python:str>`

    :param kwargs: Any additional keyword arguments will be passed to
      :func:`declarative_base() <sqlathanor.declarative.declarative_base>` when
      generating the programmatic :class:`BaseModel <sqlathanor.declarative.BaseModel>`.

    :returns: :term:`Model class` whose structure matches ``serialized``.
    :rtype: :class:`BaseModel`

    :raises UnsupportedValueTypeError: when a value in ``serialized`` does not
      have a corresponding key in ``type_mapping``
    :raises ValueError: if ``tablename`` is empty
    :raises DeserializationError: if ``serialized`` is not a valid
      :class:`str <python:str>`
    :raises CSVStructureError: if there are less than 2 (two) rows in ``serialized``
      or if column headers are not valid Python variable names

    """
    # pylint: disable=line-too-long,too-many-arguments

    if not checkers.is_file(serialized):
        serialized = read_csv_data(serialized, single_record = False)

    from_csv = parse_csv(serialized,
                         delimiter = delimiter,
                         wrap_all_strings = wrap_all_strings,
                         null_text = null_text,
                         wrapper_character = wrapper_character,
                         double_wrapper_character_when_nested = double_wrapper_character_when_nested,
                         escape_character = escape_character,
                         line_terminator = line_terminator)

    generated_model = generate_model_from_dict(from_csv,
                                               tablename,
                                               primary_key,
                                               cls = cls,
                                               serialization_config = serialization_config,
                                               skip_nested = skip_nested,
                                               default_to_str = default_to_str,
                                               type_mapping = type_mapping,
                                               base_model_attrs = base_model_attrs,
                                               **kwargs)

    return generated_model
