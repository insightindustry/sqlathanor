# -*- coding: utf-8 -*-

"""
***********************************
tests.test_utilities
***********************************

Tests for the schema extensions written in :ref:`sqlathanor.utilities`.

"""

import pytest

from validator_collection import checkers
from validator_collection.errors import NotAnIterableError

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_complex_postgresql, instance_postgresql

from sqlathanor.utilities import bool_to_tuple, callable_to_dict, format_to_tuple, \
    get_class_type_key, raise_UnsupportedSerializationError, \
    raise_UnsupportedDeserializationError, iterable__to_dict, parse_yaml, parse_json
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

    def _to_dict(self, format, max_nesting = 0, current_nesting = 0):
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
