# -*- coding: utf-8 -*-

"""
******************************************
tests.test_deserializers
******************************************

Tests for declarative :class:`BaseModel` and the ability to retireve serialization
configuration data.

"""

import pytest

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_complex_postgresql, instance_postgresql

from sqlathanor.errors import InvalidFormatError, ValueSerializationError, \
    UnsupportedDeserializationError


@pytest.mark.parametrize('attribute, format, input_value, expected_result, error', [
    ('name', 'csv', 'serialized', 'deserialized', None),
    ('id', 'csv', '1', 1, None),
    ('hybrid', 'csv', 1, 1, None),
    ('smallint_column', 'csv', '2', 2, None),
    ('addresses', 'json', [], [], None),
    ('name', 'invalid', None, None, InvalidFormatError),
    ('missing', 'csv', None, None, UnsupportedDeserializationError),
    ('hidden', 'csv', None, None, UnsupportedDeserializationError),

])
def test__get_serialized_value(request,
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
