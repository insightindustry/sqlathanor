.. SQLAthanor documentation master file, created by
   sphinx-quickstart on Fri Jun 15 11:08:09 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

####################################################
SQLAthanor
####################################################

**Drop-in serialization extension for the SQLAlchemy Declarative ORM**

.. |strong| raw:: html

 <strong>

.. |/strong| raw:: html

 </strong>

.. sidebar:: Version Compatability

  **SQLAthanor** is designed to be compatible with:

    * Python 2.7 and Python 3.4 or higher, and
    * `SQLAlchemy <http://www.sqlalchemy.org>`_ 0.8 or higher

.. include:: _unit_tests_code_coverage.rst

.. toctree::
 :hidden:
 :maxdepth: 2
 :caption: Contents:

 Home <self>
 Quickstart <quickstart>
 Using SQLAthanor <using>
 Error Reference <errors>
 Contributor Guide <contributing>
 Testing Reference <testing>
 Release History <history>
 Glossary <glossary>

**SQLAthanor** is a Python library that extends `SQLAlchemy`_'s
fantastic `Declarative ORM <http://docs.sqlalchemy.org/en/latest/orm/tutorial.html>`_
to provide easy-to-use record serialization/de-serialization with support for:

  * :ref:`dict <python:dict>`
  * CSV
  * JSON
  * YAML

The library works as a drop-in extension - change one line of existing code, and it
should just work. Furthermore, it has been extensively tested on Python 2.7, 3.4,
3.5, and 3.6 using SQLAlchemy 0.8 and higher.

.. contents::
 :depth: 3
 :backlinks: entry

***************
Installation
***************

To install **SQLAthanor**, just execute:

.. code:: bash

 $ pip install sqlathanor

Dependencies
==============

.. include:: _dependencies.rst

***********************************
Hello, World and Basic Usage
***********************************

**SQLAthanor** is a drop-in extension for the
`SQLAlchemy Declarative ORM <http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/index.html>`_
and parts of the `SQLAlchemy Core <http://docs.sqlalchemy.org/en/latest/core/api_basics.html>`_.

1. Import SQLAthanor
=======================

To start using it, all you need to do is import it in place of your standard SQLAlchemy imports:

.. tabs::

  .. tab:: Using SQLAlchemy

    .. code-block:: python

      from sqlalchemy.ext.declarative import declarative_base
      from sqlalchemy import Column, Integer, String          # ... and any other data types

      # The following are optional, depending on how your data model is designed:
      from sqlalchemy.orm import relationship
      from sqlalchemy.ext.hybrid import hybrid_property
      from sqlalchemy.ext.associationproxy import association_proxy

  .. tab:: Using SQLAthanor

    .. code-block:: python

      from sqlathanor import declarative_base
      from sqlathanor import Column, Integer, Text          # ... and any other data types

      # The following are optional, depending on how your data model is designed:
      from sqlathanor import relationship
      from sqlathanor import hybrid_property
      from sqlathanor import association_proxy

    .. tip::

      Because of its many moving parts, `SQLAlchemy <https://www.sqlalchemy.org>`_
      splits its various pieces into multiple modules and forces you to use many
      ``import`` statements.

      The example below maintains this strategy to show how **SQLAthanor** is a
      1:1 drop-in replacement. But obviously, you can import all of the items you
      need in just one ``import`` statement.


  .. tab:: Using Flask-SQLAlchemy

    .. tip::

      **SQLAthanor** is designed to work with `Flask-SQLAlchemy`_ too! The process
      is a little more involved, but just do the following:

2. Declare Your Models
=========================

Now that you have imported **SQLAthanor**, you can just declare your models
the way you normally would, even using the exact same syntax. But now when you
define your model, you can supply some additional arguments to your attribute
definitions that control whether and how they are serialized or validated.

.. note::

  By default, all columns, relationships, association proxies, and hybrid properties will
  be serialized to all formats. Using our new arguments, you can limit what gets
  serialized / de-serialized to which formats and supply custom validators that are
  used when setting values on your model instance.

.. code-block:: python

  BaseModel = declarative_base()

  class User(BaseModel):
    __tablename__ = 'users'

    id = Column("id",
                Integer,
                primary_key = True,
                autoincrement = True,
                supports_csv = True,
                csv_sequence = 1,
                supports_json = True,
                supports_yaml = True,
                supports_dict = True,
                on_serialize = None,
                on_deserialize = None)

    name = Column("name",
                  Text,
                  supports_csv = True,
                  csv_sequence = 2,
                  supports_json = True,
                  supports_yaml = True,
                  supports_dict = True,
                  on_serialize = None,
                  on_deserialize = None)

    email = Column("email",
                   Text,
                   supports_csv = True,
                   csv_sequence = 3,
                   supports_json = True,
                   supports_yaml = True,
                   supports_dict = True,
                   on_serialize = None,
                   on_deserialize = validators.email)

     password = Column("password",
                       Text,
                       supports_csv = (True, False),
                       csv_sequence = 4,
                       supports_json = (True, False),
                       supports_yaml = (True, False),
                       supports_dict = (True, False),
                       on_serialize = None,
                       on_deserialize = my_custom_password_hash_function)

As you can see, we've just added some (optional) arguments to the
:ref:`Column <sqlalchemy:sqlalchemy.schema.Column>` constructor. Hopefully, they're
pretty self-explanatory:

  * ``supports_<format>`` determines whether that attribute is included when
    :term:`serializing <serialization>` or :term:`de-serializing <de-serialization>`
    the object.

    .. tip::

      If you give these options one value, it will either enable (``True``) / disable
      (``False``) both serialization and de-serialization.

      But you can also supply a :ref:`tuple <python:tuple>` with two values,
      where the first value controls whether the attribute supports the format
      when inbound (de-serialization) or whether it supports the format when
      outbound (serialization).

      In the example above, the ``password`` attribute will **not** be included when
      serializing the object (outbound). But it *will* be expected / supported
      when de-serializing the object (inbound).

  * ``on_serialize`` indicates the function or functions that are used to prepare
    an attribute for serialization. This can either be a single function (that applies
    to all serialization formats) or a :ref:`dict <python>` where each key corresponds
    to a format and its value is the function to use when serializing to that format.

    .. tip::

      If ``on_serialize`` is left as :class:`None <python:None>`, then
      **SQLAthanor** will apply a default ``on_serialize`` function
      based on the attribute's data type.

  * ``on_deserialize`` indicates the function or functions that are used to validate
    or pre-process an attribute when de-serializing. This can either be a single
    function (that applies to all formats) or a :ref:`dict <python>` where each key corresponds
    to a format and its value is the function to use when de-serializing from that format.

    .. tip::

      If ``on_deserialize`` is left as :class:`None <python:None>`, then
      **SQLAthanor** will apply a default ``on_deserialize`` function
      based on the attribute's data type.

3. Serialize Your Model Instance
==================================

.. note:: See Also

  :ref:`Serialization Reference <serialization>`:
    * :ref:`to_csv() <BaseModel.to_csv>`
    * :ref:`to_dict() <BaseModel.to_dict>`
    * :ref:`to_json() <BaseModel.to_json>`
    * :ref:`to_yaml() <BaseModel.to_yaml>`

So now let's say you have a :term:`model instance` and want to serialize it. It's
super easy:

.. tabs::

  .. tab:: JSON

    .. code-block:: python

      # Get user with id == 123 from the database
      user = User.query.get(123)

      serialized_version = user.to_json()

  .. tab:: CSV

    .. code-block:: python

      # Get user with id == 123 from the database
      user = User.query.get(123)

      serialized_version = user.to_csv()

  .. tab:: YAML

    .. code-block:: python

      # Get user with id == 123 from the database
      user = User.query.get(123)

      serialized_version = user.to_yaml()

  .. tab:: dict

    .. code-block:: python

      # Get user with id == 123 from the database
      user = User.query.get(123)

      serialized_version = user.to_dict()

That's it! Of course, the serialization methods all support a variety of other
(*optional!*) options to fine-tune their behavior (CSV formatting, relationship
nesting, etc.).

4. De-serialize a Model Instance
==================================

.. note:: See Also

  :ref:`De-serialization Reference <de-serialization>`:
    * :ref:`from_csv() <BaseModel.from_csv>`
    * :ref:`from_dict() <BaseModel.from_dict>`
    * :ref:`from_json() <BaseModel.from_json>`
    * :ref:`from_yaml() <BaseModel.from_yaml>`

Now let's say you receive a ``User`` object in serialized form and want
to create a proper Python ``User`` object. That's easy, too:

.. tabs::

  .. tab:: JSON

    .. code-block:: python

      # Assuming you have a "deserialized_object" in JSON format

      user = deserialized_object.from_json()

  .. tab:: CSV

    .. code-block:: python

      # Assuming you have a "deserialized_object" in CSV format

      user = deserialized_object.from_csv()

  .. tab:: YAML

    .. code-block:: python

      # Assuming you have a "deserialized_object" in YAML format

      user = deserialized_object.from_yaml()

  .. tab:: dict

    .. code-block:: python

      # Assuming you have a "deserialized_object" as a Python dict

      user = deserialized_object.from_dict()

That's it! Of course, all the de-serialization functions have additional options to
fine-tune their behavior as needed. But that's it.

6. Persist Data to the Database
===================================

So now that we've serialized and de-serialized our user, let's use
`SQLAlchemy <https://www.sqlalchemy.org/>`_ to update the database. That's really
easy, too:

.. code-block:: python

  # To create a new record:
  user.add()

  # To update an existing record:
  user.save()

  # To delete an existing record:
  user.delete()

That's it!


************************************
Why SQLAthanor?
************************************

Odds are you've used `SQLAlchemy <http://www.sqlalchemy.org>`_ before. And if
you haven't, why on earth not? It is hands down the best relational database
toolkit and :term:`ORM <Object Relational Mapper (ORM)>` available for Python, and has helped me quickly write
code for many APIs, software platforms, and data science projects. Just look at
some of these great `features <http://www.sqlalchemy.org/features.html>`_.

As its name suggests, SQLAlchemy focuses on the problem of connecting your Python
code to an underlying SQL database. That's a super hard problem, especially when
you consider the complexity of abstraction, different SQL databases, different SQL
dialects, performance optimization, etc. It ain't easy, and the SQLAlchemy team
has spent years building one of the most elegant solutions out there.

.. sidebar:: What's in a name?


  Who can resist a good (for certain values of good) pun?

  .. image:: _static/athanor.png
    :alt: A diagram of an athanor
    :align: right

  In the time-honored "science" of alchemy, an :term:`athanor` is a furnace that
  provides uniform heat over an extended period of time.

  Since **SQLAthanor** extends the great `SQLAlchemy <https://www.sqlalchemy.org>`_
  library, the idea was to keep the alchemical theme going.

  Bottom line: I - for one - clearly cannot resist a pun, whether good or not.

But as hard as Pythonically communicating with a database is, in the real world
with microservices, serverless architectures, RESTful APIs and the like we often
need to do more with the data than read or write from/to our database. In almost
all of the projects I've worked on over the last fifteen years, I've had to:

  * hand data off in some fashion (:term:`serialize <serialization>`) for another
    program (possibly written by someone else in another programming language) to work
    with, or
  * accept and interpret data (:term:`de-serialize <de-serialization>`) received
    from some other program (possibly written by someone else in another programming
    language).

Python objects (pickled or not) are great, but they're rarely an effective means
of transmitting data over the wire, or communicating data between independent
applications. Which is where formats like JSON, CSV, and YAML come in.

So when writing many Python APIs, I found myself writing methods to convert my
SQLAlchemy records (technically, :term:`model instances <model instance>`) into JSON or creating new
SQLAlchemy records based on data I received in JSON. So after writing similar
methods many times over, I figured a better approach would be to write the
serialization/de-serialization code just once, and then re-use it across all of
my various projects.

Which is how **SQLAthanor** came about.

It adds simple methods like :ref:`to_json() <BaseModel.to_json>` and
:ref:`from_csv() <BaseModel.from_json>` to your SQLAlchemy declarative models
and provides powerful configuration options that give you tons of flexibility.

Key SQLAthanor Features
==========================

* **Easy to adopt**: Just tweak your existing SQLAlchemy ``import`` statements and
  you're good to go.
* With one method call, convert SQLAlchemy model instances to:
  * CSV records
  * JSON objects
  * YAML objects
  * :ref:`dict <python:dict>` objects
* With one method call, create SQLAlchemy model instances from:
  * :ref:`dict <python:dict>` objects
  * CSV records
  * JSON objects
  * YAML objects
* Decide which serialization formats you want to support for which models.
* Decide which columns you want to include in their serialized form (and pick
  different columns for different formats, too).
* Default validation for de-serialized data for every SQLAlchemy data type.
* Customize the validation used when de-serializing particular columns to match
  your needs.
* With one method call, persist (create and/or update) records to your database.
* With one method call, delete records from your database.

*********************
Questions and Issues
*********************

You can ask questions and report issues on the project's
`Github Issues Page <https://github.com/insightindustry/sqlathanor/issues>`_

*********************
Contributing
*********************

We welcome contributions and pull requests! For more information, please see the
:doc:`Contributor Guide <contributing>`

*********************
Testing
*********************

We use `TravisCI <http://travisci.org>`_ for our build automation and
`ReadTheDocs <https://readthedocs.org>`_ for our documentation.

Detailed information about our test suite and how to run tests locally can be
found in our :doc:`Testing Reference <testing>`.

**********************
License
**********************

**SQLAthanor** is made available under an :doc:`MIT License <license>`.

********************
Indices and tables
********************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
