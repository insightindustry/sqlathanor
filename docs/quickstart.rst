******************************************
Quickstart: Patterns and Best Practices
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

Installation
===============

.. include:: _installation.rst

.. _meta_configuration_pattern:

-----------

Meta Configuration Pattern
=============================

.. seealso::

  * :ref:`Configuring Serialization/De-serialization <configuration>` >
    :ref:`Meta Configuration <meta_configuration>`

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

---------

.. _declarative_configuration_pattern:

Declarative Configuration Pattern
=====================================

.. seealso::

  * :ref:`Configuring Serialization/De-serialization <configuration>` >
    :ref:`Declarative Configuration <declarative_configuration>`

.. code-block:: python

  from sqlathanor import declarative_base, Column, relationship

  from sqlalchemy import Integer, String

  BaseModel = declarative_base()

  class User(BaseModel):
    __tablename__ = 'users'

    id = Column('id',
                Integer,
                primary_key = True,
                supports_csv = True,
                csv_sequence = 1,
                supports_json = True,
                supports_yaml = True,
                supports_dict = True,
                on_serialize = None,
                on_deserialize = None)

    addresses = relationship('Address',
                             backref = 'user',
                             supports_json = True,
                             supports_yaml = (True, True),
                             supports_dict = (True, False),
                             on_serialize = None,
                             on_deserialize = None)


----------

Serializing Model Instances
===============================

.. seealso::

  * :ref:`Serializing a Model Instance <serialization>`
  * :meth:`to_csv() <sqlathanor.BaseModel.to_csv>`
  * :meth:`to_json() <sqlathanor.BaseModel.to_json>`
  * :meth:`to_yaml() <sqlathanor.BaseModel.to_yaml>`
  * :meth:`to_dict() <sqlathanor.BaseModel.to_dict>`

.. code-block:: python

  # For a SQLAlchemy Model Class named "User" with an instance named "user":

  as_csv = user.to_csv()     # CSV
  as_json = user.to_json()   # JSON
  as_yaml = user.to_yaml()   # YAML
  as_dict = user.to_dict()   # dict

--------------

Updating a Model Instance
============================

.. seealso::

  * :ref:`De-serializing Data <deserialization>` >
    :ref:`Updating Instances <updating_instances>`
  * :meth:`update_from_csv() <sqlathanor.BaseModel.update_from_csv>`
  * :meth:`update_from_json() <sqlathanor.BaseModel.update_from_json>`
  * :meth:`update_from_yaml() <sqlathanor.BaseModel.update_from_yaml>`
  * :meth:`update_from_dict() <sqlathanor.BaseModel.update_from_dict>`

.. code-block:: python

  # For a SQLAlchemy Model Class named "User" with an instance named "user"
  # and serialized objects "as_csv" (string), "as_json" (string),
  # "as_yaml" (string), and "as_dict" (dict):

  user.update_from_csv(as_csv)   # CSV
  user.update_from_json(as_json) # JSON
  user.update_from_yaml(as_yaml) # YAML
  user.update_from_dict(as_dict) # dict

--------------

Creating a New Model Instance
================================

.. seealso::

  * :ref:`De-serializing Data <deserialization>` >
    :ref:`Creating New Instances <creating_new_instances>`
  * :meth:`new_from_csv() <sqlathanor.BaseModel.new_from_csv>`
  * :meth:`new_from_json() <sqlathanor.BaseModel.new_from_json>`
  * :meth:`new_from_yaml() <sqlathanor.BaseModel.new_from_yaml>`
  * :meth:`new_from_dict() <sqlathanor.BaseModel.new_from_dict>`

.. code-block:: python

  # For a SQLAlchemy Model Class named "User" and serialized objects "as_csv"
  # (string), "as_json" (string), "as_yaml" (string), and "as_dict" (dict):

  user = User.new_from_csv(as_csv)   # CSV
  user = User.new_from_json(as_json) # JSON
  user = User.new_from_yaml(as_yaml) # YAML
  user = User.new_from_dict(as_dict) # dict

----------------------

.. _error_handling_patterns:

Error Handling
=================================

Errors During Serialization
--------------------------------

.. include:: _error_handling_serialization.rst

Errors During De-serialization
--------------------------------

.. include:: _error_handling_deserialization.rst

----------------------

Password De-serialization
=============================

.. seealso::

  * :ref:`Configuring Pre-processing and Post-processing <extra_processing>` >
    :ref:`De-serialization Post-processing <deserialization_postprocessing>`
  * :term:`Deserialization Functions <De-serialization Function>`
  * :doc:`Default Deserialization Functions <default_deserialization_functions>`

.. tabs::

  .. tab:: Meta Configuration

    .. code-block:: python

      from sqlathanor import declarative_base, Column, AttributeConfiguration

      from sqlalchemy import Integer, String

      def my_encryption_function(value):
        """Function that accepts an inbound password ``value`` and returns its
        encrypted value."""

        # ENCRYPTION LOGIC GOES HERE

        return encrypted_value

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
                             AttributeConfiguration(name = 'password',
                                                    supports_csv = (True, False),
                                                    supports_json = (True, False),
                                                    supports_yaml = (True, False),
                                                    supports_dict = (True, False),
                                                    on_serialize = None,
                                                    on_deserialize = my_encryption_function)]

        id = Column('id',
                    Integer,
                    primary_key = True)

        password = Column('password', String(255))

  .. tab:: Declarative Configuration

    .. code-block:: python

      from sqlathanor import declarative_base, Column

      from sqlalchemy import Integer, String

      def my_encryption_function(value):
        """Function that accepts an inbound password ``value`` and returns its
        encrypted value."""

        # ENCRYPTION LOGIC GOES HERE

        return encrypted_value

      BaseModel = declarative_base()

      class User(BaseModel):
        __tablename__ = 'users'

        id = Column('id',
                    Integer,
                    primary_key = True,
                    supports_csv = True,
                    csv_sequence = 1,
                    supports_json = True,
                    supports_yaml = True,
                    supports_dict = True,
                    on_serialize = None,
                    on_deserialize = None)

        password = Column('password',
                          String(255),
                          supports_csv = (True, False),
                          csv_sequence = 2,
                          supports_json = (True, False),
                          supports_yaml = (True, False),
                          supports_dict = (True, False),
                          on_serialize = None,
                          on_deserialize = my_encryption_function)

----------------------------

Using SQLAthanor with SQLAlchemy Reflection
=============================================

.. seealso::

  * :ref:`Using Declarative Reflection with SQLAthanor <using_reflection>`
  * **SQLAlchemy**: :doc:`Reflecting Database Objects <sqlalchemy:core/reflection>`
  * **SQLAlchemy**: `Using Reflection with Declarative <http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/table_config.html#using-reflection-with-declarative>`_

.. tabs::

  .. tab:: Meta Approach

    .. code-block:: python

      from sqlathanor import declarative_base, Column, AttributeConfiguration

      from sqlalchemy import create_engine, Table

      BaseModel = declarative_base()

      engine = create_engine('... ENGINE CONFIGURATION GOES HERE ...')
      # NOTE: Because reflection relies on a specific SQLAlchemy Engine existing, presumably
      # you would know how to configure / instantiate your database engine using SQLAlchemy.
      # This is just here for the sake of completeness.

      class ReflectedUser(BaseModel):
          __table__ = Table('users',
                            BaseModel.metadata,
                            autoload = True,
                            autoload_with = engine)

          __serialization__ = [AttributeConfiguration(name = 'id',
                                                      supports_csv = True,
                                                      csv_sequence = 1,
                                                      supports_json = True,
                                                      supports_yaml = True,
                                                      supports_dict = True,
                                                      on_serialize = None,
                                                      on_deserialize = None),
                               AttributeConfiguration(name = 'password',
                                                      supports_csv = (True, False),
                                                      supports_json = (True, False),
                                                      supports_yaml = (True, False),
                                                      supports_dict = (True, False),
                                                      on_serialize = None,
                                                      on_deserialize = None)]

          # ADDITIONAL RELATIONSHIPS, HYBRID PROPERTIES, OR ASSOCIATION PROXIES
          # GO HERE

  .. tab:: Declarative: with Table

    .. code-block:: python

      from sqlathanor import declarative_base, Column, AttributeConfiguration

      from sqlalchemy import create_engine, Table, Integer, String

      BaseModel = declarative_base()

      engine = create_engine('... ENGINE CONFIGURATION GOES HERE ...')
      # NOTE: Because reflection relies on a specific SQLAlchemy Engine existing, presumably
      # you would know how to configure / instantiate your database engine using SQLAlchemy.
      # This is just here for the sake of completeness.

      UserTable = Table('users',
                        BaseModel.metadata,
                        Column('id',
                               Integer,
                               primary_key = True,
                               supports_csv = True,
                               csv_sequence = 1,
                               supports_json = True,
                               supports_yaml = True,
                               supports_dict = True,
                               on_serialize = None,
                               on_deserialize = None),
                        Column('password',
                               String(255),
                               supports_csv = (True, False),
                               csv_sequence = 2,
                               supports_json = (True, False),
                               supports_yaml = (True, False),
                               supports_dict = (True, False),
                               on_serialize = None,
                               on_deserialize = None))

      class ReflectedUser(BaseModel):
          __table__ = Table('users',
                            BaseModel.metadata,
                            autoload = True,
                            autoload_with = engine)

          # ADDITIONAL RELATIONSHIPS, HYBRID PROPERTIES, OR ASSOCIATION PROXIES
          # GO HERE

  .. tab:: Declarative: without Table

    .. tip::

      In practice, this pattern eliminates the time-saving benefits of using
      `reflection <http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/table_config.html#using-reflection-with-declarative>`_
      in the first place. Instead, I would recommend adopting the
      :ref:`meta configuration <meta_configuration>` pattern with reflection
      instead.

    .. code-block:: python

      from sqlathanor import declarative_base, Column, AttributeConfiguration

      from sqlalchemy import create_engine, Table, Integer, String

      BaseModel = declarative_base()

      engine = create_engine('... ENGINE CONFIGURATION GOES HERE ...')
      # NOTE: Because reflection relies on a specific SQLAlchemy Engine existing, presumably
      # you would know how to configure / instantiate your database engine using SQLAlchemy.
      # This is just here for the sake of completeness.

      class ReflectedUser(BaseModel):
          __table__ = Table('users',
                            BaseModel.metadata,
                            autoload = True,
                            autoload_with = engine)

          id = Column('id',
                      Integer,
                      primary_key = True,
                      supports_csv = True,
                      csv_sequence = 1,
                      supports_json = True,
                      supports_yaml = True,
                      supports_dict = True,
                      on_serialize = None,
                      on_deserialize = None)

          password = Column('password',
                            String(255),
                            supports_csv = (True, False),
                            csv_sequence = 2,
                            supports_json = (True, False),
                            supports_yaml = (True, False),
                            supports_dict = (True, False),
                            on_serialize = None,
                            on_deserialize = None)

          # ADDITIONAL RELATIONSHIPS, HYBRID PROPERTIES, OR ASSOCIATION PROXIES
          # GO HERE

----------------------------

.. _automap_pattern:

Using SQLAthanor with Automap
=============================================

.. versionadded:: 0.2.0

.. seealso::

  * :ref:`Using Automap with SQLAthanor <using_automap>`
  * **SQLAlchemy**: :doc:`Automap Extension <sqlalchemy:orm/extensions/automap>`

.. error::

  If you try to use :func:`automap_base() <sqlathanor.automap.automap_base>` with
  SQLAlchemy **v.0.9.0**, you will get a
  :exc:`SQLAlchemySupportError <sqlathanor.errors.SQLAlchemySupportError>`.

.. tabs::

  .. tab:: Declarative Approach

    .. code-block:: python

      from sqlathanor.automap import automap_base
      from sqlalchemy import create_engine

      # Create your Automap Base
      Base = automap_base()

      engine = create_engine('... DATABASE CONNECTION GOES HERE ...')

      # Prepare your automap base. This reads your database and creates your models.
      Base.prepare(engine, reflect = True)

      # And here you can create a "User" model class and an "Address" model class.
      User = Base.classes.users
      Address = Base.classes.addresses


      User.set_attribute_serialization_config('email_address',
                                              supports_csv = True,
                                              supports_json = True,
                                              supports_yaml = True,
                                              supports_dict = True)
      User.set_attribute_serialization_config('password',
                                              supports_csv = (True, False),
                                              supports_json = (True, False),
                                              supports_yaml = (True, False),
                                              supports_dict = (True, False),
                                              on_deserialize = my_encryption_function)

  .. tab:: Meta Approach

    .. code-block:: python

      from sqlathanor.automap import automap_base
      from sqlalchemy import create_engine

      # Create your Automap Base
      Base = automap_base()

      engine = create_engine('... DATABASE CONNECTION GOES HERE ...')

      # Prepare your automap base. This reads your database and creates your models.
      Base.prepare(engine, reflect = True)

      # And here you can create a "User" model class and an "Address" model class.
      User = Base.classes.users
      Address = Base.classes.addresses

      User.__serialization__ = [
          {
              'name': 'email_address',
              'supports_csv': True,
              'supports_json': True,
              'supports_yaml': True,
              'supports_dict': True
          },
          {
              'name': 'password',
              'supports_csv': (True, False),
              'supports_json': (True, False),
              'supports_yaml': (True, False),
              'supports_dict': (True, False),
              'on_deserialize': my_encryption_function
          }
      ]

----------------------------

Using SQLAthanor with Flask-SQLAlchemy
=========================================

.. seealso::

  * :ref:`Import SQLAthanor <importing>` > Using Flask-SQLAlchemy
  * `Flask-SQLAlchemy Documentation <http://flask-sqlalchemy.pocoo.org>`_

.. code-block:: python

  from sqlathanor import FlaskBaseModel, initialize_flask_sqlathanor
  from flask_sqlalchemy import SQLAlchemy

  db = SQLAlchemy(model_class = FlaskBaseModel)
  db = initialize_flask_sqlathanor(db)
