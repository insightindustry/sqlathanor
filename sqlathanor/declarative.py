# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.state import InstanceState
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.util import symbol, OrderedProperties

from validator_collection import checkers

# pylint: disable=no-member

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

    @classmethod
    def _get_instance_attributes(cls,
                                 read_only = None,
                                 include_private = False,
                                 exclude_methods = True):
        """Retrieve the names of the model's attributes and methods.

        :param read_only: If :class:`None`, returns all attributes. If ``True``,
          returns only read-only properties. If ``False``, does not return any read-only
          properties. Defaults to :class:`None`.
        :type read_only: :ref:`bool <python:bool>` / :class:`None`

        :param include_private: If ``True``, includes properties whose names start
          with an underscore. Defaults to ``False``.
        :type include_private: :ref:`bool <python:bool>`

        :param exclude_methods: If ``True``, excludes attributes that correspond to
          methods (are callable). Defaults to ``True``.
        :type exclude_methods: :ref:`bool <python:bool>`

        .. note::

          This method will return all attributes, properties, and methods supported
          by the model - whether they map to database columns or not.

        :returns: An iterable of attribute names defined for the model.
        :rtype: :ref:`list <python:list>` of :ref:`str <python:str>`

        """
        base_attributes = dir(cls)
        instance_attributes = []
        for key in base_attributes:
            if key.startswith('_') and not include_private:
                continue

            item = getattr(cls, key)
            if checkers.is_callable(item) and exclude_methods:
                continue

            if isinstance(item, property):
                if read_only and item.fset is not None:
                    continue

                if read_only is False and item.fset is None:
                    continue

            elif read_only is not None:
                continue

            instance_attributes.append(key)

        return instance_attributes

    @classmethod
    def get_serializable_attributes(cls,
                                    supports_dict = True,
                                    supports_json = True,
                                    supports_csv = True,
                                    supports_yaml = True,
                                    exclude_private = True):
        """Retrieve a list of model attribute names (Python attributes) whose values
        can be serialized to a database, to JSON, CSV, etc.

        :param supports_dict: If ``True``, includes attribute names that can be
          serialized to a :ref:`dict <python:dict>`. Defaults to ``True``.
        :type supports_dict: :ref:`bool <python:bool>`

        :param supports_json: If ``True``, includes attribute names that can be
          serialized to :term:`JSON`. Defaults to ``True``.
        :type supports_json: :ref:`bool <python:bool>`

        :param supports_csv: If ``True``, includes attribute names that can be
          serialized to :term:`CSV`. Defaults to ``True``.
        :type supports_csv: :ref:`bool <python:bool>`

        :param supports_yaml: If ``True``, includes attribute names that can be
          serialized to :term:`YAML`. Defaults to ``True``.
        :type supports_yaml: :ref:`bool <python:bool>`

        :param exclude_private: If ``True``, will exclude private attributes whose
          names begin with an underscore. Defaults to ``True``.
        :type exclude_private: :ref:`bool <python:bool>`

        :returns: List of model attribute names that can be serialized.
        :rtype: :ref:`list <python:list>` of :ref:`str <python:str>`
        """
        include_private = not exclude_private

        instance_attributes = cls._get_instance_attributes(
            include_private = include_private,
            exclude_methods = True
        )

        attributes = []
        for key in instance_attributes:
            value = getattr(cls, key)

            if supports_dict and getattr(value, 'supports_dict', None):
                attributes.append(key)
                continue

            if supports_json and getattr(value, 'supports_json', None):
                attributes.append(key)
                continue

            if supports_csv and getattr(value, 'supports_csv', None):
                attributes.append(key)
                continue

            if supports_yaml and getattr(value, 'supports_yaml', None):
                attributes.append(key)
                continue

        return attributes

    @classmethod
    def get_csv_column_names(cls):
        """Retrieve the CSV column names that apply for this object.

        :returns: Ordered list of CSV column names that apply for this object.
        :rtype: :ref:`list <python:list>` of :ref:`str <python:str>`
        """
        csv_attributes = cls.get_serializable_attributes(supports_dict = None,
                                                         supports_json = None,
                                                         supports_csv = True,
                                                         supports_yaml = None)
        csv_sequences = []
        for key in csv_attributes:
            item = getattr(cls, key, None)

            csv_sequences.append(getattr(item,
                                         'csv_sequence',
                                         len(csv_attributes)))

        csv_attributes_sequenced = zip(csv_attributes, csv_sequences)

        csv_keys = [x[0] for x in sorted(csv_attributes_sequenced,
                                         key = lambda x: x[1])]

        return csv_keys

    @classmethod
    def get_dict_attribute_names(cls):
        """Retrieve the :ref:`dict <python:dict>` attribute names that apply for this object.

        :returns: Ordered list of attribute names that apply for this object.
        :rtype: :ref:`list <python:list>` of :ref:`str <python:str>`
        """
        attributes = cls.get_serializable_attributes(supports_dict = True,
                                                     supports_json = None,
                                                     supports_csv = None,
                                                     supports_yaml = None)
        return attributes

    @classmethod
    def get_json_attribute_names(cls):
        """Retrieve the JSON attribute names that apply for this object.

        :returns: Ordered list of JSON attribute names that apply for this object.
        :rtype: :ref:`list <python:list>` of :ref:`str <python:str>`
        """
        attributes = cls.get_serializable_attributes(supports_dict = None,
                                                     supports_json = True,
                                                     supports_csv = None,
                                                     supports_yaml = None)
        return attributes

    @classmethod
    def get_yaml_attribute_names(cls):
        """Retrieve the YAML attribute names that apply for this object.

        :returns: Ordered list of YAML attribute names that apply for this object.
        :rtype: :ref:`list <python:list>` of :ref:`str <python:str>`
        """
        attributes = cls.get_serializable_attributes(supports_dict = None,
                                                     supports_json = None,
                                                     supports_csv = None,
                                                     supports_yaml = True)
        return attributes

    @classmethod
    def get_csv_header(cls, delimiter = '|'):
        """Retrieve a header string for a CSV representation of the model.

        :param delimiter: The character(s) to utilize between columns. Defaults to
          a pipe (``|``).
        :type delimiter: :ref:`str <python:str>`

        :returns: A string ending in ``\n`` with the model's CSV column names
          listed, separated by the ``delimiter``.
        :rtype: :ref:`str <python:str>`
        """
        column_names = cls.get_csv_column_names()
        header_string = delimiter.join(column_names) + '\n'

        return header_string

    def get_csv_data(self,
                     delimiter = '|',
                     wrap_all_strings = False,
                     wrap_empty_values = True,
                     wrapper_character = "'"):
        """Return the CSV representation of the model instance (record).

        :param delimiter: The character(s) to place between columns. Defaults to
          a pipe ('|').
        :type delimiter: :ref:`str <python:str>`

        :param wrap_all_strings: If ``True``, will wrap all string values in the
          ``wrapper_character``. Defaults to ``False``.
        :type wrap_all_strings: :ref:`bool <python:bool>`

        :param wrap_empty_values: If ``True``, will wrap empty values with the
          ``wrapper_character``. Defaults to ``True``.

          .. note::

            This solves an issue in Microsoft Excel where an empty value in the
            last column of a CSV record will now be recognized as a valid value.

        :type wrap_empty_values: :ref:`bool <python:bool>`

        :param wrapper_character: The character to use as a wrapper if a column
          value needs to be wrapped. Defaults to a single quote (``'``).
        :type wrapper_character: :ref:`str <python:str>`

        :returns: The CSV representation of the model instance (record).
        :rtype: :ref:`str <python: str>`
        """
        if not wrapper_character:
            wrapper_character = '\''

        csv_column_names = self.get_csv_column_names()

        data = [getattr(self, x, '') for x in csv_column_names if hasattr(self, x)]

        for index, item in enumerate(data):
            if item == 'None' or item is None:
                if wrap_empty_values:
                    data[index] = wrapper_character + str(item) + wrapper_character
                else:
                    data[index] = ''
            elif checkers.is_string(item) and wrap_all_strings:
                data[index] = wrapper_character + item + wrapper_character

        data_row = delimiter.join(data) + '\n'

        return data_row

    def to_csv(self,
               include_header = False,
               delimiter = '|',
               wrap_all_strings = False,
               wrap_empty_values = True,
               wrapper_character = "'"):
        """Retrieve a CSv string with the object's data.

        :param include_header: If ``True``, will include a header row with column
          labels. If ``False``, will not include a header row. Defaults to ``True``.
        :type include_header: :ref:`bool <python:bool>`

        :returns: Data from the object in CSV (pipe-delimited) format.
        :rtype: :ref:`str <python:str>`
        """
        if include_header is True:
            return self.get_csv_header(delimiter = delimiter) + \
                   self.get_csv_data(delimiter = delimiter,
                                     wrap_all_strings = wrap_all_strings,
                                     wrap_empty_values = wrap_empty_values,
                                     wrapper_character = wrapper_character)

        return self.get_csv_data(delimiter = delimiter,
                                 wrap_all_strings = wrap_all_strings,
                                 wrap_empty_values = wrap_empty_values,
                                 wrapper_character = wrapper_character)

    def to_dict(self,
                max_nesting = 0,
                current_nesting = 0):
        """Return a :ref:`dict <python:dict>` representation of the object.

        :param max_nesting: The maximum number of levels that the resulting
          :ref:`dict <python:dict>` object can be nested. If set to ``0``, will
          not nest other serializable objects. Defaults to ``0``.
        :type max_nesting: :ref:`int <python:int>`

        :param current_nesting: The current nesting level at which the
          :ref:`dict <python:dict>` representation will reside. Defaults to ``0``.
        :type current_nesting: :ref:`int <python:int>`

        :returns: A :ref:`dict <python:dict>` representation of the object.
        :rtype: :ref:`dict <python:dict>`
        """
        dict_object = {}

        dict_attributes = self.get_dict_attribute_names()

        for key in dict_attributes:
            item = getattr(self, key, None)

            try:
                getattr(item, 'to_dict')
                has_attribute = True
            except AttributeError:
                has_attribute = False

            if has_attribute and current_nesting < max_nesting:
                item = item.to_dict(max_nesting = max_nesting,
                                    current_nesting = current_nesting + 1)

            dict_object[key] = item

        return dict_object

BaseModel = declarative_base(cls = BaseModel)
