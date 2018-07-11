************************************
Default De-serialization Functions
************************************

.. seealso::

  * :ref:`Configuring Pre-processing and Post-processing <extra_processing>`
  * :term:`De-serialization Functions <De-serialization Function>`
  * :doc:`Default Serialization Functions <default_serialization_functions>`

**SQLAthanor** applies default :term:`de-serialization functions <de-serialization function>`
to process your :term:`model attributes <model attribute>` before assigning
their de-serialized value to your :term:`model attribute`. These default functions
primarily exist to validate that a value assigned to a given attribute is valid
given that attribute's :doc:`SQLAlchemy Data Type <sqlalchemy:core/type_basics>`.

The table below shows the data type that is assigned to a :term:`model attribute`
by the default :term:`de-serialization function` based on the attribute's data type.

.. note::

  If the default de-serializer function cannot coerce the value extracted from
  your serialized data to either :obj:`None <python:None>` or the expected data
  type, **SQLAthanor** will raise
  :exc:`ValueDeserializationError <sqlathanor.errors.ValueDeserializationError>`.

.. list-table::
   :header-rows: 1

   * - Data Types
     - :term:`CSV <Comma-Separated Value (CSV)>`
     - :term:`JSON <JavaScript Object Notation (JSON)>`
     - :term:`YAML <YAML Ain't a Markup Language (YAML)>`
     - :class:`dict <python:dict>`
   * - :obj:`None <python:None>`
     -
     -
     -
     -
   * - | :class:`int <python:int>`
         :class:`Integer <sqlalchemy:sqlalchemy.types.Integer>`
         :class:`INTEGER <sqlalchemy:sqlalchemy.types.INTEGER>`
         :class:`INT <sqlalchemy:sqlalchemy.types.INT>`
       | :class:`mssql.TINYINT <sqlalchemy:sqlalchemy.dialects.mssql.TINYINT>`
         :class:`mysql.TINYINT <sqlalchemy:sqlalchemy.dialects.mysql.TINYINT>`
       | :class:`mysql.MEDIUMINT <sqlalchemy:sqlalchemy.dialects.mysql.MEDIUMINT>`
       | :class:`SmallInteger <sqlalchemy:sqlalchemy.types.SmallInteger>`
         :class:`SMALLINT <sqlalchemy:sqlalchemy.types.SMALLINT>`
       | :class:`BigInteger <sqlalchemy:sqlalchemy.types.BigInteger>`
         :class:`BIGINT <sqlalchemy:sqlalchemy.types.BIGINT>`
     - :class:`int <python:int>`
     - :class:`int <python:int>`
     - :class:`int <python:int>`
     - :class:`int <python:int>`
   * - :class:`bool <python:bool>`
       :class:`Boolean <sqlalchemy:sqlalchemy.types.Boolean>`
       :class:`BOOLEAN <sqlalchemy:sqlalchemy.types.BOOLEAN>`
     - :class:`bool <python:bool>`
     - :class:`bool <python:bool>`
     - :class:`bool <python:bool>`
     - :class:`bool <python:bool>`
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
       | :class:`Enum <sqlalchemy:sqlalchemy.types.Enum>`
         :class:`ENUM <sqlalchemy:sqlalchemy.types.ENUM>`
         :class:`SET <sqlalchemy:sqlalchemy.types.SET>`
     - :class:`str <python:str>`
     - :class:`str <python:str>`
     - :class:`str <python:str>`
     - :class:`str <python:str>`
   * - | :class:`float <python:float>`
         :class:`Float <sqlalchemy:sqlalchemy.types.Float>`
         :class:`FLOAT <sqlalchemy:sqlalchemy.types.FLOAT>`
       | :class:`oracle.BINARY_FLOAT <sqlalchemy:sqlalchemy.dialects.oracle.BINARY_FLOAT>`
     - :class:`float <python:float>`
     - :class:`float <python:float>`
     - :class:`float <python:float>`
     - :class:`float <python:float>`
   * - | :class:`long <python27:long>`
         :class:`oracle.LONG <sqlalchemy:sqlalchemy.dialects.oracle.LONG>`
       | :class:`complex <python:complex>`
         :class:`REAL <sqlalchemy:sqlalchemy.types.REAL>`
       | :class:`Numeric <sqlalchemy:sqlalchemy.types.Numeric>`
         :class:`NUMERIC <sqlalchemy:sqlalchemy.types.NUEMRIC>`
       | :class:`mysql.DOUBLE <sqlalchemy:sqlalchemy.dialects.mysql.DOUBLE>`
       | :class:`oracle.DOUBLE_PRECISION <sqlalchemy:sqlalchemy.dialects.oracle.DOUBLE_PRECISION>`
       | :class:`postgresql.DOUBLE_PRECISION <sqlalchemy:sqlalchemy.dialects.postgresql.DOUBLE_PRECISION>`
       | :class:`mssql.ROWVERSION <sqlalchemy:dialects.mssql.ROWVERSION>`
       | :class:`oracle.BINARY_DOUBLE <sqlalchemy:sqlalchemy.dialects.oracle.BINARY_DOUBLE>`
       | :class:`mssql.MONEY <sqlalchemy:sqlalchemy.dialects.mssql.MONEY>`
         :class:`mssql.SMALLMONEY <sqlalchemy:sqlalchemy.dialects.mssql.SMALLMONEY>`
       | :class:`postgresql.MONEY <sqlalchemy:sqlalchemy.dialects.postgresql.MONEY>`
     - :func:`validator_collection.validators.numeric() <validator_collection:validator_collection.validators.numeric>`
     - :func:`validator_collection.validators.numeric() <validator_collection:validator_collection.validators.numeric>`
     - :func:`validator_collection.validators.numeric() <validator_collection:validator_collection.validators.numeric>`
     - :func:`validator_collection.validators.numeric() <validator_collection:validator_collection.validators.numeric>`
   * - | :class:`decimal.Decimal <python:decimal.Decimal>`
         :class:`DECIMAL <sqlalchemy:sqlalchemy.types.DECIMAL>`
     - :class:`decimal.Decimal <python:decimal.Decimal>`
     - :class:`decimal.Decimal <python:decimal.Decimal>`
     - :class:`decimal.Decimal <python:decimal.Decimal>`
     - :class:`decimal.Decimal <python:decimal.Decimal>`
   * - | :class:`datetime.date <python:datetime.date>`
         :class:`Date <sqlalchemy:sqlalchemy.types.Date>`
         :class:`DATE <sqlalchemy:sqlalchemy.types.DATE>`
     - :class:`datetime.date <python:datetime.date>`
     - :class:`datetime.date <python:datetime.date>`
     - :class:`datetime.date <python:datetime.date>`
     - :class:`datetime.date <python:datetime.date>`
   * - | :class:`datetime.datetime <python:datetime.datetime>`
         :class:`DateTime <sqlalchemy:sqlalchemy.types.DateTime>`
       | :class:`DATETIME <sqlalchemy:sqlalchemy.types.DATETIME>`
         :class:`TIMESTAMP <sqlalchemy:sqlalchemy.types.TIMESTAMP>`
       | :class:`mssql.SMALLDATETIME <sqlalchemy:sqlalchemy.dialects.mssql.SMALLDATETIME>`
       | :class:`mssql.DATETIME2 <sqlalchemy:sqlalchemy.dialects.mssql.DATETIME2>`
     - :class:`datetime.datetime <python:datetime.datetime>`
     - :class:`datetime.datetime <python:datetime.datetime>`
     - :class:`datetime.datetime <python:datetime.datetime>`
     - :class:`datetime.datetime <python:datetime.datetime>`
   * - | :class:`datetime.time <python:datetime.time>`
         :class:`Time <sqlalchemy:sqlalchemy.types.Time>`
         :class:`TIME <sqlalchemy:sqlalchemy.types.TIME>`
     - :class:`datetime.time <python:datetime.time>`
     - :class:`datetime.time <python:datetime.time>`
     - :class:`datetime.time <python:datetime.time>`
     - :class:`datetime.time <python:datetime.time>`
   * - :class:`mysql.YEAR <sqlalchemy:sqlalchemy.dialects.mysql.YEAR>`
     -
     -
     -
     -
   * - | :class:`datetime.timedelta <python:datetime.timedelta>`
         :class:`Interval <sqlalchemy:sqlalchemy.types.Interval>`
       | :class:`INTERVAL <sqlalchemy:sqlalchemy.types.INTERVAL>`
     - :class:`datetime.timedelta <python:datetime.timedelta>`
     - :class:`datetime.timedelta <python:datetime.timedelta>`
     - :class:`datetime.timedelta <python:datetime.timedelta>`
     - :class:`datetime.timedelta <python:datetime.timedelta>`
   * - | :class:`bytes <python:bytes>`
       | :class:`mssql.IMAGE <sqlalchemy:sqlalchemy.dialects.mssql.IMAGE>`
       | :class:`BINARY <sqlalchemy:sqlalchemy.types.BINARY>`
         :class:`VARBINARY <sqlalchemy:sqlalchemy.types.VARBINARY>`
       | :class:`LargeBinary <sqlalchemy:sqlalchemy.types.LargeBinary>`
         :class:`BLOB <sqlalchemy:sqlalchemy.types.BLOB>`
       | :class:`mysql.TINYBLOB <sqlalchemy:sqlalchemy.dialects.mysql.TINYBLOB>`
       | :class:`mysql.MEDIUMBLOB <sqlalchemy:sqlalchemy.dialects.mysql.MEDIUMBLOB>`
       | :class:`mysql.LONGBLOB <sqlalchemy:sqlalchemy.dialects.mysql.LONGBLOB>`
       | :class:`PickleType <sqlalchemy:sqlalchemy.types.PickleType>`
         :class:`oracle.RAW <sqlalchemy:sqlalchemy.dialects.oracle.RAW>`
     - :class:`bytes <python:bytes>`
     - :class:`bytes <python:bytes>`
     - :class:`bytes <python:bytes>`
     - :class:`bytes <python:bytes>`
   * - | :class:`postgresql.BYTEA <sqlalchemy:sqlalchemy.dialects.postgresql.BYTEA>`
       | :class:`oracle.BFILE <sqlalchemy:sqlalchemy.dialects.oracle.BFILE>`
     -
     -
     -
     -
   * - :class:`postgresql.UUID <sqlalchemy:sqlalchemy.dialects.postgresql.UUID>`
     - :class:`uuid.UUID <python:uuid.UUID>`
     - :class:`uuid.UUID <python:uuid.UUID>`
     - :class:`uuid.UUID <python:uuid.UUID>`
     - :class:`uuid.UUID <python:uuid.UUID>`
   * - | :class:`mssql.BIT <sqlalchemy:sqlalchemy.dialects.mssql.BIT>`
         :class:`postgresql.BIT <sqlalchemy:sqlalchemy.dialects.postgresql.BIT>`
     - :class:`bool <python:bool>`
     - :class:`bool <python:bool>`
     - :class:`bool <python:bool>`
     - :class:`bool <python:bool>`
   * - | :class:`postgresql.REGCLASS <sqlalchemy:sqlalchemy.dialects.postgresql.REGCLASS>`
       | :class:`postgresql.OID <sqlalchemy:sqlalchemy.dialects.postgresql.OID>`
       | :class:`postgresql.CIDR <sqlalchemy:sqlalchemy.dialects.postgresql.CIDR>`
       | :class:`postgresql.INET <sqlalchemy:sqlalchemy.dialects.postgresql.INET>`
       | :class:`postgresql.TSVECTOR <sqlalchemy:sqlalchemy.dialects.postgresql.TSVECTOR>`
       | :class:`mssql.XML <sqlalchemy:sqlalchemy.dialects.mssql.XML>`
       | :class:`mssql.UNIQUEIDENTIFIER <sqlalchemy:sqlalchemy.dialects.mssql.UNIQUEIDENTIFIER>`
     -
     -
     -
     -
   * - :class:`postgresql.MACADDR <sqlalchemy:sqlalchemy.dialects.postgresql.MACADDR>`
     - :class:`str <python:str>`
     - :class:`str <python:str>`
     - :class:`str <python:str>`
     - :class:`str <python:str>`
   * - | :class:`JSON <sqlalchemy:sqlalchemy.types.JSON>`
         :class:`postgresql.JSONB <sqlalchemy:sqlalchemy.dialects.postgresql.JSONB>`
     - :exc:`UnsupportedDeserializationError <sqlathanor.errors.UnsupportedDeserializationError>`
     - :class:`str <python:str>`
     - :class:`str <python:str>`
     - :class:`str <python:str>`
   * - | :class:`postgresql.HSTORE <sqlalchemy:sqlalchemy.dialects.postgresql.HSTORE>`
       | :class:`ARRAY <sqlalchemy:sqlalchemy.types.ARRAY>`
     - :exc:`UnsupportedDeserializationError <sqlathanor.errors.UnsupportedDeserializationError>`
     -
     -
     -
   * - | :class:`dict <python:dict>`
         :class:`list <python:list>`
       | :class:`set <python:set>`
         :class:`tuple <python:tuple>`
     - :exc:`UnsupportedDeserializationError <sqlathanor.errors.UnsupportedDeserializationError>`
     - iterable
     - iterable
     - iterable
   * - | :class:`mssql.SQL_VARIANT <sqlalchemy:sqlalchemy.dialects.mssql.SQL_VARIANT>`
     - :exc:`UnsupportedDeserializationError <sqlathanor.errors.UnsupportedDeserializationError>`
     - :exc:`UnsupportedDeserializationError <sqlathanor.errors.UnsupportedDeserializationError>`
     - :exc:`UnsupportedDeserializationError <sqlathanor.errors.UnsupportedDeserializationError>`
     - :exc:`UnsupportedDeserializationError <sqlathanor.errors.UnsupportedDeserializationError>`
