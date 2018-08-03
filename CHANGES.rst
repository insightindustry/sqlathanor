-----------

Release 0.3.0
=========================================

New Features
-----------------

* #35: Added ``BaseModel.dump_to_csv()``
* #35: Added ``BaseModel.dump_to_json()``
* #35: Added ``BaseModel.dump_to_yaml()``
* #35: Added ``BaseModel.dump_to_dict()``
* #34: Added ``BaseModel.configure_serialization()``

-----------

Release 0.2.2
=========================================

Bugs Fixed
------------

* #36: Fixed error in documentation
  (``flask_sqlathanor.initialize_flask_sqlathanor()`` initially documented as
  ``flask_sqlathanor.initialize_sqlathanor()``).

Other Changes
---------------

* 32: Added Code of Conduct.

-----------

Release 0.2.1
=========================================

Bugs Fixed
------------

* #30: Tweaked function signature for ``declarative_base()`` to make ``cls`` a
  keyword argument.

-----------

Release 0.2.0
=========================================

Features Added
----------------

* #21: Added support for `SQLAlchemy Automap Extension`_.
* #27: Added support for programmatically modifying serialization/de-serialization
  configuration after model definition.

------------------

Release 0.1.1
=========================================

* #22: Added unit tests testing support for `SQLAlchemy Declarative Reflection`_ (#22).
* #23: Added documentation for **SQLAthanor** usage with `SQLAlchemy Declarative Reflection`_.
* #24: Added documentation comparing/contrasting to alternative serialization/deserialization
  libraries.
* Fixed project URLs in ``setup.py`` for display on PyPi.

------------------

Release 0.1.0
=========================================

* First public release

.. _SQLAlchemy Declarative Reflection: http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/table_config.html#using-reflection-with-declarative
.. _SQLAlchemy Automap Extension: http://docs.sqlalchemy.org/en/latest/orm/extensions/automap.html
