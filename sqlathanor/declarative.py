# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect

class BaseModel(object):
    """Base class that establishes shared methods, attributes,and properties."""

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


BaseModel = declarative_base(cls = BaseModel)
