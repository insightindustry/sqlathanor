# -*- coding: utf-8 -*-

"""
******************************************
tests.test_dict_support
******************************************

Tests for :ref:`dict <python:dict>` serialization/de-serialization support.

"""
# pylint: disable=line-too-long,protected-access

import pytest

from validator_collection import checkers

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_single_pk, instance_single_pk, model_complex_postgresql, instance_postgresql

from sqlathanor.errors import CSVColumnError, DeserializationError, \
    MaximumNestingExceededError, MaximumNestingExceededWarning, \
    SerializableAttributeError, InvalidFormatError, ValueSerializationError, \
    ValueDeserializationError, DeserializableAttributeError, DeserializationError, \
    ExtraKeyError
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


@pytest.mark.parametrize('supports_serialization, hybrid_value, format, max_nesting, current_nesting, expected_result, extra_keys, error_on_extra_keys, drop_extra_keys, warning, error', [
    (False, None, 'invalid', 0, 0, None, None, True, False, None, InvalidFormatError),
    (False, None, 'dict', 0, 0, None, None, True, False, None, (SerializableAttributeError, DeserializableAttributeError)),
    (False, None, 'json', 0, 0, None, None, True, False, None, (SerializableAttributeError, DeserializableAttributeError)),
    (False, None, 'yaml', 0, 0, None, None, True, False, None, (SerializableAttributeError, DeserializableAttributeError)),
    (False, None, 'csv', 0, 0, None, None, True, False, None, (SerializableAttributeError, DeserializableAttributeError)),

    (True, 'test value', 'dict', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value' }, None, True, False, None, None),
    (True, 'test value', 'json', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value' }, None, True, False, MaximumNestingExceededWarning, None),
    (True, 'test value', 'yaml', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value' }, None, True, False, MaximumNestingExceededWarning, None),
    (True, 'test value', 'csv', 0, 0, { 'id': 1, 'name': 'deserialized', 'smallint_column': 2, 'hybrid': 'test value' }, None, True, False, None, None),

    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'dict', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': { 'nested_key': 'test', 'nested_key2': 'test2' } }, None, True, False, None, None),
    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'json', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': { 'nested_key': 'test', 'nested_key2': 'test2' } }, None, True, False, MaximumNestingExceededWarning, None),
    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'yaml', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': { 'nested_key': 'test', 'nested_key2': 'test2' } }, None, True, False, MaximumNestingExceededWarning, None),
    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'csv', 0, 0, { 'id': 1, 'name': 'deserialized', 'smallint_column': 2 }, None, True, False, None, ValueSerializationError),

    (True, [{ 'nested_key': 'test', 'nested_key2': 'test2' }], 'dict', 1, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': [{ 'nested_key': 'test', 'nested_key2': 'test2' }] }, None, True, False, None, None),
    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'json', 1, 0, { 'id': 1, 'name': 'deserialized', 'addresses': [], 'hybrid': { 'nested_key': 'test', 'nested_key2': 'test2' } }, None, True, False, None, None),
    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'yaml', 1, 0, { 'id': 1, 'name': 'deserialized', 'addresses': [], 'hybrid': { 'nested_key': 'test', 'nested_key2': 'test2' } }, None, True, False, None, None),
    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'csv', 1, 0, { 'id': 1, 'name': 'deserialized', 'smallint_column': 2, 'hybrid': { 'nested_key': 'test', 'nested_key2': 'test2' } }, None, True, False, None, ValueSerializationError),

    (True, { 'nested_key': {'second-nesting-key': 'test'}, 'nested_key2': 'test2' }, 'dict', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': { 'nested_key': {'second-nesting-key': 'test'}, 'nested_key2': 'test2' } }, None, True, False, None, None),
    (True, { 'nested_key': {'second-nesting-key': {'third-nest': 3} }, 'nested_key2': 'test2' }, 'dict', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': { 'nested_key': {'second-nesting-key': {'third-nest': 3} }, 'nested_key2': 'test2' } }, None, True, False, None, None),

    # Error on Extra Keys
    (True, 'test value', 'dict', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value' }, { 'extra': 'test' }, True, False, None, ExtraKeyError),
    (True, 'test value', 'json', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value' }, { 'extra': 'test' }, True, False, MaximumNestingExceededWarning, ExtraKeyError),
    (True, 'test value', 'yaml', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value' }, { 'extra': 'test' }, True, False, MaximumNestingExceededWarning, ExtraKeyError),
    (True, 'test value', 'csv', 0, 0, { 'id': 1, 'name': 'deserialized', 'smallint_column': 2, 'hybrid': 'test value' }, { 'extra': 'test' }, True, False, None, ExtraKeyError),

    # Include Extra Keys in result
    (True, 'test value', 'dict', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value', 'extra': 'test' }, { 'extra': 'test' }, False, False, None, None),
    (True, 'test value', 'json', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value', 'extra': 'test' }, { 'extra': 'test' }, False, False, MaximumNestingExceededWarning, None),
    (True, 'test value', 'yaml', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value', 'extra': 'test' }, { 'extra': 'test' }, False, False, MaximumNestingExceededWarning, None),
    (True, 'test value', 'csv', 0, 0, { 'id': 1, 'name': 'deserialized', 'smallint_column': 2, 'hybrid': 'test value', 'extra': 'test' }, { 'extra': 'test' }, False, False, None, None),

    # Exclude Extra Keys from result
    (True, 'test value', 'dict', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value', }, { 'extra': 'test' }, False, True, None, None),
    (True, 'test value', 'json', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value', }, { 'extra': 'test' }, False, True, MaximumNestingExceededWarning, None),
    (True, 'test value', 'yaml', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value', }, { 'extra': 'test' }, False, True, MaximumNestingExceededWarning, None),
    (True, 'test value', 'csv', 0, 0, { 'id': 1, 'name': 'deserialized', 'smallint_column': 2, 'hybrid': 'test value', }, { 'extra': 'test' }, False, True, None, None),

])
def test_model__parse_dict(request,
                           model_single_pk,
                           model_complex_postgresql,
                           instance_single_pk,
                           instance_postgresql,
                           supports_serialization,
                           hybrid_value,
                           format,
                           max_nesting,
                           current_nesting,
                           extra_keys,
                           error_on_extra_keys,
                           drop_extra_keys,
                           expected_result,
                           warning,
                           error):
    if supports_serialization:
        target = model_complex_postgresql[0]
        source = instance_postgresql[0][0]
    else:
        target = model_single_pk[0]
        source = instance_single_pk[0]

    target.hybrid = hybrid_value

    if not error and not warning:
        input_data = source._to_dict(format,
                                     max_nesting = max_nesting,
                                     current_nesting = current_nesting)
        if extra_keys:
            for key in extra_keys:
                input_data[key] = extra_keys[key]

        result = target._parse_dict(input_data,
                                    format,
                                    error_on_extra_keys = error_on_extra_keys,
                                    drop_extra_keys = drop_extra_keys)

        if not error_on_extra_keys and drop_extra_keys:
            for key in extra_keys:
                assert key not in result
        elif not error_on_extra_keys and not drop_extra_keys:
            for key in extra_keys:
                assert key in result

        assert are_dicts_equivalent(result, expected_result) is True
    elif not warning:
        with pytest.raises(error):
            input_data = source._to_dict(format,
                                         max_nesting = max_nesting,
                                         current_nesting = current_nesting)
            if extra_keys:
                for key in extra_keys:
                    input_data[key] = extra_keys[key]

            result = target._parse_dict(input_data,
                                        format,
                                        error_on_extra_keys = error_on_extra_keys,
                                        drop_extra_keys = drop_extra_keys)
    elif not error:
        with pytest.warns(warning):
            input_data = source._to_dict(format,
                                         max_nesting = max_nesting,
                                         current_nesting = current_nesting)
            if extra_keys:
                for key in extra_keys:
                    input_data[key] = extra_keys[key]

            result = target._parse_dict(input_data,
                                        format,
                                        error_on_extra_keys = error_on_extra_keys,
                                        drop_extra_keys = drop_extra_keys)

        assert isinstance(result, dict)
        for key in result:
            assert key in expected_result
            assert expected_result[key] == result[key]
        for key in expected_result:
            assert key in result
            assert result[key] == expected_result[key]

        if not error_on_extra_keys and drop_extra_keys:
            for key in extra_keys:
                assert key not in result
        elif not error_on_extra_keys and not drop_extra_keys:
            for key in extra_keys:
                assert key in result

        assert are_dicts_equivalent(result, expected_result) is True


@pytest.mark.parametrize('supports_serialization, hybrid_value, format, max_nesting, current_nesting, expected_result, extra_keys, error_on_extra_keys, drop_extra_keys, warning, error', [
    (False, None, 'invalid', 0, 0, None, None, True, False, None, InvalidFormatError),
    (False, None, 'dict', 0, 0, None, None, True, False, None, (SerializableAttributeError, DeserializableAttributeError)),
    (False, None, 'json', 0, 0, None, None, True, False, None, (SerializableAttributeError, DeserializableAttributeError)),
    (False, None, 'yaml', 0, 0, None, None, True, False, None, (SerializableAttributeError, DeserializableAttributeError)),
    (False, None, 'csv', 0, 0, None, None, True, False, None, (SerializableAttributeError, DeserializableAttributeError)),

    (True, 'test value', 'dict', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value' }, None, True, False, None, None),
    (True, 'test value', 'json', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value' }, None, True, False, MaximumNestingExceededWarning, None),
    (True, 'test value', 'yaml', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value' }, None, True, False, MaximumNestingExceededWarning, None),
    (True, 'test value', 'csv', 0, 0, { 'id': 1, 'name': 'deserialized', 'smallint_column': 2, 'hybrid': 'test value' }, None, True, False, None, None),

    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'dict', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': { 'nested_key': 'test', 'nested_key2': 'test2' } }, None, True, False, None, None),
    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'json', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': { 'nested_key': 'test', 'nested_key2': 'test2' } }, None, True, False, MaximumNestingExceededWarning, None),
    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'yaml', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': { 'nested_key': 'test', 'nested_key2': 'test2' } }, None, True, False, MaximumNestingExceededWarning, None),
    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'csv', 0, 0, { 'id': 1, 'name': 'deserialized', 'smallint_column': 2 }, None, True, False, None, ValueSerializationError),

    (True, [{ 'nested_key': 'test', 'nested_key2': 'test2' }], 'dict', 1, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': [{ 'nested_key': 'test', 'nested_key2': 'test2' }] }, None, True, False, None, None),
    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'json', 1, 0, { 'id': 1, 'name': 'deserialized', 'addresses': [], 'hybrid': { 'nested_key': 'test', 'nested_key2': 'test2' } }, None, True, False, None, None),
    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'yaml', 1, 0, { 'id': 1, 'name': 'deserialized', 'addresses': [], 'hybrid': { 'nested_key': 'test', 'nested_key2': 'test2' } }, None, True, False, None, None),
    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 'csv', 1, 0, { 'id': 1, 'name': 'deserialized', 'smallint_column': 2, 'hybrid': { 'nested_key': 'test', 'nested_key2': 'test2' } }, None, True, False, None, ValueSerializationError),

    (True, { 'nested_key': {'second-nesting-key': 'test'}, 'nested_key2': 'test2' }, 'dict', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': { 'nested_key': {'second-nesting-key': 'test'}, 'nested_key2': 'test2' } }, None, True, False, None, None),
    (True, { 'nested_key': {'second-nesting-key': {'third-nest': 3} }, 'nested_key2': 'test2' }, 'dict', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': { 'nested_key': {'second-nesting-key': {'third-nest': 3} }, 'nested_key2': 'test2' } }, None, True, False, None, None),

    # Error on Extra Keys
    (True, 'test value', 'dict', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value' }, { 'extra': 'test' }, True, False, None, ExtraKeyError),
    (True, 'test value', 'json', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value' }, { 'extra': 'test' }, True, False, MaximumNestingExceededWarning, ExtraKeyError),
    (True, 'test value', 'yaml', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value' }, { 'extra': 'test' }, True, False, MaximumNestingExceededWarning, ExtraKeyError),
    (True, 'test value', 'csv', 0, 0, { 'id': 1, 'name': 'deserialized', 'smallint_column': 2, 'hybrid': 'test value' }, { 'extra': 'test' }, True, False, None, ExtraKeyError),

    # Include Extra Keys in result
    (True, 'test value', 'dict', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value', 'extra': 'test' }, { 'extra': 'test' }, False, False, None, None),
    (True, 'test value', 'json', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value', 'extra': 'test' }, { 'extra': 'test' }, False, False, MaximumNestingExceededWarning, None),
    (True, 'test value', 'yaml', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value', 'extra': 'test' }, { 'extra': 'test' }, False, False, MaximumNestingExceededWarning, None),
    (True, 'test value', 'csv', 0, 0, { 'id': 1, 'name': 'deserialized', 'smallint_column': 2, 'hybrid': 'test value', 'extra': 'test' }, { 'extra': 'test' }, False, False, None, None),

    # Exclude Extra Keys from result
    (True, 'test value', 'dict', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value', }, { 'extra': 'test' }, False, True, None, None),
    (True, 'test value', 'json', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value', }, { 'extra': 'test' }, False, True, MaximumNestingExceededWarning, None),
    (True, 'test value', 'yaml', 0, 0, { 'id': 1, 'name': 'deserialized', 'hybrid': 'test value', }, { 'extra': 'test' }, False, True, MaximumNestingExceededWarning, None),
    (True, 'test value', 'csv', 0, 0, { 'id': 1, 'name': 'deserialized', 'smallint_column': 2, 'hybrid': 'test value', }, { 'extra': 'test' }, False, True, None, None),

])
def test_instance__parse_dict(request,
                              instance_single_pk,
                              instance_postgresql,
                              supports_serialization,
                              hybrid_value,
                              format,
                              max_nesting,
                              current_nesting,
                              extra_keys,
                              error_on_extra_keys,
                              drop_extra_keys,
                              expected_result,
                              warning,
                              error):
    if supports_serialization:
        target = instance_postgresql[0][0]
    else:
        target = instance_single_pk[0]

    target.hybrid = hybrid_value

    if not error and not warning:
        input_data = target._to_dict(format,
                                     max_nesting = max_nesting,
                                     current_nesting = current_nesting)
        if extra_keys:
            for key in extra_keys:
                input_data[key] = extra_keys[key]

        result = target._parse_dict(input_data,
                                    format,
                                    error_on_extra_keys = error_on_extra_keys,
                                    drop_extra_keys = drop_extra_keys)

        if not error_on_extra_keys and drop_extra_keys:
            for key in extra_keys:
                assert key not in result
        elif not error_on_extra_keys and not drop_extra_keys:
            for key in extra_keys:
                assert key in result

        assert are_dicts_equivalent(result, expected_result) is True
    elif not warning:
        with pytest.raises(error):
            input_data = target._to_dict(format,
                                         max_nesting = max_nesting,
                                         current_nesting = current_nesting)
            if extra_keys:
                for key in extra_keys:
                    input_data[key] = extra_keys[key]

            result = target._parse_dict(input_data,
                                        format,
                                        error_on_extra_keys = error_on_extra_keys,
                                        drop_extra_keys = drop_extra_keys)
    elif not error:
        with pytest.warns(warning):
            input_data = target._to_dict(format,
                                         max_nesting = max_nesting,
                                         current_nesting = current_nesting)
            if extra_keys:
                for key in extra_keys:
                    input_data[key] = extra_keys[key]

            result = target._parse_dict(input_data,
                                        format,
                                        error_on_extra_keys = error_on_extra_keys,
                                        drop_extra_keys = drop_extra_keys)

        assert isinstance(result, dict)
        for key in result:
            assert key in expected_result
            assert expected_result[key] == result[key]
        for key in expected_result:
            assert key in result
            assert result[key] == expected_result[key]

        if not error_on_extra_keys and drop_extra_keys:
            for key in extra_keys:
                assert key not in result
        elif not error_on_extra_keys and not drop_extra_keys:
            for key in extra_keys:
                assert key in result

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


@pytest.mark.parametrize('hybrid_value, expected_name, extra_keys, error_on_extra_keys, drop_extra_keys, error', [
    ('test value', 'deserialized', None, True, False, None),
    (123, 'deserialized', None, True, False, None),

    ('test value', 'deserialized', { 'extra': 'test'}, True, False, ExtraKeyError),
    ('test value', 'deserialized', { 'extra': 'test'}, False, False, None),
    ('test value', 'deserialized', { 'extra': 'test'}, False, True, None),

])
def test_update_from_dict(request,
                          model_complex_postgresql,
                          instance_postgresql,
                          hybrid_value,
                          expected_name,
                          extra_keys,
                          error_on_extra_keys,
                          drop_extra_keys,
                          error):
    model = model_complex_postgresql[0]
    target = instance_postgresql[0][0]

    input_data = target.to_dict(max_nesting = 5,
                                current_nesting = 0)

    input_data['hybrid'] = hybrid_value

    if extra_keys:
        for key in extra_keys:
            input_data[key] = extra_keys[key]

    if not error:
        target.update_from_dict(input_data,
                                error_on_extra_keys = error_on_extra_keys,
                                drop_extra_keys = drop_extra_keys)

        assert isinstance(target, model)
        assert getattr(target, 'name') == expected_name
        assert getattr(target, 'hybrid') == hybrid_value
        assert getattr(target, 'id') == target.id

        if extra_keys and not error_on_extra_keys and not drop_extra_keys:
            for key in extra_keys:
                assert hasattr(target, key) is True
                assert getattr(target, key) == extra_keys[key]

    else:
        with pytest.raises(error):
            target.update_from_dict(input_data,
                                    error_on_extra_keys = error_on_extra_keys,
                                    drop_extra_keys = drop_extra_keys)


@pytest.mark.parametrize('hybrid_value, expected_name, extra_keys, error_on_extra_keys, drop_extra_keys, error', [
    ('test value', 'deserialized', None, True, False, None),
    (123, 'deserialized', None, True, False, None),

    ('test value', 'deserialized', { 'extra': 'test'}, True, False, ExtraKeyError),
    ('test value', 'deserialized', { 'extra': 'test'}, False, False, TypeError),
    ('test value', 'deserialized', { 'extra': 'test'}, False, True, None),

])
def test_new_from_dict(request,
                       model_complex_postgresql,
                       instance_postgresql,
                       hybrid_value,
                       expected_name,
                       extra_keys,
                       error_on_extra_keys,
                       drop_extra_keys,
                       error):
    target = model_complex_postgresql[0]
    source = instance_postgresql[0][0]

    input_data = source.to_dict(max_nesting = 5,
                                current_nesting = 0)

    input_data['hybrid'] = hybrid_value

    if extra_keys:
        for key in extra_keys:
            input_data[key] = extra_keys[key]

    if not error:
        result = target.new_from_dict(input_data,
                                      error_on_extra_keys = error_on_extra_keys,
                                      drop_extra_keys = drop_extra_keys)

        assert isinstance(result, target)
        assert getattr(result, 'name') == expected_name
        assert getattr(result, 'hybrid') == hybrid_value
        assert getattr(result, 'id') == source.id

        if extra_keys and not error_on_extra_keys and not drop_extra_keys:
            for key in extra_keys:
                assert hasattr(result, key) is True
                assert getattr(result, key) == extra_keys[key]

    else:
        with pytest.raises(error):
            result = target.new_from_dict(input_data,
                                          error_on_extra_keys = error_on_extra_keys,
                                          drop_extra_keys = drop_extra_keys)
