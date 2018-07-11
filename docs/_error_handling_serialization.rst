.. seealso::

  * :doc:`Error Reference <errors>`
  * :ref:`Serializing a Model Instance <serialization>`
  * :doc:`Default Serialization Functions <default_serialization_functions>`

.. code-block:: python

  from sqlathanor.errors import SerializableAttributeError, \
    UnsupportedSerializationError, MaximumNestingExceededError

  # For a SQLAlchemy Model Class named "User" and a model instance named "user".

  try:
    as_csv = user.to_csv()
    as_json = user.to_json()
    as_yaml = user.to_yaml()
    as_dict = user.to_dict()
  except SerializableAttributeError as error:
    # Handle the situation where "User" model class does not have any attributes
    # serializable to JSON.
    pass
  except UnsupportedSerializationError as error:
    # Handle the situation where one of the "User" model attributes is of a data
    # type that does not support serialization.
    pass
  except MaximumNestingExceededError as error:
    # Handle a situation where "user.to_json()" received max_nesting less than
    # current_nesting.
    #
    # This situation is typically an error on the programmer's part, since
    # SQLAthanor by default avoids this kind of situation.
    #
    # Best practice is simply to let this exception bubble up.
    raise error
