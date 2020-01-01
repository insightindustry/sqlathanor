# -*- coding: utf-8 -*-

"""
******************************************
tests.test_interval_deserialization
******************************************

Tests for how SQLAthanor deserializes Interval columns.

"""

import pytest
import datetime

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_complex_postgresql, instance_postgresql

from sqlathanor.errors import InvalidFormatError, ValueDeserializationError, \
    UnsupportedDeserializationError



@pytest.mark.parametrize('attribute, format, input_value, expected_result, error', [
    ('name', 'csv', 'serialized', 'deserialized', None),
    ('id', 'csv', '1', 1, None),
    ('hybrid', 'csv', 1, 1, None),
    ('smallint_column', 'csv', '2', 2, None),
    ('addresses', 'json', [], [], None),
    ('time_delta', 'csv', 86400.0, datetime.timedelta(1), None),
    ('time_delta', 'csv', '00:35:00', datetime.timedelta(minutes = 35), None),
    ('time_delta', 'csv', '00:35:00.456', datetime.timedelta(minutes = 35, milliseconds = 456), None),
    ('name', 'invalid', None, None, InvalidFormatError),
    ('missing', 'csv', None, None, UnsupportedDeserializationError),
    ('hidden', 'csv', None, None, UnsupportedDeserializationError),
    ('id', 'csv', 'invalid', None, ValueDeserializationError),
    ('time_delta', 'csv', 'not-numeric', None, ValueDeserializationError),
    ('time_delta', 'json', 86400.0, None, UnsupportedDeserializationError),
    ('time_delta', 'json', '00:35:00', None, UnsupportedDeserializationError),

])
def test__get_deserialized_value(request,
                                 instance_postgresql,
                                 attribute,
                                 format,
                                 input_value,
                                 expected_result,
                                 error):
    target = instance_postgresql[0][0]

    if not error:
        result = target._get_deserialized_value(input_value, format, attribute)
        assert result == expected_result
    else:
        with pytest.raises(error):
            result = target._get_deserialized_value(input_value, format, attribute)
