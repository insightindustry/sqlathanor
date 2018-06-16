# -*- coding: utf-8 -*-

"""
***********************************
tests.test_primary_key_retrieval
***********************************

Tests for the :class:`BaseModel` ability to retrieve primary key data.

"""

import pytest

from sqlalchemy import Column

from tests._fixtures import base_model, model_single_pk, model_composite_pk


@pytest.mark.parametrize('models, instantiate, expected_count, instance_values', [
    (model_single_pk, False, 1, None),
    (model_composite_pk, False, 3, None),
    (model_single_pk, True, 1, {
        'id': 1,
        'name': 'test name'
    }),
    (model_composite_pk, True, 3, {
        'id': 1,
        'id2': 123,
        'id3': 456,
        'name': 'test name',
    }),
])
@pytest.mark.filterwarnings('ignore:This declarative base already contains a class')
def test_get_primary_key_columns(request, base_model, models, instantiate, expected_count, instance_values):
    models = models(request, base_model)

    if not instantiate:
        target = models[0]
    else:
        model = models[0]
        target = model(**instance_values)

    primary_key_columns = target.get_primary_key_columns()

    assert len(primary_key_columns) == expected_count

    for column in primary_key_columns:
        assert isinstance(column, Column)


@pytest.mark.parametrize('models, instantiate, expected_count, instance_values, expected_names', [
    (model_single_pk, False, 1, None, ['id']),
    (model_composite_pk, False, 3, None, ['id', 'id2', 'id3']),
    (model_single_pk, True, 1, {
        'id': 1,
        'name': 'test name'
    }, ['id']),
    (model_composite_pk, True, 3, {
        'id': 1,
        'id2': 123,
        'id3': 456,
        'name': 'test name',
    }, ['id', 'id2', 'id3']),
])
@pytest.mark.filterwarnings('ignore:This declarative base already contains a class')
def test_get_primary_key_column_names(request, base_model, models, instantiate, expected_count, instance_values, expected_names):
    models = models(request, base_model)

    if not instantiate:
        target = models[0]
    else:
        model = models[0]
        target = model(**instance_values)

    pk_column_names = target.get_primary_key_column_names()

    assert len(pk_column_names) == expected_count

    for column in pk_column_names:
        assert isinstance(column, str)
        assert column in expected_names
