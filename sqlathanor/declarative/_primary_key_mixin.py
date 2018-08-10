# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

from sqlalchemy.inspection import inspect

class PrimaryKeyMixin(object):
    """Mixin that provides functionality relating to model class primary key
    columns."""

    def _check_is_model_instance(self):
        # pylint: disable=no-self-use
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
