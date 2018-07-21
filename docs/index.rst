.. SQLAthanor documentation master file, created by
   sphinx-quickstart on Fri Jun 15 11:08:09 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: _static/sqlathanor-logo.png
  :alt: SQLAthanor - Serialization / De-serialization for SQLAlchemy
  :align: right
  :width: 200
  :height: 100

|

####################################################
SQLAthanor
####################################################

**Serialization/De-serialization Support for the SQLAlchemy Declarative ORM**

.. |strong| raw:: html

 <strong>

.. |/strong| raw:: html

 </strong>

.. sidebar:: Version Compatability

  **SQLAthanor** is designed to be compatible with:

    * Python 2.7 and Python 3.4 or higher, and
    * `SQLAlchemy`_ 0.9 or higher

.. include:: _unit_tests_code_coverage.rst

.. toctree::
 :hidden:
 :maxdepth: 3
 :caption: Contents:

 Home <self>
 Quickstart: Patterns and Best Practices <quickstart>
 Using SQLAthanor <using>
 API Reference <api>
 Default Serialization Functions <default_serialization_functions>
 Default De-serialization Functions <default_deserialization_functions>
 Error Reference <errors>
 Contributor Guide <contributing>
 Testing Reference <testing>
 Release History <history>
 Glossary <glossary>
 License <license>

**SQLAthanor** is a Python library that extends `SQLAlchemy`_'s fantastic
:doc:`Declarative ORM <sqlalchemy:orm/extensions/declarative/index>` to provide
easy-to-use record :term:`serialization`/:term:`de-serialization` with support for:

  * :term:`JSON <JavaScript Object Notation (JSON)>`
  * :term:`CSV <Comma-Separated Value (CSV)>`
  * :term:`YAML <YAML Ain't a Markup Language (YAML)>`
  * :class:`dict <python:dict>`

The library works as a :term:`drop-in extension <drop-in replacement>` - change
one line of existing code, and it should just work. Furthermore, it has been
extensively tested on Python 2.7, 3.4, 3.5, and 3.6 using `SQLAlchemy`_ 0.9 and higher.

.. contents::
 :depth: 3
 :backlinks: entry

-----------------

***************
Installation
***************

.. include:: _installation.rst

Dependencies
==============

.. include:: _dependencies.rst

-------------

************************************
Why SQLAthanor?
************************************

Odds are you've used `SQLAlchemy`_ before. And if
you haven't, why on earth not? It is hands down the best relational database
toolkit and :term:`ORM <Object Relational Mapper (ORM)>` available for Python, and
has helped me quickly write code for many APIs, software platforms, and data science
projects. Just look at some of these great `features <http://www.sqlalchemy.org/features.html>`_.

As its name suggests, SQLAlchemy focuses on the problem of connecting your Python
code to an underlying relational (SQL) database. That's a super hard problem, especially
when you consider the complexity of abstraction, different SQL databases, different SQL
dialects, performance optimization, etc. It ain't easy, and the SQLAlchemy team
has spent years building one of the most elegant solutions out there.

.. sidebar:: What's in a name?

  Who can resist a good (for certain values of good) pun?

  In the time-honored "science" of alchemy, an :term:`athanor` is a furnace that
  provides uniform heat over an extended period of time.

  Since **SQLAthanor** extends the great `SQLAlchemy`_ library, the idea was to
  keep the alchemical theme going.

  Bottom line: I - for one - clearly cannot resist a pun, whether good or not.

But as hard as Pythonically communicating with a database is, in the real world
with microservices, serverless architectures, RESTful APIs and the like we often
need to do more with the data than read or write from/to our database. In almost
all of the projects I've worked on over the last two decades, I've had to:

  * hand data off in some fashion (:term:`serialize <serialization>`) for another
    program (possibly written by someone else in another programming language) to work
    with, or
  * accept and interpret data (:term:`de-serialize <de-serialization>`) received
    from some other program (possibly written by someone else in another programming
    language).

Python objects (:term:`pickled <pickling>` or not) are great, but they're rarely
the best way of transmitting data over the wire, or communicating data between
independent applications. Which is where formats like
:term:`JSON <JavaScript Object Notation (JSON)>`,
:term:`CSV <Comma-Separated Value (CSV)>`, and
:term:`YAML <YAML Ain't a Markup Language (YAML)>` come in.

So when writing many Python APIs, I found myself writing methods to convert my
SQLAlchemy records (technically, :term:`model instances <model instance>`) into JSON
or creating new SQLAlchemy records based on data I received in JSON. So after writing
similar methods many times over, I figured a better approach would be to write the
serialization/de-serialization code just once, and then re-use it across all of
my various projects.

Which is how **SQLAthanor** came about.

It adds simple methods like :meth:`to_json() <sqlathanor.BaseModel.to_json>`,
:meth:`new_from_csv() <sqlathanor.BaseModel.new_from_csv>`, and
:meth:`update_from_csv() <sqlathanor.BaseModel.update_from_json>` to your SQLAlchemy
declarative models and provides powerful configuration options that give you tons of flexibility.

Key SQLAthanor Features
==========================

* **Easy to adopt**: Just tweak your existing SQLAlchemy ``import`` statements and
  you're good to go.
* With one method call, convert SQLAlchemy model instances to:

  * CSV records
  * JSON objects
  * YAML objects
  * :class:`dict <python:dict>` objects

* With one method call, create or update SQLAlchemy model instances from:

  * :class:`dict <python:dict>` objects
  * CSV records
  * JSON objects
  * YAML objects

* Decide which serialization formats you want to support for which models.
* Decide which columns/attributes you want to include in their serialized form
  (and pick different columns for different formats, too).
* Default validation for de-serialized data for every SQLAlchemy data type.
* Customize the validation used when de-serializing particular columns to match
  your needs.

|

**SQLAthanor** vs Alternatives
================================

.. include:: _versus_alternatives.rst

---------------

***********************************
Hello, World and Basic Usage
***********************************

**SQLAthanor** is a :term:`drop-in replacement` for the
:doc:`SQLAlchemy Declarative ORM <sqlalchemy:orm/extensions/declarative/index>`
and parts of the :doc:`SQLAlchemy Core <sqlalchemy:core/api_basics>`.

1. Import SQLAthanor
=======================

.. include:: _import_sqlathanor.rst

2. Declare Your Models
=========================

Now that you have imported **SQLAthanor**, you can just declare your models
the way you normally would, even using the exact same syntax.

But now when you define your model, you can also configure serialization and
de-serialization for each attribute using two approaches:

  * The :ref:`Meta Configuration approach <meta_configuration>` lets you
    define a single ``__serialization__`` attribute on your model that configures
    serialization/de-serialization for all of your model's columns, hybrid properties,
    association proxies, and properties.
  * The :ref:`Declarative Configuration approach <declarative_configuration>` lets
    you supply additional arguments to your attribute definitions that control whether
    and how they are serialized, de-serialized, or validated.

.. seealso::

  * :ref:`Configuring Serialization and De-serialization <configuration>`

    * :ref:`Meta Configuration <meta_configuration>`
    * :ref:`Declarative Configuration <declarative_configuration>`

  * :doc:`Quickstart <quickstart>`

    * :ref:`Meta Configuration Pattern <meta_configuration_pattern>`
    * :ref:`Declarative Configuration Pattern <declarative_configuration_pattern>`

.. note::

  .. epigraph::

    explicit is better than implicit

    -- :PEP:`20` - The Zen of Python

  By default, all columns, relationships, association proxies, and hybrid properties will
  **not** be serialized. In order for a column, relationship, proxy, or hybrid property
  to be serializable to a given format or de-serializable from a given format, you
  will need to **explicitly** enable serialization/deserialization.

.. tabs::

  .. tab:: Meta Approach

    .. code-block:: python

      from sqlathanor import declarative_base, Column, relationship, AttributeConfiguration

      from sqlalchemy import Integer, String
      from sqlalchemy.ext.hybrid import hybrid_property
      from sqlalchemy.ext.associationproxy import association_proxy

      BaseModel = declarative_base()

      class User(BaseModel):
        __tablename__ = 'users'

        __serialization__ = [AttributeConfiguration(name = 'id',
                                                    supports_csv = True,
                                                    csv_sequence = 1,
                                                    supports_json = True,
                                                    supports_yaml = True,
                                                    supports_dict = True,
                                                    on_serialize = None,
                                                    on_deserialize = None),
                             AttributeConfiguration(name = 'addresses',
                                                    supports_json = True,
                                                    supports_yaml = (True, True),
                                                    supports_dict = (True, False),
                                                    on_serialize = None,
                                                    on_deserialize = None),
                             AttributeConfiguration(name = 'hybrid',
                                                    supports_csv = True,
                                                    csv_sequence = 2,
                                                    supports_json = True,
                                                    supports_yaml = True,
                                                    supports_dict = True,
                                                    on_serialize = None,
                                                    on_deserialize = None)]
                             AttributeConfiguration(name = 'keywords',
                                                    supports_csv = False,
                                                    supports_json = True,
                                                    supports_yaml = True,
                                                    supports_dict = True,
                                                    on_serialize = None,
                                                    on_deserialize = None)]
                             AttributeConfiguration(name = 'python_property',
                                                    supports_csv = (False, True),
                                                    csv_sequence = 3,
                                                    supports_json = (False, True),
                                                    supports_yaml = (False, True),
                                                    supports_dict = (False, True),
                                                    on_serialize = None,
                                                    on_deserialize = None)]

        id = Column('id',
                    Integer,
                    primary_key = True)

        addresses = relationship('Address',
                                 backref = 'user')

        _hybrid = 1

        @hybrid_property
        def hybrid(self):
            return self._hybrid

        @hybrid.setter
        def hybrid(self, value):
            self._hybrid = value

        @hybrid.expression
        def hybrid(cls):
          return False

        keywords = association_proxy('keywords', 'keyword')

        @property
        def python_property(self):
          return self._hybrid * 2

    As you can see, we've added a ``__serialization__`` attribute to your standard
    model. The ``__serialization__`` attribute takes a list of
    :class:`AttributeConfiguration <sqlathanor.attributes.AttributeConfiguration>`
    instances, where each configures the serialization and de-serialization of a
    :term:`model attribute`.

  .. tab:: Declarative Approach

    .. code-block:: python

      from sqlathanor import declarative_base

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
    :class:`Column <sqlalchemy:sqlalchemy.schema.Column>` constructor. Hopefully
    these configuration arguments are self-explanatory.

  Both the Meta and the Declarative configuration approaches use the same
  API for configuring serialization and de-serialization. While there are a lot
  of details, in general, the configuration arguments are:

  * ``supports_<format>`` determines whether that attribute is included when
    :term:`serializing <serialization>` or :term:`de-serializing <de-serialization>`
    the object to the ``<format>`` indicated.

    .. tip::

      If you give these options one value, it will either enable (``True``) or disable
      (``False``) both serialization and de-serialization, respectively.

      But you can also supply a :class:`tuple <python:tuple>` with two values,
      where the first value controls whether the attribute supports the format
      when inbound (de-serialization) or whether it supports the format when
      outbound (serialization).

      In the example above, the ``password`` attribute will **not** be included when
      serializing the object (outbound). But it *will* be expected / supported
      when de-serializing the object (inbound).

  * ``on_serialize`` indicates the function or functions that are used to prepare
    an attribute for serialization. This can either be a single function (that applies
    to all serialization formats) or a :class:`dict <python:dict>` where each key corresponds
    to a format and its value is the function to use when serializing to that format.

    .. tip::

      If ``on_serialize`` is left as :obj:`None <python:None>`, then
      **SQLAthanor** will apply a default ``on_serialize`` function
      based on the attribute's data type.

  * ``on_deserialize`` indicates the function or functions that are used to validate
    or pre-process an attribute when de-serializing. This can either be a single
    function (that applies to all formats) or a :class:`dict <python:dict>` where each key corresponds
    to a format and its value is the function to use when de-serializing from that format.

    .. tip::

      If ``on_deserialize`` is left as :obj:`None <python:None>`, then
      **SQLAthanor** will apply a default ``on_deserialize`` function
      based on the attribute's data type.

3. Serialize Your Model Instance
==================================

.. seealso::

  * :ref:`Serialization Reference <serialization>`:
  * :meth:`to_csv() <sqlathanor.BaseModel.to_csv>`
  * :meth:`to_json() <sqlathanor.BaseModel.to_json>`
  * :meth:`to_yaml() <sqlathanor.BaseMOdel.to_yaml>`
  * :meth:`to_dict() <sqlathanor.BaseModel.to_dict>`

So now let's say you have a :term:`model instance` and want to serialize it. It's
super easy:

.. tabs::

  .. tab:: JSON

    .. code-block:: python

      # Get user with id == 123 from the database
      user = User.query.get(123)

      # Serialize the user record to a JSON string.
      serialized_version = user.to_json()

  .. tab:: CSV

    .. code-block:: python

      # Get user with id == 123 from the database
      user = User.query.get(123)

      # Serialize the user record to a CSV string.
      serialized_version = user.to_csv()

  .. tab:: YAML

    .. code-block:: python

      # Get user with id == 123 from the database
      user = User.query.get(123)

      # Serialize the user record to a YAML string.
      serialized_version = user.to_yaml()

  .. tab:: dict

    .. code-block:: python

      # Get user with id == 123 from the database
      user = User.query.get(123)

      # Serialize the user record to a Python dict.
      serialized_version = user.to_dict()

That's it! Of course, the serialization methods all support a variety of other
(*optional!*) options to fine-tune their behavior (CSV formatting, relationship
nesting, etc.).

4. De-serialize a Model Instance
==================================

.. seealso::

  * :ref:`De-serialization Reference <deserialization>`:
  * Create a new :term:`model instance`:

    * :meth:`new_from_csv() <sqlathanor.BaseModel.new_from_csv>`
    * :meth:`new_from_json() <sqlathanor.BaseModel.new_from_json>`
    * :meth:`new_from_yaml() <sqlathanor.BaseModel.new_from_yaml>`
    * :meth:`new_from_dict() <sqlathanor.BaseModel.new_from_dict>`

  * Update an existing model instance:

    * :meth:`update_from_csv() <sqlathanor.BaseModel.update_from_csv>`
    * :meth:`update_from_json() <sqlathanor.BaseModel.update_from_json>`
    * :meth:`update_from_yaml() <sqlathanor.BaseModel.update_from_yaml>`
    * :meth:`update_from_dict() <sqlathanor.BaseModel.update_from_dict>`

Now let's say you receive a ``User`` object in serialized form and want
to create a proper Python ``User`` object. That's easy, too:

.. tabs::

  .. tab:: JSON

    .. code-block:: python

      # EXAMPLE 1: Create a new User from a JSON string called "deserialized_object".
      user = User.new_from_json(deserialized_object)

      # EXAMPLE 2: Update an existing "user" instance from a JSON
      # string called "deserialized_object".
      user.update_from_json(updated_object)

  .. tab:: CSV

    .. code-block:: python

      # EXAMPLE 1: Create a new User from a CSV string called "deserialized_object".
      user = User.new_from_csv(deserialized_object)

      # EXAMPLE 2: Update an existing "user" instance from a CSV
      # string called "deserialized_object".
      user.update_from_csv(updated_object)

  .. tab:: YAML

    .. code-block:: python

      # EXAMPLE 1: Create a new User from a YAML string called "deserialized_object".
      user = User.new_from_json(deserialized_object)

      # EXAMPLE 2: Update an existing "user" instance from a YAML
      # string called "deserialized_object".
      user.update_from_yaml(updated_object)

  .. tab:: dict

    .. code-block:: python

      # EXAMPLE 1: Create a new User from a dict called "deserialized_object".
      user = User.new_from_dict(deserialized_object)

      # EXAMPLE 2: Update an existing "user" instance from a dict called
      # "deserialized_object".
      user.update_from_dict(updated_object)

That's it! Of course, all the de-serialization functions have additional options to
fine-tune their behavior as needed. But that's it.

--------------

*********************
Questions and Issues
*********************

You can ask questions and report issues on the project's
`Github Issues Page <https://github.com/insightindustry/sqlathanor/issues>`_

-----------------

*********************
Contributing
*********************

We welcome contributions and pull requests! For more information, please see the
:doc:`Contributor Guide <contributing>`

-------------------

*********************
Testing
*********************

We use `TravisCI <http://travisci.org>`_ for our build automation and
`ReadTheDocs <https://readthedocs.org>`_ for our documentation.

Detailed information about our test suite and how to run tests locally can be
found in our :doc:`Testing Reference <testing>`.

--------------------

**********************
License
**********************

**SQLAthanor** is made available under an :doc:`MIT License <license>`.

----------------

********************
Indices and tables
********************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _SQLAlchemy: http://www.sqlalchemy.org
.. _Flask-SQLAlchemy: http://flask-sqlalchemy.pocoo.org/2.3/
