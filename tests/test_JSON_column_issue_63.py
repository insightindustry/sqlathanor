# -*- coding: utf-8 -*-

"""
******************************************
tests.test_JSON_column_issue_63
******************************************

Tests for an issue reported as
`Github Issue #63 <https://github.com/insightindustry/sqlathanor/issues/63>`_ where a
``JSON`` attribute is not correctly serialized.

"""
# pylint: disable=line-too-long,protected-access

import pytest

try:
    from sqlalchemy import Integer, JSON, create_engine, MetaData, Table
except ImportError:
    from sqlalchemy import Integer, create_engine, MetaData, Table
    JSON = None

from sqlalchemy.ext.declarative import declarative_base
from validator_collection import checkers

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_single_pk, instance_single_pk, model_complex_postgresql, instance_postgresql

from sqlathanor import BaseModel as Base
from sqlathanor import Column, AttributeConfiguration

from sqlathanor.errors import CSVStructureError, DeserializationError, \
    MaximumNestingExceededError, MaximumNestingExceededWarning, \
    SerializableAttributeError, InvalidFormatError, ValueSerializationError, \
    ValueDeserializationError, DeserializableAttributeError, DeserializationError, \
    ExtraKeyError
from sqlathanor.utilities import are_dicts_equivalent


@pytest.fixture
def model_class(request, db_engine):
    BaseModel = declarative_base(cls = Base, metadata = MetaData())
    if JSON is not None:
        class TestClass(BaseModel):
            __tablename__ = 'test_class'
            __serialization__ = [AttributeConfiguration(name = 'id',
                                                        supports_json = True,
                                                        supports_dict = True),
                                 AttributeConfiguration(name = 'json_column',
                                                        supports_json = True,
                                                        supports_dict = True)]

            id = Column('id',
                        Integer,
                        primary_key = True)
            json_column = Column(JSON)
    else:
        TestClass = None

    return TestClass


def test_serialization_to_dict(request, model_class):
    if JSON is not None:
        model_instance = model_class(json_column = { "test": "test string"})
        assert model_instance is not None
        assert isinstance(model_instance, model_class) is True

        dict_result = model_instance.to_dict()
        assert dict_result is not None
        assert isinstance(dict_result, dict)
