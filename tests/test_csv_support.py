# -*- coding: utf-8 -*-

"""
******************************************
tests.test_csv_support
******************************************

Tests for CSV serialization/de-serialization support.

"""

import pytest

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_complex_postgresql, instance_postgresql


@pytest.mark.parametrize('deserialize, serialize, expected_length', [
    (None, True, 4),
    (True, None, 5),
    (False, False, 6),
    (None, None, 0),
])
def test_get_csv_column_names(request,
                              instance_postgresql,
                              deserialize,
                              serialize,
                              expected_length):
    target = instance_postgresql[0][0]

    result = target.get_csv_column_names(deserialize = deserialize,
                                         serialize = serialize)

    assert len(result) == expected_length

    column_positions = []
    for index, column_name in enumerate(result):
        config = target.get_attribute_serialization_config(column_name)
        try:
            column_positions.append((column_name, index, config.csv_sequence))
        except AttributeError:
            pass

    for index, column in enumerate(column_positions):
        if index > 0:
            assert column[2] >= column_positions[index][2] or column[2] is None


@pytest.mark.parametrize('deserialize, serialize, delimiter, expected_result', [
    (None, True, '|', 'id|name|hybrid|smallint_column\n'),
    (None, True, ',', 'id,name,hybrid,smallint_column\n'),
    (None, True, None, 'id|name|hybrid|smallint_column\n'),
    (True, None, '|', 'id|name|password|hybrid|smallint_column\n'),
    (True, None, ',', 'id,name,password,hybrid,smallint_column\n'),
    (True, None, None, 'id|name|password|hybrid|smallint_column\n'),
    (None, None, None, '\n'),
])
def test_get_csv_header(request,
                        instance_postgresql,
                        deserialize,
                        serialize,
                        delimiter,
                        expected_result):
    target = instance_postgresql[0][0]

    if delimiter is not None:
        result = target.get_csv_header(deserialize = deserialize,
                                       serialize = serialize,
                                       delimiter = delimiter)
    else:
        result = target.get_csv_header(deserialize = deserialize,
                                       serialize = serialize)

    assert result == expected_result


@pytest.mark.parametrize('delimiter, wrap_all_strings, wrap_empty_values, wrapper_character, hybrid_value, expected_result', [
    ('|', False, False, "'", 1, '1|serialized|1|2\n'),
    ('|', True, False, "'", 1, "1|'serialized'|1|2\n"),
    ('|', False, True, "'", None, "1|serialized|'None'|2\n"),
    ('|', True, True, None, None, "1|'serialized'|'None'|2\n"),
    ('|', True, True, '!!', None, "1|!!serialized!!|!!None!!|2\n"),
    ('|', False, True, "'", 'test|value', "1|serialized|'test|value'|2\n"),
])
def test_get_csv_data(request,
                      instance_postgresql,
                      delimiter,
                      wrap_all_strings,
                      wrap_empty_values,
                      wrapper_character,
                      hybrid_value,
                      expected_result):
    target = instance_postgresql[0][0]

    target.hybrid = hybrid_value

    result = target.get_csv_data(delimiter = delimiter,
                                 wrap_all_strings = wrap_all_strings,
                                 wrap_empty_values = wrap_empty_values,
                                 wrapper_character = wrapper_character)

    assert result == expected_result


@pytest.mark.parametrize('include_header, delimiter, wrap_all_strings, wrap_empty_values, wrapper_character, hybrid_value, expected_result', [
    (False, '|', False, False, "'", 1, '1|serialized|1|2\n'),
    (False, '|', True, False, "'", 1, "1|'serialized'|1|2\n"),
    (False, '|', False, True, "'", None, "1|serialized|'None'|2\n"),
    (False, '|', True, True, None, None, "1|'serialized'|'None'|2\n"),
    (False, '|', True, True, '!!', None, "1|!!serialized!!|!!None!!|2\n"),
    (False, '|', False, True, "'", 'test|value', "1|serialized|'test|value'|2\n"),

    (True, '|', False, False, "'", 1, 'id|name|hybrid|smallint_column\n1|serialized|1|2\n'),
    (True, '|', True, False, "'", 1, "id|name|hybrid|smallint_column\n1|'serialized'|1|2\n"),
    (True, '|', False, True, "'", None, "id|name|hybrid|smallint_column\n1|serialized|'None'|2\n"),
    (True, '|', True, True, None, None, "id|name|hybrid|smallint_column\n1|'serialized'|'None'|2\n"),
    (True, '|', True, True, '!!', None, "id|name|hybrid|smallint_column\n1|!!serialized!!|!!None!!|2\n"),
    (True, '|', False, True, "'", 'test|value', "id|name|hybrid|smallint_column\n1|serialized|'test|value'|2\n"),

])
def test_to_csv(request,
                instance_postgresql,
                include_header,
                delimiter,
                wrap_all_strings,
                wrap_empty_values,
                wrapper_character,
                hybrid_value,
                expected_result):
    target = instance_postgresql[0][0]

    target.hybrid = hybrid_value

    result = target.to_csv(include_header = include_header,
                           delimiter = delimiter,
                           wrap_all_strings = wrap_all_strings,
                           wrap_empty_values = wrap_empty_values,
                           wrapper_character = wrapper_character)

    assert result == expected_result
