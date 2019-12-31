# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member documentation is automatically incorporated
# there as needed.

import datetime
import io

from validator_collection import validators, checkers

from sqlathanor._compat import json
from sqlathanor.utilities import format_to_tuple, get_class_type_key, \
    raise_UnsupportedSerializationError, raise_UnsupportedDeserializationError
from sqlathanor.errors import UnsupportedValueTypeError

from sqlalchemy.types import Boolean, Date, DateTime, Float, Integer, Text, Time, Interval

DEFAULT_PYTHON_SQL_TYPE_MAPPING = {
    'bool': Boolean,
    'str': Text,
    'int': Integer,
    'float': Float,
    'datetime': DateTime,
    'date': Date,
    'time': Time,
    'timedelta': Interval
}

def get_default_deserializer(class_attribute = None,
                             format = None):
    """Retrieve the default ``on_deserialize`` function that applies to the data
    type of ``class_attribute``.

    :param class_attribute: The class attribute whose default deserializer will be
      returned. Defaults to :obj:`None <python:None>`.

    :param format: The format to which the value should be serialized. Accepts
      either: ``csv``, ``json``, ``yaml``, or ``dict``. Defaults to :obj:`None <python:None>`.
    :type format: :class:`str <python:str>`

    :returns: The default :term:`deserializer function` to apply or :obj:`None <python:None>`
    :rtype: callable / :obj:`None <python:None>`

    :raises InvalidFormatError: if ``format`` is not a valid format type
    """
    format_to_tuple(format)
    format = format.lower()

    class_type_key = get_class_type_key(class_attribute, None)

    deserializer_dict = DEFAULT_DESERIALIZERS.get(class_type_key, None)

    if deserializer_dict is None:
        return None

    return deserializer_dict.get(format, None)

def from_dict(value):
    return validators.dict(value, allow_empty = True, json_serializer = json)

def from_string(value):
    return validators.string(value, allow_empty = True, coerce_value = True)

def from_integer(value):
    return validators.integer(value, allow_empty = True)

def from_numeric(value):
    return validators.numeric(value, allow_empty = True)

def from_float(value):
    return validators.float(value, allow_empty = True)

def from_fraction(value):
    return validators.fraction(value, allow_empty = True)

def from_decimal(value):
    return validators.decimal(value, allow_empty = True)

def from_uuid(value):
    return validators.uuid(value, allow_empty = True)

def from_date(value):
    return validators.date(value, allow_empty = True)

def from_datetime(value):
    try:
        value = validators.timedelta(value, allow_empty = True)
        return value
    except (ValueError, TypeError):
        pass

    return validators.datetime(value, allow_empty = True)

def from_time(value):
    return validators.time(value, allow_empty = True)

def from_bytes(value):
    if not isinstance(value, (bytes, io.BytesIO, io.StringIO)):
        value = validators.string(value, allow_empty = True)
    else:
        return value

    if value is None:
        return value

    return bytes(value)

def from_iterable(value):
    return validators.iterable(value, allow_empty = True)

def from_timedelta(value):
    value = validators.timedelta(value, allow_empty = True)

    return value

def from_mac_address(value):
    return validators.mac_address(value, allow_empty = True)

def from_bit(value):
    if value is None:
        return None

    return bool(value)

def from_json(value):
    value = validators.dict(value, allow_empty = True, json_serializer = json)
    if value is None:
        return None

    return json.dumps(value)


def get_type_mapping(value,
                     type_mapping = None,
                     skip_nested = True,
                     default_to_str = False):
    """Retrieve the SQL type mapping for ``value``.

    :param value: The value whose SQL type will be returned.

    :param type_mapping: Determines how the value type of ``value`` map to
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
         * - ``timedelta``
           - :class:`Interval <sqlalchemy:sqlalchemy.types.Interval>`

    :type type_mapping: :class:`dict <python:dict>` with type names as keys and
      column data types as values / :obj:`None <python:None>`

    :param skip_nested: If ``True`` then if ``value`` is a nested item (e.g.
      iterable, :class:`dict <python:dict>` objects, etc.) it will return
      :obj:`None <python:None>`. If ``False``, will treat nested items as
      :class:`str <python:str>`. Defaults to ``True``.
    :type skip_nested: :class:`bool <python:bool>`

    :param default_to_str: If ``True``, will automatically set a ``value`` whose
      value type cannot be determined to ``str``
      (:class:`Text <sqlalchemy:sqlalchemy.types.Text>`). If ``False``, will
      use the value type's ``__name__`` attribute and attempt to find a mapping.
      Defaults to ``False``.
    :type default_to_str: :class:`bool <python:bool>`

    :returns: The :doc:`SQLAlchemy Data Type <sqlalchemy:core/types>` for ``value``, or
      :obj:`None <python:None>` if the value should be skipped
    :rtype: :doc:`SQLAlchemy Data Type <sqlalchemy:core/types>` / :obj:`None`

    :raises UnsupportedValueTypeError: when ``value`` does not have corresponding
      :doc:`SQLAlchemy Data Type <sqlalchemy:core/types>`

    """
    if not type_mapping:
        type_mapping = DEFAULT_PYTHON_SQL_TYPE_MAPPING

    for key in DEFAULT_PYTHON_SQL_TYPE_MAPPING:
        if key not in type_mapping:
            type_mapping[key] = DEFAULT_PYTHON_SQL_TYPE_MAPPING[key]

    if checkers.is_callable(value):
        raise UnsupportedValueTypeError('value ("%s") cannot be callable' % value)
    elif checkers.is_iterable(value) and skip_nested:
        return None
    elif checkers.is_iterable(value) and default_to_str:
        target_type = 'str'
    elif value is None and default_to_str:
        target_type = 'str'
    elif isinstance(value, bool):
        target_type = 'bool'
    elif checkers.is_numeric(value):
        if checkers.is_integer(value):
            target_type = 'int'
        else:
            target_type = 'float'
    elif checkers.is_time(value) and not checkers.is_datetime(value):
        target_type = 'time'
    elif checkers.is_datetime(value):
        target_type = 'datetime'
    elif checkers.is_date(value):
        target_type = 'date'
    elif default_to_str:
        target_type = 'str'
    else:
        target_type = type(value).__name__

    column_type = type_mapping.get(target_type, None)
    if not column_type:
        raise UnsupportedValueTypeError(
            'value ("%s") is not a supported type (%s)' % (value, target_type)
        )

    return column_type




DEFAULT_DESERIALIZERS = {
    'NONE': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'str': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'int': {
        'csv': from_integer,
        'json': from_integer,
        'yaml': from_integer,
        'dict': from_integer
    },
    'Decimal': {
        'csv': from_decimal,
        'json': from_decimal,
        'yaml': from_decimal,
        'dict': from_decimal
    },
    'float': {
        'csv': from_float,
        'json': from_float,
        'yaml': from_float,
        'dict': from_float
    },
    'long': {
        'csv': from_numeric,
        'json': from_numeric,
        'yaml': from_numeric,
        'dict': from_numeric
    },
    'complex': {
        'csv': from_numeric,
        'json': from_numeric,
        'yaml': from_numeric,
        'dict': from_numeric
    },
    'real': {
        'csv': from_numeric,
        'json': from_numeric,
        'yaml': from_numeric,
        'dict': from_numeric
    },
    'bool': {
        'csv': bool,
        'json': bool,
        'yaml': bool,
        'dict': bool
    },
    'byte': {
        'csv': from_bytes,
        'json': from_bytes,
        'yaml': from_bytes,
        'dict': from_bytes
    },
    'bytes': {
        'csv': from_bytes,
        'json': from_bytes,
        'yaml': from_bytes,
        'dict': from_bytes
    },
    'unicode': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'dict': {
        'csv': raise_UnsupportedDeserializationError,
        'json': from_dict,
        'yaml': from_dict,
        'dict': from_dict
    },
    'list': {
        'csv': raise_UnsupportedDeserializationError,
        'json': from_iterable,
        'yaml': from_iterable,
        'dict': from_iterable
    },
    'set': {
        'csv': raise_UnsupportedDeserializationError,
        'json': from_iterable,
        'yaml': from_iterable,
        'dict': from_iterable
    },
    'tuple': {
        'csv': raise_UnsupportedDeserializationError,
        'json': from_iterable,
        'yaml': from_iterable,
        'dict': from_iterable
    },
    'String': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'Text': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'TEXT': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'NTEXT': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'IMAGE': {
        'csv': from_bytes,
        'json': from_bytes,
        'yaml': from_bytes,
        'dict': from_bytes
    },
    'ROWVERSION': {
        'csv': from_numeric,
        'json': from_numeric,
        'yaml': from_numeric,
        'dict': from_numeric
    },
    'CLOB': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'NCLOB': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'VARCHAR': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'NVARCHAR': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'VARCHAR2': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'NVARCHAR2': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'UNITEXT': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'UNICHAR': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'UNIVARCHAR': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'LONGTEXT': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'CHAR': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'NCHAR': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'Unicode': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'UnicodeText': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'Integer': {
        'csv': from_integer,
        'json': from_integer,
        'yaml': from_integer,
        'dict': from_integer
    },
    'INTEGER': {
        'csv': from_integer,
        'json': from_integer,
        'yaml': from_integer,
        'dict': from_integer
    },
    'INT': {
        'csv': from_integer,
        'json': from_integer,
        'yaml': from_integer,
        'dict': from_integer
    },
    'TINYINT': {
        'csv': from_integer,
        'json': from_integer,
        'yaml': from_integer,
        'dict': from_integer
    },
    'MEDIUMINT': {
        'csv': from_integer,
        'json': from_integer,
        'yaml': from_integer,
        'dict': from_integer
    },
    'SmallInteger': {
        'csv': from_integer,
        'json': from_integer,
        'yaml': from_integer,
        'dict': from_integer
    },
    'SMALLINT': {
        'csv': from_integer,
        'json': from_integer,
        'yaml': from_integer,
        'dict': from_integer
    },
    'BigInteger': {
        'csv': from_integer,
        'json': from_integer,
        'yaml': from_integer,
        'dict': from_integer
    },
    'BIGINT': {
        'csv': from_integer,
        'json': from_integer,
        'yaml': from_integer,
        'dict': from_integer
    },
    'Numeric': {
        'csv': from_numeric,
        'json': from_numeric,
        'yaml': from_numeric,
        'dict': from_numeric
    },
    'NUMERIC': {
        'csv': from_numeric,
        'json': from_numeric,
        'yaml': from_numeric,
        'dict': from_numeric
    },
    'DECIMAL': {
        'csv': from_decimal,
        'json': from_decimal,
        'yaml': from_decimal,
        'dict': from_decimal
    },
    'Float': {
        'csv': from_float,
        'json': from_float,
        'yaml': from_float,
        'dict': from_float
    },
    'FLOAT': {
        'csv': from_float,
        'json': from_float,
        'yaml': from_float,
        'dict': from_float
    },
    'REAL': {
        'csv': from_numeric,
        'json': from_numeric,
        'yaml': from_numeric,
        'dict': from_numeric
    },
    'DOUBLE': {
        'csv': from_numeric,
        'json': from_numeric,
        'yaml': from_numeric,
        'dict': from_numeric
    },
    'DOUBLE_PRECISION': {
        'csv': from_numeric,
        'json': from_numeric,
        'yaml': from_numeric,
        'dict': from_numeric
    },
    'MONEY': {
        'csv': from_numeric,
        'json': from_numeric,
        'yaml': from_numeric,
        'dict': from_numeric
    },
    'SMALLMONEY': {
        'csv': from_numeric,
        'json': from_numeric,
        'yaml': from_numeric,
        'dict': from_numeric
    },
    'DateTime': {
        'csv': from_datetime,
        'json': from_datetime,
        'yaml': from_datetime,
        'dict': from_datetime
    },
    'TIMESTAMP': {
        'csv': from_datetime,
        'json': from_datetime,
        'yaml': from_datetime,
        'dict': from_datetime
    },
    'DATETIME': {
        'csv': from_datetime,
        'json': from_datetime,
        'yaml': from_datetime,
        'dict': from_datetime
    },
    'DATETIME2': {
        'csv': from_datetime,
        'json': from_datetime,
        'yaml': from_datetime,
        'dict': from_datetime
    },
    'SMALLDATETIME': {
        'csv': from_datetime,
        'json': from_datetime,
        'yaml': from_datetime,
        'dict': from_datetime
    },
    'Date': {
        'csv': from_date,
        'json': from_date,
        'yaml': from_date,
        'dict': from_date
    },
    'DATE': {
        'csv': from_date,
        'json': from_date,
        'yaml': from_date,
        'dict': from_date
    },
    'Time': {
        'csv': from_time,
        'json': from_time,
        'yaml': from_time,
        'dict': from_time
    },
    'TIME': {
        'csv': from_time,
        'json': from_time,
        'yaml': from_time,
        'dict': from_time
    },
    'YEAR': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'Binary': {
        'csv': from_bytes,
        'json': from_bytes,
        'yaml': from_bytes,
        'dict': from_bytes
    },
    'BINARY': {
        'csv': from_bytes,
        'json': from_bytes,
        'yaml': from_bytes,
        'dict': from_bytes
    },
    'VARBINARY': {
        'csv': from_bytes,
        'json': from_bytes,
        'yaml': from_bytes,
        'dict': from_bytes
    },
    'BINARY_DOUBLE': {
        'csv': from_numeric,
        'json': from_numeric,
        'yaml': from_numeric,
        'dict': from_numeric
    },
    'BINARY_FLOAT': {
        'csv': from_float,
        'json': from_float,
        'yaml': from_float,
        'dict': from_float
    },
    'LONG': {
        'csv': from_numeric,
        'json': from_numeric,
        'yaml': from_numeric,
        'dict': from_numeric
    },
    'BLOB': {
        'csv': from_bytes,
        'json': from_bytes,
        'yaml': from_bytes,
        'dict': from_bytes
    },
    'TINYBLOB': {
        'csv': from_bytes,
        'json': from_bytes,
        'yaml': from_bytes,
        'dict': from_bytes
    },
    'LONGBLOB': {
        'csv': from_bytes,
        'json': from_bytes,
        'yaml': from_bytes,
        'dict': from_bytes
    },
    'MEDIUMBLOB': {
        'csv': from_bytes,
        'json': from_bytes,
        'yaml': from_bytes,
        'dict': from_bytes
    },
    'BFILE': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'RAW': {
        'csv': from_bytes,
        'json': from_bytes,
        'yaml': from_bytes,
        'dict': from_bytes
    },
    'LargeBinary': {
        'csv': from_bytes,
        'json': from_bytes,
        'yaml': from_bytes,
        'dict': from_bytes
    },
    'BYTEA': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'Enum': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'ENUM': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'SET': {
        'csv': from_string,
        'json': from_string,
        'yaml': from_string,
        'dict': from_string
    },
    'PickleType': {
        'csv': from_bytes,
        'json': from_bytes,
        'yaml': from_bytes,
        'dict': from_bytes
    },
    'Boolean': {
        'csv': bool,
        'json': bool,
        'yaml': bool,
        'dict': bool
    },
    'BOOLEAN': {
        'csv': bool,
        'json': bool,
        'yaml': bool,
        'dict': bool
    },
    'Interval': {
        'csv': from_timedelta,
        'json': from_timedelta,
        'yaml': from_timedelta,
        'dict': from_timedelta
    },
    'json': {
        'csv': raise_UnsupportedSerializationError,
        'json': from_json,
        'yaml': from_json,
        'dict': from_json
    },
    'JSON': {
        'csv': raise_UnsupportedSerializationError,
        'json': from_json,
        'yaml': from_json,
        'dict': from_json
    },
    'jsonb': {
        'csv': raise_UnsupportedSerializationError,
        'json': from_json,
        'yaml': from_json,
        'dict': from_json
    },
    'JSONB': {
        'csv': raise_UnsupportedSerializationError,
        'json': from_json,
        'yaml': from_json,
        'dict': from_json
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
        'json': None,
        'yaml': None,
        'dict': None
    },
    'CIDR': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'MACADDR': {
        'csv': from_mac_address,
        'json': from_mac_address,
        'yaml': from_mac_address,
        'dict': from_mac_address
    },
    'OID': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'REGCLASS': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'BIT': {
        'csv': from_bit,
        'json': from_bit,
        'yaml': from_bit,
        'dict': from_bit
    },
    'UUID': {
        'csv': from_uuid,
        'json': from_uuid,
        'yaml': from_uuid,
        'dict': from_uuid
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
        'json': None,
        'yaml': None,
        'dict': None
    },
    'XML': {
        'csv': None,
        'json': None,
        'yaml': None,
        'dict': None
    },
    'SQL_VARIANT': {
        'csv': raise_UnsupportedDeserializationError,
        'json': raise_UnsupportedDeserializationError,
        'yaml': raise_UnsupportedDeserializationError,
        'dict': raise_UnsupportedDeserializationError
    }
}
