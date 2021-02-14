# -*- coding: utf-8 -*-

"""
******************************************
tests.test_deserializers
******************************************

Tests for declarative :class:`BaseModel` and the ability to retireve serialization
configuration data.

"""

import pytest
import datetime

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_complex_postgresql, instance_postgresql

from sqlathanor.errors import InvalidFormatError, ValueDeserializationError, \
    UnsupportedDeserializationError

from sqlathanor._compat import is_py36

if is_py36:
    from pydantic import BaseModel
    from pydantic.fields import Field, ModelField

    class PydanticModel(BaseModel):
        id: datetime.timedelta

    pydantic_field = PydanticModel.__fields__.get('id', None)

else:
    pydantic_field = None
    PydanticModel = 'Python <3.6'


@pytest.mark.parametrize('attribute, format, input_value, expected_result, error', [
    ('name', 'csv', 'serialized', 'deserialized', None),
    ('id', 'csv', '1', 1, None),
    ('hybrid', 'csv', 1, 1, None),
    ('smallint_column', 'csv', '2', 2, None),
    ('addresses', 'json', [], [], None),
    ('time_delta', 'csv', 86400.0, datetime.timedelta(1), None),
    ('name', 'invalid', None, None, InvalidFormatError),
    ('missing', 'csv', None, None, UnsupportedDeserializationError),
    ('hidden', 'csv', None, None, UnsupportedDeserializationError),
    ('id', 'csv', 'invalid', None, ValueDeserializationError),
    ('time_delta', 'csv', 'not-numeric', None, ValueDeserializationError),
    ('time_delta', 'json', 86400.0, None, UnsupportedDeserializationError),

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


if is_py36:
    @pytest.mark.parametrize('attribute, format, input_value, pydantic_field, expected_result, error', [
        ('id', 'csv', '1', pydantic_field, 1, None),
        ('id', 'csv', 'invalid', pydantic_field, None, ValueDeserializationError),
        ('id', 'yaml', '1', pydantic_field, 1, UnsupportedDeserializationError),

    ])
    def test__get_deserialized_value_pydantic(request,
                                              model_complex_postgresql,
                                              instance_postgresql,
                                              attribute,
                                              format,
                                              input_value,
                                              pydantic_field,
                                              expected_result,
                                              error):
        model = model_complex_postgresql[0]
        model.set_attribute_serialization_config('id',
                                                 config = pydantic_field,
                                                 supports_csv = True,
                                                 supports_json = True,
                                                 supports_yaml = False,
                                                 supports_dict = True)
        instance_values = instance_postgresql[1][0]
        target = model(**instance_values)

        if not error:
            result = target._get_deserialized_value(input_value, format, attribute)
            assert result == expected_result
        else:
            with pytest.raises(error):
                result = target._get_deserialized_value(input_value, format, attribute)
