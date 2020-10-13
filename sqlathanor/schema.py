# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

import functools
import operator

from sqlalchemy import Column as SA_Column
from sqlalchemy import Table as SA_Table
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.relationships import RelationshipProperty as SA_RelationshipProperty
from sqlalchemy.util.langhelpers import public_factory
from sqlalchemy.ext.hybrid import hybrid_property as SA_hybrid_property

from sqlalchemy import exc, orm, util, inspect


from validator_collection import checkers, validators

from sqlathanor import attributes
from sqlathanor._serialization_support import SerializationMixin
from sqlathanor.default_deserializers import get_type_mapping
from sqlathanor.utilities import parse_json, parse_yaml, parse_csv, read_csv_data
from sqlathanor.errors import SQLAthanorError


class Column(SerializationMixin, SA_Column):
    """Represents a column in a database table. Inherits from
    :class:`sqlalchemy.schema.Column <sqlalchemy:sqlalchemy.schema.Column>`
    """

    # pylint: disable=too-many-ancestors, W0223

    def __init__(self, *args, **kwargs):
        """Construct a new ``Column`` object.

        .. warning::

          This method is analogous to the original SQLAlchemy
          :class:`Column.__init__() <sqlalchemy:sqlalchemy.schema.Column>`
          from which it inherits. The only difference is that it supports additional
          keyword arguments which are not supported in the original, and which
          are documented below.

          **For the original SQLAlchemy version, see:**

          * :doc:`SQLAlchemy <sqlalchemy:index>`: :class:`Column.__init__() <sqlalchemy:sqlalchemy.schema.Column>`

        :param supports_csv: Determines whether the column can be serialized to or
          de-serialized from CSV format.

          If ``True``, can be serialized to CSV and de-serialized from CSV.
          If ``False``, will not be included when serialized to CSV and will be
          ignored if present in a de-serialized CSV.

          Can also accept a 2-member :class:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``, which means the column will not be serialized to CSV
          or de-serialized from CSV.

        :type supports_csv: :class:`bool <python:bool>` / :class:`tuple <python:tuple>` of
          form (inbound: :class:`bool <python:bool>`, outbound: :class:`bool <python:bool>`)

        :param csv_sequence: Indicates the numbered position that the column should be in
          in a valid CSV-version of the object. Defaults to :obj:`None <python:None>`.

          .. note::

            If not specified, the column will go after any columns that *do* have a
            ``csv_sequence`` assigned, sorted alphabetically.

            If two columns have the same ``csv_sequence``, they will be sorted
            alphabetically.

        :type csv_sequence: :class:`int <python:int>` / :obj:`None <python:None>`

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

          If ``True``, can be serialized to :class:`dict <python:dict>` and
          de-serialized from a :class:`dict <python:dict>`. If ``False``, will not be
          included when serialized to :class:`dict <python:dict>` and will be
          ignored if present in a de-serialized :class:`dict <python:dict>`.

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

        """
        super(Column, self).__init__(*args, **kwargs)


class RelationshipProperty(SA_RelationshipProperty):
    """Describes an object property that holds a single item or list of items that
    correspond to a related database table.

    Public constructor is the :func:`sqlathanor.schema.relationship` function.
    """

    def __init__(self,
                 argument,
                 supports_json = False,
                 supports_yaml = False,
                 supports_dict = False,
                 on_serialize = None,
                 on_deserialize = None,
                 display_name = None,
                 **kwargs):
        """Provide a relationship between two mapped classes.

        This corresponds to a parent-child or associate table relationship.
        The constructed class is an instance of :class:`RelationshipProperty`.

        When serializing or de-serializing relationships, they essentially become
        "nested" objects. For example, if you have an ``Account`` table with a
        relationship to a ``User`` table, you might want to nest or embed a list of
        ``User`` objects within a serialized ``Account`` object.

        .. caution::

          Unlike columns, properties, or hybrid properties, relationships
          cannot be serialized to CSV. This is because a serialized relationship
          is essentially a "nested" object within another object.

          Therefore, the ``supports_csv`` option cannot be set and will always be
          interpreted as ``False``.

        .. warning::

          This constructor is analogous to the original
          :ref:`SQLAlchemy relationship() <sqlalchemy:sqlalchemy.orm.relationship>`
          from which it inherits. The only difference is that it supports additional
          keyword arguments which are not supported in the original, and which
          are documented below.

          **For the original SQLAlchemy version, see:**
          :ref:`(SQLAlchemy) relationship() <sqlalchemy:sqlalchemy.orm.relationship>`

        :param argument: see
          :ref:`(SQLAlchemy) relationship() <sqlalchemy:sqlalchemy.orm.relationship>`

        :param supports_json: Determines whether the column can be serialized to or
          de-serialized from JSON format. If ``True``, can be serialized to JSON and
          de-serialized from JSON. If ``False``, will not be included when serialized
          to JSON and will be ignored if present in a de-serialized JSON.

          Can also accept a 2-member :class:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``, which means the column will not be serialized to JSON
          or de-serialized from JSON.

        :type supports_json: :class:`bool <python:bool>` / :class:`tuple <python:tuple>` of
          form (inbound: :class:`bool <python:bool>`, outbound: :class:`bool <python:bool>`)

        :param supports_yaml: Determines whether the column can be serialized to or
          de-serialized from YAML format. If ``True``, can be serialized to YAML and
          de-serialized from YAML. If ``False``, will not be included when serialized
          to YAML and will be ignored if present in a de-serialized YAML.

          Can also accept a 2-member :class:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``, which means the column will not be serialized to YAML
          or de-serialized from YAML.

        :type supports_yaml: :class:`bool <python:bool>` / :class:`tuple <python:tuple>` of
          form (inbound: :class:`bool <python:bool>`, outbound: :class:`bool <python:bool>`)

        :param supports_dict: Determines whether the column can be serialized to or
          de-serialized to a Python :class:`dict <python:dict>`. If ``True``, can
          be serialized to :class:`dict <python:dict>` and de-serialized from a
          :class:`dict <python:dict>`. If ``False``, will not be included when serialized
          to :class:`dict <python:dict>` and will be ignored if present in a de-serialized
          :class:`dict <python:dict>`.

          Can also accept a 2-member :class:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``, which means the column will not be serialized to a
          :class:`dict <python:dict>` or de-serialized from a :class:`dict <python:dict>`.

        :type supports_dict: :class:`bool <python:bool>` / :class:`tuple <python:tuple>` of
          form (inbound: :class:`bool <python:bool>`, outbound: :class:`bool <python:bool>`)

        """
        # pylint: disable=too-many-branches
        if on_serialize is not None and not isinstance(on_serialize, dict):
            on_serialize = {
                'csv': on_serialize,
                'json': on_serialize,
                'yaml': on_serialize,
                'dict': on_serialize
            }
        elif on_serialize is not None:
            if 'csv' not in on_serialize:
                on_serialize['csv'] = None
            if 'json' not in on_serialize:
                on_serialize['json'] = None
            if 'yaml' not in on_serialize:
                on_serialize['yaml'] = None
            if 'dict' not in on_serialize:
                on_serialize['dict'] = None
        else:
            on_serialize = {
                'csv': None,
                'json': None,
                'yaml': None,
                'dict': None
            }

        for key in on_serialize:
            item = on_serialize[key]
            if item is not None and not checkers.is_callable(item):
                raise SQLAthanorError('on_serialize for %s must be callable' % key)

        if on_deserialize is not None and not isinstance(on_deserialize, dict):
            on_deserialize = {
                'csv': on_deserialize,
                'json': on_deserialize,
                'yaml': on_deserialize,
                'dict': on_deserialize
            }
        elif on_deserialize is not None:
            if 'csv' not in on_deserialize:
                on_deserialize['csv'] = None
            if 'json' not in on_deserialize:
                on_deserialize['json'] = None
            if 'yaml' not in on_deserialize:
                on_deserialize['yaml'] = None
            if 'dict' not in on_deserialize:
                on_deserialize['dict'] = None
        else:
            on_deserialize = {
                'csv': None,
                'json': None,
                'yaml': None,
                'dict': None
            }

        for key in on_deserialize:
            item = on_deserialize[key]
            if item is not None and not checkers.is_callable(item):
                raise SQLAthanorError('on_deserialize for %s must be callable' % key)

        if supports_json is True:
            supports_json = (True, True)
        elif not supports_json:
            supports_json = (False, False)

        if supports_yaml is True:
            supports_yaml = (True, True)
        elif not supports_yaml:
            supports_yaml = (False, False)

        if supports_dict is True:
            supports_dict = (True, True)
        elif not supports_dict:
            supports_dict = (False, False)

        self.supports_csv = (False, False)
        self.csv_sequence = None
        self.supports_json = supports_json
        self.supports_yaml = supports_yaml
        self.supports_dict = supports_dict
        self.on_serialize = on_serialize
        self.on_deserialize = on_deserialize
        self.display_name = display_name

        comparator_factory = kwargs.pop('comparator_factory', RelationshipProperty.Comparator)

        super(RelationshipProperty, self).__init__(argument,
                                                   comparator_factory = comparator_factory,
                                                   **kwargs)

    class Comparator(SA_RelationshipProperty.Comparator):
        # pylint: disable=missing-docstring,abstract-method
        @property
        def supports_csv(self):
            return self.prop.supports_csv

        @property
        def csv_sequence(self):
            return self.prop.csv_sequence

        @property
        def supports_json(self):
            return self.prop.supports_json

        @property
        def supports_yaml(self):
            return self.prop.supports_yaml

        @property
        def supports_dict(self):
            return self.prop.supports_dict

        @property
        def on_serialize(self):
            return self.prop.on_serialize

        @property
        def on_deserialize(self):
            return self.prop.on_deserialize\

        @property
        def display_name(self):
            return self.prop.display_name


relationship = public_factory(RelationshipProperty, ".orm.relationship")


class Table(SA_Table):
    """Represents a table in a database. Inherits from
    :class:`sqlalchemy.schema.Table <sqlalchemy:sqlalchemy.schema.Table>`
    """

    # pylint: disable=too-many-ancestors, W0223

    def __init__(self, *args, **kwargs):
        """Construct a new ``Table`` object.

        .. warning::

          This method is analogous to the original SQLAlchemy
          :meth:`Table.__init__() <sqlalchemy:sqlalchemy.schema.Table.__init__>`
          from which it inherits. The only difference is that it supports additional
          keyword arguments which are not supported in the original, and which
          are documented below.

          **For the original SQLAlchemy version, see:**

          * **SQLAlchemy:** :class:`sqlalchemy.schema.Table <sqlalchemy:sqlalchemy.schema.Table>`

        """
        super(Table, self).__init__(*args, **kwargs)

    @classmethod
    def from_dict(cls,
                  serialized,
                  tablename,
                  metadata,
                  primary_key,
                  column_kwargs = None,
                  skip_nested = True,
                  default_to_str = False,
                  type_mapping = None,
                  **kwargs):
        """Generate a :class:`Table` object from a :class:`dict <python:dict>`.

        .. versionadded: 0.3.0

        :param serialized: The :class:`dict <python:dict>` that has been de-serialized
          from a given string. Keys will be treated as column names, while value data
          types will determine :class:`Column` data types.
        :type serialized: :class:`dict <python:dict>`

        :param tablename: The name of the SQL table to which the model corresponds.
        :type tablename: :class:`str <python:str>`

        :param metadata: a :class:`MetaData <sqlalchemy:sqlalchemy.schema.MetaData>`
          object which will contain this table. The metadata is used as a point of
          association of this table with other tables which are referenced via foreign
          key. It also may be used to associate this table with a particular
          :class:`Connectable <sqlalchemy:sqlalchemy.engine.Connectable>`.
        :type metadata: :class:`MetaData <sqlalchemy:sqlalchemy.schema.MetaData>`

        :param primary_key: The name of the column/key that should be used as the table's
          primary key.
        :type primary_key: :class:`str <python:str>`

        :param column_kwargs: An optional dictionary whose keys correspond to
          column/key, and whose values are themselves dictionaries with keyword
          arguments that will be passed ot the applicable :class:`Column`
          constructor. Defaults to :obj:`None <python:None>`.
        :type column_kwargs: :class:`dict <python:dict>` / :obj:`None <python:None>`

        :param skip_nested: If ``True`` then any keys in ``serialized`` that
          feature nested items (e.g. iterables, :class:`dict <python:dict>` objects,
          etc.) will be ignored. If ``False``, will treat nested items as
          :class:`str <python:str>`. Defaults to ``True``.
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

        :param kwargs: Any additional keyword arguments will be passed to the
          :class:`Table` constructor. For a full list of options, please see
          :class:`sqlalchemy.schema.Table <sqlalchemy:sqlalchemy.schema.Table>`.

        :returns: A :class:`Table` object.
        :rtype: :class:`Table`

        :raises UnsupportedValueTypeError: when a value in ``serialized`` does not
          have a corresponding key in ``type_mapping``
        :raises ValueError: if ``serialized`` is not a :class:`dict <python:dict>`
          or is empty
        :raises ValueError: if ``tablename`` is empty
        :raises ValueError: if ``primary_key`` is empty

        """
        if not isinstance(serialized, dict):
            raise ValueError('serialized must be a dict')

        if not serialized:
            raise ValueError('serialized cannot be empty')

        if not tablename:
            raise ValueError('tablename cannot be empty')

        if not primary_key:
            raise ValueError('primary_key cannot be empty')

        if column_kwargs is None:
            column_kwargs = {}

        columns = []
        for key in serialized:
            column_dict = {
                'name': key,
                'primary_key': key == primary_key
            }

            value = serialized[key]

            column_type = get_type_mapping(value,
                                           type_mapping = type_mapping,
                                           skip_nested = skip_nested,
                                           default_to_str = default_to_str)
            if column_type is None:
                continue

            column_dict['type_'] = column_type

            additional_kwargs = column_kwargs.get(key, {})
            for kwarg in additional_kwargs:
                column_dict[kwarg] = additional_kwargs[kwarg]

            column = Column(**column_dict)
            columns.append(column)

        return cls(tablename,
                   metadata,
                   *columns,
                   **kwargs)

    @classmethod
    def from_json(cls,
                  serialized,
                  tablename,
                  metadata,
                  primary_key,
                  column_kwargs = None,
                  skip_nested = True,
                  default_to_str = False,
                  type_mapping = None,
                  deserialize_function = None,
                  deserialize_kwargs = None,
                  **kwargs):
        """Generate a :class:`Table` object from a
        :term:`JSON <JavaScript Object Notation (JSON)>` string.

        .. versionadded: 0.3.0

        :param serialized: The :term:`JSON <JavaScript Object Notation (JSON)>`
          data to use. Keys will be treated as column names, while value data
          types will determine :class:`Column` data types.

          .. note::

            If providing a path to a file, and if the file contains more than one JSON
            object, will only use the first JSON object listed.

        :type serialized: :class:`str <python:str>` / Path-like object

        :param tablename: The name of the SQL table to which the model corresponds.
        :type tablename: :class:`str <python:str>`

        :param metadata: a :class:`MetaData <sqlalchemy:sqlalchemy.schema.MetaData>`
          object which will contain this table. The metadata is used as a point of
          association of this table with other tables which are referenced via foreign
          key. It also may be used to associate this table with a particular
          :class:`Connectable <sqlalchemy:sqlalchemy.engine.Connectable>`.
        :type metadata: :class:`MetaData <sqlalchemy:sqlalchemy.schema.MetaData>`

        :param primary_key: The name of the column/key that should be used as the table's
          primary key.
        :type primary_key: :class:`str <python:str>`

        :param column_kwargs: An optional dictionary whose keys correspond to
          column/key, and whose values are themselves dictionaries with keyword
          arguments that will be passed ot the applicable :class:`Column`
          constructor. Defaults to :obj:`None <python:None>`.
        :type column_kwargs: :class:`dict <python:dict>` / :obj:`None <python:None>`

        :param skip_nested: If ``True`` then any keys in ``serialized`` that
          feature nested items (e.g. iterables, :class:`dict <python:dict>` objects,
          etc.) will be ignored. If ``False``, will treat nested items as
          :class:`str <python:str>`. Defaults to ``True``.
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

        :param deserialize_kwargs: Optional additional keyword arguments that will be
          passed to the deserialize function. Defaults to :obj:`None <python:None>`.
        :type deserialize_kwargs: :class:`dict <python:dict>` / :obj:`None <python:None>`

        :param kwargs: Any additional keyword arguments will be passed to the
          :class:`Table` constructor. For a full list of options, please see
          :class:`sqlalchemy.schema.Table <sqlalchemy:sqlalchemy.schema.Table>`.

        :returns: A :class:`Table` object.
        :rtype: :class:`Table`

        :raises UnsupportedValueTypeError: when a value in ``serialized`` does not
          have a corresponding key in ``type_mapping``
        :raises DeserializationError: if ``serialized`` is not a valid
          :class:`str <python:str>`
        :raises ValueError: if ``tablename`` is empty
        :raises ValueError: if ``primary_key`` is empty

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

        table = cls.from_dict(from_json,
                              tablename,
                              metadata,
                              primary_key,
                              column_kwargs = column_kwargs,
                              skip_nested = skip_nested,
                              default_to_str = default_to_str,
                              type_mapping = type_mapping,
                              **kwargs)

        return table

    @classmethod
    def from_yaml(cls,
                  serialized,
                  tablename,
                  metadata,
                  primary_key,
                  column_kwargs = None,
                  skip_nested = True,
                  default_to_str = False,
                  type_mapping = None,
                  deserialize_function = None,
                  deserialize_kwargs = None,
                  **kwargs):
        """Generate a :class:`Table` object from a
        :term:`YAML <YAML Ain't a Markup Language (YAML)>` string.

        .. versionadded: 0.3.0

        :param serialized: The :term:`YAML <YAML Ain't a Markup Language (YAML)>`
          string to use. Keys will be treated as column names, while value data
          types will determine :class:`Column` data types.

          .. note::

            If providing a path to a file, and if the file contains more than one
            object, will only use the first object listed.

        :type serialized: :class:`str <python:str>` / Path-like object

        :param tablename: The name of the SQL table to which the model corresponds.
        :type tablename: :class:`str <python:str>`

        :param metadata: a :class:`MetaData <sqlalchemy:sqlalchemy.schema.MetaData>`
          object which will contain this table. The metadata is used as a point of
          association of this table with other tables which are referenced via foreign
          key. It also may be used to associate this table with a particular
          :class:`Connectable <sqlalchemy:sqlalchemy.engine.Connectable>`.
        :type metadata: :class:`MetaData <sqlalchemy:sqlalchemy.schema.MetaData>`

        :param primary_key: The name of the column/key that should be used as the table's
          primary key.
        :type primary_key: :class:`str <python:str>`

        :param column_kwargs: An optional dictionary whose keys correspond to
          column/key, and whose values are themselves dictionaries with keyword
          arguments that will be passed ot the applicable :class:`Column`
          constructor. Defaults to :obj:`None <python:None>`.
        :type column_kwargs: :class:`dict <python:dict>` / :obj:`None <python:None>`

        :param skip_nested: If ``True`` then any keys in ``serialized`` that
          feature nested items (e.g. iterables, :class:`dict <python:dict>` objects,
          etc.) will be ignored. If ``False``, will treat nested items as
          :class:`str <python:str>`. Defaults to ``True``.
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

        :param deserialize_kwargs: Optional additional keyword arguments that will be
          passed to the deserialize function. Defaults to :obj:`None <python:None>`.
        :type deserialize_kwargs: :class:`dict <python:dict>` / :obj:`None <python:None>`

        :param kwargs: Any additional keyword arguments will be passed to the
          :class:`Table` constructor. For a full list of options, please see
          :class:`sqlalchemy.schema.Table <sqlalchemy:sqlalchemy.schema.Table>`.

        :returns: A :class:`Table` object.
        :rtype: :class:`Table`

        :raises UnsupportedValueTypeError: when a value in ``serialized`` does not
          have a corresponding key in ``type_mapping``
        :raises DeserializationError: if ``serialized`` is not a valid
          :class:`str <python:str>`
        :raises ValueError: if ``tablename`` is empty
        :raises ValueError: if ``primary_key`` is empty

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

        table = cls.from_dict(from_yaml,
                              tablename,
                              metadata,
                              primary_key,
                              column_kwargs = column_kwargs,
                              skip_nested = skip_nested,
                              default_to_str = default_to_str,
                              type_mapping = type_mapping,
                              **kwargs)

        return table

    @classmethod
    def from_csv(cls,
                 serialized,
                 tablename,
                 metadata,
                 primary_key,
                 column_kwargs = None,
                 skip_nested = True,
                 default_to_str = False,
                 type_mapping = None,
                 delimiter = '|',
                 wrap_all_strings = False,
                 null_text = 'None',
                 wrapper_character = "'",
                 double_wrapper_character_when_nested = False,
                 escape_character = "\\",
                 line_terminator = '\r\n',
                 **kwargs):
        """Generate a :class:`Table` object from a
        :term:`CSV <Comma-Separated Value (CSV)>` string.

        .. versionadded: 0.3.0

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

        :param metadata: a :class:`MetaData <sqlalchemy:sqlalchemy.schema.MetaData>`
          object which will contain this table. The metadata is used as a point of
          association of this table with other tables which are referenced via foreign
          key. It also may be used to associate this table with a particular
          :class:`Connectable <sqlalchemy:sqlalchemy.engine.Connectable>`.
        :type metadata: :class:`MetaData <sqlalchemy:sqlalchemy.schema.MetaData>`

        :param primary_key: The name of the column/key that should be used as the table's
          primary key.
        :type primary_key: :class:`str <python:str>`

        :param column_kwargs: An optional dictionary whose keys correspond to
          column/key, and whose values are themselves dictionaries with keyword
          arguments that will be passed ot the applicable :class:`Column`
          constructor. Defaults to :obj:`None <python:None>`.
        :type column_kwargs: :class:`dict <python:dict>` / :obj:`None <python:None>`

        :param skip_nested: If ``True`` then any keys in ``serialized`` that
          feature nested items (e.g. iterables, :class:`dict <python:dict>` objects,
          etc.) will be ignored. If ``False``, will treat nested items as
          :class:`str <python:str>`. Defaults to ``True``.
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

        :param delimiter: The delimiter used between columns. Defaults to ``|``.
        :type delimiter: :class:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is applied. Defaults to ``'``.
        :type wrapper_character: :class:`str <python:str>`

        :param null_text: The string used to indicate an empty value if empty
          values are wrapped. Defaults to `None`.
        :type null_text: :class:`str <python:str>`

        :param kwargs: Any additional keyword arguments will be passed to the
          :class:`Table` constructor. For a full list of options, please see
          :class:`sqlalchemy.schema.Table <sqlalchemy:sqlalchemy.schema.Table>`.

        :returns: A :class:`Table` object.
        :rtype: :class:`Table`

        :raises DeserializationError: if ``serialized`` is not a valid
          :class:`str <python:str>`
        :raises UnsupportedValueTypeError: when a value in ``serialized`` does not
          have a corresponding key in ``type_mapping``
        :raises ValueError: if ``tablename`` is empty
        :raises ValueError: if ``primary_key`` is empty
        :raises CSVStructureError: if there are less than 2 (two) rows in ``serialized``
          or if column headers are not valid Python variable names

        """
        # pylint: disable=line-too-long,invalid-name,too-many-arguments

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

        table = cls.from_dict(from_csv,
                              tablename,
                              metadata,
                              primary_key,
                              column_kwargs = column_kwargs,
                              skip_nested = skip_nested,
                              default_to_str = default_to_str,
                              type_mapping = type_mapping,
                              **kwargs)

        return table
