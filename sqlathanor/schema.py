# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

import functools

from sqlalchemy import Column as SA_Column
from sqlalchemy.orm.relationships import RelationshipProperty as SA_RelationshipProperty
from sqlalchemy.util.langhelpers import public_factory
from sqlalchemy.ext.hybrid import hybrid_property as SA_hybrid_property

from validator_collection import checkers

from sqlathanor.errors import SQLAthanorError


class Column(SA_Column):
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

        """
        on_serialize = kwargs.pop('on_serialize', None)
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

        on_deserialize = kwargs.pop('on_deserialize', None)
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

        supports_csv = kwargs.pop('supports_csv', (False, False))
        csv_sequence = kwargs.pop('csv_sequence', None)
        supports_json = kwargs.pop('supports_json', (False, False))
        supports_yaml = kwargs.pop('supports_yaml', (False, False))
        supports_dict = kwargs.pop('supports_dict', (False, False))

        if supports_csv is True:
            supports_csv = (True, True)
        elif not supports_csv:
            supports_csv = (False, False)

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

        self.supports_csv = supports_csv
        self.csv_sequence = csv_sequence
        self.supports_json = supports_json
        self.supports_yaml = supports_yaml
        self.supports_dict = supports_dict
        self.on_serialize = on_serialize
        self.on_deserialize = on_deserialize

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
                 **kwargs):
        """Provide a relationship between two mapped classes.

        This corresponds to a parent-child or associate table relationship.
        The constructed class is an instance of :class:`RelationshipProperty`.

        When serializing or de-serializing relationships, they essentially become
        "nested" objects. For example, if you have an ``Account`` table with a
        relationship to a ``User`` table, you might want to nest or embed a list of
        ``User`` objects within a serialized ``Account`` object.

        .. caution::

          Unlike columns, hybrid properties, or association proxies, relationships
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


class hybrid_property(SA_hybrid_property):
    """A decorator which allows definition of a Python descriptor with both
    instance-level and class-level behavior.

    """
    def __init__(self,
                 fget = None,
                 fset = None,
                 fdel = None,
                 expr = None,
                 custom_comparator = None,
                 update_expr = None,
                 supports_csv = False,
                 csv_sequence = None,
                 supports_json = False,
                 supports_yaml = False,
                 supports_dict = False,
                 on_serialize = None,
                 on_deserialize = None):
        """Create a new :class:`hybrid_property`.

        Usage is typically via decorator::

            from sqlathanor import hybrid_property

            class SomeClass(object):
                @hybrid_property
                def value(self):
                    return self._value

                @value.setter
                def value(self, value):
                    self._value = value

        When configuring serialization using the decorator, pass
        ``supports_<format>`` and ``csv_sequence`` as arguments to the decorator::

            from sqlathanor import hybrid_property

            class SomeClass(object):

                @hybrid_property(supports_csv = False, supports_json = True)
                def value(self):
                    return self._value

                @value.setter
                def value(self, value):
                    self._value = value

        .. tip::

          When configuring serializaton on your hybrid property's generic
          ``@hybrid_property`` decorator, the configuration will apply to both
          the *inbound* (:term:`de-serialization`) and *outbound*
          (:term:`serialization`) processes, just as for a :class:`Column`
          or :func:`relationship`.

          If you don't specify a setter for your :term:`hybrid property`, then
          *inbound* (:term:`de-serialization`) data for the property will be
          ignored, as if you had set it to ``False``.

        :param supports_csv: Determines whether the property can be serialized to or
          de-serialized from CSV format. If ``True``, can be serialized to CSV and
          de-serialized from CSV. If ``False``, will not be included when serialized to CSV
          and will be ignored if present in a de-serialized CSV.

          Can also accept a 2-member :ref:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``, which means the property will not be serialized to CSV
          or de-serialized from CSV.

        :type supports_csv: :ref:`bool <python:bool>` / :ref:`tuple <python:tuple>` of
          form (inbound: :ref:`bool <python:bool>`, outbound: :ref:`bool <python:bool>`)

        :param csv_sequence: Indicates the numbered position that the property should be in
          in a valid CSV-version of the object. Defaults to :class:`None`.

          .. note::

            If not specified, the column will go after any columns that *do* have a
            ``csv_sequence`` assigned, sorted alphabetically.

            If two items have the same ``csv_sequence``, they will be sorted
            alphabetically.

        :type csv_sequence: :ref:`int <python:int>` / :class:`None`

        :param supports_json: Determines whether the property can be serialized to or
          de-serialized from JSON format. If ``True``, can be serialized to JSON and
          de-serialized from JSON. If ``False``, will not be included when serialized
          to JSON and will be ignored if present in a de-serialized JSON.

          Can also accept a 2-member :ref:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``, which means the property will not be serialized to JSON
          or de-serialized from JSON.

        :type supports_json: :ref:`bool <python:bool>` / :ref:`tuple <python:tuple>` of
          form (inbound: :ref:`bool <python:bool>`, outbound: :ref:`bool <python:bool>`)

        :param supports_yaml: Determines whether the property can be serialized to or
          de-serialized from YAML format. If ``True``, can be serialized to YAML and
          de-serialized from YAML. If ``False``, will not be included when serialized
          to YAML and will be ignored if present in a de-serialized YAML.

          Can also accept a 2-member :ref:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``, which means the property will not be serialized to YAML
          or de-serialized from YAML.

        :type supports_yaml: :ref:`bool <python:bool>` / :ref:`tuple <python:tuple>` of
          form (inbound: :ref:`bool <python:bool>`, outbound: :ref:`bool <python:bool>`)

        :param supports_dict: Determines whether the property can be serialized to or
          de-serialized to a Python :ref:`dict <python:dict>`. If ``True``, can
          be serialized to :ref:`dict <python:dict>` and de-serialized from a
          :ref:`dict <python:dict>`. If ``False``, will not be included when serialized
          to :ref:`dict <python:dict>` and will be ignored if present in a de-serialized
          :ref:`dict <python:dict>`.

          Can also accept a 2-member :ref:`tuple <python:tuple>` (inbound / outbound)
          which determines de-serialization and serialization support respectively.

          Defaults to ``False``, which means the property will not be serialized to a
          :ref:`dict <python:dict>` or de-serialized from a :ref:`dict <python:dict>`.

        :type supports_dict: :ref:`bool <python:bool>` / :ref:`tuple <python:tuple>` of
          form (inbound: :ref:`bool <python:bool>`, outbound: :ref:`bool <python:bool>`)

        """

        if supports_csv is True:
            supports_csv = (True, True)
        elif not supports_csv:
            supports_csv = (False, False)

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

        self.supports_csv = supports_csv
        self.csv_sequence = csv_sequence
        self.supports_json = supports_json
        self.supports_yaml = supports_yaml
        self.supports_dict = supports_dict

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

        self.on_serialize = on_serialize
        self.on_deserialize = on_deserialize

        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.expr = expr
        self.custom_comparator = custom_comparator
        self.update_expr = update_expr
        functools.update_wrapper(self, fget)

    def __call__(self, fget, **kwargs):

        return self._copy(fget = fget, **kwargs)
