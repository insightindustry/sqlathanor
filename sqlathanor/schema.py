# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

from sqlalchemy import Column as SA_Column

from validator_collection import checkers


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

        :param value_validator: A function that will be called when assigning a value
          to the column. The function will either coerce the value being assigned
          to a form that is acceptable by the column, or will raise an exception
          if it cannot be coerced. If :class:`None`, the data type's default validator
          function will be called instead.

          Defaults to :class:`None`.

        :type value_validator: function

        """
        value_validator = kwargs.pop('value_validator', None)
        if value_validator is not None and not checkers.is_callable(value_validator):
            raise ValueError('value_validator must be callable')

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
        self.value_validator = value_validator

        super(Column, self).__init__(*args, **kwargs)
