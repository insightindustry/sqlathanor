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

    (1, False, 'email', (False, False)),
    (1, True, 'email', (True, True)),
    (1, False, 'user_id', (False, False)),
    (1, True, 'user_id', (False, False)),
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

    assert hasattr(target, column_name)
    column = getattr(target, column_name)

    assert column.supports_csv == expected_result


@pytest.mark.parametrize('test_index, test_complex, column_name, expected_result', [
    (0, False, 'id', (False, False)),
    (0, True, 'id', (True, True)),
    (0, False, 'name', (False, False)),
    (0, True, 'name', (True, True)),

    (0, True, 'password', (True, False)),
    (0, True, 'hidden', (False, False)),

    (1, False, 'email', (False, False)),
    (1, True, 'email', (True, True)),
    (1, False, 'user_id', (False, False)),
    (1, True, 'user_id', (False, False)),
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

    assert hasattr(target, column_name)
    column = getattr(target, column_name)

    assert column.supports_json == expected_result


@pytest.mark.parametrize('test_index, test_complex, column_name, expected_result', [
    (0, False, 'id', (False, False)),
    (0, True, 'id', (True, True)),
    (0, False, 'name', (False, False)),
    (0, True, 'name', (True, True)),

    (0, True, 'password', (True, False)),
    (0, True, 'hidden', (False, False)),

    (1, False, 'email', (False, False)),
    (1, True, 'email', (True, True)),
    (1, False, 'user_id', (False, False)),
    (1, True, 'user_id', (False, False)),
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

    assert hasattr(target, column_name)
    column = getattr(target, column_name)

    assert column.supports_yaml == expected_result


@pytest.mark.parametrize('test_index, test_complex, column_name, expected_result', [
    (0, False, 'id', (False, False)),
    (0, True, 'id', (True, True)),
    (0, False, 'name', (False, False)),
    (0, True, 'name', (True, True)),

    (0, True, 'password', (True, False)),
    (0, True, 'hidden', (False, False)),

    (1, False, 'email', (False, False)),
    (1, True, 'email', (True, True)),
    (1, False, 'user_id', (False, False)),
    (1, True, 'user_id', (False, False)),
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

    assert hasattr(target, column_name)
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
def test_model_value_validator(request,
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

    assert hasattr(target, column_name)
    column = getattr(target, column_name)

    assert (column.value_validator is not None) is not_none
