# -*- coding: utf-8 -*-

"""
******************************************
tests.test_table_deserialization
******************************************

Tests for ``Table.from_<format>()`` deserialization.

"""
from datetime import datetime
from typing import Any, Union, Optional

import pytest

import simplejson as json
import yaml

from validator_collection import checkers

from sqlalchemy import MetaData
from sqlalchemy.types import Integer, Text, Float, DateTime, Date, Time, Boolean

from sqlathanor import Table
from sqlathanor.errors import UnsupportedValueTypeError, CSVStructureError

from sqlathanor._compat import is_py36

from tests.fixtures import check_input_file, input_files

if is_py36:
    class_def = """
from pydantic import BaseModel
from pydantic.fields import Field, ModelField

class PydanticModel(BaseModel):
    id: int
    field_1: str
    field_2: str

class PydanticModel2(BaseModel):
    id: int
    field_1: str
    field_2: str
    field_3: Any

class PydanticModel3(BaseModel):
    id: int
    field_4: Optional[str]
    field_5: bool
    field_6: Union[str, int]
"""
    try:
        exec(class_def)
    except SyntaxError:
        def Field(*args, **kwargs):
            return None
        PydanticModel = 'Python <3.6'
        PydanticModel2 = 'Python <3.6'
        PydanticModel3 = 'Python <3.6'
else:
    def Field(*args, **kwargs):
        return None
    PydanticModel = 'Python <3.6'
    PydanticModel2 = 'Python <3.6'
    PydanticModel3 = 'Python <3.6'


# pylint: disable=line-too-long

def test_func():
    pass

@pytest.mark.parametrize('input_data, tablename, primary_key, column_kwargs, skip_nested, default_to_str, type_mapping, expected_types, error', [
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time(),
      'nested1': ['test', 'test2']
     }, 'test_table0', 'int1', None, True, False, None, [('int1', Integer),
                                                         ('string1', Text),
                                                         ('float1', Float),
                                                         ('bool1', Boolean),
                                                         ('datetime1', DateTime),
                                                         ('date1', Date),
                                                         ('time1', Time)], None),
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time(),
      'nested1': ['test', 'test2']
     }, 'test_table1', 'int1', None, False, True, None, [('int1', Integer),
                                                         ('string1', Text),
                                                         ('float1', Float),
                                                         ('bool1', Boolean),
                                                         ('datetime1', DateTime),
                                                         ('date1', Date),
                                                         ('time1', Time),
                                                         ('nested1', Text)], None),
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time(),
      'nested1': ['test', 'test2']
     }, 'test_table2', 'int1', None, False, False, None, [('int1', Integer),
                                                          ('string1', Text),
                                                          ('float1', Float),
                                                          ('bool1', Boolean),
                                                          ('datetime1', DateTime),
                                                          ('date1', Date),
                                                          ('time1', Time)], UnsupportedValueTypeError),
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time(),
      'nested1': ['test', 'test2'],
      'callable1': test_func
     }, 'test_table3', 'int1', None, True, False, None, [('int1', Integer),
                                                         ('string1', Text),
                                                         ('float1', Float),
                                                         ('bool1', Boolean),
                                                         ('datetime1', DateTime),
                                                         ('date1', Date),
                                                         ('time1', Time)], UnsupportedValueTypeError),
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time(),
      'nested1': ['test', 'test2']
     }, 'test_table4', 'int1', {
         'float1': {
             'default': 543.21
         }
     },
     True, False, None, [('int1', Integer),
                         ('string1', Text),
                         ('float1', Float),
                         ('bool1', Boolean),
                         ('datetime1', DateTime),
                         ('date1', Date),
                         ('time1', Time)], None),
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time(),
      'nested1': ['test', 'test2']
     }, 'test_table5', 'int1', None, True, False, {'float': Text}, [('int1', Integer),
                                                                    ('string1', Text),
                                                                    ('float1', Text),
                                                                    ('bool1', Boolean),
                                                                    ('datetime1', DateTime),
                                                                    ('date1', Date),
                                                                    ('time1', Time)], None),
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time(),
      'nested1': ['test', 'test2']
     }, 'test_table6', 'int1', None, True, False, None, [('int1', Integer),
                                                         ('string1', Text),
                                                         ('float1', Float),
                                                         ('bool1', Boolean),
                                                         ('datetime1', DateTime),
                                                         ('date1', Date),
                                                         ('time1', Time)], None),

])
def test_from_dict(input_data,
                   tablename,
                   primary_key,
                   column_kwargs,
                   skip_nested,
                   default_to_str,
                   type_mapping,
                   expected_types,
                   error):
    # pylint: disable=no-member,line-too-long
    if column_kwargs is None:
        column_kwargs = {}

    if error:
        with pytest.raises(error):
            result = Table.from_dict(input_data,
                                     tablename = tablename,
                                     metadata = MetaData(),
                                     primary_key = primary_key,
                                     column_kwargs = column_kwargs,
                                     skip_nested = skip_nested,
                                     default_to_str = default_to_str,
                                     type_mapping = type_mapping)
    else:
        result = Table.from_dict(input_data,
                                 tablename = tablename,
                                 metadata = MetaData(),
                                 primary_key = primary_key,
                                 column_kwargs = column_kwargs,
                                 skip_nested = skip_nested,
                                 default_to_str = default_to_str,
                                 type_mapping = type_mapping)

        assert isinstance(result, Table)

        assert result.name == tablename

        for key in column_kwargs:
            item_column = None
            for column in result.c:
                if column.name == key:
                    item_column = column
                    break

            assert item_column is not None
            for subkey in column_kwargs[key]:
                assert hasattr(item_column, subkey) is True
                item_value = getattr(item_column, subkey)

                if subkey == 'default':
                    item_value = item_value.arg

                expected_value = column_kwargs[key][subkey]

                assert item_value == expected_value

        for item in expected_types:
            item_column = None
            for column in result.c:
                if item[0] == column.name:
                    item_column = column
                    break

            assert item_column is not None
            assert isinstance(item_column.type, item[1]) is True

            assert item_column.primary_key is (item[0] == primary_key)


@pytest.mark.parametrize('input_data, tablename, primary_key, column_kwargs, skip_nested, default_to_str, type_mapping, expected_types, error', [
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time().isoformat(),
      'nested1': ['test', 'test2']
     }, 'test_table0', 'int1', None, True, False, None, [('int1', Integer),
                                                         ('string1', Text),
                                                         ('float1', Float),
                                                         ('bool1', Boolean),
                                                         ('datetime1', DateTime),
                                                         ('date1', Date),
                                                         ('time1', Text)], None),
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time().isoformat(),
      'nested1': ['test', 'test2']
     }, 'test_table1', 'int1', None, False, True, None, [('int1', Integer),
                                                         ('string1', Text),
                                                         ('float1', Float),
                                                         ('bool1', Boolean),
                                                         ('datetime1', DateTime),
                                                         ('date1', Date),
                                                         ('time1', Text),
                                                         ('nested1', Text)], None),
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time().isoformat(),
      'nested1': ['test', 'test2']
     }, 'test_table2', 'int1', None, False, False, None, [('int1', Integer),
                                                          ('string1', Text),
                                                          ('float1', Float),
                                                          ('bool1', Boolean),
                                                          ('datetime1', DateTime),
                                                          ('date1', Date),
                                                          ('time1', Text)], UnsupportedValueTypeError),
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time().isoformat(),
      'nested1': ['test', 'test2']
     }, 'test_table4', 'int1', {
         'float1': {
             'default': 543.21
         }
     },
     True, False, None, [('int1', Integer),
                         ('string1', Text),
                         ('float1', Float),
                         ('bool1', Boolean),
                         ('datetime1', DateTime),
                         ('date1', Date),
                         ('time1', Text)], None),
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time().isoformat(),
      'nested1': ['test', 'test2']
     }, 'test_table5', 'int1', None, True, False, {'float': Text}, [('int1', Integer),
                                                                    ('string1', Text),
                                                                    ('float1', Text),
                                                                    ('bool1', Boolean),
                                                                    ('datetime1', DateTime),
                                                                    ('date1', Date),
                                                                    ('time1', Text)], None),
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time().isoformat(),
      'nested1': ['test', 'test2']
     }, 'test_table6', 'int1', None, True, False, None, [('int1', Integer),
                                                         ('string1', Text),
                                                         ('float1', Float),
                                                         ('bool1', Boolean),
                                                         ('datetime1', DateTime),
                                                         ('date1', Date),
                                                         ('time1', Text)], None),

    ("JSON/input_json1.json", 'test_table7', 'test', None, True, False, None, [('test', Integer),
                                                                               ('second_test', Text)], None),
    ("JSON/input_json2.json", 'test_table8', 'test', None, True, False, None, [('test', Integer),
                                                                               ('second_test', Text)], None),
    ("JSON/update_from_json1.json", 'test_table9', 'id', None, True, False, None, [('id', Integer),
                                                                                   ('name', Text),
                                                                                   ('hybrid_value', Text)], None),
    ("JSON/update_from_json2.json", 'test_table10', 'id', None, True, False, None, [('id', Integer),
                                                                                    ('name', Text),
                                                                                    ('hybrid_value', Text)], None),
    ("JSON/update_from_json3.json", 'test_table11', 'id', None, True, False, None, [('id', Integer),
                                                                                    ('name', Text),
                                                                                    ('hybrid_value', Text)], ValueError),

])
def test_from_json(input_files,
                   input_data,
                   tablename,
                   primary_key,
                   column_kwargs,
                   skip_nested,
                   default_to_str,
                   type_mapping,
                   expected_types,
                   error):
    # pylint: disable=no-member,line-too-long
    input_data = check_input_file(input_files, input_data)

    if not checkers.is_file(input_data):
        input_data = json.dumps(input_data)

    # pylint: disable=no-member,line-too-long
    if column_kwargs is None:
        column_kwargs = {}

    if error:
        with pytest.raises(error):
            result = Table.from_json(input_data,
                                     tablename = tablename,
                                     metadata = MetaData(),
                                     primary_key = primary_key,
                                     column_kwargs = column_kwargs,
                                     skip_nested = skip_nested,
                                     default_to_str = default_to_str,
                                     type_mapping = type_mapping)
    else:
        result = Table.from_json(input_data,
                                 tablename = tablename,
                                 metadata = MetaData(),
                                 primary_key = primary_key,
                                 column_kwargs = column_kwargs,
                                 skip_nested = skip_nested,
                                 default_to_str = default_to_str,
                                 type_mapping = type_mapping)

        assert isinstance(result, Table)

        assert result.name == tablename

        for key in column_kwargs:
            item_column = None
            for column in result.c:
                if column.name == key:
                    item_column = column
                    break

            assert item_column is not None
            for subkey in column_kwargs[key]:
                assert hasattr(item_column, subkey) is True
                item_value = getattr(item_column, subkey)

                if subkey == 'default':
                    item_value = item_value.arg

                expected_value = column_kwargs[key][subkey]

                assert item_value == expected_value

        for item in expected_types:
            item_column = None
            for column in result.c:
                if item[0] == column.name:
                    item_column = column
                    break

            assert item_column is not None
            assert isinstance(item_column.type, item[1]) is True

            assert item_column.primary_key is (item[0] == primary_key)


@pytest.mark.parametrize('input_data, tablename, primary_key, column_kwargs, skip_nested, default_to_str, type_mapping, expected_types, error', [
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time().isoformat(),
      'nested1': ['test', 'test2']
     }, 'test_table0', 'int1', None, True, False, None, [('int1', Integer),
                                                         ('string1', Text),
                                                         ('float1', Float),
                                                         ('bool1', Boolean),
                                                         ('datetime1', DateTime),
                                                         ('date1', Date),
                                                         ('time1', Text)], None),
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time().isoformat(),
      'nested1': ['test', 'test2']
     }, 'test_table1', 'int1', None, False, True, None, [('int1', Integer),
                                                         ('string1', Text),
                                                         ('float1', Float),
                                                         ('bool1', Boolean),
                                                         ('datetime1', DateTime),
                                                         ('date1', Date),
                                                         ('time1', Text),
                                                         ('nested1', Text)], None),
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time().isoformat(),
      'nested1': ['test', 'test2']
     }, 'test_table2', 'int1', None, False, False, None, [('int1', Integer),
                                                          ('string1', Text),
                                                          ('float1', Float),
                                                          ('bool1', Boolean),
                                                          ('datetime1', DateTime),
                                                          ('date1', Date),
                                                          ('time1', Text)], UnsupportedValueTypeError),
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time().isoformat(),
      'nested1': ['test', 'test2']
     }, 'test_table4', 'int1', {
         'float1': {
             'default': 543.21
         }
     },
     True, False, None, [('int1', Integer),
                         ('string1', Text),
                         ('float1', Float),
                         ('bool1', Boolean),
                         ('datetime1', DateTime),
                         ('date1', Date),
                         ('time1', Text)], None),
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time().isoformat(),
      'nested1': ['test', 'test2']
     }, 'test_table5', 'int1', None, True, False, {'float': Text}, [('int1', Integer),
                                                                    ('string1', Text),
                                                                    ('float1', Text),
                                                                    ('bool1', Boolean),
                                                                    ('datetime1', DateTime),
                                                                    ('date1', Date),
                                                                    ('time1', Text)], None),
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time().isoformat(),
      'nested1': ['test', 'test2']
     }, 'test_table6', 'int1', None, True, False, None, [('int1', Integer),
                                                         ('string1', Text),
                                                         ('float1', Float),
                                                         ('bool1', Boolean),
                                                         ('datetime1', DateTime),
                                                         ('date1', Date),
                                                         ('time1', Text)], None),

    ("JSON/input_json1.json", 'test_table7', 'test', None, True, False, None, [('test', Integer),
                                                                               ('second_test', Text)], None),
    ("JSON/input_json2.json", 'test_table8', 'test', None, True, False, None, [('test', Integer),
                                                                               ('second_test', Text)], None),
    ("JSON/update_from_json1.json", 'test_table9', 'id', None, True, False, None, [('id', Integer),
                                                                                   ('name', Text),
                                                                                   ('hybrid_value', Text)], None),
    ("JSON/update_from_json2.json", 'test_table10', 'id', None, True, False, None, [('id', Integer),
                                                                                    ('name', Text),
                                                                                    ('hybrid_value', Text)], None),
    ("JSON/update_from_json3.json", 'test_table11', 'id', None, True, False, None, [('id', Integer),
                                                                                    ('name', Text),
                                                                                    ('hybrid_value', Text)], ValueError),

])
def test_from_yaml(input_files,
                   input_data,
                   tablename,
                   primary_key,
                   column_kwargs,
                   skip_nested,
                   default_to_str,
                   type_mapping,
                   expected_types,
                   error):
    # pylint: disable=no-member,line-too-long

    input_data = check_input_file(input_files, input_data)

    if not checkers.is_file(input_data):
        input_data = yaml.dump(input_data)

    # pylint: disable=no-member,line-too-long
    if column_kwargs is None:
        column_kwargs = {}

    if error:
        with pytest.raises(error):
            result = Table.from_yaml(input_data,
                                     tablename = tablename,
                                     metadata = MetaData(),
                                     primary_key = primary_key,
                                     column_kwargs = column_kwargs,
                                     skip_nested = skip_nested,
                                     default_to_str = default_to_str,
                                     type_mapping = type_mapping)
    else:
        result = Table.from_yaml(input_data,
                                 tablename = tablename,
                                 metadata = MetaData(),
                                 primary_key = primary_key,
                                 column_kwargs = column_kwargs,
                                 skip_nested = skip_nested,
                                 default_to_str = default_to_str,
                                 type_mapping = type_mapping)

        assert isinstance(result, Table)

        assert result.name == tablename

        for key in column_kwargs:
            item_column = None
            for column in result.c:
                if column.name == key:
                    item_column = column
                    break

            assert item_column is not None
            for subkey in column_kwargs[key]:
                assert hasattr(item_column, subkey) is True
                item_value = getattr(item_column, subkey)

                if subkey == 'default':
                    item_value = item_value.arg

                expected_value = column_kwargs[key][subkey]

                assert item_value == expected_value

        for item in expected_types:
            item_column = None
            for column in result.c:
                if item[0] == column.name:
                    item_column = column
                    break

            assert item_column is not None
            assert isinstance(item_column.type, item[1]) is True

            assert item_column.primary_key is (item[0] == primary_key)


@pytest.mark.parametrize('input_data, tablename, primary_key, column_kwargs, skip_nested, default_to_str, type_mapping, expected_types, error', [
    (["int1|string1|float1|bool1|datetime1|date1|time1|nested1",
      "123|test|123.45|True|2018-01-01T00:00:00.00000|2018-01-01|2018-01-01T00:00:00.00000|['test','test2']"],
     'test_table0', 'int1', None, True, False, None, [('int1', Integer),
                                                     ('string1', Text),
                                                     ('float1', Float),
                                                     ('bool1', Text),
                                                     ('datetime1', DateTime),
                                                     ('date1', Date),
                                                     ('time1', DateTime)], None),

    ("CSV/update_from_csv1.csv", 'test_table1', 'id', None, True, False, None, [('id', Integer),
                                                                                ('name', Text),
                                                                                ('password', Text),
                                                                                ('smallint_column', Integer),
                                                                                ('hybrid_value', Integer)], CSVStructureError),
    ("CSV/update_from_csv2.csv", 'test_table2', 'id', None, True, False, None, [('id', Integer),
                                                                                ('name', Text),
                                                                                ('password', Text),
                                                                                ('smallint_column', Integer),
                                                                                ('hybrid_value', Integer)], CSVStructureError),
    ("CSV/update_from_csv3.csv", 'test_table3', 'id', None, True, False, None, [('id', Integer),
                                                                                ('name', Text),
                                                                                ('password', Text),
                                                                                ('smallint_column', Integer),
                                                                                ('hybrid_value', Integer)], None),

])
def test_from_csv(input_files,
                  input_data,
                  tablename,
                  primary_key,
                  column_kwargs,
                  skip_nested,
                  default_to_str,
                  type_mapping,
                  expected_types,
                  error):
    input_data = check_input_file(input_files, input_data)

    if column_kwargs is None:
        column_kwargs = {}

    # pylint: disable=no-member,line-too-long
    if error:
        with pytest.raises(error):
            result = Table.from_csv(input_data,
                                    tablename = tablename,
                                    metadata = MetaData(),
                                    primary_key = primary_key,
                                    column_kwargs = column_kwargs,
                                    skip_nested = skip_nested,
                                    default_to_str = default_to_str,
                                    type_mapping = type_mapping)
    else:
        result = Table.from_csv(input_data,
                                tablename = tablename,
                                metadata = MetaData(),
                                primary_key = primary_key,
                                column_kwargs = column_kwargs,
                                skip_nested = skip_nested,
                                default_to_str = default_to_str,
                                type_mapping = type_mapping)

        assert isinstance(result, Table)

        assert result.name == tablename

        for key in column_kwargs:
            item_column = None
            for column in result.c:
                if column.name == key:
                    item_column = column
                    break

            assert item_column is not None
            for subkey in column_kwargs[key]:
                assert hasattr(item_column, subkey) is True
                item_value = getattr(item_column, subkey)

                if subkey == 'default':
                    item_value = item_value.arg

                expected_value = column_kwargs[key][subkey]

                assert item_value == expected_value

        for item in expected_types:
            item_column = None
            for column in result.c:
                if item[0] == column.name:
                    item_column = column
                    break

            assert item_column is not None
            assert isinstance(item_column.type, item[1]) is True

            assert item_column.primary_key is (item[0] == primary_key)


@pytest.mark.parametrize('kwargs, expected_columns, error', [
    ({}, 0, (TypeError, ValueError)),
    ('invalid-type', 0, (TypeError, ValueError)),
    ({'primary_key': 'id'}, 0, (TypeError, ValueError)),
    ({'tablename': 'some_tablename'}, 0, (TypeError, ValueError)),
    ({'models': 'invalid-type',
      'tablename': 'some_tablename',
      'primary_key': 'id'}, 0, (TypeError, ValueError)),
    ({'models': {
        '_single': [PydanticModel]
      },
      'tablename': 'some_tablename',
      'primary_key': 'id'}, 3, None),
    ({'models': {
        'set_one': [PydanticModel],
        'set_two': [PydanticModel2, PydanticModel3]
      },
      'tablename': 'some_tablename',
      'primary_key': 'id'}, 7, None),
    ({'models': {
        'set_one': [PydanticModel],
        'set_two': [PydanticModel2]
      },
      'tablename': 'some_tablename',
      'primary_key': 'id'}, 4, None),
    ({'models': {
        'set_one': [PydanticModel],
        'set_two': [PydanticModel2],
        'set_three': [PydanticModel3]
      },
      'tablename': 'some_tablename',
      'primary_key': 'id'}, 7, None),
])
def test_from_pydantic(kwargs, expected_columns, error):
    if not error and not isinstance(PydanticModel, str):
        tablename = kwargs.get('tablename', None)
        primary_key = kwargs.get('primary_key', None)

        kwargs['metadata'] = MetaData()

        result = Table.from_pydantic(**kwargs)

        assert isinstance(result, Table)
        assert result.name == tablename

        assert len(result.c) == expected_columns
    elif not error:
        pass
    else:
        with pytest.raises(error):
            result = Table.from_pydantic(**kwargs)
