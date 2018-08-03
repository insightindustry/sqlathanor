# -*- coding: utf-8 -*-

"""
***********************************
tests.test_utilities
***********************************

Tests for the schema extensions written in :ref:`sqlathanor.utilities`.

"""

import pytest
import sqlalchemy

from validator_collection import checkers
from validator_collection.errors import NotAnIterableError

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_complex_postgresql, instance_postgresql

from sqlathanor.utilities import bool_to_tuple, callable_to_dict, format_to_tuple, \
    get_class_type_key, raise_UnsupportedSerializationError, \
    raise_UnsupportedDeserializationError, iterable__to_dict, parse_yaml, parse_json, \
    get_attribute_names, is_an_attribute
from sqlathanor.errors import InvalidFormatError, UnsupportedSerializationError, \
    UnsupportedDeserializationError, MaximumNestingExceededError, \
    MaximumNestingExceededWarning, DeserializationError



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

    def _to_dict(self, format, max_nesting = 0, current_nesting = 0, is_dumping = False):
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

])
def test_parse_json(input_value,
                    deserialize_function,
                    expected_result,
                    error):
    if not error:
        result = parse_json(input_value,
                            deserialize_function = deserialize_function)

        assert isinstance(result, dict)
        assert checkers.are_dicts_equivalent(result, expected_result)
    else:
        with pytest.raises(error):
            result = parse_json(input_value)


@pytest.mark.parametrize('input_value, deserialize_function, expected_result, error', [
    ('{"test": 123, "second_test": "this is a test"}', None, { 'test': 123, 'second_test': 'this is a test' }, None),

    (None, None, None, DeserializationError),
    (None, 'not-callable', None, ValueError),

])
def test_parse_yaml(input_value,
                    deserialize_function,
                    expected_result,
                    error):
    if not error:
        result = parse_yaml(input_value,
                            deserialize_function = deserialize_function)

        assert isinstance(result, dict)
        assert checkers.are_dicts_equivalent(result, expected_result)
    else:
        with pytest.raises(error):
            result = parse_yaml(input_value)


@pytest.mark.parametrize('use_instance, include_callable, include_nested, include_private, include_special, include_utilities, expected_result', [
    (False, False, False, False, False, False, 7),
    (False, False, False, False, False, True, 9),
    (False, False, False, True, False, False, 8),
    (False, False, False, True, False, True, 11),
    (False, False, True, False, False, False, 9),
    (False, False, True, True, False, False, 10),
    (False, False, True, True, False, True, 14),
    (False, True, False, False, False, False, 37),
    (False, True, True, False, False, False, 39),
    (False, True, True, True, False, False, 52),
    (False, True, True, True, False, True, 56),

    (True, False, False, False, False, False, 8),
    (True, False, False, False, False, True, 10),
    (True, False, False, True, False, False, 9),
    (True, False, False, True, False, True, (12, 13)),
    (True, False, True, False, False, False, 9),
    (True, False, True, True, False, False, 10),
    (True, False, True, True, False, True, (14, 15)),
    (True, True, False, False, False, False, 38),
    (True, True, True, False, False, False, 39),
    (True, True, True, True, False, False, 52),
    (True, True, True, True, False, True, 57),

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
