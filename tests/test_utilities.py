# -*- coding: utf-8 -*-

"""
***********************************
tests.test_utilities
***********************************

Tests for the schema extensions written in :ref:`sqlathanor.utilities`.

"""

import pytest

from sqlathanor.utilities import bool_to_tuple, callable_to_dict


def sample_callable():
    pass


@pytest.mark.parametrize('value, expected_result, fails', [
    (True, (True, True), False),
    (False, (False, False), False),
    (None, (False, False), False),
    ((True, True), (True, True), False),
    ((False, False), (False, False), False),
    ((True, False), (True, False), False),
    ((False, True), (False, True), False),
    ('not-a-bool', None, True),
])
def test_bool_to_tuple(value, expected_result, fails):
    if not fails:
        result = bool_to_tuple(value)
        assert result == expected_result
    else:
        with pytest.raises(ValueError):
            result = bool_to_tuple(value)


@pytest.mark.parametrize('value', [
    (sample_callable),
    ({
        'csv': sample_callable,
        'json': sample_callable,
        'yaml': sample_callable,
        'dict': sample_callable
    }),
    (None),
    ({
        'csv': None,
        'json': sample_callable,
        'yaml': None,
        'dict': None
    }),
])
def test_callable_to_dict(value):
    result = callable_to_dict(value)

    assert isinstance(result, dict)
    assert 'csv' in result
    assert 'json' in result
    assert 'yaml' in result
    assert 'dict' in result

    if isinstance(value, dict):
        assert result['csv'] == value['csv']
        assert result['json'] == value['json']
        assert result['yaml'] == value['yaml']
        assert result['dict'] == value['dict']
    else:
        for key in result:
            assert result[key] == value
