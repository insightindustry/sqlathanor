**********************************
API Reference
**********************************

.. contents::
  :local:
  :depth: 4
  :backlinks: entry

----------

.. module:: sqlathanor.declarative

Declarative ORM
===================

**SQLAthanor** provides a drop-in replacement for SQLAlchemy's
:func:`declarative_base() <sqlalchemy:sqlalchemy.ext.declarative.declarative_base>`
function and decorators, which can either be used as a base for your SQLAlchemy
models directly or can be mixed into your SQLAlchemy models.

.. seealso::

  It is :class:`BaseModel` which exposes the methods and properties that enable
  :term:`serialization` and :term:`de-serialization` support.

  For more information, please see:

  * :doc:`Using SQLAthanor <using>`.

BaseModel
------------------------

.. autoclass:: BaseModel
  :members:
  :inherited-members:

------------------------

declarative_base()
-------------------------

.. autofunction:: declarative_base

----------------------------------------

@as_declarative
--------------------

.. autofunction:: as_declarative

----------------------------------------

generate_model_from_csv()
----------------------------

.. autofunction:: generate_model_from_csv

----------------------------------------

generate_model_from_json()
-----------------------------

.. autofunction:: generate_model_from_json

----------------------------------------

generate_model_from_yaml()
----------------------------

.. autofunction:: generate_model_from_yaml

----------------------------------------

generate_model_from_dict()
----------------------------

.. autofunction:: generate_model_from_dict

----------------------------------------

generate_model_from_pydantic()
-------------------------------------

.. autofunction:: generate_model_from_pydantic

--------------------------------------------------------

.. module:: sqlathanor.schema

Schema
===========

The classes defined in ``sqlathanor.schema`` are drop-in replacements for
SQLAlchemy's
`Core Schema elements <http://docs.sqlalchemy.org/en/latest/core/metadata.html>`_.

They add :term:`serialization` and :term:`de-serialization` support to your
model's columns and relationsips, and so should replace your imports of their
:doc:`SQLAlchemy <sqlalchemy:index>` analogs.

.. seealso::

  * :doc:`Using SQLAthanor <using>`

Column
------------

.. autoclass:: Column

  .. automethod:: Column.__init__

----------------------------

relationship()
----------------

.. function:: relationship(argument, supports_json = False, supports_yaml = False, supports_dict = False, **kwargs)

  Provide a relationship between two mapped classes.

  .. seealso::

      * :class:`RelationshipProperty`
      * :func:`sqlalchemy.orm.relationship() <sqlalchemy:sqlalchemy.orm.relationship>`

  .. warning::

    This constructor is analogous to the original
    SQLAlchemy :func:`relationship() <sqlalchemy:sqlalchemy.orm.relationship>`
    from which it inherits. The only difference is that it supports additional
    keyword arguments which are not supported in the original, and which
    are documented below.

    **For the original SQLAlchemy version, see:** :func:`sqlalchemy.orm.relationship() <sqlalchemy:sqlalchemy.orm.relationship>`

  :param argument: see
    :func:`sqlalchemy.orm.relationship() <sqlalchemy:sqlalchemy.orm.relationship>`

  :param supports_json: Determines whether the column can be serialized to or
    de-serialized from JSON format.

    If ``True``, can be serialized to JSON and de-serialized from JSON.
    If ``False``, will not be included when serialized
    to JSON and will be ignored if present in a de-serialized JSON.

    Can also accept a 2-member :class:`tuple <python:tuple>` (inbound / outbound)
    which determines de-serialization and serialization support respectively.

    Defaults to ``False``, which means the column will not be serialized to JSON
    or de-serialized from JSON.

  :type supports_json: :class:`bool <python:bool>` / :class:`tuple <python:tuple>` of
    form (inbound: :class:`bool <python:bool>`, outbound: :class:`bool <python:bool>`)

  :param supports_yaml: Determines whether the column can be serialized to or
    de-serialized from YAML format.

    If ``True``, can be serialized to YAML and
    de-serialized from YAML. If ``False``, will not be included when serialized
    to YAML and will be ignored if present in a de-serialized YAML.

    Can also accept a 2-member :class:`tuple <python:tuple>` (inbound / outbound)
    which determines de-serialization and serialization support respectively.

    Defaults to ``False``, which means the column will not be serialized to YAML
    or de-serialized from YAML.

  :type supports_yaml: :class:`bool <python:bool>` / :class:`tuple <python:tuple>` of
    form (inbound: :class:`bool <python:bool>`, outbound: :class:`bool <python:bool>`)

  :param supports_dict: Determines whether the column can be serialized to or
    de-serialized to a Python :class:`dict <python:dict>`.

    If ``True``, can
    be serialized to :class:`dict <python:dict>` and de-serialized from a
    :class:`dict <python:dict>`. If ``False``, will not be included when serialized
    to :class:`dict <python:dict>` and will be ignored if present in a de-serialized
    :class:`dict <python:dict>`.

    Can also accept a 2-member :class:`tuple <python:tuple>` (inbound / outbound)
    which determines de-serialization and serialization support respectively.

    Defaults to ``False``, which means the column will not be serialized to a
    :class:`dict <python:dict>` or de-serialized from a :class:`dict <python:dict>`.

  :type supports_dict: :class:`bool <python:bool>` / :class:`tuple <python:tuple>` of
    form (inbound: :class:`bool <python:bool>`, outbound: :class:`bool <python:bool>`)

----------------

Table
--------

.. autoclass:: Table

  .. automethod:: Table.__init__

  .. automethod:: Table.from_csv

  .. automethod:: Table.from_dict

  .. automethod:: Table.from_json

  .. automethod:: Table.from_yaml

  .. automethod:: Table.from_pydantic

----------------------------

.. module:: sqlathanor.attributes

Attribute Configuration
===========================

The following classes and functions are used to apply :term:`meta configuration`
to your SQLAlchemy model.

.. seealso::

    * :doc:`Using SQLAthanor <using>`

AttributeConfiguration
-------------------------

.. autoclass:: AttributeConfiguration
  :members: fromkeys, name, from_attribute
  :inherited-members:

  .. automethod:: AttributeConfiguration.__init__

  .. automethod:: from_pydantic_model

----------------------

validate_serialization_config()
-----------------------------------

.. autofunction:: validate_serialization_config

---------------------

.. module:: sqlathanor.flask_sqlathanor

Flask-SQLAlchemy / Flask-SQLAthanor
======================================

initialize_flask_sqlathanor()
--------------------------------

.. autofunction:: initialize_flask_sqlathanor

-----------------------------------------------------

FlaskBaseModel
------------------

.. class:: FlaskBaseModel

  Base class that establishes shared methods, attributes, and properties.

  Designed to be supplied as a ``model_class`` when initializing
  `Flask-SQLAlchemy`_.

  .. seealso::

    For detailed explanation of functionality, please see
    :class:`BaseModel <sqlathanor.declarative.BaseModel>`.

---------------------

.. module:: sqlathanor.automap

Automap
======================================

.. autofunction:: automap_base

---------------------

SQLAthanor Internals
=======================

RelationshipProperty
-----------------------

.. autoclass:: sqlathanor.schema.RelationshipProperty

.. _SQLAlchemy: http://www.sqlalchemy.org
.. _Flask-SQLAlchemy: http://flask-sqlalchemy.pocoo.org
