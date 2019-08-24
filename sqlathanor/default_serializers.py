# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member documentation is automatically incorporated
# there as needed.

from validator_collection import validators

from sqlathanor.utilities import format_to_tuple, get_class_type_key, \
    raise_UnsupportedSerializationError
from sqlathanor.errors import ValueSerializationError

def get_default_serializer(class_attribute = None,
                           format = None,
                           value = None):
    """Retrieve the default ``on_serialize`` function that applies to the data
    type of ``class_attribute``.

    .. note::

      If ``class_attribute`` does not have a SQLAlchemy data type, then
      determines the data type based on ``value``.

    :param class_attribute: The class attribute whose default serializer will be
      returned. Defaults to :obj:`None <python:None>`.

    :param format: The format to which the value should be serialized. Accepts
      either: ``csv``, ``json``, ``yaml``, or ``dict``. Defaults to :obj:`None <python:None>`.
    :type format: :class:`str <python:str>`

    :param value: The class attribute's value.

    :returns: The default :term:`serializer function` to apply or :obj:`None <python:None>`
    :rtype: callable / :obj:`None <python:None>`

    :raises InvalidFormatError: if ``format`` is not a valid format type
    """
    format_to_tuple(format)
    format = format.lower()

    class_type_key = get_class_type_key(class_attribute, value)

    serializer_dict = DEFAULT_SERIALIZERS.get(class_type_key, None)

    if serializer_dict is None:
        return None

    return serializer_dict.get(format, None)

def empty_string(value):
    """Convert a :obj:`None <python:None>` ``value`` to an empty string."""
    # pylint: disable=unused-argument
    return ''

def to_str(value):
    value = validators.string(value,
                              allow_empty = True,
                              coerce_value = True)

    return value

def to_isoformat(value):
    if value is None:
        return None

    try:
        value = value.isoformat()
    except AttributeError as error:
        try:
            value = to_total_seconds(value)
        except AttributeError:
            raise ValueSerializationError(error.args[0])

    return value

def to_total_seconds(value):
    if value is None:
        return None

    try:
        value = value.total_seconds()
    except AttributeError as error:
        raise ValueSerializationError(error.args[0])

    return value

def to_list(value):
    if value is None:
        return None

    return list(value)

DEFAULT_SERIALIZERS = {
    'NONE': {
        'csv': empty_string,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'str': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'int': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'Decimal': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'float': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'long': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'complex': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'real': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'bool': {
        'csv': to_str,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'byte': {
        'csv': to_str,
        'json': to_str,
        'yaml': to_str,
        'dict': None
    },
    'bytes': {
        'csv': to_str,
        'json': to_str,
        'yaml': to_str,
        'dict': None
    },
    'unicode': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'dict': {
        'csv': raise_UnsupportedSerializationError,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'list': {
        'csv': raise_UnsupportedSerializationError,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'set': {
        'csv': raise_UnsupportedSerializationError,
        'json': to_list,
        'yaml': to_list,
        'dict': None
    },
    'tuple': {
        'csv': raise_UnsupportedSerializationError,
        'json': to_list,
        'yaml': to_list,
        'dict': None
    },
    'timedelta': {
        'csv': to_total_seconds,
        'json': to_total_seconds,
        'yaml': to_total_seconds,
        'dict': None
    },
    'String': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'Text': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'TEXT': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'NTEXT': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'IMAGE': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'ROWVERSION': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'CLOB': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'NCLOB': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'VARCHAR': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'NVARCHAR': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'VARCHAR2': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'NVARCHAR2': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'UNITEXT': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'UNICHAR': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'UNIVARCHAR': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'LONGTEXT': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'CHAR': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'NCHAR': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'Unicode': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'UnicodeText': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'Integer': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'INTEGER': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'INT': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'TINYINT': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'MEDIUMINT': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'SmallInteger': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'SMALLINT': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'BigInteger': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'BIGINT': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'Numeric': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'NUMERIC': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'DECIMAL': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'Float': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'REAL': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'FLOAT': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'DOUBLE': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'DOUBLE_PRECISION': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'MONEY': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'SMALLMONEY': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'DateTime': {
        'csv': to_isoformat,
        'json': to_isoformat,
        'yaml': to_isoformat,
        'dict': None
    },
    'TIMESTAMP': {
        'csv': to_isoformat,
        'json': to_isoformat,
        'yaml': to_isoformat,
        'dict': None
    },
    'DATETIME': {
        'csv': to_isoformat,
        'json': to_isoformat,
        'yaml': to_isoformat,
        'dict': None
    },
    'datetime': {
        'csv': to_isoformat,
        'json': to_isoformat,
        'yaml': to_isoformat,
        'dict': None
    },
    'DATETIME2': {
        'csv': to_isoformat,
        'json': to_isoformat,
        'yaml': to_isoformat,
        'dict': None
    },
    'SMALLDATETIME': {
        'csv': to_isoformat,
        'json': to_isoformat,
        'yaml': to_isoformat,
        'dict': None
    },
    'Date': {
        'csv': to_isoformat,
        'json': to_isoformat,
        'yaml': to_isoformat,
        'dict': None
    },
    'date': {
        'csv': to_isoformat,
        'json': to_isoformat,
        'yaml': to_isoformat,
        'dict': None
    },
    'DATE': {
        'csv': to_isoformat,
        'json': to_isoformat,
        'yaml': to_isoformat,
        'dict': None
    },
    'Time': {
        'csv': to_isoformat,
        'json': to_isoformat,
        'yaml': to_isoformat,
        'dict': None
    },
    'TIME': {
        'csv': to_isoformat,
        'json': to_isoformat,
        'yaml': to_isoformat,
        'dict': None
    },
    'YEAR': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'Binary': {
        'csv': None,
        'json': to_str,
        'yaml': None,
        'dict': None
    },
    'BINARY': {
        'csv': None,
        'json': to_str,
        'yaml': None,
        'dict': None
    },
    'VARBINARY': {
        'csv': None,
        'json': to_str,
        'yaml': None,
        'dict': None
    },
    'BINARY_DOUBLE': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'BINARY_FLOAT': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'LONG': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'BLOB': {
        'csv': None,
        'json': to_str,
        'yaml': None,
        'dict': None
    },
    'TINYBLOB': {
        'csv': None,
        'json': to_str,
        'yaml': None,
        'dict': None
    },
    'LONGBLOB': {
        'csv': None,
        'json': to_str,
        'yaml': None,
        'dict': None
    },
    'MEDIUMBLOB': {
        'csv': None,
        'json': to_str,
        'yaml': None,
        'dict': None
    },
    'BFILE': {
        'csv': None,
        'json': to_str,
        'yaml': to_str,
        'dict': None
    },
    'RAW': {
        'csv': None,
        'json': to_str,
        'yaml': to_str,
        'dict': None
    },
    'LargeBinary': {
        'csv': None,
        'json': to_str,
        'yaml': None,
        'dict': None
    },
    'BYTEA': {
        'csv': None,
        'json': to_str,
        'yaml': None,
        'dict': None
    },
    'Enum': {
        'csv': None,
        'json': to_str,
        'yaml': to_str,
        'dict': to_str
    },
    'ENUM': {
        'csv': None,
        'json': to_str,
        'yaml': to_str,
        'dict': to_str
    },
    'SET': {
        'csv': None,
        'json': to_str,
        'yaml': to_str,
        'dict': to_str
    },
    'PickleType': {
        'csv': None,
        'json': to_str,
        'yaml': None,
        'dict': None
    },
    'Boolean': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'BOOLEAN': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'Interval': {
        'csv': to_total_seconds,
        'json': to_total_seconds,
        'yaml': to_total_seconds,
        'dict': None
    },
    'json': {
        'csv': raise_UnsupportedSerializationError,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'JSON': {
        'csv': raise_UnsupportedSerializationError,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'jsonb': {
        'csv': raise_UnsupportedSerializationError,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'JSONB': {
        'csv': raise_UnsupportedSerializationError,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'array': {
        'csv': raise_UnsupportedSerializationError,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'ARRAY': {
        'csv': raise_UnsupportedSerializationError,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'hstore': {
        'csv': raise_UnsupportedSerializationError,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'HSTORE': {
        'csv': raise_UnsupportedSerializationError,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'INET': {
        'csv': None,
        'json': to_str,
        'yaml': to_str,
        'dict': to_str
    },
    'CIDR': {
        'csv': None,
        'json': to_str,
        'yaml': to_str,
        'dict': to_str
    },
    'MACADDR': {
        'csv': None,
        'json': to_str,
        'yaml': to_str,
        'dict': to_str
    },
    'OID': {
        'csv': None,
        'json': to_str,
        'yaml': to_str,
        'dict': to_str
    },
    'REGCLASS': {
        'csv': None,
        'json': to_str,
        'yaml': to_str,
        'dict': to_str
    },
    'BIT': {
        'csv': None,
        'json': to_str,
        'yaml': to_str,
        'dict': to_str
    },
    'UUID': {
        'csv': None,
        'json': to_str,
        'yaml': to_str,
        'dict': to_str
    },
    'UNIQUEIDENTIFIER': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'ROWID': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'TSVECTOR': {
        'csv': None,
        'json': to_str,
        'yaml': to_str,
        'dict': to_str
    },
    'XML': {
        'csv': None,
        'json': to_str,
        'yaml': to_str,
        'dict': to_str
    },
    'SQL_VARIANT': {
        'csv': raise_UnsupportedSerializationError,
        'json': raise_UnsupportedSerializationError,
        'yaml': raise_UnsupportedSerializationError,
        'dict': raise_UnsupportedSerializationError
    }
}
