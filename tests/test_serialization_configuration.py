# -*- coding: utf-8 -*-

"""
***********************************
tests.test_serialization_configuration
***********************************

Tests for declarative :class:`BaseModel` and the ability to retireve serialization
configuration data.

"""

import pytest

from sqlathanor import Column

from tests.fixtures import db_engine, tables, base_model, db_session, \
    model_single_pk, model_composite_pk, instance_single_pk, instance_composite_pk, \
    model_complex, model_complex_meta, instance_complex, instance_complex_meta


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
    (0, False, False, 24),
    (0, False, False, 24),
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
        with pytest.raises(AttributeError):
            result = target.does_support_serialization(attribute,
                                                       **format_support)





@pytest.mark.parametrize('test_index, include_private, exclude_methods, expected_length', [
    (0, False, True, 10),
    (0, True, True, 13),
    (0, False, False, 24),
    (0, False, False, 24),
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
        with pytest.raises(AttributeError):
            result = target.does_support_serialization(attribute,
                                                       **format_support)
