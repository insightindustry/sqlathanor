# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

import functools
import operator

from sqlalchemy import Column as SA_Column
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.relationships import RelationshipProperty as SA_RelationshipProperty
from sqlalchemy.util.langhelpers import public_factory
from sqlalchemy.ext.hybrid import hybrid_property as SA_hybrid_property

from sqlalchemy import exc, orm, util, inspect


from validator_collection import checkers, validators

from sqlathanor import attributes
from sqlathanor._serialization_support import SerializationMixin
from sqlathanor.errors import SQLAthanorError


class Column(SerializationMixin, SA_Column):
    """Represents a column in a database table."""

    # pylint: disable=too-many-ancestors, W0223

    def __init__(self, *args, **kwargs):
        """Construct a new ``Column`` object.

        .. warning::

          This method is analogous to the original
          :ref:`SQLAlchemy Column.__init__() <sqlalchemy:sqlalchemy.sql.schema.Column.__init__>`
          from which it inherits. The only difference is that it supports additional
          keyword arguments which are not supported in the original, and which
          are documented below.

          **For the original SQLAlchemy version, see:**
          :ref:`(SQLAlchemy) Column.__init__() <sqlalchemy:sqlalchemy.sql.schema.Column.__init__>`

        :param supports_csv: Determines whether the column can be serialized to or
          de-serialized from CSV format. If ``True``, can be serialized to CSV and
          de-serialized from CSV. If ``False``, will not be included when serialized to CSV
          and will be ignored if present in a de-serialized CSV.

          Can also accept a 2-member :ref:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``, which means the column will not be serialized to CSV
          or de-serialized from CSV.

        :type supports_csv: :ref:`bool <python:bool>` / :ref:`tuple <python:tuple>` of
          form (inbound: :ref:`bool <python:bool>`, outbound: :ref:`bool <python:bool>`)

        :param csv_sequence: Indicates the numbered position that the column should be in
          in a valid CSV-version of the object. Defaults to :class:`None`.

          .. note::

            If not specified, the column will go after any columns that *do* have a
            ``csv_sequence`` assigned, sorted alphabetically.

            If two columns have the same ``csv_sequence``, they will be sorted
            alphabetically.

        :type csv_sequence: :ref:`int <python:int>` / :class:`None`

        :param supports_json: Determines whether the column can be serialized to or
          de-serialized from JSON format. If ``True``, can be serialized to JSON and
          de-serialized from JSON. If ``False``, will not be included when serialized
          to JSON and will be ignored if present in a de-serialized JSON.

          Can also accept a 2-member :ref:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``, which means the column will not be serialized to JSON
          or de-serialized from JSON.

        :type supports_json: :ref:`bool <python:bool>` / :ref:`tuple <python:tuple>` of
          form (inbound: :ref:`bool <python:bool>`, outbound: :ref:`bool <python:bool>`)

        :param supports_yaml: Determines whether the column can be serialized to or
          de-serialized from YAML format. If ``True``, can be serialized to YAML and
          de-serialized from YAML. If ``False``, will not be included when serialized
          to YAML and will be ignored if present in a de-serialized YAML.

          Can also accept a 2-member :ref:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``, which means the column will not be serialized to YAML
          or de-serialized from YAML.

        :type supports_yaml: :ref:`bool <python:bool>` / :ref:`tuple <python:tuple>` of
          form (inbound: :ref:`bool <python:bool>`, outbound: :ref:`bool <python:bool>`)

        :param supports_dict: Determines whether the column can be serialized to or
          de-serialized to a Python :ref:`dict <python:dict>`. If ``True``, can
          be serialized to :ref:`dict <python:dict>` and de-serialized from a
          :ref:`dict <python:dict>`. If ``False``, will not be included when serialized
          to :ref:`dict <python:dict>` and will be ignored if present in a de-serialized
          :ref:`dict <python:dict>`.

          Can also accept a 2-member :ref:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``, which means the column will not be serialized to a
          :ref:`dict <python:dict>` or de-serialized from a :ref:`dict <python:dict>`.

        :type supports_dict: :ref:`bool <python:bool>` / :ref:`tuple <python:tuple>` of
          form (inbound: :ref:`bool <python:bool>`, outbound: :ref:`bool <python:bool>`)

        :param on_deserialize: A function that will be called when attempting to
          assign a de-serialized value to the column. This is intended to either coerce
          the value being assigned to a form that is acceptable by the column, or
          raise an exception if it cannot be coerced. If :class:`None`, the data
          type's default ``on_deserialize`` function will be called instead.

          .. tip::

            If you need to execute different ``on_deserialize`` functions for
            different formats, you can also supply a :ref:`dict <python:dict>`:

            .. code-block:: python

              on_deserialize = {
                'csv': csv_on_deserialize_callable,
                'json': json_on_deserialize_callable,
                'yaml': yaml_on_deserialize_callable,
                'dict': dict_on_deserialize_callable
              }

          Defaults to :class:`None`.

        :type on_deserialize: callable / :ref:`dict <python:dict>` with formats
          as keys and values as callables

        :param on_serialize: A function that will be called when attempting to
          serialize a value from the column. If :class:`None`, the data
          type's default ``on_serialize`` function will be called instead.

          .. tip::

            If you need to execute different ``on_serialize`` functions for
            different formats, you can also supply a :ref:`dict <python:dict>`:

            .. code-block:: python

              on_serialize = {
                'csv': csv_on_serialize_callable,
                'json': json_on_serialize_callable,
                'yaml': yaml_on_serialize_callable,
                'dict': dict_on_serialize_callable
              }

          Defaults to :class:`None`.

        :type on_serialize: callable / :ref:`dict <python:dict>` with formats
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

          Can also accept a 2-member :ref:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``, which means the column will not be serialized to JSON
          or de-serialized from JSON.

        :type supports_json: :ref:`bool <python:bool>` / :ref:`tuple <python:tuple>` of
          form (inbound: :ref:`bool <python:bool>`, outbound: :ref:`bool <python:bool>`)

        :param supports_yaml: Determines whether the column can be serialized to or
          de-serialized from YAML format. If ``True``, can be serialized to YAML and
          de-serialized from YAML. If ``False``, will not be included when serialized
          to YAML and will be ignored if present in a de-serialized YAML.

          Can also accept a 2-member :ref:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``, which means the column will not be serialized to YAML
          or de-serialized from YAML.

        :type supports_yaml: :ref:`bool <python:bool>` / :ref:`tuple <python:tuple>` of
          form (inbound: :ref:`bool <python:bool>`, outbound: :ref:`bool <python:bool>`)

        :param supports_dict: Determines whether the column can be serialized to or
          de-serialized to a Python :ref:`dict <python:dict>`. If ``True``, can
          be serialized to :ref:`dict <python:dict>` and de-serialized from a
          :ref:`dict <python:dict>`. If ``False``, will not be included when serialized
          to :ref:`dict <python:dict>` and will be ignored if present in a de-serialized
          :ref:`dict <python:dict>`.

          Can also accept a 2-member :ref:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``, which means the column will not be serialized to a
          :ref:`dict <python:dict>` or de-serialized from a :ref:`dict <python:dict>`.

        :type supports_dict: :ref:`bool <python:bool>` / :ref:`tuple <python:tuple>` of
          form (inbound: :ref:`bool <python:bool>`, outbound: :ref:`bool <python:bool>`)

        """
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

        comparator_factory = kwargs.pop('comparator_factory', RelationshipProperty.Comparator)

        super(RelationshipProperty, self).__init__(argument,
                                                   comparator_factory = comparator_factory,
                                                   **kwargs)

    class Comparator(SA_RelationshipProperty.Comparator):
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

relationship = public_factory(RelationshipProperty, ".orm.relationship")
