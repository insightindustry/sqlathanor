# -*- coding: utf-8 -*-

"""
******************************************
tests.test_yaml_support
******************************************

Tests for :term:`YAML` serialization/de-serialization support.

"""
# pylint: disable=line-too-long

from collections import OrderedDict

import pytest
import datetime

import yaml
from yaml.error import MarkedYAMLError, YAMLError
from yaml.constructor import ConstructorError

from validator_collection import checkers

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_single_pk, instance_single_pk, model_complex_postgresql, instance_postgresql,\
    input_files, check_input_file

from sqlathanor._compat import json
from sqlathanor.errors import CSVStructureError, DeserializationError, \
    MaximumNestingExceededError, MaximumNestingExceededWarning, \
    SerializableAttributeError, InvalidFormatError, ValueSerializationError, \
    ExtraKeyError
from sqlathanor.utilities import are_dicts_equivalent

def replace_timedelta(value):
    try:
        result = yaml.dump(value)
    except TypeError:
        for key in value:
            if isinstance(value[key], datetime.timedelta):
                value[key] = value[key].total_seconds()

        result = yaml.dump(value)

    return result


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
def test_to_yaml(request,
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
                interim_dict = target._to_dict('yaml',
                                               max_nesting = max_nesting,
                                               current_nesting = current_nesting)
        else:
            interim_dict = target._to_dict('yaml',
                                           max_nesting = max_nesting,
                                           current_nesting = current_nesting)

    if not error and not warning:
        result = target.to_yaml(max_nesting = max_nesting,
                                current_nesting = current_nesting,
                                serialize_function = serialize_function)

        print('RESULT:')
        print(result)
        assert isinstance(result, str)

        deserialized_dict = yaml.safe_load(result)
        print('\nDESERIALIZED DICT:')
        print(deserialized_dict)

        assert isinstance(deserialized_dict, dict)

        assert are_dicts_equivalent(interim_dict, deserialized_dict) is True

    elif not warning:
        with pytest.raises(error):
            result = target.to_yaml(max_nesting = max_nesting,
                                    current_nesting = current_nesting,
                                    serialize_function = serialize_function)
    elif not error:
        with pytest.warns(warning):
            result = target.to_yaml(max_nesting = max_nesting,
                                    current_nesting = current_nesting,
                                    serialize_function = serialize_function)

        print('RESULT:')
        print(result)
        assert isinstance(result, str)

        deserialized_dict = yaml.safe_load(result)
        print('\nDESERIALIZED DICT:')
        print(deserialized_dict)

        assert isinstance(deserialized_dict, dict)

        assert are_dicts_equivalent(interim_dict, deserialized_dict) is True


@pytest.mark.parametrize('supports_serialization, hybrid_value, max_nesting, current_nesting, serialize_function, warning, error', [
    (False, None, 0, 0, None, MaximumNestingExceededWarning, None),

    (False, None, 0, 3, None, None, MaximumNestingExceededError),

    (True, 'test value', 0, 0, 'not-callable', None, ValueError),

    (True, 'test value', 0, 0, None, MaximumNestingExceededWarning, YAMLError),

    (True, [{ 'nested_key': 'test', 'nested_key2': 'test2' }], 0, 0, None, MaximumNestingExceededWarning, ConstructorError),
    (True, [{ 'nested_key': 'test', 'nested_key2': 'test2' }], 1, 0, None, None, None),

    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 1, 0, None, None, None),

    (True, { 'nested_key': {'second-nesting-key': 'test'}, 'nested_key2': 'test2' }, 0, 0, None, MaximumNestingExceededWarning, None),
    (True, { 'nested_key': {'second-nesting-key': {'third-nest': 3} }, 'nested_key2': 'test2' }, 0, 0, None, MaximumNestingExceededWarning, None),

    # Replace Timedelta
    (True, 'test value', 0, 0, replace_timedelta, MaximumNestingExceededWarning, None),

    (True, [{ 'nested_key': 'test', 'nested_key2': 'test2' }], 0, 0, replace_timedelta, MaximumNestingExceededWarning, None),
    (True, [{ 'nested_key': 'test', 'nested_key2': 'test2' }], 1, 0, replace_timedelta, None, None),

    (True, { 'nested_key': 'test', 'nested_key2': 'test2' }, 1, 0, replace_timedelta, None, None),

    (True, { 'nested_key': {'second-nesting-key': 'test'}, 'nested_key2': 'test2' }, 0, 0, replace_timedelta, MaximumNestingExceededWarning, None),
    (True, { 'nested_key': {'second-nesting-key': {'third-nest': 3} }, 'nested_key2': 'test2' }, 0, 0, replace_timedelta, MaximumNestingExceededWarning, None),


])
def test_dump_to_yaml(request,
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
                interim_dict = target._to_dict('yaml',
                                               max_nesting = max_nesting,
                                               current_nesting = current_nesting,
                                               is_dumping = True)
        else:
            interim_dict = target._to_dict('yaml',
                                           max_nesting = max_nesting,
                                           current_nesting = current_nesting,
                                           is_dumping = True)

    if not error and not warning:
        result = target.dump_to_yaml(max_nesting = max_nesting,
                                     current_nesting = current_nesting,
                                     serialize_function = serialize_function)

        print('RESULT:')
        print(result)
        assert isinstance(result, str)

        should_pass = False
        try:
            deserialized_dict = yaml.safe_load(result)
            print('\nDESERIALIZED DICT:')
            print(deserialized_dict)

            assert isinstance(deserialized_dict, dict)
            assert are_dicts_equivalent(interim_dict, deserialized_dict) is True

        except ConstructorError as raised_error:
            for key in interim_dict:
                if isinstance(interim_dict[key], datetime.timedelta):
                    should_pass = True

            if not should_pass:
                raise raised_error

    elif not warning:
        with pytest.raises(error):
            result = target.dump_to_yaml(max_nesting = max_nesting,
                                         current_nesting = current_nesting,
                                         serialize_function = serialize_function)
            print('THIS IS THE RESULT:')
            print(result)
    elif not error:
        with pytest.warns(warning):
            result = target.dump_to_yaml(max_nesting = max_nesting,
                                         current_nesting = current_nesting,
                                         serialize_function = serialize_function)

        print('RESULT:')
        print(result)
        assert isinstance(result, str)

        should_pass = False
        try:
            deserialized_dict = yaml.safe_load(result)
            print('\nDESERIALIZED DICT:')
            print(deserialized_dict)

            assert isinstance(deserialized_dict, dict)

            assert are_dicts_equivalent(interim_dict, deserialized_dict) is True
        except ConstructorError as raised_error:
            for key in interim_dict:
                if isinstance(interim_dict[key], datetime.timedelta):
                    should_pass = True

            if not should_pass:
                raise raised_error

@pytest.mark.parametrize('use_file, filename, hybrid_value, expected_name, extra_keys, error_on_extra_keys, drop_extra_keys, deserialize_function, error', [
    (False, None, 'test value', 'deserialized', None, True, False, None, None),
    (False, None, 123, 'deserialized', None, True, False, None, None),

    (False, None, 'test value', 'deserialized', { 'extra': 'test'}, True, False, None, ExtraKeyError),
    (False, None, 'test value', 'deserialized', { 'extra': 'test'}, False, False, None, None),
    (False, None, 'test value', 'deserialized', { 'extra': 'test'}, False, True, None, None),

    (False, None, 'test value', 'deserialized', None, True, False, 'not-a-callable', ValueError),

    (True, 'JSON/update_from_json1.json', 'test value', 'deserialized', None, True, False, None, None),
    (True, 'JSON/update_from_json2.json', 'test value', 'deserialized', None, True, False, None, None),
    (True, 'JSON/update_from_json3.json', 'test value', 'deserialized', None, True, False, None, DeserializationError),

])
def test_update_from_yaml(request,
                          model_complex_postgresql,
                          instance_postgresql,
                          input_files,
                          use_file,
                          filename,
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

    if isinstance(as_dict, OrderedDict):
        as_dict = dict(as_dict)

    as_dict['hybrid_value'] = hybrid_value

    if extra_keys:
        for key in extra_keys:
            as_dict[key] = extra_keys[key]

    if not use_file:
        input_data = yaml.dump(as_dict)
    else:
        input_data = check_input_file(input_files, filename)

    if not error:
        target.update_from_yaml(input_data,
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
            target.update_from_yaml(input_data,
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
def test_new_from_yaml(request,
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

    if isinstance(input_data, OrderedDict):
        input_data = dict(input_data)

    input_data['hybrid_value'] = hybrid_value

    if extra_keys:
        for key in extra_keys:
            input_data[key] = extra_keys[key]

    as_yaml = yaml.dump(input_data)

    if not error:
        result = target.new_from_yaml(as_yaml,
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
            result = target.new_from_yaml(as_yaml,
                                          deserialize_function = deserialize_function,
                                          error_on_extra_keys = error_on_extra_keys,
                                          drop_extra_keys = drop_extra_keys)
