# -*- coding: utf-8 -*-

"""
***********************************
tests.test_attributes
***********************************

Tests for the schema extensions written in :ref:`sqlathanor.attributes`.

"""
from typing import Any

import pytest

from sqlathanor._compat import is_py36

if is_py36:
    from pydantic import BaseModel
    from pydantic.fields import Field, ModelField

    class PydanticModel(BaseModel):
        field_1: int
        field_2: str
        field_3: Any
else:
    def Field(*args, **kwargs):
        return None
    PydanticModel = 'Python <3.6'


from sqlathanor.attributes import AttributeConfiguration, validate_serialization_config, \
    BLANK_ON_SERIALIZE
from sqlathanor.utilities import bool_to_tuple, callable_to_dict
from sqlathanor.errors import FieldNotFoundError


@pytest.mark.parametrize('kwargs', [
    (None),
    ({
        'name': 'test_name',
        'supports_csv': False,
        'csv_sequence': None,
        'supports_json': False,
        'supports_yaml': False,
        'supports_dict': False,
        'on_serialize': None,
        'on_deserialize': None
    }),
    ({
        'name': 'test_callable',
        'supports_csv': (True, False),
        'csv_sequence': 34,
        'supports_json': (False, False),
        'supports_yaml': (True, False),
        'supports_dict': (False, True),
        'on_serialize': bool_to_tuple,
        'on_deserialize': bool_to_tuple
    }),
    ({
        'name': 'test_display_name',
        'supports_csv': False,
        'csv_sequence': None,
        'supports_json': False,
        'supports_yaml': False,
        'supports_dict': False,
        'on_serialize': None,
        'on_deserialize': None,
        'display_name': 'some_display_name'
    }),
    ({
        'name': 'test_pydantic_field',
        'supports_csv': False,
        'csv_sequence': None,
        'supports_json': False,
        'supports_yaml': False,
        'supports_dict': False,
        'on_serialize': None,
        'on_deserialize': None,
        'pydantic_field': Field(alias = 'test_pydantic_field',
                                title = 'Test Pydantic Field')
    })
])
def test_AttributeConfiguration__init__(kwargs):
    if kwargs is None:
        result = AttributeConfiguration()
        kwargs = {}
    else:
        result = AttributeConfiguration(**kwargs)

    assert result.name == kwargs.get('name', None)
    assert result.display_name == kwargs.get('display_name', None)
    assert result.pydantic_field == kwargs.get('pydantic_field', None)
    assert result.supports_csv == bool_to_tuple(kwargs.get('supports_csv',
                                                           (False, False)))
    assert result.csv_sequence == kwargs.get('csv_sequence', None)
    assert result.supports_json == bool_to_tuple(kwargs.get('supports_json',
                                                            (False, False)))
    assert result.supports_yaml == bool_to_tuple(kwargs.get('supports_yaml',
                                                            (False, False)))
    assert result.supports_dict == bool_to_tuple(kwargs.get('supports_dict',
                                                            (False, False)))

    assert result.on_serialize is not None
    assert isinstance(result.on_serialize, dict)
    input_on_serialize = callable_to_dict(
        kwargs.get('on_serialize', BLANK_ON_SERIALIZE) or BLANK_ON_SERIALIZE
    )
    for key in result.on_serialize:
        assert key in input_on_serialize
        assert result.on_serialize[key] == input_on_serialize[key]

    assert result.on_deserialize is not None
    assert isinstance(result.on_deserialize, dict)

    input_on_deserialize = callable_to_dict(
        kwargs.get('on_deserialize', BLANK_ON_SERIALIZE) or BLANK_ON_SERIALIZE
    )

    for key in result.on_deserialize:
        assert key in input_on_deserialize
        assert result.on_deserialize[key] == input_on_deserialize[key]


@pytest.mark.parametrize('key, value, expected_result, error', [
    ('name', 'test_name', 'test_name', None),
    ('name', 123, None, (ValueError, TypeError)),
    ('supports_csv', True, (True, True), None),
    ('supports_csv', (True, False), (True, False), None),
    ('on_serialize', None, BLANK_ON_SERIALIZE, None),
    ('on_deserialize', None, BLANK_ON_SERIALIZE, None),
    ('on_serialize', bool_to_tuple, {
        'csv': bool_to_tuple,
        'json': bool_to_tuple,
        'yaml': bool_to_tuple,
        'dict': bool_to_tuple
    }, None),
    ('random_key', 'test', 'test', None),
])
def test_AttributeConfiguration__get_set__(key, value, expected_result, error):
    config = AttributeConfiguration()
    if not error:
        config[key] = value
        assert key in config
        assert config[key] == expected_result
        assert getattr(config, key) == expected_result
    else:
        with pytest.raises(error):
            config[key] = value


def test_AttributeConfiguration__missing_key():
    config = AttributeConfiguration()
    with pytest.raises(KeyError):
        assert config['key'] is not None


@pytest.mark.parametrize('key, expected_result', [
    ('name', True),
    ('supports_csv', True),
    ('csv_sequence', True),
    ('supports_json', True),
    ('supports_yaml', True),
    ('supports_dict', True),
    ('on_serialize', True),
    ('on_deserialize', True),
    ('supports_xml', False),
    ('random_key', False),
])
def test_AttributeConfiguration__contains__(key, expected_result):
    config = AttributeConfiguration()
    assert (key in config) is expected_result


def test_AttributeConfiguration_keys():
    config = AttributeConfiguration()
    keys = config.keys()
    assert keys is not None
    assert len(keys) == len(config)


def test_AttributeConfiguration__iterate__():
    config = AttributeConfiguration()
    length = len(config)
    index = 0
    for key in config:
        index += 1

    assert index == length

    assert len(config.values()) == len(config) == len(config.keys()) == index


if is_py36:
    @pytest.mark.parametrize('model, name, error', [
        (PydanticModel, 'field_1', None),
        (PydanticModel, 'missing_field', FieldNotFoundError),
    ])
    def test_AttributeConfiguration_from_pydantic_model(model, name, error):
        if not error:
            result = AttributeConfiguration.from_pydantic_model(model, name)
            assert result.name == name
            assert result.pydantic_field is not None
            assert isinstance(result.pydantic_field, ModelField)
        else:
            with pytest.raises(error):
                result = AttributeConfiguration.from_pydantic_model(model, name)


@pytest.mark.parametrize('config, expected_length', [
    ([], 0),
    (None, 0),
    (AttributeConfiguration(), 1),
    ([AttributeConfiguration()], 1),
    ([AttributeConfiguration(), AttributeConfiguration()], 1),
    ({ 'name': 'test_1' }, 1),
    ([{ 'name': 'test_2' }, {'name': 'test_3'}], 2),
    (PydanticModel, 3),
])
def test_validate_serialization_config(config, expected_length):
    if config == 'Python <3.6':
        config = None
        expected_length = 0
    result = validate_serialization_config(config)
    assert len(result) == expected_length
    if len(result) > 0:
        for item in result:
            assert isinstance(item, AttributeConfiguration)
