# -*- coding: utf-8 -*-

"""
***********************************
tests.test_schema
***********************************

Tests for the schema extensions written in :ref:`sqlathanor.schema`.

"""

import pytest

from sqlathanor import Column

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_single_pk, model_composite_pk, instance_single_pk, instance_composite_pk, \
    model_complex, instance_complex


@pytest.mark.parametrize('test_index, test_complex, column_name, expected_result', [
    (0, False, 'id', (False, False)),
    (0, True, 'id', (True, True)),
    (0, False, 'name', (False, False)),
    (0, True, 'name', (True, True)),

    (0, True, 'password', (True, False)),
    (0, True, 'hidden', (False, False)),

    (0, False, 'addresses', (False, False)),
    (0, True, 'addresses', (False, False)),

    (1, False, 'email', (False, False)),
    (1, True, 'email', (True, True)),
    (1, False, 'user_id', (False, False)),
    (1, True, 'user_id', (False, False)),

    (0, False, 'hybrid', (False, False)),
    (0, True, 'hybrid', (True, True)),

    (0, False, 'hybrid_differentiated', (False, False)),
    (0, True, 'hybrid_differentiated', (False, True)),

])
def test_model_supports_csv(request,
                            model_single_pk,
                            model_complex,
                            test_index,
                            test_complex,
                            column_name,
                            expected_result):
    if test_complex:
        target = model_complex[test_index]
    else:
        target = model_single_pk[test_index]

    column = getattr(target, column_name)

    assert column.supports_csv == expected_result


@pytest.mark.parametrize('test_index, test_complex, column_name, expected_result', [
    (0, False, 'id', (False, False)),
    (0, True, 'id', (True, True)),
    (0, False, 'name', (False, False)),
    (0, True, 'name', (True, True)),

    (0, True, 'password', (True, False)),
    (0, True, 'hidden', (False, False)),

    (0, False, 'addresses', (False, False)),
    (0, True, 'addresses', (True, True)),

    (1, False, 'email', (False, False)),
    (1, True, 'email', (True, True)),
    (1, False, 'user_id', (False, False)),
    (1, True, 'user_id', (False, False)),

    (0, False, 'hybrid', (False, False)),
    (0, True, 'hybrid', (True, True)),

    (0, False, 'hybrid_differentiated', (False, False)),
    (0, True, 'hybrid_differentiated', (False, True)),

])
def test_model_supports_json(request,
                             model_single_pk,
                             model_complex,
                             test_index,
                             test_complex,
                             column_name,
                             expected_result):
    if test_complex:
        target = model_complex[test_index]
    else:
        target = model_single_pk[test_index]

    column = getattr(target, column_name)

    assert column.supports_json == expected_result


@pytest.mark.parametrize('test_index, test_complex, column_name, expected_result', [
    (0, False, 'id', (False, False)),
    (0, True, 'id', (True, True)),
    (0, False, 'name', (False, False)),
    (0, True, 'name', (True, True)),

    (0, True, 'password', (True, False)),
    (0, True, 'hidden', (False, False)),

    (0, False, 'addresses', (False, False)),
    (0, True, 'addresses', (True, True)),

    (1, False, 'email', (False, False)),
    (1, True, 'email', (True, True)),
    (1, False, 'user_id', (False, False)),
    (1, True, 'user_id', (False, False)),

    (0, False, 'hybrid', (False, False)),
    (0, True, 'hybrid', (False, False)),

    (0, False, 'hybrid_differentiated', (False, False)),
    (0, True, 'hybrid_differentiated', (False, True)),
])
def test_model_supports_yaml(request,
                             model_single_pk,
                             model_complex,
                             test_index,
                             test_complex,
                             column_name,
                             expected_result):
    if test_complex:
        target = model_complex[test_index]
    else:
        target = model_single_pk[test_index]

    column = getattr(target, column_name)

    assert column.supports_yaml == expected_result


@pytest.mark.parametrize('test_index, test_complex, column_name, expected_result', [
    (0, False, 'id', (False, False)),
    (0, True, 'id', (True, True)),
    (0, False, 'name', (False, False)),
    (0, True, 'name', (True, True)),

    (0, True, 'password', (True, False)),
    (0, True, 'hidden', (False, False)),

    (0, False, 'addresses', (False, False)),
    (0, True, 'addresses', (True, False)),

    (1, False, 'email', (False, False)),
    (1, True, 'email', (True, True)),
    (1, False, 'user_id', (False, False)),
    (1, True, 'user_id', (False, False)),

    (0, False, 'hybrid', (False, False)),
    (0, True, 'hybrid', (True, True)),

    (0, False, 'hybrid_differentiated', (False, False)),
    (0, True, 'hybrid_differentiated', (False, True)),
])
def test_model_supports_dict(request,
                             model_single_pk,
                             model_complex,
                             test_index,
                             test_complex,
                             column_name,
                             expected_result):
    if test_complex:
        target = model_complex[test_index]
    else:
        target = model_single_pk[test_index]

    column = getattr(target, column_name)

    assert column.supports_dict == expected_result


@pytest.mark.parametrize('test_index, test_complex, column_name, not_none', [
    (0, False, 'id', False),
    (0, True, 'id', False),
    (0, False, 'name', False),
    (0, True, 'name', False),

    (0, True, 'password', False),
    (0, True, 'hidden', False),

    (1, False, 'email', False),
    (1, True, 'email', True),
    (1, False, 'user_id', False),
    (1, True, 'user_id', False),
])
def test_model_on_serialize(request,
                            model_single_pk,
                            model_complex,
                            test_index,
                            test_complex,
                            column_name,
                            not_none):
    if test_complex:
        target = model_complex[test_index]
    else:
        target = model_single_pk[test_index]

    column = getattr(target, column_name)

    assert isinstance(column.on_serialize, dict)
    for key in column.on_serialize:
        assert (column.on_serialize[key] is not None) is not_none


@pytest.mark.parametrize('test_index, test_complex, column_name, not_none', [
    (0, False, 'id', False),
    (0, True, 'id', False),
    (0, False, 'name', False),
    (0, True, 'name', False),

    (0, True, 'password', False),
    (0, True, 'hidden', False),

    (1, False, 'email', False),
    (1, True, 'email', True),
    (1, False, 'user_id', False),
    (1, True, 'user_id', False),
])
def test_model_on_deserialize(request,
                              model_single_pk,
                              model_complex,
                              test_index,
                              test_complex,
                              column_name,
                              not_none):
    if test_complex:
        target = model_complex[test_index]
    else:
        target = model_single_pk[test_index]

    column = getattr(target, column_name)

    assert isinstance(column.on_deserialize, dict)
    for key in column.on_deserialize:
        assert (column.on_deserialize[key] is not None) is not_none


@pytest.mark.parametrize('test_index, column_name, expected_result', [
    (0, 'hybrid', 1),
])
def test_instance_hybrid_property_get(request,
                                      test_index,
                                      instance_complex,
                                      column_name,
                                      expected_result):
    target = instance_complex[0][test_index]
    result = getattr(target, column_name)

    assert result == expected_result


@pytest.mark.parametrize('test_index, column_name, new_value', [
    (0, 'hybrid', 3),
])
def test_instance_hybrid_property_set(request,
                                      test_index,
                                      instance_complex,
                                      column_name,
                                      new_value):
    target = instance_complex[0][test_index]
    setattr(target, column_name, new_value)

    result = getattr(target, column_name)

    assert result == new_value


@pytest.mark.parametrize('test_index, column_name, expected_result', [
    (0, 'keywords_basic', (False, False)),
])
def test_instance_association_proxy_supports_json(request,
                                                  test_index,
                                                  instance_complex,
                                                  column_name,
                                                  expected_result):
    target = instance_complex[0][test_index]
    result = getattr(target.__class__, column_name)

    pass
