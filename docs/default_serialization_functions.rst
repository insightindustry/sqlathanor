**********************************
Default Serialization Functions
**********************************

.. seealso::

  * :ref:`Configuring Pre-processing and Post-processing <extra_processing>`
  * :term:`Serialization Functions <Serialization Function>`
  * :doc:`Default Deserialization Functions <default_deserialization_functions>`

**SQLAthanor** applies default :term:`serialization functions <serialization function>`
to pre-process your :term:`model attributes <model attribute>` before serializing
them. These default functions primarily exist to convert a
:doc:`SQLAlchemy Data Type <sqlalchemy:core/type_basics>` into a type appropriate
for the format to which you are serializing your :term:`model instance`.

The table below explains how a given :term:`model attribute` data type is serialized
using the default :term:`serialization function` for each data type. If no information
is provided, that means the value is serialized "as-is".

.. list-table::
   :header-rows: 1

   * - Data Types
     - :term:`CSV <Comma-Separated Value (CSV)>`
     - :term:`JSON <JavaScript Object Notation (JSON)>`
     - :term:`YAML <YAML Ain't a Markup Language (YAML)>`
     - :class:`dict <python:dict>`
   * - :obj:`None <python:None>`
     - | Empty string
         ``''``
     -
     -
     -
   * - | :class:`int <python:int>`
         :class:`Integer <sqlalchemy:sqlalchemy.types.Integer>`
         :class:`INTEGER <sqlalchemy:sqlalchemy.types.INTEGER>`
         :class:`INT <sqlalchemy:sqlalchemy.types.INT>`
       | :class:`long <python27:long>`
         :class:`oracle.LONG <sqlalchemy:sqlalchemy.dialects.oracle.LONG>`
       | :class:`mssql.TINYINT <sqlalchemy:sqlalchemy.dialects.mssql.TINYINT>`
         :class:`mysql.TINYINT <sqlalchemy:sqlalchemy.dialects.mysql.TINYINT>`
       | :class:`mysql.MEDIUMINT <sqlalchemy:sqlalchemy.dialects.mysql.MEDIUMINT>`
       | :class:`SmallInteger <sqlalchemy:sqlalchemy.types.SmallInteger>`
         :class:`SMALLINT <sqlalchemy:sqlalchemy.types.SMALLINT>`
       | :class:`BigInteger <sqlalchemy:sqlalchemy.types.BigInteger>`
         :class:`BIGINT <sqlalchemy:sqlalchemy.types.BIGINT>`
       | :class:`mssql.UNIQUEIDENTIFIER <sqlalchemy:sqlalchemy.dialects.mssql.UNIQUEIDENTIFIER>`
     -
     -
     -
     -
   * - :class:`bool <python:bool>`
       :class:`Boolean <sqlalchemy:sqlalchemy.types.Boolean>`
       :class:`BOOLEAN <sqlalchemy:sqlalchemy.types.BOOLEAN>`
     -
     -
     -
     -
   * - | :class:`str <python:str>`
         :class:`String <sqlalchemy:sqlalchemy.types.String>`
       | :class:`Text <sqlalchemy:sqlalchemy.types.Text>`
         :class:`TEXT <sqlalchemy:sqlalchemy.types.TEXT>`
       | :class:`mssql.NTEXT <sqlalchemy:sqlalchemy.dialects.mssql.NTEXT>`
         :class:`mysql.LONGTEXT <sqlalchemy:sqlalchemy.dialects.mysql.LONGTEXT>`
       | :class:`VARCHAR <sqlalchemy:sqlalchemy.types.VARCHAR>`
         :class:`oracle.VARCHAR2 <sqlalchemy:sqlalchemy.dialects.oracle.VARCHAR2>`
       | :class:`NVARCHAR <sqlalchemy:sqlalchemy.types.NVARCHAR>`
         :class:`oracle.NVARCHAR2 <sqlalchemy:sqlalchemy.dialects.oracle.NVARCHAR2>`
       | :class:`CHAR <sqlalchemy:sqlalchemy.types.CHAR>`
         :class:`NCHAR <sqlalchemy:sqlalchemy.types.NCHAR>`
       | :class:`Unicode <sqlalchemy:sqlalchemy.types.Unicode>`
         :class:`UnicodeText <sqlalchemy:sqlalchemy.types.UnicodeText>`
       | :class:`CLOB <sqlalchemy:sqlalchemy.types.CLOB>`
         :class:`oracle.NCLOB <sqlalchemy:sqlalchemy.dialects.oracle.NCLOB>`
     -
     -
     -
     -
   * - | :class:`float <python:float>`
         :class:`Float <sqlalchemy:sqlalchemy.types.Float>`
         :class:`FLOAT <sqlalchemy:sqlalchemy.types.FLOAT>`
       | :class:`decimal.Decimal <python:decimal.Decimal>`
         :class:`DECIMAL <sqlalchemy:sqlalchemy.types.DECIMAL>`
       | :class:`complex <python:complex>`
         :class:`REAL <sqlalchemy:sqlalchemy.types.REAL>`
       | :class:`Numeric <sqlalchemy:sqlalchemy.types.Numeric>`
         :class:`NUMERIC <sqlalchemy:sqlalchemy.types.NUEMRIC>`
       | :class:`mysql.DOUBLE <sqlalchemy:sqlalchemy.dialects.mysql.DOUBLE>`
       | :class:`oracle.DOUBLE_PRECISION <sqlalchemy:sqlalchemy.dialects.oracle.DOUBLE_PRECISION>`
       | :class:`postgresql.DOUBLE_PRECISION <sqlalchemy:sqlalchemy.dialects.postgresql.DOUBLE_PRECISION>`
     -
     -
     -
     -
   * - | :class:`datetime.date <python:datetime.date>`
         :class:`Date <sqlalchemy:sqlalchemy.types.Date>`
         :class:`DATE <sqlalchemy:sqlalchemy.types.DATE>`
       | :class:`datetime.datetime <python:datetime.datetime>`
         :class:`DateTime <sqlalchemy:sqlalchemy.types.DateTime>`
       | :class:`DATETIME <sqlalchemy:sqlalchemy.types.DATETIME>`
         :class:`TIMESTAMP <sqlalchemy:sqlalchemy.types.TIMESTAMP>`
       | :class:`datetime.time <python:datetime.time>`
         :class:`Time <sqlalchemy:sqlalchemy.types.Time>`
         :class:`TIME <sqlalchemy:sqlalchemy.types.TIME>`
       | :class:`mssql.SMALLDATETIME <sqlalchemy:sqlalchemy.dialects.mssql.SMALLDATETIME>`
       | :class:`mssql.DATETIME2 <sqlalchemy:sqlalchemy.dialects.mssql.DATETIME2>`
     - | ISO-8601
         formatted
       | string
     - | ISO-8601
         formatted
       | string
     - | ISO-8601
         formatted
       | string
     -
   * - | :class:`mysql.YEAR <sqlalchemy:sqlalchemy.dialects.mysql.YEAR>`
     -
     -
     -
     -
   * - :class:`bytes <python:bytes>`
     - string
     - string
     - string
     -
   * - | :class:`datetime.timedelta <python:datetime.timedelta>`
         :class:`Interval <sqlalchemy:sqlalchemy.types.Interval>`
       | :class:`INTERVAL <sqlalchemy:sqlalchemy.types.INTERVAL>`
     - | total number
         of seconds
     - | total number
         of seconds
     - | total number
         of seconds
     -
   * - | :class:`BINARY <sqlalchemy:sqlalchemy.types.BINARY>`
         :class:`VARBINARY <sqlalchemy:sqlalchemy.types.VARBINARY>`
       | :class:`LargeBinary <sqlalchemy:sqlalchemy.types.LargeBinary>`
         :class:`BLOB <sqlalchemy:sqlalchemy.types.BLOB>`
       | :class:`mysql.TINYBLOB <sqlalchemy:sqlalchemy.dialects.mysql.TINYBLOB>`
       | :class:`mysql.MEDIUMBLOB <sqlalchemy:sqlalchemy.dialects.mysql.MEDIUMBLOB>`
       | :class:`mysql.LONGBLOB <sqlalchemy:sqlalchemy.dialects.mysql.LONGBLOB>`
       | :class:`PickleType <sqlalchemy:sqlalchemy.types.PickleType>`
       | :class:`postgresql.BYTEA <sqlalchemy:sqlalchemy.dialects.postgresql.BYTEA>`
     -
     - string
     -
     -
   * - | :class:`mssql.MONEY <sqlalchemy:sqlalchemy.dialects.mssql.MONEY>`
         :class:`mssql.SMALLMONEY <sqlalchemy:sqlalchemy.dialects.mssql.SMALLMONEY>`
       | :class:`postgresql.MONEY <sqlalchemy:sqlalchemy.dialects.postgresql.MONEY>`
     -
     -
     -
     -
   * - | :class:`oracle.BINARY_FLOAT <sqlalchemy:sqlalchemy.dialects.oracle.BINARY_FLOAT>`
       | :class:`oracle.BINARY_DOUBLE <sqlalchemy:sqlalchemy.dialects.oracle.BINARY_DOUBLE>`
       | :class:`mssql.IMAGE <sqlalchemy:sqlalchemy.dialects.mssql.IMAGE>`
     -
     -
     -
     -
   * - :class:`oracle.BFILE <sqlalchemy:sqlalchemy.dialects.oracle.BFILE>`
       :class:`oracle.RAW <sqlalchemy:sqlalchemy.dialects.oracle.RAW>`
     -
     - string
     - string
     -
   * - | :class:`Enum <sqlalchemy:sqlalchemy.types.Enum>`
         :class:`ENUM <sqlalchemy:sqlalchemy.types.ENUM>`
         :class:`SET <sqlalchemy:sqlalchemy.types.SET>`
       | :class:`postgresql.UUID <sqlalchemy:sqlalchemy.dialects.postgresql.UUID>`
       | :class:`mssql.BIT <sqlalchemy:sqlalchemy.dialects.mssql.BIT>`
         :class:`postgresql.BIT <sqlalchemy:sqlalchemy.dialects.postgresql.BIT>`
       | :class:`postgresql.REGCLASS <sqlalchemy:sqlalchemy.dialects.postgresql.REGCLASS>`
       | :class:`postgresql.OID <sqlalchemy:sqlalchemy.dialects.postgresql.OID>`
       | :class:`postgresql.CIDR <sqlalchemy:sqlalchemy.dialects.postgresql.CIDR>`
       | :class:`postgresql.INET <sqlalchemy:sqlalchemy.dialects.postgresql.INET>`
       | :class:`postgresql.MACADDR <sqlalchemy:sqlalchemy.dialects.postgresql.MACADDR>`
       | :class:`mssql.XML <sqlalchemy:sqlalchemy.dialects.mssql.XML>`
       | :class:`postgresql.TSVECTOR <sqlalchemy:sqlalchemy.dialects.postgresql.TSVECTOR>`
     -
     - string
     - string
     - string
   * - | :class:`dict <python:dict>`
         :class:`list <python:list>`
       | :class:`JSON <sqlalchemy:sqlalchemy.types.JSON>`
         :class:`postgresql.JSONB <sqlalchemy:sqlalchemy.dialects.postgresql.JSONB>`
       | :class:`postgresql.HSTORE <sqlalchemy:sqlalchemy.dialects.postgresql.HSTORE>`
       | :class:`ARRAY <sqlalchemy:sqlalchemy.types.ARRAY>`
     - :exc:`UnsupportedSerializationError <sqlathanor.errors.UnsupportedSerializationError>`
     -
     -
     -
   * - | :class:`set <python:set>`
         :class:`tuple <python:tuple>`
     - :exc:`UnsupportedSerializationError <sqlathanor.errors.UnsupportedSerializationError>`
     - list
     - list
     -
   * - | :class:`mssql.SQL_VARIANT <sqlalchemy:sqlalchemy.dialects.mssql.SQL_VARIANT>`
     - :exc:`UnsupportedSerializationError <sqlathanor.errors.UnsupportedSerializationError>`
     - :exc:`UnsupportedSerializationError <sqlathanor.errors.UnsupportedSerializationError>`
     - :exc:`UnsupportedSerializationError <sqlathanor.errors.UnsupportedSerializationError>`
     - :exc:`UnsupportedSerializationError <sqlathanor.errors.UnsupportedSerializationError>`
