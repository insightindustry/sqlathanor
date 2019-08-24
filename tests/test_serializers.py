# -*- coding: utf-8 -*-

"""
******************************************
tests.test_serializers
******************************************

Tests for :term:`serializer functions <serializer function>`.

"""

import pytest

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_complex_postgresql, instance_postgresql

from sqlathanor.errors import InvalidFormatError, ValueSerializationError, \
    UnsupportedSerializationError


@pytest.mark.parametrize('attribute, format, expected_result, error', [
    ('name', 'csv', 'serialized', None),
    ('id', 'csv', 1, None),
    ('hybrid', 'csv', 1, None),
    ('smallint_column', 'csv', 2, None),
    ('addresses', 'json', [], None),
    ('time_delta', 'csv', 86400, None),
    ('name', 'invalid', None, InvalidFormatError),
    ('missing', 'csv', None, UnsupportedSerializationError),
    ('hidden', 'csv', None, UnsupportedSerializationError),
    ('time_delta', 'json', 86400, UnsupportedSerializationError),

])
def test__get_serialized_value(request,
                               instance_postgresql,
                               attribute,
                               format,
                               expected_result,
                               error):
    target = instance_postgresql[0][0]

    if not error:
        result = target._get_serialized_value(format, attribute)
        assert result == expected_result
    else:
        with pytest.raises(error):
            result = target._get_serialized_value(format, attribute)
