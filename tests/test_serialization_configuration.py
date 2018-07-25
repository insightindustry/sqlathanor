# -*- coding: utf-8 -*-

"""
******************************************
tests.test_serialization_configuration
******************************************

Tests for declarative :class:`BaseModel` and the ability to retireve serialization
configuration data.

"""

import pytest

from validator_collection import checkers

from sqlathanor import Column
from sqlathanor.attributes import BLANK_ON_SERIALIZE, AttributeConfiguration
from sqlathanor.errors import UnsupportedSerializationError

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_single_pk, model_composite_pk, instance_single_pk, instance_composite_pk, \
    model_complex, model_complex_meta, instance_complex, instance_complex_meta, \
    original_hybrid_config

def test_func():
    pass


@pytest.mark.parametrize('test_index, expected_result', [
    (0, True),
    (1, True),
])
def test_model___serialization__(request,
                                 model_complex_meta,
                                 test_index,
                                 expected_result):
    target = model_complex_meta[test_index]
    result = hasattr(target, '__serialization__')
    assert result == expected_result

@pytest.mark.parametrize('test_index, expected_result', [
    (0, True),
    (1, True),
])
def test_instance__serialization__(request,
                                   instance_complex_meta,
                                   test_index,
                                   expected_result):
    target = instance_complex_meta[0][test_index]
    result = hasattr(target, '__serialization__')
    assert result == expected_result


@pytest.mark.parametrize('test_index, include_private, exclude_methods, expected_length', [
    (0, False, True, 10),
    (0, True, True, 13),
    (0, False, False, 35),
    (0, False, False, 35),
])
def test_model__get_instance_attributes(request,
                                        model_complex_meta,
                                        test_index,
                                        include_private,
                                        exclude_methods,
                                        expected_length):
    target = model_complex_meta[test_index]
    instance_attributes = target._get_instance_attributes(
        include_private = include_private,
        exclude_methods = exclude_methods
    )
    print(instance_attributes)
    assert len(instance_attributes) == expected_length


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
    }, True, 8),
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
    }, True, 4),
])
def test_model__get_declarative_serializable_attributes(request,
                                                        model_complex,
                                                        model_complex_meta,
                                                        use_meta,
                                                        test_index,
                                                        format_support,
                                                        exclude_private,
                                                        expected_length):
    if not use_meta:
        model = model_complex
    else:
        model = model_complex_meta

    target = model[test_index]

    result = target._get_declarative_serializable_attributes(
        exclude_private = exclude_private,
        **format_support
    )

    print(result)

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
    }, 4),
    (True, 0, {
        'from_csv': True,
        'to_csv': None,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 4),
    (True, 0, {
        'from_csv': None,
        'to_csv': False,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 2),
    (True, 0, {
        'from_csv': True,
        'to_csv': False,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 1),
    (True, 0, {
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
                                                 model_complex,
                                                 model_complex_meta,
                                                 use_meta,
                                                 test_index,
                                                 format_support,
                                                 expected_length):
    if not use_meta:
        model = model_complex
    else:
        model = model_complex_meta

    target = model[test_index]

    result = target._get_meta_serializable_attributes(
        **format_support
    )

    for item in result:
        print(item.name)

    assert len(result) == expected_length


@pytest.mark.parametrize('use_meta, test_index, expected_length', [
    (False, 0, 4),
    (True, 0, 5),
])
def test_model__get_attribute_configurations(request,
                                             model_complex,
                                             model_complex_meta,
                                             use_meta,
                                             test_index,
                                             expected_length):
    if not use_meta:
        model = model_complex
    else:
        model = model_complex_meta

    target = model[test_index]

    result = target._get_attribute_configurations()

    for item in result:
        print(item.name)

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
    }, 4),
    (True, 0, {
        'from_csv': True,
        'to_csv': None,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 4),
    (True, 0, {
        'from_csv': None,
        'to_csv': False,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 7),
    (True, 0, {
        'from_csv': True,
        'to_csv': False,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 1),
    (True, 0, {
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
def test_model_get_serialization_config(request,
                                        model_complex,
                                        model_complex_meta,
                                        use_meta,
                                        test_index,
                                        format_support,
                                        expected_length):
    if not use_meta:
        model = model_complex
    else:
        model = model_complex_meta

    target = model[test_index]

    result = target.get_serialization_config(
        **format_support
    )

    for item in result:
        print(item.name)

    assert len(result) == expected_length


@pytest.mark.parametrize('use_meta, test_index, deserialize, serialize, expected_length', [
    (False, 0, False, False, 7),
    (True, 0, True, False, 1),
    (True, 0, False, True, 0),
    (True, 0, True, True, 3),
    (False, 0, None, None, 0),
    (True, 0, True, None, 4),
    (True, 0, None, True, 3),
    (True, 0, False, None, 6),
    (True, 0, None, False, 7),
    (True, 0, None, None, 0),
])
def test_model_csv_serialization_config(request,
                                        model_complex,
                                        model_complex_meta,
                                        use_meta,
                                        test_index,
                                        deserialize,
                                        serialize,
                                        expected_length):
    if not use_meta:
        model = model_complex
    else:
        model = model_complex_meta

    target = model[test_index]

    result = target.get_csv_serialization_config(deserialize = deserialize,
                                                 serialize = serialize)

    for item in result:
        print(item.name)

    assert len(result) == expected_length


@pytest.mark.parametrize('use_meta, test_index, deserialize, serialize, expected_length', [
    (False, 0, False, False, 6),
    (True, 0, True, False, 1),
    (True, 0, False, True, 0),
    (True, 0, True, True, 4),
    (False, 0, None, None, 0),
    (True, 0, True, None, 5),
    (True, 0, None, True, 4),
    (True, 0, False, None, 5),
    (True, 0, None, False, 6),
    (True, 0, None, None, 0),
])
def test_model_json_serialization_config(request,
                                         model_complex,
                                         model_complex_meta,
                                         use_meta,
                                         test_index,
                                         deserialize,
                                         serialize,
                                         expected_length):
    if not use_meta:
        model = model_complex
    else:
        model = model_complex_meta

    target = model[test_index]

    result = target.get_json_serialization_config(deserialize = deserialize,
                                                  serialize = serialize)

    for item in result:
        print(item.name)

    assert len(result) == expected_length


@pytest.mark.parametrize('use_meta, test_index, deserialize, serialize, expected_length', [
    (False, 0, False, False, 6),
    (True, 0, True, False, 1),
    (True, 0, False, True, 0),
    (True, 0, True, True, 4),
    (False, 0, None, None, 0),
    (True, 0, True, None, 5),
    (True, 0, None, True, 4),
    (True, 0, False, None, 5),
    (True, 0, None, False, 6),
    (True, 0, None, None, 0),
])
def test_model_yaml_serialization_config(request,
                                         model_complex,
                                         model_complex_meta,
                                         use_meta,
                                         test_index,
                                         deserialize,
                                         serialize,
                                         expected_length):
    if not use_meta:
        model = model_complex
    else:
        model = model_complex_meta

    target = model[test_index]

    result = target.get_yaml_serialization_config(deserialize = deserialize,
                                                  serialize = serialize)

    for item in result:
        print(item.name)

    assert len(result) == expected_length


@pytest.mark.parametrize('use_meta, test_index, deserialize, serialize, expected_length', [
    (False, 0, False, False, 6),
    (True, 0, True, False, 2),
    (True, 0, False, True, 0),
    (True, 0, True, True, 3),
    (False, 0, None, None, 0),
    (True, 0, True, None, 5),
    (True, 0, None, True, 3),
    (True, 0, False, None, 5),
    (True, 0, None, False, 7),
    (True, 0, None, None, 0),
])
def test_model_dict_serialization_config(request,
                                         model_complex,
                                         model_complex_meta,
                                         use_meta,
                                         test_index,
                                         deserialize,
                                         serialize,
                                         expected_length):
    if not use_meta:
        model = model_complex
    else:
        model = model_complex_meta

    target = model[test_index]

    result = target.get_dict_serialization_config(deserialize = deserialize,
                                                  serialize = serialize)

    for item in result:
        print(item.name)

    assert len(result) == expected_length


@pytest.mark.parametrize('use_meta, test_index, attribute, returns_value', [
    (False, 0, 'hybrid', False),
    (True, 0, 'hybrid', True),
    (True, 0, 'password', True),
    (True, 0, 'hybrid_differentiated', False),
    (True, 0, 'missing-attribute', False),
])
def test_model_get_attribute_serialization_config(request,
                                                  model_complex,
                                                  model_complex_meta,
                                                  use_meta,
                                                  test_index,
                                                  attribute,
                                                  returns_value):
    if not use_meta:
        model = model_complex
    else:
        model = model_complex_meta

    target = model[test_index]

    result = target.get_attribute_serialization_config(attribute)

    assert (result is not None) is returns_value


@pytest.mark.parametrize('use_meta, test_index, attribute, format_support, returns_value, fails', [
    (False, 0, 'id', {
        'from_csv': None,
        'to_csv': None,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, None, False),
    (True, 0, 'name', {
        'from_csv': True,
        'to_csv': None,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, True, False),
    (True, 0, 'password',{
        'from_csv': True,
        'to_csv': None,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, True, False),
    (True, 0, 'password',{
        'from_csv': None,
        'to_csv': True,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, False, False),
    (True, 0, 'missing-attribute',{
        'from_csv': None,
        'to_csv': True,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, False, True),
])
def test_model_does_support_serialization(request,
                                          model_complex,
                                          model_complex_meta,
                                          use_meta,
                                          test_index,
                                          attribute,
                                          format_support,
                                          returns_value,
                                          fails):
    if not use_meta:
        model = model_complex
    else:
        model = model_complex_meta

    target = model[test_index]

    if not fails:
        result = target.does_support_serialization(attribute,
                                                   **format_support)

        assert result is returns_value
    else:
        with pytest.raises(UnsupportedSerializationError):
            result = target.does_support_serialization(attribute,
                                                       **format_support)

@pytest.mark.parametrize('use_meta, test_index, expected_length', [
    (False, 0, 4),
    (True, 0, 5),
])
def test_instance__get_attribute_configurations(request,
                                                instance_complex,
                                                instance_complex_meta,
                                                use_meta,
                                                test_index,
                                                expected_length):
    if not use_meta:
        instance = instance_complex
    else:
        instance = instance_complex_meta

    target = instance[0][test_index]

    result = target._get_attribute_configurations()

    for item in result:
        print(item.name)

    assert len(result) == expected_length


@pytest.mark.parametrize('use_meta, test_index, attribute, returns_value', [
    (False, 0, 'hybrid', False),
    (True, 0, 'hybrid', True),
    (True, 0, 'password', True),
    (True, 0, 'hybrid_differentiated', False),
    (True, 0, 'missing-attribute', False),
])
def test_instance_get_attribute_serialization_config(request,
                                                     instance_complex,
                                                     instance_complex_meta,
                                                     use_meta,
                                                     test_index,
                                                     attribute,
                                                     returns_value):
    if not use_meta:
        instance = instance_complex
    else:
        instance = instance_complex_meta

    target = instance[0][test_index]

    result = target.get_attribute_serialization_config(attribute)

    assert (result is not None) is returns_value

@pytest.mark.parametrize('use_meta, test_index, attribute, params, expected_result_params', [
    (False, 0, 'hybrid', {
        'config': None,
        'supports_csv': True,
        'csv_sequence': None,
        'supports_json': (True, False),
        'supports_yaml': False,
        'on_serialize': None,
        'on_deserialize': test_func
        },
     {
         'supports_csv': (True, True),
         'supports_json': (True, False),
         'supports_yaml': (False, False),
         'supports_dict': (False, False),
         'csv_sequence': None,
         'on_deserialize': {
             'csv': test_func,
             'json': test_func,
             'yaml': test_func,
             'dict': test_func
         },
         'on_serialize': {
             'csv': None,
             'json': None,
             'yaml': None,
             'dict': None
         }
     }
    ),
    (True, 0, 'hybrid', {
        'config': AttributeConfiguration(name = 'hybrid',
                                         supports_csv = False,
                                         supports_json = True,
                                         supports_yaml = True,
                                         supports_dict = True,
                                         on_deserialize = test_func,
                                         on_serialize = test_func)
        },
     {
         'supports_csv': (False, False),
         'supports_json': (True, True),
         'supports_yaml': (True, True),
         'supports_dict': (True, True),
         'csv_sequence': None,
         'on_deserialize': {
             'csv': test_func,
             'json': test_func,
             'yaml': test_func,
             'dict': test_func
         },
         'on_serialize': {
             'csv': test_func,
             'json': test_func,
             'yaml': test_func,
             'dict': test_func
         }
     }
    ),
    (False, 0, 'hybrid', {
        'config': AttributeConfiguration(name = 'hybrid',
                                         supports_csv = True,
                                         supports_json = True,
                                         supports_yaml = True,
                                         supports_dict = True,
                                         csv_sequence = 7,
                                         on_deserialize = test_func,
                                         on_serialize = test_func)
        },
     {
         'supports_csv': (True, True),
         'supports_json': (True, True),
         'supports_yaml': (True, True),
         'supports_dict': (True, True),
         'csv_sequence': 7,
         'on_deserialize': {
             'csv': test_func,
             'json': test_func,
             'yaml': test_func,
             'dict': test_func
         },
         'on_serialize': {
             'csv': test_func,
             'json': test_func,
             'yaml': test_func,
             'dict': test_func
         }
     }
    ),
])
def test_instance_set_attribute_serialization_config(request,
                                                     model_complex,
                                                     model_complex_meta,
                                                     instance_complex,
                                                     instance_complex_meta,
                                                     original_hybrid_config,
                                                     use_meta,
                                                     test_index,
                                                     attribute,
                                                     params,
                                                     expected_result_params):
    if not use_meta:
        model = model_complex[test_index]
        target = instance_complex[0][test_index]
    else:
        model = model_complex_meta[test_index]
        target = instance_complex_meta[0][test_index]

    target.set_attribute_serialization_config(attribute, **params)

    result = target.get_attribute_serialization_config(attribute)
    assert result.supports_csv == expected_result_params.get('supports_csv')
    assert result.csv_sequence == expected_result_params.get('csv_sequence')
    assert result.supports_json == expected_result_params.get('supports_json')
    assert result.supports_yaml == expected_result_params.get('supports_yaml')
    assert result.supports_dict == expected_result_params.get('supports_dict')
    assert checkers.are_dicts_equivalent(result.on_deserialize,
                                         expected_result_params.get('on_deserialize'))
    assert checkers.are_dicts_equivalent(result.on_serialize,
                                         expected_result_params.get('on_serialize'))

    updated_model_config = model.get_attribute_serialization_config(attribute)

    assert updated_model_config.supports_csv == expected_result_params.get('supports_csv')
    assert updated_model_config.csv_sequence == expected_result_params.get('csv_sequence')
    assert updated_model_config.supports_json == expected_result_params.get('supports_json')
    assert updated_model_config.supports_yaml == expected_result_params.get('supports_yaml')
    assert updated_model_config.supports_dict == expected_result_params.get('supports_dict')
    assert checkers.are_dicts_equivalent(updated_model_config.on_deserialize,
                                         expected_result_params.get('on_deserialize'))
    assert checkers.are_dicts_equivalent(updated_model_config.on_serialize,
                                         expected_result_params.get('on_serialize'))

    model.set_attribute_serialization_config(
        attribute,
        config = original_hybrid_config,
        supports_csv = True,
        supports_json = True,
        supports_yaml = True,
        supports_dict = True,
        csv_sequence = False,
        on_serialize = False,
        on_deserialize = False)

    target.set_attribute_serialization_config(
        attribute,
        config = original_hybrid_config,
        supports_csv = True,
        supports_json = True,
        supports_yaml = True,
        supports_dict = True,
        csv_sequence = False,
        on_serialize = False,
        on_deserialize = False)


@pytest.mark.parametrize('use_meta, test_index, attribute, params, expected_result_params', [
    (False, 0, 'hybrid', {
        'config': None,
        'supports_csv': True,
        'csv_sequence': None,
        'supports_json': (True, False),
        'supports_yaml': False,
        'on_serialize': None,
        'on_deserialize': test_func
        },
     {
         'supports_csv': (True, True),
         'supports_json': (True, False),
         'supports_yaml': (False, False),
         'supports_dict': (False, False),
         'csv_sequence': None,
         'on_deserialize': {
             'csv': test_func,
             'json': test_func,
             'yaml': test_func,
             'dict': test_func
         },
         'on_serialize': {
             'csv': None,
             'json': None,
             'yaml': None,
             'dict': None
         }
     }
    ),
    (False, 0, 'hybrid', {
        'config': AttributeConfiguration(name = 'hybrid',
                                         supports_csv = True,
                                         supports_json = True,
                                         supports_yaml = True,
                                         supports_dict = True,
                                         csv_sequence = 7,
                                         on_deserialize = test_func,
                                         on_serialize = test_func)
        },
     {
         'supports_csv': (True, True),
         'supports_json': (True, True),
         'supports_yaml': (True, True),
         'supports_dict': (True, True),
         'csv_sequence': 7,
         'on_deserialize': {
             'csv': test_func,
             'json': test_func,
             'yaml': test_func,
             'dict': test_func
         },
         'on_serialize': {
             'csv': test_func,
             'json': test_func,
             'yaml': test_func,
             'dict': test_func
         }
     }
    ),
    (True, 0, 'hybrid',
     {
         'config': AttributeConfiguration(name = 'hybrid',
                                          supports_csv = False,
                                          supports_json = True,
                                          supports_yaml = True,
                                          supports_dict = True,
                                          csv_sequence = None,
                                          on_deserialize = test_func,
                                          on_serialize = test_func),
         'csv_sequence': None
     },
     {
         'supports_csv': (False, False),
         'supports_json': (True, True),
         'supports_yaml': (True, True),
         'supports_dict': (True, True),
         'csv_sequence': None,
         'on_deserialize': {
             'csv': test_func,
             'json': test_func,
             'yaml': test_func,
             'dict': test_func
         },
         'on_serialize': {
             'csv': test_func,
             'json': test_func,
             'yaml': test_func,
             'dict': test_func
         }
     }
    ),
])
def test_model_set_attribute_serialization_config(request,
                                                  model_complex,
                                                  model_complex_meta,
                                                  original_hybrid_config,
                                                  use_meta,
                                                  test_index,
                                                  attribute,
                                                  params,
                                                  expected_result_params):
    if not use_meta:
        model = model_complex
    else:
        model = model_complex_meta

    target = model[test_index]

    target.set_attribute_serialization_config(attribute, **params)

    result = target.get_attribute_serialization_config(attribute)
    assert result.supports_csv == expected_result_params.get('supports_csv')
    assert result.csv_sequence == expected_result_params.get('csv_sequence')
    assert result.supports_json == expected_result_params.get('supports_json')
    assert result.supports_yaml == expected_result_params.get('supports_yaml')
    assert result.supports_dict == expected_result_params.get('supports_dict')
    assert checkers.are_dicts_equivalent(result.on_deserialize,
                                         expected_result_params.get('on_deserialize'))
    assert checkers.are_dicts_equivalent(result.on_serialize,
                                         expected_result_params.get('on_serialize'))

    target.set_attribute_serialization_config(attribute,
                                              config = original_hybrid_config,
                                              supports_csv = True,
                                              supports_json = True,
                                              supports_yaml = True,
                                              supports_dict = True,
                                              csv_sequence = False,
                                              on_serialize = False,
                                              on_deserialize = False)

    assert target.get_attribute_serialization_config(attribute).supports_csv == \
        (True, True)


@pytest.mark.parametrize('test_index, include_private, exclude_methods, expected_length', [
    (0, False, True, 10),
    (0, True, True, 13),
    (0, False, False, 35),
    (0, False, False, 35),
])
def test_instance__get_instance_attributes(request,
                                           instance_complex_meta,
                                           test_index,
                                           include_private,
                                           exclude_methods,
                                           expected_length):
    target = instance_complex_meta[0][test_index]
    instance_attributes = target._get_instance_attributes(
        include_private = include_private,
        exclude_methods = exclude_methods
    )
    print(instance_attributes)
    assert len(instance_attributes) == expected_length


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
    }, True, 8),
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
    }, True, 4),
])
def test_instance__get_declarative_serializable_attributes(request,
                                                           instance_complex,
                                                           instance_complex_meta,
                                                           use_meta,
                                                           test_index,
                                                           format_support,
                                                           exclude_private,
                                                           expected_length):
    if not use_meta:
        instance = instance_complex
    else:
        instance = instance_complex_meta

    target = instance[0][test_index]

    result = target._get_declarative_serializable_attributes(
        exclude_private = exclude_private,
        **format_support
    )

    print(result)

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
    }, 4),
    (True, 0, {
        'from_csv': True,
        'to_csv': None,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 4),
    (True, 0, {
        'from_csv': None,
        'to_csv': False,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 2),
    (True, 0, {
        'from_csv': True,
        'to_csv': False,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 1),
    (True, 0, {
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
def test_instance__get_meta_serializable_attributes(request,
                                                    instance_complex,
                                                    instance_complex_meta,
                                                    use_meta,
                                                    test_index,
                                                    format_support,
                                                    expected_length):
    if not use_meta:
        instance = instance_complex
    else:
        instance = instance_complex_meta

    target = instance[0][test_index]

    result = target._get_meta_serializable_attributes(
        **format_support
    )

    for item in result:
        print(item.name)

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
    }, 4),
    (True, 0, {
        'from_csv': True,
        'to_csv': None,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 4),
    (True, 0, {
        'from_csv': None,
        'to_csv': False,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 7),
    (True, 0, {
        'from_csv': True,
        'to_csv': False,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, 1),
    (True, 0, {
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
def test_instance_get_serialization_config(request,
                                           instance_complex,
                                           instance_complex_meta,
                                           use_meta,
                                           test_index,
                                           format_support,
                                           expected_length):
    if not use_meta:
        instance = instance_complex
    else:
        instance = instance_complex_meta

    target = instance[0][test_index]

    result = target.get_serialization_config(
        **format_support
    )

    for item in result:
        print(item.name)

    assert len(result) == expected_length


@pytest.mark.parametrize('use_meta, test_index, deserialize, serialize, expected_length', [
    (False, 0, False, False, 6),
    (True, 0, True, False, 1),
    (True, 0, False, True, 0),
    (True, 0, True, True, 3),
    (False, 0, None, None, 0),
    (True, 0, True, None, 4),
    (True, 0, None, True, 3),
    (True, 0, False, None, 6),
    (True, 0, None, False, 7),
    (True, 0, None, None, 0),
])
def test_instance_csv_serialization_config(request,
                                           instance_complex,
                                           instance_complex_meta,
                                           use_meta,
                                           test_index,
                                           deserialize,
                                           serialize,
                                           expected_length):
    if not use_meta:
        instance = instance_complex
    else:
        instance = instance_complex_meta

    target = instance[0][test_index]

    result = target.get_csv_serialization_config(deserialize = deserialize,
                                                 serialize = serialize)

    for item in result:
        print(item.name)

    assert len(result) == expected_length


@pytest.mark.parametrize('use_meta, test_index, deserialize, serialize, expected_length', [
    (False, 0, False, False, 5),
    (True, 0, True, False, 1),
    (True, 0, False, True, 0),
    (True, 0, True, True, 4),
    (False, 0, None, None, 0),
    (True, 0, True, None, 5),
    (True, 0, None, True, 4),
    (True, 0, False, None, 5),
    (True, 0, None, False, 6),
    (True, 0, None, None, 0),
])
def test_instance_json_serialization_config(request,
                                            instance_complex,
                                            instance_complex_meta,
                                            use_meta,
                                            test_index,
                                            deserialize,
                                            serialize,
                                            expected_length):
    if not use_meta:
        instance = instance_complex
    else:
        instance = instance_complex_meta

    target = instance[0][test_index]

    result = target.get_json_serialization_config(deserialize = deserialize,
                                                  serialize = serialize)

    for item in result:
        print(item.name)

    assert len(result) == expected_length


@pytest.mark.parametrize('use_meta, test_index, deserialize, serialize, expected_length', [
    (False, 0, False, False, 5),
    (True, 0, True, False, 1),
    (True, 0, False, True, 0),
    (True, 0, True, True, 4),
    (False, 0, None, None, 0),
    (True, 0, True, None, 5),
    (True, 0, None, True, 4),
    (True, 0, False, None, 5),
    (True, 0, None, False, 6),
    (True, 0, None, None, 0),
])
def test_instance_yaml_serialization_config(request,
                                            instance_complex,
                                            instance_complex_meta,
                                            use_meta,
                                            test_index,
                                            deserialize,
                                            serialize,
                                            expected_length):
    if not use_meta:
        instance = instance_complex
    else:
        instance = instance_complex_meta

    target = instance[0][test_index]

    result = target.get_yaml_serialization_config(deserialize = deserialize,
                                                  serialize = serialize)

    for item in result:
        print(item.name)

    assert len(result) == expected_length


@pytest.mark.parametrize('use_meta, test_index, deserialize, serialize, expected_length', [
    (False, 0, False, False, 5),
    (True, 0, True, False, 2),
    (True, 0, False, True, 0),
    (True, 0, True, True, 3),
    (False, 0, None, None, 0),
    (True, 0, True, None, 5),
    (True, 0, None, True, 3),
    (True, 0, False, None, 5),
    (True, 0, None, False, 7),
    (True, 0, None, None, 0),
])
def test_instance_dict_serialization_config(request,
                                            instance_complex,
                                            instance_complex_meta,
                                            use_meta,
                                            test_index,
                                            deserialize,
                                            serialize,
                                            expected_length):
    if not use_meta:
        instance = instance_complex
    else:
        instance = instance_complex_meta

    target = instance[0][test_index]

    result = target.get_dict_serialization_config(deserialize = deserialize,
                                                  serialize = serialize)

    for item in result:
        print(item.name)

    assert len(result) == expected_length


@pytest.mark.parametrize('use_meta, test_index, attribute, format_support, returns_value, fails', [
    (False, 0, 'id', {
        'from_csv': None,
        'to_csv': None,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, None, False),
    (True, 0, 'name', {
        'from_csv': True,
        'to_csv': None,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, True, False),
    (True, 0, 'password',{
        'from_csv': True,
        'to_csv': None,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, True, False),
    (True, 0, 'password',{
        'from_csv': None,
        'to_csv': True,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, False, False),
    (True, 0, 'missing-attribute',{
        'from_csv': None,
        'to_csv': True,
        'from_json': None,
        'to_json': None,
        'from_yaml': None,
        'to_yaml': None,
        'from_dict': None,
        'to_dict': None
    }, False, True),
])
def test_instance_does_support_serialization(request,
                                             instance_complex,
                                             instance_complex_meta,
                                             use_meta,
                                             test_index,
                                             attribute,
                                             format_support,
                                             returns_value,
                                             fails):
    if not use_meta:
        instance = instance_complex
    else:
        instance = instance_complex_meta

    target = instance[0][test_index]

    if not fails:
        result = target.does_support_serialization(attribute,
                                                   **format_support)

        assert result is returns_value
    else:
        with pytest.raises(UnsupportedSerializationError):
            result = target.does_support_serialization(attribute,
                                                       **format_support)
