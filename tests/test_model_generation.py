# -*- coding: utf-8 -*-

"""
***********************************
tests.test_model_generation
***********************************

Tests for functions which programmatically generate declarative models.

"""
from datetime import datetime
try:
    from typing import Any, Union, Optional
except ImportError:
    Any = 'Any'
    Union = 'Union'
    Optional = 'Optional'

import pytest

import simplejson as json
import yaml

from sqlalchemy.types import Integer, Text, Float, DateTime, Date, Time, Boolean
from validator_collection import checkers

from sqlathanor._compat import is_py36

from sqlathanor.declarative import generate_model_from_dict, generate_model_from_json, \
    generate_model_from_yaml, generate_model_from_csv, generate_model_from_pydantic
from sqlathanor.attributes import AttributeConfiguration
from sqlathanor.errors import UnsupportedValueTypeError, CSVStructureError

from tests.fixtures import check_input_file, input_files

# pylint: disable=line-too-long


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


def test_func():
    pass

@pytest.mark.parametrize('input_data, tablename, primary_key, serialization_config, skip_nested, default_to_str, type_mapping, base_model_attrs, expected_types, error', [
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time(),
      'nested1': ['test', 'test2']
     }, 'test_table', 'int1', None, True, False, None, None, [('int1', Integer),
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
     }, 'test_table', 'int1', None, False, True, None, None, [('int1', Integer),
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
     }, 'test_table', 'int1', None, False, False, None, None, [('int1', Integer),
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
     }, 'test_table', 'int1', None, True, False, None, None, [('int1', Integer),
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
     }, 'test_table', 'int1', [AttributeConfiguration(name = 'bool1', supports_csv = False, supports_json = True, supports_yaml = True, supports_dict = True)],
     True, False, None, None, [('int1', Integer),
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
     }, 'test_table', 'int1', None, True, False, {'float': Text}, None, [('int1', Integer),
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
     }, 'test_table', 'int1', None, True, False, None, {'test_attr': 123}, [('int1', Integer),
                                                                            ('string1', Text),
                                                                            ('float1', Float),
                                                                            ('bool1', Boolean),
                                                                            ('datetime1', DateTime),
                                                                            ('date1', Date),
                                                                            ('time1', Time)], None),

])
def test_generate_model_from_dict(input_data,
                                  tablename,
                                  primary_key,
                                  serialization_config,
                                  skip_nested,
                                  default_to_str,
                                  type_mapping,
                                  base_model_attrs,
                                  expected_types,
                                  error):
    # pylint: disable=no-member,line-too-long

    if error:
        with pytest.raises(error):
            result = generate_model_from_dict(input_data,
                                              tablename = tablename,
                                              primary_key = primary_key,
                                              serialization_config = serialization_config,
                                              skip_nested = skip_nested,
                                              default_to_str = default_to_str,
                                              type_mapping = type_mapping,
                                              base_model_attrs = base_model_attrs)
    else:
        result = generate_model_from_dict(input_data,
                                          tablename = tablename,
                                          primary_key = primary_key,
                                          serialization_config = serialization_config,
                                          skip_nested = skip_nested,
                                          default_to_str = default_to_str,
                                          type_mapping = type_mapping,
                                          base_model_attrs = base_model_attrs)

        assert hasattr(result, 'to_json') is True
        assert hasattr(result, 'new_from_json') is True
        assert hasattr(result, 'update_from_json') is True
        assert hasattr(result, '__serialization__') is True

        assert result.__tablename__ == tablename

        for item in expected_types:
            assert hasattr(result, item[0]) is True
            attribute = getattr(result, item[0], None)
            assert isinstance(attribute.type, item[1]) is True

        if serialization_config:
            for item in serialization_config:
                assert hasattr(result, item.name) is True
                assert result.get_attribute_serialization_config(item.name) == item
        else:
            for item in expected_types:
                assert hasattr(result, item[0]) is True
                assert result.get_attribute_serialization_config(item[0]).supports_csv == (True, True)
                assert result.get_attribute_serialization_config(item[0]).supports_json == (True, True)
                assert result.get_attribute_serialization_config(item[0]).supports_yaml == (True, True)
                assert result.get_attribute_serialization_config(item[0]).supports_dict == (True, True)

        if base_model_attrs:
            for key in base_model_attrs:
                assert hasattr(result, key) is True
                assert getattr(result, key) == base_model_attrs[key]


@pytest.mark.parametrize('input_data, tablename, primary_key, serialization_config, skip_nested, default_to_str, type_mapping, base_model_attrs, expected_types, error', [
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time().isoformat(),
      'nested1': ['test', 'test2']
     }, 'test_table0', 'int1', None, True, False, None, None, [('int1', Integer),
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
     }, 'test_table1', 'int1', None, False, True, None, None, [('int1', Integer),
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
     }, 'test_table2', 'int1', None, False, False, None, None, [('int1', Integer),
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
     }, 'test_table3', 'int1', [AttributeConfiguration(name = 'bool1', supports_csv = False, supports_json = True, supports_yaml = True, supports_dict = True)],
     True, False, None, None, [('int1', Integer),
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
     }, 'test_table4', 'int1', None, True, False, {'float': Text}, None, [('int1', Integer),
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
     }, 'test_table5', 'int1', None, True, False, None, {'test_attr': 123}, [('int1', Integer),
                                                                             ('string1', Text),
                                                                             ('float1', Float),
                                                                             ('bool1', Boolean),
                                                                             ('datetime1', DateTime),
                                                                             ('date1', Date),
                                                                             ('time1', Text)], None),

    ("JSON/input_json1.json", 'test_table6', 'test', None, True, False, None, None, [('test', Integer),
                                                                                     ('second_test', Text)], None),
    ("JSON/input_json2.json", 'test_table7', 'test', None, True, False, None, None, [('test', Integer),
                                                                                     ('second_test', Text)], None),
    ("JSON/update_from_json1.json", 'test_table8', 'id', None, True, False, None, None, [('id', Integer),
                                                                                         ('name', Text),
                                                                                         ('hybrid_value', Text)], None),
    ("JSON/update_from_json2.json", 'test_table9', 'id', None, True, False, None, None, [('id', Integer),
                                                                                         ('name', Text),
                                                                                         ('hybrid_value', Text)], None),
    ("JSON/update_from_json3.json", 'test_table10', 'id', None, True, False, None, None, [('id', Integer),
                                                                                          ('name', Text),
                                                                                          ('hybrid_value', Text)], ValueError),

])
def test_generate_model_from_json(input_files,
                                  input_data,
                                  tablename,
                                  primary_key,
                                  serialization_config,
                                  skip_nested,
                                  default_to_str,
                                  type_mapping,
                                  base_model_attrs,
                                  expected_types,
                                  error):
    # pylint: disable=no-member,line-too-long
    input_data = check_input_file(input_files, input_data)

    if not checkers.is_file(input_data):
        input_data = json.dumps(input_data)

    if error:
        with pytest.raises(error):
            result = generate_model_from_json(input_data,
                                              tablename = tablename,
                                              primary_key = primary_key,
                                              serialization_config = serialization_config,
                                              skip_nested = skip_nested,
                                              default_to_str = default_to_str,
                                              type_mapping = type_mapping,
                                              base_model_attrs = base_model_attrs)
    else:
        result = generate_model_from_json(input_data,
                                          tablename = tablename,
                                          primary_key = primary_key,
                                          serialization_config = serialization_config,
                                          skip_nested = skip_nested,
                                          default_to_str = default_to_str,
                                          type_mapping = type_mapping,
                                          base_model_attrs = base_model_attrs)

        assert hasattr(result, 'to_json') is True
        assert hasattr(result, 'new_from_json') is True
        assert hasattr(result, 'update_from_json') is True
        assert hasattr(result, '__serialization__') is True

        assert result.__tablename__ == tablename

        for item in expected_types:
            assert hasattr(result, item[0]) is True
            attribute = getattr(result, item[0], None)
            assert isinstance(attribute.type, item[1]) is True

        if serialization_config:
            for item in serialization_config:
                assert hasattr(result, item.name) is True
                assert result.get_attribute_serialization_config(item.name) == item
        else:
            for item in expected_types:
                assert hasattr(result, item[0]) is True
                assert result.get_attribute_serialization_config(item[0]).supports_csv == (True, True)
                assert result.get_attribute_serialization_config(item[0]).supports_json == (True, True)
                assert result.get_attribute_serialization_config(item[0]).supports_yaml == (True, True)
                assert result.get_attribute_serialization_config(item[0]).supports_dict == (True, True)

        if base_model_attrs:
            for key in base_model_attrs:
                assert hasattr(result, key) is True
                assert getattr(result, key) == base_model_attrs[key]


@pytest.mark.parametrize('input_data, tablename, primary_key, serialization_config, skip_nested, default_to_str, type_mapping, base_model_attrs, expected_types, error', [
    ({'int1': 123,
      'string1': 'test',
      'float1': 123.45,
      'bool1': True,
      'datetime1': '2018-01-01T00:00:00.00000',
      'date1': '2018-01-01',
      'time1': datetime.utcnow().time().isoformat(),
      'nested1': ['test', 'test2']
     }, 'test_table0', 'int1', None, True, False, None, None, [('int1', Integer),
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
     }, 'test_table1', 'int1', None, False, True, None, None, [('int1', Integer),
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
     }, 'test_table2', 'int1', None, False, False, None, None, [('int1', Integer),
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
     }, 'test_table3', 'int1', [AttributeConfiguration(name = 'bool1', supports_csv = False, supports_json = True, supports_yaml = True, supports_dict = True)],
     True, False, None, None, [('int1', Integer),
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
     }, 'test_table4', 'int1', None, True, False, {'float': Text}, None, [('int1', Integer),
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
     }, 'test_table5', 'int1', None, True, False, None, {'test_attr': 123}, [('int1', Integer),
                                                                             ('string1', Text),
                                                                             ('float1', Float),
                                                                             ('bool1', Boolean),
                                                                             ('datetime1', DateTime),
                                                                             ('date1', Date),
                                                                             ('time1', Text)], None),

    ("JSON/input_json1.json", 'test_table6', 'test', None, True, False, None, None, [('test', Integer),
                                                                                     ('second_test', Text)], None),
    ("JSON/input_json2.json", 'test_table7', 'test', None, True, False, None, None, [('test', Integer),
                                                                                     ('second_test', Text)], None),
    ("JSON/update_from_json1.json", 'test_table8', 'id', None, True, False, None, None, [('id', Integer),
                                                                                         ('name', Text),
                                                                                         ('hybrid_value', Text)], None),
    ("JSON/update_from_json2.json", 'test_table9', 'id', None, True, False, None, None, [('id', Integer),
                                                                                         ('name', Text),
                                                                                         ('hybrid_value', Text)], None),
    ("JSON/update_from_json3.json", 'test_table10', 'id', None, True, False, None, None, [('id', Integer),
                                                                                          ('name', Text),
                                                                                          ('hybrid_value', Text)], ValueError),

])
def test_generate_model_from_yaml(input_files,
                                  input_data,
                                  tablename,
                                  primary_key,
                                  serialization_config,
                                  skip_nested,
                                  default_to_str,
                                  type_mapping,
                                  base_model_attrs,
                                  expected_types,
                                  error):
    # pylint: disable=no-member,line-too-long
    input_data = check_input_file(input_files, input_data)

    if not checkers.is_file(input_data):
        input_data = yaml.dump(input_data)

    if error:
        with pytest.raises(error):
            result = generate_model_from_yaml(input_data,
                                              tablename = tablename,
                                              primary_key = primary_key,
                                              serialization_config = serialization_config,
                                              skip_nested = skip_nested,
                                              default_to_str = default_to_str,
                                              type_mapping = type_mapping,
                                              base_model_attrs = base_model_attrs)
    else:
        result = generate_model_from_yaml(input_data,
                                          tablename = tablename,
                                          primary_key = primary_key,
                                          serialization_config = serialization_config,
                                          skip_nested = skip_nested,
                                          default_to_str = default_to_str,
                                          type_mapping = type_mapping,
                                          base_model_attrs = base_model_attrs)

        assert hasattr(result, 'to_json') is True
        assert hasattr(result, 'new_from_json') is True
        assert hasattr(result, 'update_from_json') is True
        assert hasattr(result, '__serialization__') is True

        assert result.__tablename__ == tablename

        for item in expected_types:
            assert hasattr(result, item[0]) is True
            attribute = getattr(result, item[0], None)
            assert isinstance(attribute.type, item[1]) is True

        if serialization_config:
            for item in serialization_config:
                assert hasattr(result, item.name) is True
                assert result.get_attribute_serialization_config(item.name) == item
        else:
            for item in expected_types:
                assert hasattr(result, item[0]) is True
                assert result.get_attribute_serialization_config(item[0]).supports_csv == (True, True)
                assert result.get_attribute_serialization_config(item[0]).supports_json == (True, True)
                assert result.get_attribute_serialization_config(item[0]).supports_yaml == (True, True)
                assert result.get_attribute_serialization_config(item[0]).supports_dict == (True, True)

        if base_model_attrs:
            for key in base_model_attrs:
                assert hasattr(result, key) is True
                assert getattr(result, key) == base_model_attrs[key]


@pytest.mark.parametrize('input_data, tablename, primary_key, serialization_config, skip_nested, default_to_str, type_mapping, base_model_attrs, expected_types, error', [
    (["int1|string1|float1|bool1|datetime1|date1|time1|nested1",
      "123|test|123.45|True|2018-01-01T00:00:00.00000|2018-01-01|2018-01-01T00:00:00.00000|['test','test2']"],
     'test_table0', 'int1', None, True, False, None, None, [('int1', Integer),
                                                            ('string1', Text),
                                                            ('float1', Float),
                                                            ('bool1', Text),
                                                            ('datetime1', DateTime),
                                                            ('date1', Date),
                                                            ('time1', DateTime)], None),

    ("CSV/update_from_csv1.csv", 'test_table1', 'id', None, True, False, None, None, [('id', Integer),
                                                                                      ('name', Text),
                                                                                      ('password', Text),
                                                                                      ('smallint_column', Integer),
                                                                                      ('hybrid_value', Integer)], CSVStructureError),
    ("CSV/update_from_csv2.csv", 'test_table2', 'id', None, True, False, None, None, [('id', Integer),
                                                                                      ('name', Text),
                                                                                      ('password', Text),
                                                                                      ('smallint_column', Integer),
                                                                                      ('hybrid_value', Integer)], CSVStructureError),
    ("CSV/update_from_csv3.csv", 'test_table3', 'id', None, True, False, None, None, [('id', Integer),
                                                                                      ('name', Text),
                                                                                      ('password', Text),
                                                                                      ('smallint_column', Integer),
                                                                                      ('hybrid_value', Integer)], None),

])
def test_generate_model_from_csv(input_files,
                                 input_data,
                                 tablename,
                                 primary_key,
                                 serialization_config,
                                 skip_nested,
                                 default_to_str,
                                 type_mapping,
                                 base_model_attrs,
                                 expected_types,
                                 error):
    # pylint: disable=no-member,line-too-long

    input_data = check_input_file(input_files, input_data)

    if error:
        with pytest.raises(error):
            result = generate_model_from_csv(input_data,
                                             tablename = tablename,
                                             primary_key = primary_key,
                                             serialization_config = serialization_config,
                                             skip_nested = skip_nested,
                                             default_to_str = default_to_str,
                                             type_mapping = type_mapping,
                                             base_model_attrs = base_model_attrs)
    else:
        result = generate_model_from_csv(input_data,
                                         tablename = tablename,
                                         primary_key = primary_key,
                                         serialization_config = serialization_config,
                                         skip_nested = skip_nested,
                                         default_to_str = default_to_str,
                                         type_mapping = type_mapping,
                                         base_model_attrs = base_model_attrs)

        assert hasattr(result, 'to_json') is True
        assert hasattr(result, 'new_from_json') is True
        assert hasattr(result, 'update_from_json') is True
        assert hasattr(result, '__serialization__') is True

        assert result.__tablename__ == tablename

        for item in expected_types:
            assert hasattr(result, item[0]) is True
            attribute = getattr(result, item[0], None)
            assert isinstance(attribute.type, item[1]) is True

        if serialization_config:
            for item in serialization_config:
                assert hasattr(result, item.name) is True
                assert result.get_attribute_serialization_config(item.name) == item
        else:
            for item in expected_types:
                assert hasattr(result, item[0]) is True
                assert result.get_attribute_serialization_config(item[0]).supports_csv == (True, True)
                assert result.get_attribute_serialization_config(item[0]).supports_json == (True, True)
                assert result.get_attribute_serialization_config(item[0]).supports_yaml == (True, True)
                assert result.get_attribute_serialization_config(item[0]).supports_dict == (True, True)

        if base_model_attrs:
            for key in base_model_attrs:
                assert hasattr(result, key) is True
                assert getattr(result, key) == base_model_attrs[key]


@pytest.mark.parametrize('kwargs, error', [
    ({}, (TypeError, ValueError)),
    ('invalid-type', (TypeError, ValueError)),
    ({'primary_key': 'id'}, (TypeError, ValueError)),
    ({'tablename': 'some_tablename'}, (TypeError, ValueError)),
    ({'pydantic_models': 'invalid-type',
      'tablename': 'some_tablename',
      'primary_key': 'id'}, (TypeError, ValueError)),
    ({'pydantic_models': {
        '_single': [PydanticModel]
      },
      'tablename': 'some_tablename',
      'primary_key': 'id'}, None),
    ({'pydantic_models': {
        'set_one': [PydanticModel],
        'set_two': [PydanticModel2, PydanticModel3]
      },
      'tablename': 'some_tablename',
      'primary_key': 'id'}, None),
    ({'pydantic_models': {
        'set_one': [PydanticModel],
        'set_two': [PydanticModel2]
      },
      'tablename': 'some_tablename',
      'primary_key': 'id'}, None),
    ({'pydantic_models': {
        'set_one': [PydanticModel],
        'set_two': [PydanticModel2],
        'set_three': [PydanticModel3]
      },
      'tablename': 'some_tablename',
      'primary_key': 'id'}, None),
])
def test_generate_model_from_pydantic(kwargs, error):
    if not error and not isinstance(PydanticModel, str):
        tablename = kwargs.get('tablename', None)
        primary_key = kwargs.get('primary_key', None)
        base_model_attrs = kwargs.get('base_model_attrs', None)

        result = generate_model_from_pydantic(**kwargs)

        assert hasattr(result, 'to_json') is True
        assert hasattr(result, 'new_from_json') is True
        assert hasattr(result, 'update_from_json') is True
        assert hasattr(result, '__serialization__') is True

        assert result.__tablename__ == tablename

        if base_model_attrs:
            for key in base_model_attrs:
                assert hasattr(result, key) is True
                assert getattr(result, key) == base_model_attrs[key]
    elif not error:
        pass
    else:
        with pytest.raises(error):
            result = generate_model_from_pydantic(**kwargs)
