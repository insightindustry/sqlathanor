******************************************
SQLAthanor and Pydantic
******************************************

.. |strong| raw:: html

 <strong>

.. |/strong| raw:: html

 </strong>

.. contents::
  :local:
  :depth: 3
  :backlinks: entry

----------

.. versionadded:: 0.8.0

SQLAthanor, Pydantic, and FastAPI
=====================================

.. sidebar:: Some Caveats

  I'm a huge fan of the `Pydantic`_ library. Its authors have made many choices that I
  would not have made, but that does not change my immense respect for the work they have
  done. My interpretation of "priorities" below reflects my subjective evaluation of the
  library and its API semantics, and from my experience using the library in a number of
  web application projects of varying complexity.

  My observations are in no way meant to be a criticism: They are merely an observation of
  where the libraries have taken different philosophical and stylistic paths.

  My respect for `Pydantic`_ is one of the main reasons why I have decided to extend
  **SQLAthanor** with built-in support for the `Pydantic`_ library.

**SQLAthanor** and `Pydantic`_ are both concerned with the serialization and
deserialization of data. However, they approach the topic from different angles and have
made a variety of (very different) architectural and stylistic choices. These choices
reflect a different set of priorities:

.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - SQLAthanor Priorities
     - Pydantic Priorities
   * - Database/ORM compatibility with `SQLAlchemy`_
     - Database/ORM agnosticism
   * - The maintenance of a single representation of your data model, tied to its database implementation
     - Multiple representations of your data model, each of which is tied to its usage in your code
   * - Explicit reference and conceptual documentation
     - Documentation by example / in code
   * - Explicit APIs for the data model's lifecycle
     - Implicit APIs relying on the Python standard library

Both libraries have their place: in general terms, if I were working on a simple web
application, on a microservice, or on a relatively simple data model I would consider
`Pydantic`_ as a perfectly viable "quick-and-dirty" option. Its use of Python's native
typing hints/annotation is a beautifully elegant solution.

However, if I need to build a robust API with complex data model representations, tables
with multiple relationships, or complicated business logic? Then I would prefer the
robust and extensible capabilities afforded by the `SQLAlchemy`_ Delarative ORM and
the **SQLAthanor** library.

If that were it, I would consider `Pydantic`_ to be equivalent to `Marshmallow`_ and
`Colander`_: an interesting tool for serialization/deserialization, and one that has its
place, but not one that **SQLAthanor** need be concerned with.

But there's one major difference: `FastAPI`_.

`FastAPI`_ is an amazing microframework, and is rapidly rising in popularity across the
Python ecosystem. That's for very good reason: It is blisteringly fast, its API is
relatively simple, and it has the ability to automatically generate OpenAPI/Swagger
schemas of your API endpoints. What's not to love?

Well, its tight coupling with `Pydantic`_, for one thing. When building an application
using the `FastAPI`_ framework, I am practically forced to use
:term:`Pydantic models <Pydantic Model>` as my API inputs, outputs, and validators. If I
choose not to use Pydantic models, then I lose many of the valuable features (besides
performance) which make `FastAPI`_ so attractive for writing API applications.

But using `FastAPI`_ and `Pydantic`_ in a complex API application may require a lot of
"extra" code: the repetition of object models, the replication of business logic,
the duplication of context, etc. All of these are concerns that **SQLAthanor** was
explicitly designed to minimize.

So what to do? Most patterns, documentation, and best practices found on the internet for
authoring `FastAPI`_ applications explicitly suggest that you (manually, in your code):

  * Create a `SQLAlchemy`_ :term:`model class` for the database interface for each data
    model
  * Create one `Pydantic`_ :term:`model class <Pydantic Model>` for *each* "version" of
    your data model's output/input. So if you need one read version and a different write
    version? You need two :term:`Pydantic models <Pydantic Model>`.
  * Use your :term:`Pydantic models <Pydantic Model>` as the validators for your API
    endpoints, as needed.

This is all fine and dandy, but now what happens if you need to add an attribute to your
data model? You have to make a change to your `SQLAlchemy`_ model class, and to one or
more `Pydantic`_ models, and possibly to your API endpoints. And let's not get started on
changes to your data model's underlying business logic!

There has to be a better way.

Which is why I added `Pydantic`_ support to **SQLAthanor**. With this added support, you
can effectively use your :term:`Pydantic models <Pydantic Model>` as the "canonical
definition" of your data model. Think of the lifecycle this way:

  * You define your data model in one or more :term:`Pydantic models <Pydantic Model>`.
  * You programmatically create a `SQLAlchemy`_ :term:`model class` whose columns are
    *automatically* derived from the underlying :term:`Pydantic models <Pydantic Model>`
    and for whom each :term:`Pydantic Model` serves as a serialization/deserialization
    :term:`configuration set`.

Thus, you remove one of the (more complicated) steps in the process of writing your
`FastAPI`_ application. Now all you have to do is create your `Pydantic`_ models, and then
generate your **SQLAthanor** :term:`model classes <model class>`. Your `FastAPI`_ can
still validate based on your `Pydantic`_ models, even if you choose to drive
serialization/deserialization from your `SQLAlchemy`_ :term:`model classes <model class>`.

In other words: It saves you code! Just look at the example below:

.. tabs::

  .. tab:: FastAPI with Pydantic only

    .. todo::

      Add an example

  .. tab:: FastAPI with SQLAthanor/Pydantic

   .. todo::

     Add an example

----------------

.. _generating_and_configuring_model_classes_using_pydantic:

Generating and Configuring Model Classes Using Pydantic
==========================================================

As **SQLAthanor** relies on the creation of :term:`model classes <model class>` which
both define your database representation and provide serialization/deserialization
configuration instructions, the first step to using `Pydantic`_ with **SQLAthanor** is
to generate your :term:`model classes <model class>` based on your
:term:`Pydantic models <Pydantic Model>`.

You can do this in **SQLAthanor** using the
:func:`generate_model_from_pydantic() <sqlathanor.declarative.generate_model_from_pydantic>`
function. This function takes your :term:`Pydantic models <Pydantic Model>` as an input,
and creates a **SQLAthanor** :term:`model class` (which is a subclass of
:class:`sqlathanor.declarative.BaseModel`).

When generating your model classes from :term:`Pydantic models <Pydantic Model>`, you can
supply multiple models which will then get consolidated into a single **SQLAthanor**
:class:`BaseModel <sqlathanor.declarative.BaseModel>`. For example:

.. tabs::

  .. tab:: 1 Model

    This example shows how you would generate a single
    :class:`sqlathanor.BaseModel <sqlathanor.declarative.BaseModel>` from a single
    :class:`pydantic.BaseModel`. Since it only has one model, it would have only one
    serialization/deserialization :term:`configuration set` by default:

    .. code-block:: python

      from pydantic import BaseModel as PydanticBaseModel
      from sqlathanor import generate_model_from_pydantic

      class SinglePydanticModel(PydanticBaseModel):
          id: int
          username: str
          email: str

      SingleSQLAthanorModel = generate_model_from_pydantic(SinglePydanticModel,
                                                           tablename = 'my_tablename',
                                                           primary_key = 'id')

    This code will generate a single **SQLAthanor** :term:`model class` named
    ``SingleSQLAthanorModel``, which will contain three columns: ``id``, ``username``,
    and ``email``. The column types will be set to correspond to the data types annotated
    in the ``SinglePydanticModel`` class definition.

  .. tab:: 2 Models (shared config set)

    This example shows how you would combine multiple
    :term:`Pydantic models <Pydantic Model>` into a single
    :class:`sqlathanor.BaseModel <sqlathanor.declarative.BaseModel>`. A typical use case
    would be if one :term:`Pydantic model` represents the output when
    you are retrieving/viewing a user's data (which does not have a ``password`` field for
    security reasons) and hte other :term:`Pydantic model` represents the input when
    you are writing/creating a new user (which does need the password field).

    .. note::

      Because both :term:`Pydantic models <Pydantic Model>` are passed to the function in
      a single :class:`list <python:list>`, they will receive a single **SQLAthanor**
      :term:`configuration set`.

    .. code-block:: python

      from pydantic import BaseModel as PydanticBaseModel
      from sqlathanor import generate_model_from_pydantic

      class ReadUserModel(PydanticBaseModel):
          id: int
          username: str
          email: str

      class WriteUserModel(ReadUserModel):
          password: str

      SingleSQLAthanorModel = generate_model_from_pydantic([ReadUserModel,
                                                            WriteUserModel],
                                                           tablename = 'my_tablename',
                                                           primary_key = 'id')

    This code will generate a single **SQLAthanor** :term:`model class` named
    ``SingleSQLAthanorModel`` with four columns (``id``, ``username``, ``email``, and
    ``password``). However, because all models were passed in as a single list, the
    columns will be consolidated with only *one* :term:`configuration set`.

    .. caution::

      In my experience, it is very rare that you would want to consolidate multiple
      :term:`Pydantic models <Pydantic Model>` with only one :term:`configuration set`.
      Most of the type, each :term:`Pydantic model` will actually represent its own
      :term:`configuration set` as documented in the next example.

  .. tab:: 2 Models (independent config sets)

    This example shows how you would combine multiple
    :term:`Pydantic models <Pydantic Model>` into a single
    :class:`sqlathanor.BaseModel <sqlathanor.declarative.BaseModel>`, but configure
    multiple serialization/deserialization
    :term:`configuration sets <configuration set>` based on those
    :term:`Pydantic models <Pydantic model>`.

    This is the most-common use case, and is fairly practical. To define multiple
    :term:`configuration sets <configuration set>`, simply pass the
    :term:`Pydantic models <Pydantic Model>` as key/value pairs in the first argument:

    .. code-block:: python

      from pydantic import BaseModel as PydanticBaseModel
      from sqlathanor import generate_model_from_pydantic

      class ReadUserModel(PydanticBaseModel):
          id: int
          username: str
          email: str

      class WriteUserModel(ReadUserModel):
          password: str

      SQLAthanorModel = generate_model_from_pydantic({ 'read': ReadUserModel,
                                                       'write': WriteUserModel
                                                     },
                                                     tablename = 'my_tablename',
                                                     primary_key = 'id')

    This code will generate a single **SQLAthanor** :term:`model class`
    (``SQLAthanorModel``, with four columns - ``id``, ``username``, ``email``, and
    ``password``), but that model class will have two configuration sets: ``read`` which
    will serialize/de-serialize only three columns (``id``, ``username``, and ``email``) and
    ``write`` which will serialize/de-serialize four columns (``id``, ``username``,
    ``email``, and ``password``).

    This ``SQLAthanorModel`` then becomes useful when serializing your
    :term:`model instances <model instance>` to :class:`dict <python:dict>` or de-serializing
    them from :class:`dict <python:dict>` using the context-appropriate
    :term:`configuration set`:

    .. code-block:: python

      # Assumes that "as_dict" contains a string JSON representation with attributes as
      # defined in your "WriteUserModel" Pydantic model.
      model_instance = SQLAthanorModel.new_from_json(as_json, config_set = 'write')

      # Produces a dict representation of the object with three attributes, corresponding
      # to your "ReadUserModel" Pydantic model.
      readable_as_dict = model_instance.to_dict(config_set = 'read')

.. tip::

  When generating your **SQLAthanor** :term:`model classes <model class>` from your
  :term:`Pydantic models <Pydantic Model>`, it is important to remember that serialization
  and de-serialization is disabled by default for security reasons. Therefore a best
  practice is to
  :ref:`enable/disable your serialization and de-serialization at runtime <configuring_at_runtime>`.

  .. seealso::

    * :meth:`BaseModel.configure_serialization() <sqlathanor.declarative.BaseModel.configure_serialization>`
    * :meth:`BaseModel.set_attribute_serialization_config() <sqlathanor.declarative.BaseModel.set_attribute_serialization_config>`

.. caution::

  This functionality *does not* support more complex table structures, including
  relationships, hybrid properties, or association proxies.

-------------------------

Generating Tables from Pydantic Models
==========================================

Just as you can
:ref:`generate SQLAthanor model classes from Pydantic models <generating_and_configuring_model_classes_using_pydantic>`,
you can also create :class:`Table <sqlathanor.schema.Table>` objects from
:term:`Pydantic models <Pydantic Model>`, consolidating their attributes into standard
SQL :class:`Column <sqlathanor.schema.Column>` definitions.

.. code-block:: python

  from pydantic import BaseModel
  from sqlathanor import Table

  # Define Your Pydantic Models
  class UserWriteModel(BaseModel):
      id: int
      username: str
      email: str
      password: str

  class UserReadModel(BaseModel):
      id: int
      username: str
      email: str

  # Create Your Table
  pydantic_table = Table.from_pydantic([UserWriteModel, UserReadModel],
                                       tablename = 'my_tablename_goes_here',
                                       primary_key = 'id')

This code will generate a single :class:`Table <sqlathanor.schema.Table>` instance
(``pydantic_table``) which will have four columns: ``id``, ``username``, ``email``, and
``password``. Their column types will correspond to the type hints defined in the Pydantic
models.

.. seealso::

  * :class:`Table <sqlathanor.schema.Table>`
  * :meth:`Table.from_pydantic() <sqlathanor.schema.Table.from_pydantic>`

----------------------

.. _configuring_attributes_from_pydantic_models:

Configuring Attributes from Pydantic Models
===============================================

There may be times when you wish to configure the serialization / de-serialization of
:term:`model class` attributes based on a related :term:`Pydantic model`. You can
programmatically create a new
:class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>` instance
from a :term:`Pydantic model` by calling the
:meth:`AttributeConfiguration.from_pydantic_model() <sqlathanor.attributes.AttributeConfiguration.from_pydantic_model>`
class method:

.. code-block:: python

  from pydantic import BaseModel
  from sqlathanor import Table

  # Define Your Pydantic Models
  class UserWriteModel(BaseModel):
      id: int
      username: str
      email: str
      password: str

  class UserReadModel(BaseModel):
      id: int
      username: str
      email: str

  password_config = AttributeConfiguration.from_pydantic_model(UserWriteModel,
                                                               field = 'password',
                                                               supports_csv = (True, False),
                                                               supports_json = (True, False),
                                                               supports_yaml = (True, False),
                                                               supports_dict = (True, False),
                                                               on_deserialize = my_encryption_function)

This code will produce a single
:class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>` instance
named ``password_config``. It will support the de-serialization of data, but will never be
serialized (a typical pattern for password fields!). Furthermore, it will execute the
``my_encryption_function`` during the de-serialization process.

A very common use case is to configure the serialization/de-serialization profile for
attributes that were programmatically derived from
:term:`Pydantic models <Pydantic Model>`.

.. seealso::

  * :meth:`AttributeConfiguration.from_pydantic_model() <sqlathanor.attributes.AttributeConfiguration.from_pydantic_model>`

.. _Pydantic: https://pydantic-docs.helpmanual.io/
.. _FastAPI: https://fastapi.tiangolo.com/
.. _SQLAlchemy: http://www.sqlalchemy.org
.. _Marshmallow: https://marshmallow.readthedocs.io/en/3.0/
.. _Colander: https://docs.pylonsproject.org/projects/colander/en/latest/
