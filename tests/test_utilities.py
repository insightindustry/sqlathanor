# -*- coding: utf-8 -*-

"""
***********************************
tests.test_utilities
***********************************

Tests for the schema extensions written in :ref:`sqlathanor.utilities`.

"""
import os
try:
    from typing import Any, Union, Optional
except ImportError:
    Any = 'Any'
    Union = 'Union'
    Optional = 'Optional'

import pytest
import sqlalchemy

from validator_collection import checkers
from validator_collection.errors import NotAnIterableError

from sqlathanor._compat import is_py36

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_complex_postgresql, instance_postgresql, input_files, check_input_file

from sqlathanor.utilities import bool_to_tuple, callable_to_dict, format_to_tuple, \
    get_class_type_key, raise_UnsupportedSerializationError, \
    raise_UnsupportedDeserializationError, iterable__to_dict, parse_yaml, parse_json, \
    get_attribute_names, is_an_attribute, parse_csv, read_csv_data, columns_from_pydantic
from sqlathanor.errors import InvalidFormatError, UnsupportedSerializationError, \
    UnsupportedDeserializationError, MaximumNestingExceededError, \
    MaximumNestingExceededWarning, DeserializationError, CSVStructureError

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



def sample_callable():
    pass


@pytest.mark.parametrize('value, expected_result, fails', [
    (True, (True, True), False),
    (False, (False, False), False),
    (None, (False, False), False),
    ((True, True), (True, True), False),
    ((False, False), (False, False), False),
    ((True, False), (True, False), False),
    ((False, True), (False, True), False),
    ('not-a-bool', None, True),
])
def test_bool_to_tuple(value, expected_result, fails):
    if not fails:
        result = bool_to_tuple(value)
        assert result == expected_result
    else:
        with pytest.raises(ValueError):
            result = bool_to_tuple(value)


@pytest.mark.parametrize('value', [
    (sample_callable),
    ({
        'csv': sample_callable,
        'json': sample_callable,
        'yaml': sample_callable,
        'dict': sample_callable
    }),
    (None),
    ({
        'csv': None,
        'json': sample_callable,
        'yaml': None,
        'dict': None
    }),
])
def test_callable_to_dict(value):
    result = callable_to_dict(value)

    assert isinstance(result, dict)
    assert 'csv' in result
    assert 'json' in result
    assert 'yaml' in result
    assert 'dict' in result

    if isinstance(value, dict):
        assert result['csv'] == value['csv']
        assert result['json'] == value['json']
        assert result['yaml'] == value['yaml']
        assert result['dict'] == value['dict']
    else:
        for key in result:
            assert result[key] == value


@pytest.mark.parametrize('value, expected_result, fails', [
    ('csv', (True, None, None, None), False),
    ('json', (None, True, None, None), False),
    ('yaml', (None, None, True, None), False),
    ('dict', (None, None, None, True), False),
    ('invalid', None, True)
])
def test_format_to_tuple(value,
                         expected_result,
                         fails):
    if not fails:
        result = format_to_tuple(value)
        assert result == expected_result
    else:
        with pytest.raises(InvalidFormatError):
            result = format_to_tuple(value)


@pytest.mark.parametrize('attribute, value, expected_result', [
    (None, None, 'NONE'),
    (None, 1, 'int'),
    (None, 'string', 'str'),

    ('id', 1, 'INTEGER'),
    ('smallint_column', 2, 'SMALLINT'),

])
def test_get_class_type_key(request,
                            model_complex_postgresql,
                            attribute,
                            value,
                            expected_result):
    target = model_complex_postgresql[0]
    if attribute is not None:
        attribute = getattr(target, attribute)

    result = get_class_type_key(attribute, value = value)

    assert result == expected_result


def test_raise_UnsupportedSerializationError():
    with pytest.raises(UnsupportedSerializationError):
        raise_UnsupportedSerializationError('test')


def test_raise_UnsupportedDeserializationError():
    with pytest.raises(UnsupportedDeserializationError):
        raise_UnsupportedDeserializationError('test')


class DummyClass(object):
    def __init__(self, *args, **kwargs):
        pass

    def _to_dict(self, format, max_nesting = 0, current_nesting = 0, is_dumping = False, config_set = None):
        if format not in ['csv', 'json', 'yaml', 'dict']:
            raise InvalidFormatError()

        if current_nesting > max_nesting:
            raise MaximumNestingExceededError()

        return {
            'test': 'nested-one',
            'test2': 'nested-two'
        }


@pytest.mark.parametrize('input_value, format, max_nesting, current_nesting, expected_result, warning, error', [
    ([], 'invalid-format', 0, 0, None, None, InvalidFormatError),
    (123, 'dict', 0, 0, None, None, NotAnIterableError),
    ([1, 2, 3], 'dict', 0, 3, None, None, MaximumNestingExceededError),

    ([1, 2, 3], 'dict', 0, 0, [1, 2, 3], None, None),
    ([1, 2, 3], 'json', 0, 0, [1, 2, 3], None, None),
    ([1, 2, 3], 'yaml', 0, 0, [1, 2, 3], None, None),
    ([1, 2, 3], 'csv', 0, 0, [1, 2, 3], None, None),

    ([{
        'test': 'one',
        'test2': 'two'
    }, 2], 'dict', 0, 0, [{
        'test': 'one',
        'test2': 'two'
    }, 2], None, None),

    ([DummyClass()], 'dict', 1, 0, [{
        'test': 'nested-one',
        'test2': 'nested-two'
    }], None, None),
    ([DummyClass()], 'dict', 0, 0, [{
        'test': 'nested-one',
        'test2': 'nested-two'
    }], None, MaximumNestingExceededError),

])
def test_iterable__to_dict(input_value,
                           format,
                           max_nesting,
                           current_nesting,
                           expected_result,
                           warning,
                           error):
    if not error:
        result = iterable__to_dict(input_value,
                                   format,
                                   max_nesting = max_nesting,
                                   current_nesting = current_nesting)

        if isinstance(result, dict):
            assert checkers.are_dicts_equivalent(result, expected_result)
        else:
            assert result == expected_result
    else:
        with pytest.raises(error):
            result = iterable__to_dict(input_value,
                                       format,
                                       max_nesting = max_nesting,
                                       current_nesting = current_nesting)


@pytest.mark.parametrize('input_value, deserialize_function, expected_result, error', [
    ('{"test": 123, "second_test": "this is a test"}', None, { 'test': 123, 'second_test': 'this is a test' }, None),

    (None, None, None, DeserializationError),
    (None, 'not-callable', None, ValueError),

    ('JSON/input_json1.json', None, { 'test': 123, 'second_test': 'this is a test' }, None),
    ('JSON/input_json2.json', None, [{ 'test': 123, 'second_test': 'this is a test' },
                                     { 'test': 123, 'second_test': 'this is another test' }], None),
])
def test_parse_json(input_files,
                    input_value,
                    deserialize_function,
                    expected_result,
                    error):
    input_value = check_input_file(input_files, input_value)

    if not error:
        result = parse_json(input_value,
                            deserialize_function = deserialize_function)

        assert isinstance(result, (dict, list))
        assert checkers.are_equivalent(result, expected_result)
    else:
        with pytest.raises(error):
            result = parse_json(input_value)


@pytest.mark.parametrize('input_value, deserialize_function, expected_result, error', [
    ('{"test": 123, "second_test": "this is a test"}', None, { 'test': 123, 'second_test': 'this is a test' }, None),

    (None, None, None, DeserializationError),
    (None, 'not-callable', None, ValueError),

    ('JSON/input_json1.json', None, { 'test': 123, 'second_test': 'this is a test' }, None),
    ('JSON/input_json2.json', None, [{ 'test': 123, 'second_test': 'this is a test' },
                                     { 'test': 123, 'second_test': 'this is another test' }], None),

])
def test_parse_yaml(input_files,
                    input_value,
                    deserialize_function,
                    expected_result,
                    error):
    input_value = check_input_file(input_files, input_value)

    if not error:
        result = parse_yaml(input_value,
                            deserialize_function = deserialize_function)

        assert isinstance(result, (dict, list))
        assert checkers.are_equivalent(result, expected_result)
    else:
        with pytest.raises(error):
            result = parse_yaml(input_value)


@pytest.mark.parametrize('input_value, kwargs, expected_result, error', [
    (["col1|col2|col3", "123|456|789"], None, {'col1': '123', 'col2': '456', 'col3': '789'}, None),
    (["col1|col2|col3"], None, None, CSVStructureError),
    (["col1|col2|col3", "123|456|789", "987|654|321"], None, {'col1': '123', 'col2': '456', 'col3': '789'}, None),
    (["not a variable name|col2|col3", "123|456|789"], None, None, CSVStructureError),
])
def test_parse_csv(input_value, kwargs, expected_result, error):
    if not error:
        if kwargs:
            result = parse_csv(input_value, **kwargs)
        else:
            result = parse_csv(input_value)

        print(result)

        assert isinstance(result, dict)
        assert checkers.are_dicts_equivalent(result, expected_result)
    else:
        with pytest.raises(error):
            if kwargs:
                result = parse_csv(input_value, **kwargs)
            else:
                result = parse_csv(input_value)


@pytest.mark.parametrize('use_instance, include_callable, include_nested, include_private, include_special, include_utilities, expected_result', [
    (False, False, False, False, False, False, 8),
    (False, False, False, False, False, True, 10),
    (False, False, False, True, False, False, 9),
    (False, False, False, True, False, True, 12),
    (False, False, True, False, False, False, 10),
    (False, False, True, True, False, False, 11),
    (False, False, True, True, False, True, 15),
    (False, True, False, False, False, False, 39),
    (False, True, True, False, False, False, 41),
    (False, True, True, True, False, False, 57),
    (False, True, True, True, False, True, 61),

    (True, False, False, False, False, False, 9),
    (True, False, False, False, False, True, 11),
    (True, False, False, True, False, False, 10),
    (True, False, False, True, False, True, (13, 14)),
    (True, False, True, False, False, False, 10),
    (True, False, True, True, False, False, 11),
    (True, False, True, True, False, True, (15, 16)),
    (True, True, False, False, False, False, 40),
    (True, True, True, False, False, False, 41),
    (True, True, True, True, False, False, 57),
    (True, True, True, True, False, True, 62),

])
def test_get_attribute_names(model_complex_postgresql,
                             instance_postgresql,
                             use_instance,
                             include_callable,
                             include_nested,
                             include_private,
                             include_special,
                             include_utilities,
                             expected_result):
    if use_instance:
        target = instance_postgresql[0][0]
    else:
        target = model_complex_postgresql[0]

    result = get_attribute_names(target,
                                 include_callable = include_callable,
                                 include_nested = include_nested,
                                 include_private = include_private,
                                 include_utilities = include_utilities)

    print(result)
    if sqlalchemy.__version__[2] == '9' and isinstance(expected_result, tuple):
        expected_result = expected_result[0]
    elif isinstance(expected_result, tuple):
        expected_result = expected_result[1]

    assert len(result) == expected_result


@pytest.mark.parametrize('use_instance, attribute, forbid_callable, forbid_nested, expected_result', [
    (False, 'boolean_attribute', False, False, True),
    (False, 'string_attribute', False, False, True),
    (False, 'int_attribute', False, False, True),
    (False, 'dict_attribute', False, False, True),
    (False, 'dict_attribute', False, True, False),
    (False, 'list_attribute', False, False, True),
    (False, 'list_string', False, False, True),
    (False, 'list_dict', False, False, True),
    (False, 'list_dict', False, True, False),
    (False, 'set_attribute', False, False, True),
    (False, 'set_int', False, False, True),
    (False, 'property_attribute', False, False, True),
    (False, 'property_attribute', True, False, True),
    (False, 'method_attribute', False, False, True),
    (False, 'method_attribute', True, False, False),

    (True, 'boolean_attribute', False, False, True),
    (True, 'string_attribute', False, False, True),
    (True, 'int_attribute', False, False, True),
    (True, 'dict_attribute', False, False, True),
    (True, 'dict_attribute', False, True, False),
    (True, 'list_attribute', False, False, True),
    (True, 'list_string', False, False, True),
    (True, 'list_dict', False, False, True),
    (True, 'list_dict', False, True, False),
    (True, 'set_attribute', False, False, True),
    (True, 'set_int', False, False, True),
    (True, 'property_attribute', False, False, True),
    (True, 'property_attribute', True, False, True),
    (True, 'method_attribute', False, False, True),
    (True, 'method_attribute', True, False, False),
])
def test_is_an_attribute(use_instance, attribute, forbid_callable, forbid_nested, expected_result):
    class TestClass(object):
        boolean_attribute = True
        string_attribute = 'string'
        int_attribute = 1
        dict_attribute = {}
        list_attribute = []
        list_string = ['test', 'test']
        list_dict = [{}, {}]
        set_attribute = set()
        set_int = set([1, 2, 3])

        def __init__(self, *args, **kwargs):
            pass

        @property
        def property_attribute(self):
            pass

        def method_attribute(self, value):
            pass

    if use_instance:
        target = TestClass()
    else:
        target = TestClass

    assert is_an_attribute(target,
                           attribute,
                           include_callable = not forbid_callable,
                           include_nested = not forbid_nested) == expected_result


@pytest.mark.parametrize('input_data, single_record, expected_result', [
    ("col1|col2|col3\r\n123|456|789\r\n987|654|321", True, '123|456|789'),
    ("col1|col2|col3\n123|456|789", True, '123|456|789'),
    ("col1|col2|col3\r123|456|789", True, '123|456|789'),
    ("col1|col2|col3", True, "col1|col2|col3"),

    ("CSV/input_csv1.csv", True, '123|456|789'),
    ("CSV/input_csv2.csv", True, 'col1|col2|col3'),
    ("CSV/update_from_csv1.csv", True, "1|serialized|test-password|3|2"),

    ("col1|col2|col3\r\n123|456|789\r\n987|654|321", False, 'col1|col2|col3\r\n123|456|789\r\n987|654|321'),
    ("col1|col2|col3\n123|456|789", False, 'col1|col2|col3\n123|456|789'),
    ("col1|col2|col3\r123|456|789", False, 'col1|col2|col3\r123|456|789'),
    ("col1|col2|col3", False, "col1|col2|col3"),

    ("CSV/input_csv1.csv", False, 'col1|col2|col3\n123|456|789\n987|654|321'),
    ("CSV/input_csv2.csv", False, "col1|col2|col3"),
    ("CSV/update_from_csv1.csv", False, "1|serialized|test-password|3|2"),

])
def test_read_csv_data(input_files, input_data, single_record, expected_result):
    inputs = os.path.abspath(input_files)
    if not os.path.exists(input_files):
        raise AssertionError('input directory (%s) does not exist' % inputs)
    elif not os.path.isdir(input_files):
        raise AssertionError('input directory (%s) is not a directory' % inputs)

    input_file = os.path.join(input_files, input_data)

    if checkers.is_file(input_file):
        input_data = input_file

    result = read_csv_data(input_data,
                           single_record = single_record)

    if result is None:
        assert result == expected_result
    else:
        assert result.strip() == expected_result.strip()


if is_py36:
    @pytest.mark.parametrize('kwargs, expected_columns, expected_config_sets, error', [
        ({'config_sets': {
            '_single': [PydanticModel]
         },
         'primary_key': 'id'}, 3, 1, None),
        ({'config_sets': {
            'set_one': [PydanticModel],
            'set_two': [PydanticModel2, PydanticModel3]
         },
         'primary_key': 'id'}, 7, 2, None),
        ({'config_sets': {
            'set_one': [PydanticModel],
            'set_two': [PydanticModel2]
         },
         'primary_key': 'id'}, 4, 2, None),
        ({'config_sets': {
            'set_one': [PydanticModel],
            'set_two': [PydanticModel2],
            'set_three': [PydanticModel3]
         },
         'primary_key': 'id'}, 7, 3, None),
    ])
    def test_columns_from_pydantic(kwargs, expected_columns, expected_config_sets, error):
        if not error:
            columns, serialization_config = columns_from_pydantic(**kwargs)
            assert len(columns) == expected_columns
            if expected_config_sets > 1:
                assert isinstance(serialization_config, dict)
                assert len(serialization_config.keys()) == expected_config_sets
                for config_set in serialization_config:
                    assert len(serialization_config[config_set]) <= expected_columns
            else:
                assert isinstance(serialization_config, list)
                assert len(serialization_config) == expected_columns
        else:
            with pytest.raises(error):
                columns, serialization_config = columns_from_pydantic(**kwargs)
