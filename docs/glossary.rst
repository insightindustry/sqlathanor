**********
Glossary
**********

.. glossary::

  Association Proxy
    A concept in :doc:`SQLAlchemy <sqlalchemy:orm/extensions/associationproxy>`
    that is used to define a :term:`model attribute` within one :term:`model class`
    that acts as a proxy (mapping to) a model attribute on a different
    :term:`model class`, related by way of a :term:`relationship`.

    .. seealso::

      * **SQLAlchemy**: :func:`association_proxy <sqlalchemy:sqlalchemy.ext.associationproxy.association_proxy>`

  Athanor
    An alchemical furnace, sometimes called a *piger henricus* (slow henry),
    philosophical furnace, Furnace of Arcana, or Tower furnace. They were used
    by alchemists to apply uniform heat over an extended (weeks, even!) period
    of time and require limited maintenance / management.

    Basically, these were alchemical slow cookers.

    The term "athanor" is believed to derive from the Arabic *al-tannoor* ("bread
    oven") which Califate-era alchemical texts describe as being used for slow,
    uniform alchemical disgestion in talismanic alchemy.

  Comma-Separated Value (CSV)
    A text-based data exchange format where data is represented in one row of text,
    with fields (columns) separated by a delimiter character (typically a comma
    ``,`` or pipe ``|``).

  Declarative Configuration
    A way of configuring :term:`serialization` and :term:`de-serialization`
    for particular :term:`model attributes <model attribute>` when defining
    those attributes on the :term:`model class` using the
    :doc:`SQLAlchemy Declarative ORM <sqlalchemy:orm/extensions/declarative/index>`.

    .. tip::

      The Declarative Configuration approach does **not** support serialization
      or de-serialization for :term:`model attributes <model attribute>` that are not
      :class:`Column <sqlalthanor.schema.Column>` or
      :func:`relationship() <sqlathanor.schema.relationship>`.

      If you want to support serialization on
      :term:`hybrid properties <hybrid property>`,
      :term:`association proxies <association proxy>`, or
      :term:`instance attributes <instance attribute>` please use
      :term:`Meta Configuration`.

    .. seealso::

      * :ref:`Configure Serialization/De-serialization <configuration>` >
        :ref:`Declarative Configuration <declarative_configuration>`
      * :doc:`Quickstart <quickstart>` >
        :ref:`Declarative Configuration Pattern <declarative_configuration_pattern>`

  De-serialization
    De-Serialization - as you can probably guess - is the reverse of
    :term:`serialization`. It's the process whereby data is received in one format
    (say a JSON string) and is converted into a Python object (a
    :term:`model instance`) that you can more easily work with in your Python code.

    Think of it this way: A web app written in JavaScript needs to ask your Python
    code to register a user. Your Python code will need to know that user's details
    to register the user. So how does the web app deliver that information to your
    Python code? It'll most typically send JSON - but your Python code will need
    to then de-serialize (translate) it from JSON into an object representation
    (your ``User`` object) that it can work with.

  De-serialization Function
    A function that is called when :term:`de-serializing <de-serialization>` a
    specific value. The function accepts a single positional argument (the value
    to be de-serialized), does whatever it needs to do to the value, and then
    returns the value that will be assigned to the appropriate :term:`model attribute`.

    Typical usages include value validation and hashing/salting/encryption.
    **SQLAthanor** applies a set of default de-serialization functions that apply for
    the data types supported by :doc:`SQLAlchemy <sqlalchemy:index>` and its
    dialects.

    .. seealso::

      * :ref:`De-serialization Post-processing <deserialization_postprocessing>`

  Drop-in Replacement
    A Python library that extends the functionality of an existing library
    by inheriting from (and extending or modifying) its original classes or
    replacing its original functions.

  Hybrid Property
    A concept in :doc:`SQLAlchemy <sqlalchemy:orm/extensions/hybrid>` that
    is used to define a :term:`model attribute` that is not directly represented
    in the :term:`model class`'s underlying database table (i.e. the hybrid property
    is calculated/determined on-the-fly in your Python code when referenced).

    .. seealso::

      * **SQLAlchemy**: :class:`hybrid_property <sqlalchemy:sqlalchemy.ext.hybrid.hybrid_property>`

  Instance Attribute
    A :term:`model attribute` that is only present within a :term:`model instance`
    that is defined using Python's built-in :func:`@property <python:property>`
    decorator.

  JavaScript Object Notation (JSON)
    A lightweight data-interchange format that has become the *de facto* standard
    for communication across internet-enabled APIs.

    For a formal definition, please see the
    `ECMA-404 Standard: JSON Data Interchange Syntax <http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf>`_

  Meta Configuration
    A way of configuring :term:`serialization` and :term:`de-serialization` using
    a private :term:`model attribute` labeled ``__serialization__``.

    .. tip::

      Meta configuration is used to configure serialization/de-serialization for
      :term:`hybrid properties <hybrid property>`,
      :term:`association proxies <association proxy>`, and regular (non-hybrid)
      Python properties.

      .. seealso::

        * :ref:`Configure Serialization/De-serialization <configuration>` >
          :ref:`Meta Configuration <meta_configuration>`
        * :doc:`Quickstart <quickstart>` >
          :ref:`Meta Configuration Pattern <meta_configuration_pattern>`

  Model Attribute
    A property or attribute that belongs to a :term:`model class` or
    :term:`model instance`. It will typically correspond to an underlying database
    column, relationship (foreign key constraint), :term:`hybrid property`, or
    :term:`association proxy`.

    :term:`Serialization` and :term:`De-serialization` both operate on
    model attributes.

  Model Class
    A model class is a Python class that is used to instantiate
    :term:`model instances <model instance>`. It typically is constructed using
    the :doc:`SQLAlchemy ORM <sqlalchemy:orm/tutorial>`.

    A model class is composed of one or more :term:`model attributes <model attribute>`
    which correspond to columns in an underlying SQL table. The SQLAlchemy
    :term:`ORM <Object Relational Mapper (ORM)>` maps the model class to a corresponding
    :class:`Table <sqlalchemy:sqlalchemy.schema.Table>` object, which in turn
    describes the structure of the underlying SQL table.

    .. note::

      Throughout **SQLAthanor** we use the terms "model class" and "model"
      interchangably.

  Model Instance
    A model instance is an object representation of a database record in your
    Python code. Technically, it is an instance of a :term:`model class`.

    It stores and exposes the record's data and (if you're using a robust
    :term:`ORM <Object Relational Mapper (ORM)>` like
    `SQLAlchemy <https://www.sqlalchemy.org>`_) exposes methods to modify that data.

    .. note::

      Throughout **SQLAthanor** we use the terms "model instance" and "record"
      interchangably.

  Object Relational Mapper (ORM)
    An **Object Relational Mapper** (ORM) is a software tool that makes it easier
    to write code that reads data from or writes data to a relational database.

    Fundamentally, it maps a class in your code to the tables and columns in the
    underlying database so that you can work with that class, rather than worrying
    about how to construct multiple (often related!) records directly in SQL.

    The :doc:`SQLAlchemy ORM <sqlalchemy:orm/tutorial>`
    is one of the most powerful Python ORMs available, and also provides a great
    :doc:`Declarative <sqlalchemy:orm/extensions/declarative/index>`
    system that makes their super-powerful ORM incredibly easy to use.

  Pickling
    A process of :term:`serializing <serialization>` a Python object to a binary
    representation. Typically performed using the :doc:`pickle <python:library/pickle>`
    module from the standard Python library, or an outside pickling library like
    `dill <https://github.com/uqfoundation/dill>`_.

  Relationship
    A connection between two database tables or their corresponding
    :term:`model classes <model class>` defined using a foreign key constraint.

  Serialization
    Serialization is a process where a Python object (like a :term:`model instance`)
    is converted into a different format, typically more suited to transmission to
    or interpretation by some other program.

    Think of it this way: You've got a virtual representation of some information
    in your Python code. It's an object that you can work with in your Python code.
    But how do you give that information to some other application (like a web app)
    written in JavaScript? You serialize (translate) it into a format that other
    language can understand.

  Serialization Function
    A function that is called when :term:`serializing <serialization>` a specific
    value. The function accepts a single positional argument (the :term:`model attribute`
    value to serialize), does whatever it needs to do to the value, and then returns
    the value that will be included in the serialized output.

    Typical usages include value format conversion. **SQLAthanor** applies a set of
    default serialization functions that apply for the data types supported by
    :doc:`SQLAlchemy <sqlalchemy:index>` and its dialects.

    .. seealso::

      * :ref:`Serialization Pre-processing <serialization_preprocessing>`

  YAML Ain't a Markup Language (YAML)
    YAML is a text-based data serialization format similar in some respects to
    :term:`JSON <JavaScript Object Notation (JSON)>`. For more information, please
    see the `YAML 1.2 (3rd Edition) Specification <http://yaml.org/spec/1.2/spec.html>`_.

    .. note::

      If we're being absolutely formal, JSON is actually a subset of YAML's syntax.
      But that's being needlessly formal.
