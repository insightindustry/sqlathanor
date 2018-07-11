.. seealso::

  * :doc:`Error Reference <errors>`
  * :ref:`De-serializing Data <deserialization>`
  * :ref:`Configuring Pre-processing and Post-processing <extra_processing>`

.. code-block:: python

  from sqlathanor.errors import DeserializableAttributeError, \
    CSVStructureError, DeserializationError, ValueDeserializationError, \
    ExtraKeysError, UnsupportedDeserializationError

  # For a SQLAlchemy Model Class named "User" and a model instance named "user",
  # with serialized data in "as_csv", "as_json", "as_yaml", and "as_dict" respectively.

  try:
    user.update_from_csv(as_csv)
    user.update_from_json(as_json)
    user.update_from_yaml(as_yaml)
    user.update_from_dict(as_dict)

    new_user = User.new_from_csv(as_csv)
    new_user = User.new_from_json(as_json)
    new_user = User.new_from_yaml(as_yaml)
    new_user = User.new_from_dict(as_dict)
  except DeserializableAttributeError as error:
    # Handle the situation where "User" model class does not have any attributes
    # de-serializable from the given format (CSV, JSON, YAML, or dict).
    pass
  except DeserializationError as error:
    # Handle the situation where the serialized object ("as_csv", "as_json",
    # "as_yaml", "as_dict") cannot be parsed, for example because it is not
    # valid JSON, YAML, or dict.
    pass
  except CSVStructureError as error:
    # Handle the situation where the structure of "as_csv" does not match the
    # expectation configured for the "User" model class.
    raise error
  except ExtraKeysError as error:
    # Handle the situation where the serialized object ("as_json",
    # "as_yaml", "as_dict") may have unexpected keys/attributes and
    # the error_on_extra_keys argument is False.
    #
    # Applies to: *_from_json(), *_from_yaml(), and *_from_dict() methods
    pass
  except ValueDeserializationError as error:
    # Handle the situation where an input value in the serialized object
    # raises an exception in the deserialization post-processing function.
    pass
  except UnsupportedDeserializationError as error:
    # Handle the situation where the de-serialization process attempts to
    # assign a value to an attribute that does not support de-serialization.
    pass
