# -*- coding: utf-8 -*-

"""
******************************************
tests.test_dict_support
******************************************

Tests for :ref:`dict <python:dict>` serialization/de-serialization support.

"""
# pylint: disable=line-too-long

import pytest

from validator_collection import checkers

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_single_pk, instance_single_pk, model_complex_postgresql, instance_postgresql

from sqlathanor.errors import CSVColumnError, DeserializationError, \
    MaximumNestingExceededError, MaximumNestingExceededWarning, \
    SerializableAttributeError, InvalidFormatError, ValueSerializationError
from sqlathanor.utilities import are_dicts_equivalent

@pytest.mark.parametrize('supports_serialization, hybrid_value, format, max_nesting, current_nesting, expected_result, warning, error', [
    (False, None, 'invalid', 0, 0, None, None, InvalidFormatError),
    (False, None, 'dict', 0, 0, None, None, SerializableAttributeError),
    (False, None, 'json', 0, 0, None, None, SerializableAttributeError),
    (False, None, 'yaml', 0, 0, None, None, SerializableAttributeError),
    (False, None, 'csv', 0, 0, None, None, SerializableAttributeError),

    (False, None, 'dict', 0, 3, None, None, MaximumNestingExceededError),
    (False, None, 'json', 0, 3, None, None, MaximumNestingExceededError),
    (False, None, 'yaml', 0, 3, None, None, MaximumNestingExceededError),
    (False, None, 'csv', 0, 3, None, None, MaximumNestingExceededError),

    (True, 'test value', 'dict', 0, 0, { 'id': 1, 'name': 'serialized', 'hybrid': 'test value' }, None, None),
    (True, 'test value', 'json', 0, 0, { 'id': 1, 'name': 'serialized', 'hybrid': 'test value' }, MaximumNestingExceededWarning, None),
    (True, 'test value', 'yaml', 0, 0, { 'id': 1, 'name': 'serialized', 'hybrid': 'test value' }, MaximumNestingExceededWarning, None),
    (True, 'test value', 'csv', 0, 0, { 'id': 1, 'name': 'serialized', 'smallint_column': 2, 'hybrid': 'test value' }, None, None),

    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'dict', 0, 0, { 'id': 1, 'name': 'serialized', 'hybrid': { 'nested_key': 'test', 'nested_key2': 'test2' } }, None, None),
    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'json', 0, 0, { 'id': 1, 'name': 'serialized', 'hybrid': { 'nested_key': 'test', 'nested_key2': 'test2' } }, MaximumNestingExceededWarning, None),
    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'yaml', 0, 0, { 'id': 1, 'name': 'serialized', 'hybrid': { 'nested_key': 'test', 'nested_key2': 'test2' } }, MaximumNestingExceededWarning, None),
    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'csv', 0, 0, { 'id': 1, 'name': 'serialized', 'smallint_column': 2 }, None, ValueSerializationError),

    (True, [{ 'nested_key': 'test', 'nested_key2': 'test2' }], 'dict', 1, 0, { 'id': 1, 'name': 'serialized', 'hybrid': [{ 'nested_key': 'test', 'nested_key2': 'test2' }] }, None, None),
    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'json', 1, 0, { 'id': 1, 'name': 'serialized', 'addresses': [], 'hybrid': { 'nested_key': 'test', 'nested_key2': 'test2' } }, None, None),
    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'yaml', 1, 0, { 'id': 1, 'name': 'serialized', 'addresses': [], 'hybrid': { 'nested_key': 'test', 'nested_key2': 'test2' } }, None, None),
    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'csv', 1, 0, { 'id': 1, 'name': 'serialized', 'smallint_column': 2, 'hybrid': { 'nested_key': 'test', 'nested_key2': 'test2' } }, None, ValueSerializationError),

    (True, { 'nested_key': {'second-nesting-key': 'test'}, 'nested_key2': 'test2' }, 'dict', 0, 0, { 'id': 1, 'name': 'serialized', 'hybrid': { 'nested_key': {'second-nesting-key': 'test'}, 'nested_key2': 'test2' } }, None, None),
    (True, { 'nested_key': {'second-nesting-key': {'third-nest': 3} }, 'nested_key2': 'test2' }, 'dict', 0, 0, { 'id': 1, 'name': 'serialized', 'hybrid': { 'nested_key': {'second-nesting-key': {'third-nest': 3} }, 'nested_key2': 'test2' } }, None, None),

])
def test__to_dict(request,
                  instance_single_pk,
                  instance_postgresql,
                  supports_serialization,
                  hybrid_value,
                  format,
                  max_nesting,
                  current_nesting,
                  expected_result,
                  warning,
                  error):
    if supports_serialization:
        target = instance_postgresql[0][0]
    else:
        target = instance_single_pk[0]

    target.hybrid = hybrid_value

    if not error and not warning:
        result = target._to_dict(format,
                                 max_nesting = max_nesting,
                                 current_nesting = current_nesting)

        assert isinstance(result, dict)
        print('RESULT:')
        print(result)
        print('\nEXPECTED:')
        print(expected_result)
        for key in result:
            assert key in expected_result
            assert expected_result[key] == result[key]
        for key in expected_result:
            assert key in result
            assert result[key] == expected_result[key]
        assert are_dicts_equivalent(result, expected_result) is True
    elif not warning:
        with pytest.raises(error):
            result = target._to_dict(format,
                                     max_nesting = max_nesting,
                                     current_nesting = current_nesting)
    elif not error:
        with pytest.warns(warning):
            result = target._to_dict(format,
                                     max_nesting = max_nesting,
                                     current_nesting = current_nesting)

        assert isinstance(result, dict)
        for key in result:
            assert key in expected_result
            assert expected_result[key] == result[key]
        for key in expected_result:
            assert key in result
            assert result[key] == expected_result[key]
        assert are_dicts_equivalent(result, expected_result) is True


@pytest.mark.parametrize('supports_serialization, hybrid_value, max_nesting, current_nesting, expected_result, warning, error', [
    (False, None, 0, 0, None, None, SerializableAttributeError),

    (False, None, 0, 3, None, None, MaximumNestingExceededError),

    (True, 'test value', 0, 0, { 'id': 1, 'name': 'serialized', 'hybrid': 'test value' }, None, None),

    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 0, 0, { 'id': 1, 'name': 'serialized', 'hybrid': { 'nested_key': 'test', 'nested_key2': 'test2' } }, None, None),

    (True, [{ 'nested_key': 'test', 'nested_key2': 'test2' }], 1, 0, { 'id': 1, 'name': 'serialized', 'hybrid': [{ 'nested_key': 'test', 'nested_key2': 'test2' }] }, None, None),

    (True, { 'nested_key': {'second-nesting-key': 'test'}, 'nested_key2': 'test2' }, 0, 0, { 'id': 1, 'name': 'serialized', 'hybrid': { 'nested_key': {'second-nesting-key': 'test'}, 'nested_key2': 'test2' } }, None, None),
    (True, { 'nested_key': {'second-nesting-key': {'third-nest': 3} }, 'nested_key2': 'test2' }, 0, 0, { 'id': 1, 'name': 'serialized', 'hybrid': { 'nested_key': {'second-nesting-key': {'third-nest': 3} }, 'nested_key2': 'test2' } }, None, None),

])
def test_to_dict(request,
                 instance_single_pk,
                 instance_postgresql,
                 supports_serialization,
                 hybrid_value,
                 max_nesting,
                 current_nesting,
                 expected_result,
                 warning,
                 error):
    if supports_serialization:
        target = instance_postgresql[0][0]
    else:
        target = instance_single_pk[0]

    target.hybrid = hybrid_value

    if not error and not warning:
        result = target.to_dict(max_nesting = max_nesting,
                                current_nesting = current_nesting)

        assert isinstance(result, dict)
        print('RESULT:')
        print(result)
        print('\nEXPECTED:')
        print(expected_result)
        for key in result:
            assert key in expected_result
            assert expected_result[key] == result[key]
        for key in expected_result:
            assert key in result
            assert result[key] == expected_result[key]
        assert are_dicts_equivalent(result, expected_result) is True
    elif not warning:
        with pytest.raises(error):
            result = target.to_dict(max_nesting = max_nesting,
                                    current_nesting = current_nesting)
    elif not error:
        with pytest.warns(warning):
            result = target.to_dict(max_nesting = max_nesting,
                                    current_nesting = current_nesting)

        assert isinstance(result, dict)
        for key in result:
            assert key in expected_result
            assert expected_result[key] == result[key]
        for key in expected_result:
            assert key in result
            assert result[key] == expected_result[key]
        assert are_dicts_equivalent(result, expected_result) is True
