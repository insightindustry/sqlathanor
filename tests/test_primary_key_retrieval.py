# -*- coding: utf-8 -*-

"""
***********************************
tests.test_primary_key_retrieval
***********************************

Tests for the :class:`BaseModel` ability to retrieve primary key data.

"""

import pytest

from sqlathanor import Column

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_single_pk, model_composite_pk, instance_single_pk, instance_composite_pk


@pytest.mark.parametrize('expected_count', [
    (1),
    (3),
])
@pytest.mark.filterwarnings('ignore:This declarative base already contains a class')
def test_get_primary_key_columns_classmethod(request,
                                             model_single_pk,
                                             model_composite_pk,
                                             expected_count):
    if expected_count == 1:
        target = model_single_pk[0]
    elif expected_count > 1:
        target = model_composite_pk[0]

    primary_key_columns = target.get_primary_key_columns()

    assert len(primary_key_columns) == expected_count

    for column in primary_key_columns:
        assert isinstance(column, Column)


@pytest.mark.parametrize('expected_count', [
    (1),
    (3),
])
@pytest.mark.filterwarnings('ignore:This declarative base already contains a class')
def test_get_primary_key_columns_instance(request,
                                          instance_single_pk,
                                          instance_composite_pk,
                                          expected_count):
    if expected_count == 1:
        instances = instance_single_pk
    elif expected_count > 1:
        instances = instance_composite_pk

    target = instances[0]
    instance_values = instances[1]

    primary_key_columns = target.get_primary_key_columns()

    assert len(primary_key_columns) == expected_count

    for column in primary_key_columns:
        assert isinstance(column, Column)


@pytest.mark.parametrize('expected_count, expected_names', [
    (1, ['id']),
    (3, ['id', 'id2', 'id3']),
])
@pytest.mark.filterwarnings('ignore:This declarative base already contains a class')
def test_get_primary_key_column_names_classmethod(request,
                                                  model_single_pk,
                                                  model_composite_pk,
                                                  expected_count,
                                                  expected_names):

    if expected_count == 1:
        target = model_single_pk[0]
    elif expected_count > 1:
        target = model_composite_pk[0]

    pk_column_names = target.get_primary_key_column_names()

    assert len(pk_column_names) == expected_count

    for column in pk_column_names:
        assert isinstance(column, str)
        assert column in expected_names


@pytest.mark.parametrize('expected_count, expected_names', [
    (1, ['id']),
    (3, ['id', 'id2', 'id3']),
])
@pytest.mark.filterwarnings('ignore:This declarative base already contains a class')
def test_get_primary_key_column_names_instance(request,
                                               instance_single_pk,
                                               instance_composite_pk,
                                               expected_count,
                                               expected_names):
    if expected_count == 1:
        target = instance_single_pk[0]
        instance_values = instance_single_pk[1]
    elif expected_count > 1:
        target = instance_composite_pk[0]
        instance_values = instance_composite_pk[1]

    pk_column_names = target.get_primary_key_column_names()

    assert len(pk_column_names) == expected_count

    for column in pk_column_names:
        assert isinstance(column, str)
        assert column in expected_names



@pytest.mark.parametrize('is_composite, expected_count', [
    (False, None),
    (True, None),
    (False, 1),
    (True, 3),
])
@pytest.mark.filterwarnings('ignore:This declarative base already contains a class')
def test_primary_key_value(request,
                           db_session,
                           instance_single_pk,
                           instance_composite_pk,
                           is_composite,
                           expected_count):
    if is_composite or (expected_count is not None and expected_count > 1):
        target = instance_composite_pk[0]
        instance_values = instance_composite_pk[1]
    else:
        target = instance_single_pk[0]
        instance_values = instance_single_pk[1]

    if expected_count:
        db_session.add(target)
        db_session.commit()

    pk_values = target.primary_key_value

    if expected_count is None:
        assert pk_values is None
    elif expected_count == 1:
        assert not isinstance(pk_values, tuple)
        assert pk_values == instance_values['id']
    elif expected_count > 1:
        assert isinstance(pk_values, tuple)
        assert len(pk_values) == expected_count

        id_values = [instance_values[key] for key in instance_values
                     if 'id' in key]

        for index, value in enumerate(pk_values):
            assert pk_values[index] == id_values[index]
