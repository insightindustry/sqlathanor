# -*- coding: utf-8 -*-

"""
******************************************
tests.test_issue87_nested_one_to_one
******************************************

Tests for Issue #87: deserialization support for 1:1 relationship.

"""
# pylint: disable=line-too-long

import pytest
import datetime

import simplejson
from validator_collection import checkers

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_single_pk, instance_single_pk, model_complex_postgresql, instance_postgresql,\
    input_files, check_input_file, model_nested_one_to_one, instance_nested_one_to_one

from sqlathanor._compat import json
from sqlathanor.errors import CSVStructureError, DeserializationError, \
    MaximumNestingExceededError, MaximumNestingExceededWarning, \
    SerializableAttributeError, InvalidFormatError, ValueSerializationError, \
    DeserializationError, ExtraKeyError
from sqlathanor.utilities import are_dicts_equivalent

"""
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
def test_update_from_json(request,
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

    as_dict['hybrid_value'] = hybrid_value

    if extra_keys:
        for key in extra_keys:
            as_dict[key] = extra_keys[key]

    dumped_data = json.dumps(as_dict)

    if not use_file:
        input_data = dumped_data
    else:
        input_data = check_input_file(input_files, filename)

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
"""

@pytest.mark.parametrize('use_nested_dict, nested_dict, error', [
    (False, None, None),
    (True, { 'id': 123, 'email': 'john@test.com' }, None),
    (True, [ {'id': 123, 'email': 'john@test.com' }, { 'id': 2, 'email': 'jane@test.com' }], AttributeError),

])
def test_new_from_json(request,
                       model_nested_one_to_one,
                       instance_nested_one_to_one,
                       use_nested_dict,
                       nested_dict,
                       error):
    target = model_nested_one_to_one[0]
    nested_target = model_nested_one_to_one[1]
    source = instance_nested_one_to_one[0][0]

    assert source.address is not None
    assert isinstance(source.address, nested_target) is True

    as_dict = source.to_dict(max_nesting = 5,
                             current_nesting = 0)

    if use_nested_dict:
        as_dict['address'] = nested_dict

    dumped_data = json.dumps(as_dict)

    as_json = dumped_data
    print(as_json)

    if not error:
        result = target.new_from_json(as_json)

        assert isinstance(result, target) is True
        assert getattr(result, 'name') == source.name
        assert getattr(result, 'id') == source.id
        if not use_nested_dict or nested_dict is not None:
            assert getattr(result, 'address') is not None
            assert isinstance(getattr(result, 'address'), nested_target) is True
        elif use_nested_dict and nested_dict is None:
            assert getattr(result, 'address') is None

    else:
        with pytest.raises(error):
            result = target.new_from_json(as_json)
