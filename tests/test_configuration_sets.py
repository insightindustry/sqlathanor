# -*- coding: utf-8 -*-

"""
******************************************
tests.test_configuration_sets
******************************************

Tests for the addition of Configuration Set support.

"""
# pylint: disable=line-too-long,protected-access

import pytest


from sqlalchemy import Integer, Text, create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from validator_collection import checkers
import yaml

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_single_pk, instance_single_pk, model_complex_postgresql, instance_postgresql

from sqlathanor import BaseModel as Base
from sqlathanor import Column, AttributeConfiguration
from sqlathanor._compat import json

from sqlathanor.errors import CSVStructureError, DeserializationError, \
    MaximumNestingExceededError, MaximumNestingExceededWarning, \
    SerializableAttributeError, InvalidFormatError, ValueSerializationError, \
    ValueDeserializationError, DeserializableAttributeError, DeserializationError, \
    ExtraKeyError, ConfigurationError
from sqlathanor.utilities import are_dicts_equivalent, parse_csv, parse_json, parse_yaml


@pytest.fixture
def model_class(request, db_engine):
    BaseModel = declarative_base(cls = Base, metadata = MetaData())

    class TestClass(BaseModel):
        __tablename__ = 'test_class'
        __serialization__ = {
            'two_properties': [AttributeConfiguration(name = 'id',
                                                      supports_csv = False,
                                                      supports_json = True,
                                                      supports_dict = True,
                                                      supports_yaml = False),
                               AttributeConfiguration(name = 'second_column',
                                                      supports_csv = True,
                                                      supports_json = True,
                                                      supports_dict = True,
                                                      supports_yaml = False)],
            'one_property': [AttributeConfiguration(name = 'id',
                                                    supports_csv = True,
                                                    supports_json = True,
                                                    supports_dict = True,
                                                    supports_yaml = True)]
        }

        id = Column('id',
                    Integer,
                    primary_key = True)
        second_column = Column('second_column',
                               Text)

    return TestClass


@pytest.mark.parametrize('config_set, format, has_id, has_second_column, error', [
    ('two_properties', 'dict', True, True, None),
    ('one_property', 'dict', True, False, None),
    ('two_properties', 'json', True, True, None),
    ('one_property', 'json', True, False, None),
    ('two_properties', 'csv', False, True, None),
    ('one_property', 'csv', True, False, None),
    ('two_properties', 'yaml', False, False, SerializableAttributeError),
    ('one_property', 'yaml', True, False, None),
    ('missing_config_set', 'dict', False, False, (ValueError, ConfigurationError)),
])
def test_configuration_sets(request,
                            model_class,
                            config_set,
                            format,
                            has_id,
                            has_second_column,
                            error):
    model_instance = model_class(id = 1,
                                 second_column = 'test_string')
    assert model_instance is not None
    assert isinstance(model_instance, model_class) is True

    kwargs = {
        'config_set': config_set
    }

    if format == 'dict':
        method = model_instance.to_dict
        expected_result = dict
    elif format == 'json':
        method = model_instance.to_json
        expected_result = str
        parse_function = parse_json
    elif format == 'yaml':
        method = model_instance.to_yaml
        expected_result = str
        parse_function = parse_yaml
    elif format == 'csv':
        method = model_instance.to_csv
        expected_result = str
        parse_function = parse_csv
        kwargs['include_header'] = True

    if not error:
        result = method(**kwargs)
    else:
        with pytest.raises(error):
            result = method(**kwargs)

    if not error:
        assert result is not None
        assert isinstance(result, expected_result) is True

        if format == 'csv':
            result = result.split('\n')
        if format != 'dict':
            result = parse_function(result)

        assert ('id' in result) is has_id
        assert ('second_column' in result) is has_second_column
        if has_id:
            if format == 'csv':
                assert result['id'] == str(model_instance.id)
            else:
                assert result['id'] == model_instance.id
        if has_second_column:
            assert result['second_column'] == model_instance.second_column
