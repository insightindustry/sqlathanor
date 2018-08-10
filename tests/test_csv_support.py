# -*- coding: utf-8 -*-

"""
******************************************
tests.test_csv_support
******************************************

Tests for CSV serialization/de-serialization support.

"""

import pytest

from validator_collection import checkers

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_complex_postgresql, instance_postgresql, input_files, check_input_file

from sqlathanor.errors import CSVStructureError, DeserializationError
from sqlathanor.utilities import get_attribute_names

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
    print(result)

    column_positions = []
    for index, column_name in enumerate(result):
        config = target.get_attribute_serialization_config(column_name)
        try:
            csv_sequence = config.csv_sequence
        except AttributeError:
            csv_sequence = len(result) + 1

        if csv_sequence is None:
            csv_sequence = len(result) + 1

        column_positions.append((column_name, index, csv_sequence))

    print(column_positions)

    smallint_column_sequence = None
    hybrid_sequence = None
    for index, column in enumerate(column_positions):
        if column[0] == 'smallint_column':
            smallint_column_sequence = column[2]
        elif column[0] == 'hybrid':
            hybrid_sequence = column[2]

    if smallint_column_sequence is not None and hybrid_sequence is not None:
        assert smallint_column_sequence < hybrid_sequence

@pytest.mark.parametrize('delimiter, expected_result', [
    ('|', '_hybrid|addresses|hidden|hybrid|hybrid_differentiated|id|name|password|smallint_column\r\n'),
    (',', '_hybrid,addresses,hidden,hybrid,hybrid_differentiated,id,name,password,smallint_column\r\n'),
    (None, '_hybrid|addresses|hidden|hybrid|hybrid_differentiated|id|name|password|smallint_column\r\n'),
])
def test__get_attribute_csv_header(request,
                                   instance_postgresql,
                                   delimiter,
                                   expected_result):
    target = instance_postgresql[0][0]
    attributes = [x for x in get_attribute_names(target,
                                                 include_callable = False,
                                                 include_nested = False,
                                                 include_private = True,
                                                 include_utilities = False)
                  if x[0:2] != '__']

    if delimiter is not None:
        result = target._get_attribute_csv_header(attributes,
                                                  delimiter = delimiter)
    else:
        result = target._get_attribute_csv_header(attributes)

    print(result)

    assert result == expected_result


@pytest.mark.parametrize('deserialize, serialize, delimiter, expected_result', [
    (None, True, '|', 'id|name|smallint_column|hybrid\r\n'),
    (None, True, ',', 'id,name,smallint_column,hybrid\r\n'),
    (None, True, None, 'id|name|smallint_column|hybrid\r\n'),
    (True, None, '|', 'id|name|password|smallint_column|hybrid\r\n'),
    (True, None, ',', 'id,name,password,smallint_column,hybrid\r\n'),
    (True, None, None, 'id|name|password|smallint_column|hybrid\r\n'),
    (None, None, None, '\r\n'),
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


@pytest.mark.parametrize('delimiter, wrap_all_strings, wrapper_character, hybrid_value, expected_result', [
    ('|', False, "'", 1, '1|serialized|2|1\r\n'),
    ('|', True, "'", 1, "1|'serialized'|2|1\r\n"),
    ('|', False, "'", None, "1|serialized|2|None\r\n"),
    ('|', True, None, None, "1|'serialized'|2|'None'\r\n"),
    ('|', True, '!', None, "1|!serialized!|2|!None!\r\n"),
    ('|', False, "'", 'test|value', "1|serialized|2|'test|value'\r\n"),
])
def test_get_csv_data(request,
                      instance_postgresql,
                      delimiter,
                      wrap_all_strings,
                      wrapper_character,
                      hybrid_value,
                      expected_result):
    target = instance_postgresql[0][0]

    target.hybrid = hybrid_value

    result = target.get_csv_data(delimiter = delimiter,
                                 wrap_all_strings = wrap_all_strings,
                                 wrapper_character = wrapper_character)

    assert result == expected_result


@pytest.mark.parametrize('delimiter, wrap_all_strings, wrapper_character, hybrid_value, expected_result', [
    ('|', False, "'", 1, '1|[]|hidden value|1|1|1|serialized|test_password|2\r\n'),
    ('|', True, "'", 1, "1|'[]'|'hidden value'|1|1|1|'serialized'|'test_password'|2\r\n"),
    ('|', False, "'", None, "None|[]|hidden value|None|None|1|serialized|test_password|2\r\n"),
    ('|', True, None, None, "'None'|'[]'|'hidden value'|'None'|'None'|1|'serialized'|'test_password'|2\r\n"),
    ('|', True, '!', None, "!None!|![]!|!hidden value!|!None!|!None!|1|!serialized!|!test_password!|2\r\n"),
    ('|', False, "'", 'test|value', "'test|value'|[]|hidden value|'test|value'|'test|value'|1|serialized|test_password|2\r\n"),
])
def test__get_attribute_csv_data(request,
                                 instance_postgresql,
                                 delimiter,
                                 wrap_all_strings,
                                 wrapper_character,
                                 hybrid_value,
                                 expected_result):
    target = instance_postgresql[0][0]

    target.hybrid = hybrid_value

    attributes = [x for x in get_attribute_names(target,
                                                 include_callable = False,
                                                 include_nested = False,
                                                 include_private = True,
                                                 include_utilities = False)
                  if x[0:2] != '__']

    result = target._get_attribute_csv_data(attributes,
                                            is_dumping = True,
                                            delimiter = delimiter,
                                            wrap_all_strings = wrap_all_strings,
                                            wrapper_character = wrapper_character)

    print(result)
    assert result == expected_result



@pytest.mark.parametrize('include_header, delimiter, wrap_all_strings, wrapper_character, hybrid_value, expected_result', [
    (False, '|', False, "'", 1, '1|serialized|2|1\r\n'),
    (False, '|', True, "'", 1, "1|'serialized'|2|1\r\n"),
    (False, '|', False, "'", None, "1|serialized|2|None\r\n"),
    (False, '|', True, None, None, "1|'serialized'|2|'None'\r\n"),
    (False, '|', True, '!', None, "1|!serialized!|2|!None!\r\n"),
    (False, '|', False, "'", 'test|value', "1|serialized|2|'test|value'\r\n"),

    (True, '|', False, "'", 1, 'id|name|smallint_column|hybrid\r\n1|serialized|2|1\r\n'),
    (True, '|', True, "'", 1, "id|name|smallint_column|hybrid\r\n1|'serialized'|2|1\r\n"),
    (True, '|', False, "'", None, "id|name|smallint_column|hybrid\r\n1|serialized|2|None\r\n"),
    (True, '|', True, None, None, "id|name|smallint_column|hybrid\r\n1|'serialized'|2|'None'\r\n"),
    (True, '|', True, '!', None, "id|name|smallint_column|hybrid\r\n1|!serialized!|2|!None!\r\n"),
    (True, '|', False, "'", 'test|value', "id|name|smallint_column|hybrid\r\n1|serialized|2|'test|value'\r\n"),

])
def test_to_csv(request,
                instance_postgresql,
                include_header,
                delimiter,
                wrap_all_strings,
                wrapper_character,
                hybrid_value,
                expected_result):
    target = instance_postgresql[0][0]

    target.hybrid = hybrid_value

    result = target.to_csv(include_header = include_header,
                           delimiter = delimiter,
                           wrap_all_strings = wrap_all_strings,
                           wrapper_character = wrapper_character)

    assert result == expected_result


@pytest.mark.parametrize('include_header, delimiter, wrap_all_strings, wrapper_character, hybrid_value, expected_result', [
    (False, '|', False, "'", 1, '1|[]|hidden value|1|1|1|serialized|test_password|2\r\n'),
    (False, '|', True, "'", 1, "1|'[]'|'hidden value'|1|1|1|'serialized'|'test_password'|2\r\n"),
    (False, '|', False, "'", None, "None|[]|hidden value|None|None|1|serialized|test_password|2\r\n"),
    (False, '|', True, None, None, "'None'|'[]'|'hidden value'|'None'|'None'|1|'serialized'|'test_password'|2\r\n"),
    (False, '|', True, '!', None, "!None!|![]!|!hidden value!|!None!|!None!|1|!serialized!|!test_password!|2\r\n"),
    (False, '|', False, "'", 'test|value', "'test|value'|[]|hidden value|'test|value'|'test|value'|1|serialized|test_password|2\r\n"),

    (True, '|', False, "'", 1, '_hybrid|addresses|hidden|hybrid|hybrid_differentiated|id|name|password|smallint_column\r\n1|[]|hidden value|1|1|1|serialized|test_password|2\r\n'),
    (True, '|', True, "'", 1, "_hybrid|addresses|hidden|hybrid|hybrid_differentiated|id|name|password|smallint_column\r\n1|'[]'|'hidden value'|1|1|1|'serialized'|'test_password'|2\r\n"),
    (True, '|', False, "'", None, "_hybrid|addresses|hidden|hybrid|hybrid_differentiated|id|name|password|smallint_column\r\nNone|[]|hidden value|None|None|1|serialized|test_password|2\r\n"),
    (True, '|', True, None, None, "_hybrid|addresses|hidden|hybrid|hybrid_differentiated|id|name|password|smallint_column\r\n'None'|'[]'|'hidden value'|'None'|'None'|1|'serialized'|'test_password'|2\r\n"),
    (True, '|', True, '!', None, "_hybrid|addresses|hidden|hybrid|hybrid_differentiated|id|name|password|smallint_column\r\n!None!|![]!|!hidden value!|!None!|!None!|1|!serialized!|!test_password!|2\r\n"),
    (True, '|', False, "'", 'test|value', "_hybrid|addresses|hidden|hybrid|hybrid_differentiated|id|name|password|smallint_column\r\n'test|value'|[]|hidden value|'test|value'|'test|value'|1|serialized|test_password|2\r\n"),

])
def test_dump_to_csv(request,
                     instance_postgresql,
                     include_header,
                     delimiter,
                     wrap_all_strings,
                     wrapper_character,
                     hybrid_value,
                     expected_result):
    target = instance_postgresql[0][0]

    target.hybrid = hybrid_value

    result = target.dump_to_csv(include_header = include_header,
                                delimiter = delimiter,
                                wrap_all_strings = wrap_all_strings,
                                wrapper_character = wrapper_character)

    print(result)
    assert result == expected_result


@pytest.mark.parametrize('input_value, expected_name, expected_smallint, expected_id, expected_serialization, error', [
    ('1|serialized|test-password|3|2\r\n', 'deserialized', 3, 1, '1|serialized|3|2\r\n', None),
    ('1|serialized|test-password|3|2|extra\r\n', 'deserialized', 3, 1, '1|serialized|3|2\r\n', CSVStructureError),
    (123, 'deserialized', 3, 1, '1|serialized|3|2\r\n', DeserializationError),

    ('CSV/update_from_csv1.csv', 'deserialized', 3, 1, '1|serialized|3|2\r\n', None),
    ('CSV/update_from_csv2.csv', 'deserialized', 3, 1, '1|serialized|3|2\r\n', CSVStructureError),
    ('CSV/update_from_csv3.csv', 'deserialized', 3, 1, '1|serialized|3|2\r\n', None),

])
def test_update_from_csv(request,
                         model_complex_postgresql,
                         instance_postgresql,
                         input_files,
                         input_value,
                         expected_name,
                         expected_smallint,
                         expected_id,
                         expected_serialization,
                         error):
    model = model_complex_postgresql[0]
    target = instance_postgresql[0][0]

    input_value = check_input_file(input_files, input_value)

    if not error:
        target.update_from_csv(input_value)

        assert isinstance(target, model)
        assert getattr(target, 'name') == expected_name
        assert getattr(target, 'smallint_column') == expected_smallint
        assert getattr(target, 'id') == expected_id

        serialized = target.to_csv(include_header = False)

        assert serialized == expected_serialization
    else:
        with pytest.raises(error):
            target.update_from_csv(input_value)


@pytest.mark.parametrize('input_value, expected_name, expected_smallint, expected_id, expected_serialization, error', [
    ('1|serialized|test-password|3|2\r\n', 'deserialized', 3, 1, '1|serialized|3|2\r\n', None),
    ('1|serialized|test-password|3|2|extra\r\n', 'deserialized', 3, 1, '1|serialized|3|2\r\n', CSVStructureError),
    (123, 'deserialized', 3, 1, '1|serialized|3|2\r\n', DeserializationError),

    ('CSV/update_from_csv1.csv', 'deserialized', 3, 1, '1|serialized|3|2\r\n', None),
    ('CSV/update_from_csv2.csv', 'deserialized', 3, 1, '1|serialized|3|2\r\n', CSVStructureError),
    ('CSV/update_from_csv3.csv', 'deserialized', 3, 1, '1|serialized|3|2\r\n', None),

])
def test_new_from_csv(request,
                      model_complex_postgresql,
                      input_files,
                      input_value,
                      expected_name,
                      expected_smallint,
                      expected_id,
                      expected_serialization,
                      error):
    model = model_complex_postgresql[0]

    input_value = check_input_file(input_files, input_value)

    if not error:
        result = model.new_from_csv(input_value)

        assert isinstance(result, model)
        assert getattr(result, 'name') == expected_name
        assert getattr(result, 'smallint_column') == expected_smallint
        assert getattr(result, 'id') == expected_id

        serialized = result.to_csv(include_header = False)

        assert serialized == expected_serialization
    else:
        with pytest.raises(error):
            result = model.new_from_csv(input_value)
