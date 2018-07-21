# -*- coding: utf-8 -*-

"""
******************************************
tests.test_reflected_tables
******************************************

Tests for declarative :class:`BaseModel` and the ability to retireve serialization
configuration data when using
:doc:`reflected tables <sqlalchemy:using-reflection-with-declarative>`_.

"""

import pytest

from sqlathanor import Column
from sqlathanor.errors import UnsupportedSerializationError

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_reflected_tables, instance_complex

@pytest.mark.parametrize('test_index, expected_result, column_names', [
    (0, True, ('id', 'username', 'password')),
    (1, True, ('id', 'username', 'password')),
])
def test_model___serialization__(request,
                                 model_reflected_tables,
                                 test_index,
                                 expected_result,
                                 column_names):
    target = model_reflected_tables[test_index]
    result = hasattr(target, '__serialization__')
    assert result == expected_result

    for column_name in column_names:
        assert hasattr(target, column_name) == True

@pytest.mark.parametrize('use_meta, test_index, format_support, exclude_private, expected_length', [
    (False, 0, {
        'from_csv': None,
        'to_csv': None,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, True, 0),
    (True, 0, {
        'from_csv': True,
        'to_csv': True,
        'from_json': True,
        'to_json': True,
        'from_yaml': True,
        'to_yaml': True,
        'from_dict': True,
        'to_dict': True
    }, True, 0),
    (False, 0, {
        'from_csv': True,
        'to_csv': None,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, True, 3),
    (False, 0, {
        'from_csv': None,
        'to_csv': False,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, True, 4),
    (False, 0, {
        'from_csv': True,
        'to_csv': False,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, True, 1),
    (False, 0, {
        'from_csv': None,
        'to_csv': None,
        'from_json': None,
        'to_json': None,
        'from_yaml': True,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, True, 3),
])
def test_model__get_declarative_serializable_attributes(request,
                                                        model_reflected_tables,
                                                        use_meta,
                                                        test_index,
                                                        format_support,
                                                        exclude_private,
                                                        expected_length):
    if not use_meta:
        target = model_reflected_tables[0]
    else:
        target = model_reflected_tables[1]

    result = target._get_declarative_serializable_attributes(
        exclude_private = exclude_private,
        **format_support
    )

    print(result)
    print(target.__serialization__)

    assert len(result) == expected_length

@pytest.mark.parametrize('use_meta, test_index, format_support, expected_length', [
    (False, 0, {
        'from_csv': None,
        'to_csv': None,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 0),
    (True, 0, {
        'from_csv': True,
        'to_csv': True,
        'from_json': True,
        'to_json': True,
        'from_yaml': True,
        'to_yaml': True,
        'from_dict': True,
        'to_dict': True
    }, 0),
    (True, 0, {
        'from_csv': True,
        'to_csv': None,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 0),
    (True, 0, {
        'from_csv': None,
        'to_csv': False,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 0),
    (True, 0, {
        'from_csv': True,
        'to_csv': False,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 0),
    (True, 0, {
        'from_csv': None,
        'to_csv': None,
        'from_json': None,
        'to_json': None,
        'from_yaml': True,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 0),


    (False, 0, {
        'from_csv': None,
        'to_csv': None,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 0),
    (True, 1, {
        'from_csv': True,
        'to_csv': True,
        'from_json': True,
        'to_json': True,
        'from_yaml': True,
        'to_yaml': True,
        'from_dict': True,
        'to_dict': True
    }, 4),
    (True, 1, {
        'from_csv': True,
        'to_csv': None,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 4),
    (True, 1, {
        'from_csv': None,
        'to_csv': False,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 2),
    (True, 1, {
        'from_csv': True,
        'to_csv': False,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 1),
    (True, 1, {
        'from_csv': None,
        'to_csv': None,
        'from_json': None,
        'to_json': None,
        'from_yaml': True,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 5),
])
def test_model__get_meta_serializable_attributes(request,
                                                 model_reflected_tables,
                                                 use_meta,
                                                 test_index,
                                                 format_support,
                                                 expected_length):
    if not use_meta:
        target = model_reflected_tables[0]
    else:
        target = model_reflected_tables[1 + test_index]

    result = target._get_meta_serializable_attributes(
        **format_support
    )

    for item in result:
        print(item.name)

    assert len(result) == expected_length

@pytest.mark.parametrize('use_meta, test_index, expected_length', [
    (False, 0, 3),
    (True, 0, 0),
    (True, 1, 5),
])
def test_model__get_attribute_configurations(request,
                                             model_reflected_tables,
                                             use_meta,
                                             test_index,
                                             expected_length):
    if not use_meta:
        target = model_reflected_tables[0]
    else:
        target = model_reflected_tables[1 + test_index]

    result = target._get_attribute_configurations()

    print(target.__dict__)
    for item in result:
        print(item.name)

    assert len(result) == expected_length
