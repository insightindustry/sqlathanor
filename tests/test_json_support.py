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
from sqlathanor.errors import CSVColumnError, DeserializationError, \
    MaximumNestingExceededError, MaximumNestingExceededWarning, \
    SerializableAttributeError, InvalidFormatError, ValueSerializationError
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
