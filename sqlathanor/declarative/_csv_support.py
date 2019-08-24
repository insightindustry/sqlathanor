# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

import csv

from validator_collection import checkers, validators

from sqlathanor._compat import StringIO, dict as dict_
from sqlathanor.utilities import read_csv_data, get_attribute_names
from sqlathanor.errors import SerializableAttributeError, \
    UnsupportedSerializationError, CSVStructureError, DeserializationError


class CSVSupportMixin(object):
    """Mixin that provides CSV serialization/de-serialization support."""

    @classmethod
    def get_csv_column_names(cls,
                             deserialize = True,
                             serialize = True,
                             config_set = None):
        """Retrieve a list of CSV column names.

        :param deserialize: If ``True``, returns columns that support
          :term:`de-serialization`. If ``False``, returns columns that do *not*
          support deserialization. If :obj:`None <python:None>`, does not take
          deserialization into account. Defaults to ``True``.
        :type deserialize: :class:`bool <python:bool>`

        :param serialize: If ``True``, returns columns that support
          :term:`serialization`. If ``False``, returns columns that do *not*
          support serialization. If :obj:`None <python:None>`, does not take
          serialization into account. Defaults to ``True``.
        :type serialize: :class:`bool <python:bool>`

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          to use. Defaults to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :returns: List of CSV column names, sorted according to their configuration.
        :rtype: :class:`list <python:list>` of :class:`str <python:str>`
        """
        config = cls.get_csv_serialization_config(deserialize = deserialize,
                                                  serialize = serialize,
                                                  config_set = config_set)
        attribute_names = [x.name for x in config]
        display_names = [x.display_name for x in config]

        return [x[0] or x[1] for x in zip(display_names, attribute_names)]

    @classmethod
    def _get_csv_attribute_names(cls,
                                 deserialize = True,
                                 serialize = True,
                                 config_set = None):
        """Retrieve a list of the attribute names that are to be serialized to CSV.

        :param deserialize: If ``True``, returns columns that support
          :term:`de-serialization`. If ``False``, returns columns that do *not*
          support deserialization. If :obj:`None <python:None>`, does not take
          deserialization into account. Defaults to ``True``.
        :type deserialize: :class:`bool <python:bool>`

        :param serialize: If ``True``, returns columns that support
          :term:`serialization`. If ``False``, returns columns that do *not*
          support serialization. If :obj:`None <python:None>`, does not take
          serialization into account. Defaults to ``True``.
        :type serialize: :class:`bool <python:bool>`

        :returns: List of attribute names, sorted according to their configuration.
        :rtype: :class:`list <python:list>` of :class:`str <python:str>`
        """
        config = cls.get_csv_serialization_config(deserialize = deserialize,
                                                  serialize = serialize,
                                                  config_set = config_set)
        return [x.name for x in config]

    @classmethod
    def _get_attribute_csv_header(cls,
                                  attributes,
                                  delimiter = '|',
                                  wrap_all_strings = False,
                                  wrapper_character = "'",
                                  double_wrapper_character_when_nested = False,
                                  escape_character = "\\",
                                  line_terminator = '\r\n'):
        r"""Retrieve a header string for a CSV representation of the model.

        :param attributes: List of :term:`model attributes <model attribute>` to
          include.
        :type attributes: :class:`list <python:list>` of :class:`str <python:str>`

        :param delimiter: The character(s) to utilize between columns. Defaults to
          a pipe (``|``).
        :type delimiter: :class:`str <python:str>`

        :param wrap_all_strings: If ``True``, wraps any string data in the
          ``wrapper_character``. If ``None``, only wraps string data if it contains
          the ``delimiter``. Defaults to ``False``.
        :type wrap_all_strings: :class:`bool <python:bool>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is necessary. Defaults to ``'``.
        :type wrapper_character: :class:`str <python:str>`

        :param double_wrapper_character_when_nested: If ``True``, will double the
          ``wrapper_character`` when it is found inside a column value. If ``False``,
          will precede the ``wrapper_character`` by the ``escape_character`` when
          it is found inside a column value. Defaults to ``False``.
        :type double_wrapper_character_when_nested: :class:`bool <python:bool>`

        :param escape_character: The character to use when escaping nested wrapper
          characters. Defaults to ``\``.
        :type escape_character: :class:`str <python:str>`

        :param line_terminator: The character used to mark the end of a line.
          Defaults to ``\r\n``.
        :type line_terminator: :class:`str <python:str>`

        :returns: A string ending in ``line_terminator`` with the model's CSV column names
          listed, separated by the ``delimiter``.
        :rtype: :class:`str <python:str>`
        """
        if not wrapper_character:
            wrapper_character = '\''

        if wrap_all_strings:
            quoting = csv.QUOTE_NONNUMERIC
        else:
            quoting = csv.QUOTE_MINIMAL

        if 'sqlathanor' in csv.list_dialects():
            csv.unregister_dialect('sqlathanor')

        csv.register_dialect('sqlathanor',
                             delimiter = delimiter,
                             doublequote = double_wrapper_character_when_nested,
                             escapechar = escape_character,
                             quotechar = wrapper_character,
                             quoting = quoting,
                             lineterminator = line_terminator)

        output = StringIO()
        csv_writer = csv.DictWriter(output,
                                    fieldnames = attributes,
                                    dialect = 'sqlathanor')

        csv_writer.writeheader()

        header_string = output.getvalue()
        output.close()

        csv.unregister_dialect('sqlathanor')

        return header_string

    def _get_attribute_csv_data(self,
                                attributes,
                                is_dumping = False,
                                delimiter = '|',
                                wrap_all_strings = False,
                                null_text = 'None',
                                wrapper_character = "'",
                                double_wrapper_character_when_nested = False,
                                escape_character = "\\",
                                line_terminator = '\r\n',
                                config_set = None):
        r"""Return the CSV representation of ``attributes`` extracted from the
        model instance (record).

        :param attributes: Names of :term:`model attributes <model attribute>` to
          include in the CSV output.
        :type attributes: :class:`list <python:list>` of :class:`str <python:str>`

        :param is_dumping: If ``True``, then allow
          :exc:`UnsupportedSerializationError <sqlathanor.errors.UnsupportedSerializationError>`.
          Defaults to ``False``.
        :type is_dumping: :class:`bool <python:bool>`

        :param delimiter: The delimiter used between columns. Defaults to ``|``.
        :type delimiter: :class:`str <python:str>`

        :param wrap_all_strings: If ``True``, wraps any string data in the
          ``wrapper_character``. If ``None``, only wraps string data if it contains
          the ``delimiter``. Defaults to ``False``.
        :type wrap_all_strings: :class:`bool <python:bool>`

        :param null_text: The text value to use in place of empty values. Only
          applies if ``wrap_empty_values`` is ``True``. Defaults to ``'None'``.
        :type null_text: :class:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is necessary. Defaults to ``'``.
        :type wrapper_character: :class:`str <python:str>`

        :param double_wrapper_character_when_nested: If ``True``, will double the
          ``wrapper_character`` when it is found inside a column value. If ``False``,
          will precede the ``wrapper_character`` by the ``escape_character`` when
          it is found inside a column value. Defaults to ``False``.
        :type double_wrapper_character_when_nested: :class:`bool <python:bool>`

        :param escape_character: The character to use when escaping nested wrapper
          characters. Defaults to ``\``.
        :type escape_character: :class:`str <python:str>`

        :param line_terminator: The character used to mark the end of a line.
          Defaults to ``\r\n``.
        :type line_terminator: :class:`str <python:str>`

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          to use. Defaults to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :returns: Data from the object in CSV format ending in ``line_terminator``.
        :rtype: :class:`str <python:str>`
        """
        if not wrapper_character:
            wrapper_character = '\''

        if not attributes:
            raise SerializableAttributeError("attributes cannot be empty")

        if wrap_all_strings:
            quoting = csv.QUOTE_NONNUMERIC
        else:
            quoting = csv.QUOTE_MINIMAL

        if 'sqlathanor' in csv.list_dialects():
            csv.unregister_dialect('sqlathanor')

        csv.register_dialect('sqlathanor',
                             delimiter = delimiter,
                             doublequote = double_wrapper_character_when_nested,
                             escapechar = escape_character,
                             quotechar = wrapper_character,
                             quoting = quoting,
                             lineterminator = line_terminator)

        data = []
        for item in attributes:
            try:
                value = self._get_serialized_value(format = 'csv',
                                                   attribute = item,
                                                   config_set = config_set)
            except UnsupportedSerializationError as error:
                if is_dumping:
                    value = getattr(self, item)
                else:
                    raise error

            data.append(value)

        for index, item in enumerate(data):
            if item == '' or item is None or item == 'None':
                data[index] = null_text
            elif not checkers.is_string(item) and not checkers.is_numeric(item):
                data[index] = str(item)

        data_dict = dict_()
        for index, column_name in enumerate(attributes):
            data_dict[column_name] = data[index]

        output = StringIO()
        csv_writer = csv.DictWriter(output,
                                    fieldnames = attributes,
                                    dialect = 'sqlathanor')


        csv_writer.writerow(data_dict)

        data_row = output.getvalue()
        output.close()

        csv.unregister_dialect('sqlathanor')

        return data_row

    @classmethod
    def get_csv_header(cls,
                       deserialize = None,
                       serialize = True,
                       delimiter = '|',
                       wrap_all_strings = False,
                       wrapper_character = "'",
                       double_wrapper_character_when_nested = False,
                       escape_character = "\\",
                       line_terminator = '\r\n',
                       config_set = None):
        r"""Retrieve a header string for a CSV representation of the model.

        :param attributes: List of :term:`model attributes <model attribute>` to
          include.
        :type attributes: :class:`list <python:list>` of :class:`str <python:str>`

        :param delimiter: The character(s) to utilize between columns. Defaults to
          a pipe (``|``).
        :type delimiter: :class:`str <python:str>`

        :param wrap_all_strings: If ``True``, wraps any string data in the
          ``wrapper_character``. If ``None``, only wraps string data if it contains
          the ``delimiter``. Defaults to ``False``.
        :type wrap_all_strings: :class:`bool <python:bool>`

        :param null_text: The text value to use in place of empty values. Only
          applies if ``wrap_empty_values`` is ``True``. Defaults to ``'None'``.
        :type null_text: :class:`str <python:str>`

        :param null_text: The text value to use in place of empty values. Only
          applies if ``wrap_empty_values`` is ``True``. Defaults to ``'None'``.
        :type null_text: :class:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is necessary. Defaults to ``'``.
        :type wrapper_character: :class:`str <python:str>`

        :param double_wrapper_character_when_nested: If ``True``, will double the
          ``wrapper_character`` when it is found inside a column value. If ``False``,
          will precede the ``wrapper_character`` by the ``escape_character`` when
          it is found inside a column value. Defaults to ``False``.
        :type double_wrapper_character_when_nested: :class:`bool <python:bool>`

        :param escape_character: The character to use when escaping nested wrapper
          characters. Defaults to ``\``.
        :type escape_character: :class:`str <python:str>`

        :param line_terminator: The character used to mark the end of a line.
          Defaults to ``\r\n``.
        :type line_terminator: :class:`str <python:str>`

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          to use. Defaults to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :returns: A string ending in ``line_terminator`` with the model's CSV column names
          listed, separated by the ``delimiter``.
        :rtype: :class:`str <python:str>`
        """
        # pylint: disable=line-too-long

        column_names = cls.get_csv_column_names(deserialize = deserialize,
                                                serialize = serialize,
                                                config_set = config_set)

        header_string = cls._get_attribute_csv_header(column_names,
                                                      delimiter = delimiter,
                                                      wrap_all_strings = wrap_all_strings,
                                                      wrapper_character = wrapper_character,
                                                      double_wrapper_character_when_nested = double_wrapper_character_when_nested,
                                                      escape_character = escape_character,
                                                      line_terminator = line_terminator)
        return header_string

    def get_csv_data(self,
                     delimiter = '|',
                     wrap_all_strings = False,
                     null_text = 'None',
                     wrapper_character = "'",
                     double_wrapper_character_when_nested = False,
                     escape_character = "\\",
                     line_terminator = '\r\n',
                     config_set = None):
        r"""Return the CSV representation of the model instance (record).

        :param delimiter: The delimiter used between columns. Defaults to ``|``.
        :type delimiter: :class:`str <python:str>`

        :param wrap_all_strings: If ``True``, wraps any string data in the
          ``wrapper_character``. If ``None``, only wraps string data if it contains
          the ``delimiter``. Defaults to ``False``.
        :type wrap_all_strings: :class:`bool <python:bool>`

        :param null_text: The text value to use in place of empty values. Only
          applies if ``wrap_empty_values`` is ``True``. Defaults to ``'None'``.
        :type null_text: :class:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is necessary. Defaults to ``'``.
        :type wrapper_character: :class:`str <python:str>`

        :param double_wrapper_character_when_nested: If ``True``, will double the
          ``wrapper_character`` when it is found inside a column value. If ``False``,
          will precede the ``wrapper_character`` by the ``escape_character`` when
          it is found inside a column value. Defaults to ``False``.
        :type double_wrapper_character_when_nested: :class:`bool <python:bool>`

        :param escape_character: The character to use when escaping nested wrapper
          characters. Defaults to ``\``.
        :type escape_character: :class:`str <python:str>`

        :param line_terminator: The character used to mark the end of a line.
          Defaults to ``\r\n``.
        :type line_terminator: :class:`str <python:str>`

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          to use. Defaults to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :returns: Data from the object in CSV format ending in ``line_terminator``.
        :rtype: :class:`str <python:str>`
        """
        # pylint: disable=line-too-long
        csv_attribute_names = [x
                               for x in self._get_csv_attribute_names(deserialize = None,
                                                                      serialize = True,
                                                                      config_set = config_set)
                               if hasattr(self, x)]

        if not csv_attribute_names:
            raise SerializableAttributeError("no 'csv' serializable attributes found")

        data_row = self._get_attribute_csv_data(csv_attribute_names,
                                                is_dumping = False,
                                                delimiter = delimiter,
                                                wrap_all_strings = wrap_all_strings,
                                                null_text = null_text,
                                                wrapper_character = wrapper_character,
                                                double_wrapper_character_when_nested = double_wrapper_character_when_nested,
                                                escape_character = escape_character,
                                                line_terminator = line_terminator,
                                                config_set = config_set)

        return data_row

    def to_csv(self,
               include_header = False,
               delimiter = '|',
               wrap_all_strings = False,
               null_text = 'None',
               wrapper_character = "'",
               double_wrapper_character_when_nested = False,
               escape_character = "\\",
               line_terminator = '\r\n',
               config_set = None):
        r"""Retrieve a CSV string with the object's data.

        :param include_header: If ``True``, will include a header row with column
          labels. If ``False``, will not include a header row. Defaults to ``True``.
        :type include_header: :class:`bool <python:bool>`

        :param delimiter: The delimiter used between columns. Defaults to ``|``.
        :type delimiter: :class:`str <python:str>`

        :param wrap_all_strings: If ``True``, wraps any string data in the
          ``wrapper_character``. If ``None``, only wraps string data if it contains
          the ``delimiter``. Defaults to ``False``.
        :type wrap_all_strings: :class:`bool <python:bool>`

        :param null_text: The text value to use in place of empty values. Only
          applies if ``wrap_empty_values`` is ``True``. Defaults to ``'None'``.
        :type null_text: :class:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is necessary. Defaults to ``'``.
        :type wrapper_character: :class:`str <python:str>`

        :param double_wrapper_character_when_nested: If ``True``, will double the
          ``wrapper_character`` when it is found inside a column value. If ``False``,
          will precede the ``wrapper_character`` by the ``escape_character`` when
          it is found inside a column value. Defaults to ``False``.
        :type double_wrapper_character_when_nested: :class:`bool <python:bool>`

        :param escape_character: The character to use when escaping nested wrapper
          characters. Defaults to ``\``.
        :type escape_character: :class:`str <python:str>`

        :param line_terminator: The character used to mark the end of a line.
          Defaults to ``\r\n``.
        :type line_terminator: :class:`str <python:str>`

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          to use. Defaults to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :returns: Data from the object in CSV format ending in a newline (``\n``).
        :rtype: :class:`str <python:str>`
        """
        if include_header:
            return self.get_csv_header(delimiter = delimiter,
                                       config_set = config_set) + \
                   self.get_csv_data(delimiter = delimiter,
                                     wrap_all_strings = wrap_all_strings,
                                     null_text = null_text,
                                     wrapper_character = wrapper_character,
                                     double_wrapper_character_when_nested = double_wrapper_character_when_nested,     # pylint: disable=line-too-long
                                     escape_character = escape_character,
                                     line_terminator = line_terminator,
                                     config_set = config_set)


        return self.get_csv_data(delimiter = delimiter,
                                 wrap_all_strings = wrap_all_strings,
                                 null_text = null_text,
                                 wrapper_character = wrapper_character,
                                 double_wrapper_character_when_nested = double_wrapper_character_when_nested,     # pylint: disable=line-too-long
                                 escape_character = escape_character,
                                 line_terminator = line_terminator,
                                 config_set = config_set)

    @classmethod
    def _parse_csv(cls,
                   csv_data,
                   delimiter = '|',
                   wrap_all_strings = False,
                   null_text = 'None',
                   wrapper_character = "'",
                   double_wrapper_character_when_nested = False,
                   escape_character = "\\",
                   line_terminator = '\r\n',
                   config_set = None):
        """Generate a :class:`dict <python:dict>` from a CSV record.

        .. tip::

          Unwrapped empty column values are automatically interpreted as null
          (:obj:`None <python:None>`).

        :param csv_data: The CSV record. Should be a single row and should **not**
          include column headers.
        :type csv_data: :class:`str <python:str>`

        :param delimiter: The delimiter used between columns. Defaults to ``|``.
        :type delimiter: :class:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is applied. Defaults to ``'``.
        :type wrapper_character: :class:`str <python:str>`

        :param null_text: The string used to indicate an empty value if empty
          values are wrapped. Defaults to `None`.
        :type null_text: :class:`str <python:str>`

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          to use. Defaults to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :returns: A :class:`dict <python:dict>` representation of the CSV record.
        :rtype: :class:`dict <python:dict>`

        :raises DeserializationError: if ``csv_data`` is not a valid
          :class:`str <python:str>`
        :raises CSVStructureError: if the columns in ``csv_data`` do not match
          the expected columns returned by
          :func:`get_csv_column_names() <BaseModel.get_csv_column_names>`
        :raises ValueDeserializationError: if a value extracted from the CSV
          failed when executing its :term:`de-serialization function`.

        """
        try:
            csv_data = validators.string(csv_data, allow_empty = False)
        except (ValueError, TypeError):
            raise DeserializationError("csv_data expects a 'str', received '%s'" \
                                       % type(csv_data))

        if not wrapper_character:
            wrapper_character = '\''

        if wrap_all_strings:
            quoting = csv.QUOTE_NONNUMERIC
        else:
            quoting = csv.QUOTE_MINIMAL

        if 'sqlathanor' in csv.list_dialects():
            csv.unregister_dialect('sqlathanor')

        csv.register_dialect('sqlathanor',
                             delimiter = delimiter,
                             doublequote = double_wrapper_character_when_nested,
                             escapechar = escape_character,
                             quotechar = wrapper_character,
                             quoting = quoting,
                             lineterminator = line_terminator)

        csv_column_names = [x
                            for x in cls.get_csv_column_names(deserialize = True,
                                                              serialize = None,
                                                              config_set = config_set)]

        csv_reader = csv.DictReader([csv_data],
                                    fieldnames = csv_column_names,
                                    dialect = 'sqlathanor',
                                    restkey = None,
                                    restval = None)

        rows = [x for x in csv_reader]

        if len(rows) > 1:
            raise CSVStructureError('expected 1 row of data, received %s' % len(csv_reader))
        elif len(rows) == 0:
            data = dict_()
            for column_name in csv_column_names:
                data[column_name] = None
        else:
            data = rows[0]

        if data.get(None, None) is not None:
            raise CSVStructureError('expected %s fields, found %s' % (len(csv_column_names),
                                                                      len(data.keys())))

        deserialized_data = dict_()
        for key in data:
            if data[key] == null_text:
                deserialized_data[key] = None
                continue

            attribute_name = cls._get_attribute_name(key)
            deserialized_value = cls._get_deserialized_value(data[key],
                                                             'csv',
                                                             key,
                                                             config_set = config_set)

            deserialized_data[attribute_name] = deserialized_value

        csv.unregister_dialect('sqlathanor')

        return deserialized_data

    def update_from_csv(self,
                        csv_data,
                        delimiter = '|',
                        wrap_all_strings = False,
                        null_text = 'None',
                        wrapper_character = "'",
                        double_wrapper_character_when_nested = False,
                        escape_character = "\\",
                        line_terminator = '\r\n',
                        config_set = None):
        """Update the model instance from a CSV record.

        .. tip::

          Unwrapped empty column values are automatically interpreted as null
          (:obj:`None <python:None>`).

        :param csv_data: The CSV data. If a Path-like object, will read the first
          record from a file that is assumed to include a header row. If a
          :class:`str <python:str>` and has more than one record (line), will assume
          the first line is a header row.
        :type csv_data: :class:`str <python:str>` / Path-like object

        :param delimiter: The delimiter used between columns. Defaults to ``|``.
        :type delimiter: :class:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is applied. Defaults to ``'``.
        :type wrapper_character: :class:`str <python:str>`

        :param null_text: The string used to indicate an empty value if empty
          values are wrapped. Defaults to `None`.
        :type null_text: :class:`str <python:str>`

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          to use. Defaults to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :raises DeserializationError: if ``csv_data`` is not a valid
          :class:`str <python:str>`
        :raises CSVStructureError: if the columns in ``csv_data`` do not match
          the expected columns returned by
          :func:`get_csv_column_names() <BaseModel.get_csv_column_names>`
        :raises ValueDeserializationError: if a value extracted from the CSV
          failed when executing its :term:`de-serialization function`.

        """
        csv_data = read_csv_data(csv_data,
                                 single_record = True)

        data = self._parse_csv(csv_data,
                               delimiter = delimiter,
                               wrap_all_strings = wrap_all_strings,
                               null_text = null_text,
                               wrapper_character = wrapper_character,
                               double_wrapper_character_when_nested = double_wrapper_character_when_nested,
                               escape_character = escape_character,
                               line_terminator = line_terminator,
                               config_set = config_set)

        for key in data:
            setattr(self, key, data[key])

    @classmethod
    def new_from_csv(cls,
                     csv_data,
                     delimiter = '|',
                     wrap_all_strings = False,
                     null_text = 'None',
                     wrapper_character = "'",
                     double_wrapper_character_when_nested = False,
                     escape_character = "\\",
                     line_terminator = '\r\n',
                     config_set = None):
        """Create a new model instance from a CSV record.

        .. tip::

          Unwrapped empty column values are automatically interpreted as null
          (:obj:`None <python:None>`).

        :param csv_data: The CSV data. If a Path-like object, will read the first
          record from a file that is assumed to include a header row. If a
          :class:`str <python:str>` and has more than one record (line), will assume
          the first line is a header row.
        :type csv_data: :class:`str <python:str>` / Path-like object

        :param delimiter: The delimiter used between columns. Defaults to ``|``.
        :type delimiter: :class:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is applied. Defaults to ``'``.
        :type wrapper_character: :class:`str <python:str>`

        :param null_text: The string used to indicate an empty value if empty
          values are wrapped. Defaults to `None`.
        :type null_text: :class:`str <python:str>`

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          to use. Defaults to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :returns: A :term:`model instance` created from the record.
        :rtype: model instance

        :raises DeserializationError: if ``csv_data`` is not a valid
          :class:`str <python:str>`
        :raises CSVStructureError: if the columns in ``csv_data`` do not match
          the expected columns returned by
          :func:`get_csv_column_names() <BaseModel.get_csv_column_names>`
        :raises ValueDeserializationError: if a value extracted from the CSV
          failed when executing its :term:`de-serialization function`.

        """
        csv_data = read_csv_data(csv_data,
                                 single_record = True)

        data = cls._parse_csv(csv_data,
                              delimiter = delimiter,
                              wrap_all_strings = wrap_all_strings,
                              null_text = null_text,
                              wrapper_character = wrapper_character,
                              double_wrapper_character_when_nested = double_wrapper_character_when_nested,
                              escape_character = escape_character,
                              line_terminator = line_terminator,
                              config_set = config_set)

        return cls(**data)

    def dump_to_csv(self,
                    include_header = False,
                    delimiter = '|',
                    wrap_all_strings = False,
                    null_text = 'None',
                    wrapper_character = "'",
                    double_wrapper_character_when_nested = False,
                    escape_character = "\\",
                    line_terminator = '\r\n',
                    config_set = None):
        r"""Retrieve a :term:`CSV <Comma-Separated Value (CSV)>` representation of
        the object, *with all attributes* serialized regardless of configuration.

        .. caution::

          Nested objects (such as :term:`relationships <relationship>` or
          :term:`association proxies <association proxy>`) will **not**
          be serialized.

        .. note::

          This method ignores any ``display_name`` contributed on the
          :class:`AttributeConfiguration`.

        :param include_header: If ``True``, will include a header row with column
          labels. If ``False``, will not include a header row. Defaults to ``True``.
        :type include_header: :class:`bool <python:bool>`

        :param delimiter: The delimiter used between columns. Defaults to ``|``.
        :type delimiter: :class:`str <python:str>`

        :param wrap_all_strings: If ``True``, wraps any string data in the
          ``wrapper_character``. If ``None``, only wraps string data if it contains
          the ``delimiter``. Defaults to ``False``.
        :type wrap_all_strings: :class:`bool <python:bool>`

        :param null_text: The text value to use in place of empty values. Only
          applies if ``wrap_empty_values`` is ``True``. Defaults to ``'None'``.
        :type null_text: :class:`str <python:str>`

        :param wrapper_character: The string used to wrap string values when
          wrapping is necessary. Defaults to ``'``.
        :type wrapper_character: :class:`str <python:str>`

        :param double_wrapper_character_when_nested: If ``True``, will double the
          ``wrapper_character`` when it is found inside a column value. If ``False``,
          will precede the ``wrapper_character`` by the ``escape_character`` when
          it is found inside a column value. Defaults to ``False``.
        :type double_wrapper_character_when_nested: :class:`bool <python:bool>`

        :param escape_character: The character to use when escaping nested wrapper
          characters. Defaults to ``\``.
        :type escape_character: :class:`str <python:str>`

        :param line_terminator: The character used to mark the end of a line.
          Defaults to ``\r\n``.
        :type line_terminator: :class:`str <python:str>`

        :param config_set: If not :obj:`None <python:None>`, the named configuration set
          to use. Defaults to :obj:`None <python:None>`.
        :type config_set: :class:`str <python:str>` / :obj:`None <python:None>`

        :returns: Data from the object in CSV format ending in a newline (``\n``).
        :rtype: :class:`str <python:str>`
        """
        # pylint: disable=line-too-long

        attributes = [x for x in get_attribute_names(self,
                                                     include_callable = False,
                                                     include_nested = False,
                                                     include_private = True,
                                                     include_special = False,
                                                     include_utilities = False)
                      if x[0:2] != '__']

        if include_header:
            return self._get_attribute_csv_header(attributes,
                                                  delimiter = delimiter) + \
                   self._get_attribute_csv_data(attributes,
                                                is_dumping = True,
                                                delimiter = delimiter,
                                                wrap_all_strings = wrap_all_strings,
                                                null_text = null_text,
                                                wrapper_character = wrapper_character,
                                                double_wrapper_character_when_nested = double_wrapper_character_when_nested,
                                                escape_character = escape_character,
                                                line_terminator = line_terminator,
                                                config_set = config_set)


        return self._get_attribute_csv_data(attributes,
                                            is_dumping = True,
                                            delimiter = delimiter,
                                            wrap_all_strings = wrap_all_strings,
                                            null_text = null_text,
                                            wrapper_character = wrapper_character,
                                            double_wrapper_character_when_nested = double_wrapper_character_when_nested,
                                            escape_character = escape_character,
                                            line_terminator = line_terminator,
                                            config_set = config_set)
