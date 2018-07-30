# -*- coding: utf-8 -*-

"""
******************************************
tests.test_json_support
******************************************

Tests for :ref:`JSON` serialization/de-serialization support.

"""
# pylint: disable=line-too-long

import pytest

from validator_collection import checkers

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_single_pk, instance_single_pk, model_complex_postgresql, instance_postgresql

from sqlathanor._compat import json
from sqlathanor.errors import CSVStructureError, DeserializationError, \
    MaximumNestingExceededError, MaximumNestingExceededWarning, \
    SerializableAttributeError, InvalidFormatError, ValueSerializationError, \
    DeserializationError, ExtraKeyError
from sqlathanor.utilities import are_dicts_equivalent

@pytest.mark.parametrize('supports_serialization, hybrid_value, max_nesting, current_nesting, serialize_function, warning, error', [
    (False, None, 0, 0, None, None, SerializableAttributeError),

    (False, None, 0, 3, None, None, MaximumNestingExceededError),

    (True, 'test value', 0, 0, 'not-callable', None, ValueError),

    (True, 'test value', 0, 0, None, MaximumNestingExceededWarning, None),

    (True, [{ 'nested_key': 'test', 'nested_key2': 'test2' }], 0, 0, None, MaximumNestingExceededWarning, None),
    (True, [{ 'nested_key': 'test', 'nested_key2': 'test2' }], 1, 0, None, None, None),

    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 1, 0, None, None, None),

    (True, { 'nested_key': {'second-nesting-key': 'test'}, 'nested_key2': 'test2' }, 0, 0, None, MaximumNestingExceededWarning, None),
    (True, { 'nested_key': {'second-nesting-key': {'third-nest': 3} }, 'nested_key2': 'test2' }, 0, 0, None, MaximumNestingExceededWarning, None),

])
def test_to_json(request,
                 instance_single_pk,
                 instance_postgresql,
                 supports_serialization,
                 hybrid_value,
                 max_nesting,
                 current_nesting,
                 serialize_function,
                 warning,
                 error):
    if supports_serialization:
        target = instance_postgresql[0][0]
    else:
        target = instance_single_pk[0]

    target.hybrid = hybrid_value

    if not error:
        if warning:
            with pytest.warns(warning):
                interim_dict = target._to_dict('json',
                                               max_nesting = max_nesting,
                                               current_nesting = current_nesting)
        else:
            interim_dict = target._to_dict('json',
                                           max_nesting = max_nesting,
                                           current_nesting = current_nesting)

    if not error and not warning:
        result = target.to_json(max_nesting = max_nesting,
                                current_nesting = current_nesting,
                                serialize_function = serialize_function)

        print('RESULT:')
        print(result)
        assert isinstance(result, str)

        deserialized_dict = json.loads(result)
        print('\nDESERIALIZED DICT:')
        print(deserialized_dict)

        assert isinstance(deserialized_dict, dict)

        assert are_dicts_equivalent(interim_dict, deserialized_dict) is True
    elif not warning:
        with pytest.raises(error):
            result = target.to_json(max_nesting = max_nesting,
                                    current_nesting = current_nesting,
                                    serialize_function = serialize_function)
    elif not error:
        with pytest.warns(warning):
            result = target.to_json(max_nesting = max_nesting,
                                    current_nesting = current_nesting,
                                    serialize_function = serialize_function)

        print('RESULT:')
        print(result)
        assert isinstance(result, str)

        deserialized_dict = json.loads(result)
        print('\nDESERIALIZED DICT:')
        print(deserialized_dict)

        assert isinstance(deserialized_dict, dict)

        assert are_dicts_equivalent(interim_dict, deserialized_dict) is True


@pytest.mark.parametrize('supports_serialization, hybrid_value, max_nesting, current_nesting, serialize_function, warning, error', [
    (False, None, 0, 0, None, None, None),

    (False, None, 0, 3, None, None, MaximumNestingExceededError),

    (True, 'test value', 0, 0, 'not-callable', None, ValueError),

    (True, 'test value', 0, 0, None, MaximumNestingExceededWarning, None),

    (True, [{ 'nested_key': 'test', 'nested_key2': 'test2' }], 0, 0, None, MaximumNestingExceededWarning, None),
    (True, [{ 'nested_key': 'test', 'nested_key2': 'test2' }], 1, 0, None, None, None),

    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 1, 0, None, None, None),

    (True, { 'nested_key': {'second-nesting-key': 'test'}, 'nested_key2': 'test2' }, 0, 0, None, MaximumNestingExceededWarning, None),
    (True, { 'nested_key': {'second-nesting-key': {'third-nest': 3} }, 'nested_key2': 'test2' }, 0, 0, None, MaximumNestingExceededWarning, None),

])
def test_dump_to_json(request,
                      instance_single_pk,
                      instance_postgresql,
                      supports_serialization,
                      hybrid_value,
                      max_nesting,
                      current_nesting,
                      serialize_function,
                      warning,
                      error):
    if supports_serialization:
        target = instance_postgresql[0][0]
    else:
        target = instance_single_pk[0]

    target.hybrid = hybrid_value

    if not error:
        if warning:
            with pytest.warns(warning):
                interim_dict = target._to_dict('json',
                                               max_nesting = max_nesting,
                                               current_nesting = current_nesting,
                                               is_dumping = True)
        else:
            interim_dict = target._to_dict('json',
                                           max_nesting = max_nesting,
                                           current_nesting = current_nesting,
                                           is_dumping = True)

    if not error and not warning:
        result = target.dump_to_json(max_nesting = max_nesting,
                                     current_nesting = current_nesting,
                                     serialize_function = serialize_function)

        print('RESULT:')
        print(result)
        assert isinstance(result, str)

        deserialized_dict = json.loads(result)
        print('\nDESERIALIZED DICT:')
        print(deserialized_dict)

        assert isinstance(deserialized_dict, dict)

        assert are_dicts_equivalent(interim_dict, deserialized_dict) is True
    elif not warning:
        with pytest.raises(error):
            result = target.dump_to_json(max_nesting = max_nesting,
                                         current_nesting = current_nesting,
                                         serialize_function = serialize_function)
    elif not error:
        with pytest.warns(warning):
            result = target.dump_to_json(max_nesting = max_nesting,
                                         current_nesting = current_nesting,
                                         serialize_function = serialize_function)

        print('RESULT:')
        print(result)
        assert isinstance(result, str)

        deserialized_dict = json.loads(result)
        print('\nDESERIALIZED DICT:')
        print(deserialized_dict)

        assert isinstance(deserialized_dict, dict)

        assert are_dicts_equivalent(interim_dict, deserialized_dict) is True


@pytest.mark.parametrize('hybrid_value, expected_name, extra_keys, error_on_extra_keys, drop_extra_keys, deserialize_function, error', [
    ('test value', 'deserialized', None, True, False, None, None),
    (123, 'deserialized', None, True, False, None, None),

    ('test value', 'deserialized', { 'extra': 'test'}, True, False, None, ExtraKeyError),
    ('test value', 'deserialized', { 'extra': 'test'}, False, False, None, None),
    ('test value', 'deserialized', { 'extra': 'test'}, False, True, None, None),

    ('test value', 'deserialized', None, True, False, 'not-a-callable', ValueError),

])
def test_update_from_json(request,
                          model_complex_postgresql,
                          instance_postgresql,
                          hybrid_value,
                          expected_name,
                          extra_keys,
                          error_on_extra_keys,
                          drop_extra_keys,
                          deserialize_function,
                          error):
    model = model_complex_postgresql[0]
    target = instance_postgresql[0][0]

    as_dict = target.to_dict(max_nesting = 5,
                             current_nesting = 0)

    as_dict['hybrid'] = hybrid_value

    if extra_keys:
        for key in extra_keys:
            as_dict[key] = extra_keys[key]

    input_data = json.dumps(as_dict)

    if not error:
        target.update_from_json(input_data,
                                deserialize_function = deserialize_function,
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
            target.update_from_json(input_data,
                                    deserialize_function = deserialize_function,
                                    error_on_extra_keys = error_on_extra_keys,
                                    drop_extra_keys = drop_extra_keys)


@pytest.mark.parametrize('hybrid_value, expected_name, extra_keys, error_on_extra_keys, drop_extra_keys, deserialize_function, error', [
    ('test value', 'deserialized', None, True, False, None, None),
    (123, 'deserialized', None, True, False, None, None),

    ('test value', 'deserialized', { 'extra': 'test'}, True, False, None, ExtraKeyError),
    ('test value', 'deserialized', { 'extra': 'test'}, False, False, None, TypeError),
    ('test value', 'deserialized', { 'extra': 'test'}, False, True, None, None),

    ('test value', 'deserialized', None, True, False, 'not-a-callable', ValueError),

])
def test_new_from_json(request,
                       model_complex_postgresql,
                       instance_postgresql,
                       hybrid_value,
                       expected_name,
                       extra_keys,
                       error_on_extra_keys,
                       drop_extra_keys,
                       deserialize_function,
                       error):
    target = model_complex_postgresql[0]
    source = instance_postgresql[0][0]

    input_data = source.to_dict(max_nesting = 5,
                                current_nesting = 0)

    input_data['hybrid'] = hybrid_value

    if extra_keys:
        for key in extra_keys:
            input_data[key] = extra_keys[key]

    as_json = json.dumps(input_data)

    if not error:
        result = target.new_from_json(as_json,
                                      deserialize_function = deserialize_function,
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
            result = target.new_from_json(as_json,
                                          deserialize_function = deserialize_function,
                                          error_on_extra_keys = error_on_extra_keys,
                                          drop_extra_keys = drop_extra_keys)
