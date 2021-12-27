-----------

Release 0.8.0
=========================================

.. image:: https://travis-ci.com/insightindustry/sqlathanor.svg?branch=v.0.8.0
  :target: https://travis-ci.com/insightindustry/sqlathanor
  :alt: Build Status (Travis CI)

.. image:: https://codecov.io/gh/insightindustry/sqlathanor/branch/v.0.8.0/graph/badge.svg
  :target: https://codecov.io/gh/insightindustry/sqlathanor
  :alt: Code Coverage Status (Codecov)

.. image:: https://readthedocs.org/projects/sqlathanor/badge/?version=v.0.8.0
  :target: http://sqlathanor.readthedocs.io/en/latest/?badge=v.0.8.0
  :alt: Documentation Status (ReadTheDocs)

New Features
-----------------

* #99: Added `Pydantic <https://pydantic-docs.helpmanual.io/>`_ support. This includes:

  * the ability to generate **SQLAthanor** model classes from Pydantic models
    (``generate_model_from_pydantic()``)
  * the ability to generate ``Table`` objects from Pydantic models
    (``Table.from_pydantic()``)
  * the ability to create ``AttributeConfiguration`` instances from fields in a Pydantic
    model (``AttributeConfiguration.from_pydantic_model()``)
  * updates to documentation to reflect new functionality

Other Changes
------------------

* Updated PyYAML requirement to v.5.4 to address security vulnerability.
* #100: Fixed missing documentation.
* Cleaned up ``requirements.txt`` to reduce dependencies.
* Minor bug fixes.

-----------

Release 0.7.0
=========================================

.. image:: https://travis-ci.com/insightindustry/sqlathanor.svg?branch=v.0.7.0
  :target: https://travis-ci.com/insightindustry/sqlathanor
  :alt: Build Status (Travis CI)

.. image:: https://codecov.io/gh/insightindustry/sqlathanor/branch/v.0.7.0/graph/badge.svg
  :target: https://codecov.io/gh/insightindustry/sqlathanor
  :alt: Code Coverage Status (Codecov)

.. image:: https://readthedocs.org/projects/sqlathanor/badge/?version=v.0.7.0
  :target: http://sqlathanor.readthedocs.io/en/latest/?badge=v.0.7.0
  :alt: Documentation Status (ReadTheDocs)

Bug Fixes
-----------------

* Fixed a typo in the documentation (thanks, @timmy224!)

Other Changes
------------------

* Significant performance improvement through the introduction of a heap cache (thanks,
  @digitalkaoz!)
* Added contributors list.

-----------

Release 0.6.0
=========================================

.. image:: https://travis-ci.com/insightindustry/sqlathanor.svg?branch=v.0.6.0
  :target: https://travis-ci.com/insightindustry/sqlathanor
  :alt: Build Status (Travis CI)

.. image:: https://codecov.io/gh/insightindustry/sqlathanor/branch/v.0.6.0/graph/badge.svg
  :target: https://codecov.io/gh/insightindustry/sqlathanor
  :alt: Code Coverage Status (Codecov)

.. image:: https://readthedocs.org/projects/sqlathanor/badge/?version=v.0.6.0
  :target: http://sqlathanor.readthedocs.io/en/latest/?badge=v.0.6.0
  :alt: Documentation Status (ReadTheDocs)

Bug Fixes
-----------------

* #87: Fixed a longstanding bug that prevented one-to-one relationships from being
  deserialized properly.

Other Changes
------------------

* #89: Implemented support for ``display_name`` on relationships.
* Updated test matrix to maintain test compability in the Python 3.4 environment.

-----------

Release 0.5.1
=========================================

.. image:: https://travis-ci.com/insightindustry/sqlathanor.svg?branch=v.0.5.1
  :target: https://travis-ci.com/insightindustry/sqlathanor
  :alt: Build Status (Travis CI)

.. image:: https://codecov.io/gh/insightindustry/sqlathanor/branch/v.0.5.1/graph/badge.svg
  :target: https://codecov.io/gh/insightindustry/sqlathanor
  :alt: Code Coverage Status (Codecov)

.. image:: https://readthedocs.org/projects/sqlathanor/badge/?version=v.0.5.1
  :target: http://sqlathanor.readthedocs.io/en/latest/?badge=v.0.5.1
  :alt: Documentation Status (ReadTheDocs)

Bug Fixes
-----------------

* #80: Revised how the default deserializer functions for ``datetime.timedelta``
  and ``datetime.datetime`` objects functions. When deserializing either, the
  default deserializer now starts by attempting to coerce the value to a
  ``datetime.timedelta`` using the Validator Collection ``timedelta()`` validator
  function, which supports the expression of amounts of time as both integers (e.g.
  ``23 seconds``) and strings (e.g. ``00:00:23``). If the object cannot be
  converted to a ``timedelta`` (if it is a complete / proper datetime with both
  a time and date value), the default deserializer will then revert to returning
  a ``datetime.datetime`` object.
* #82: Revised the minimum version needed for the Validator Collection library
  to resolve a bug in iterable serialization/deserialization.

Other Changes
------------------

* #84: Added Python 3.8 to test matrix.

-----------

Release 0.5.0
=========================================

.. image:: https://travis-ci.com/insightindustry/sqlathanor.svg?branch=v.0.5.0
  :target: https://travis-ci.com/insightindustry/sqlathanor
  :alt: Build Status (Travis CI)

.. image:: https://codecov.io/gh/insightindustry/sqlathanor/branch/v.0.5.0/graph/badge.svg
  :target: https://codecov.io/gh/insightindustry/sqlathanor
  :alt: Code Coverage Status (Codecov)

.. image:: https://readthedocs.org/projects/sqlathanor/badge/?version=v.0.5.0
  :target: http://sqlathanor.readthedocs.io/en/latest/?badge=v.0.5.0
  :alt: Documentation Status (ReadTheDocs)

New Features
-----------------

* #68: Replaced serialization to ``dict`` with serialization to ``OrderedDict`` to preserve
  key ordering when serializing to JSON and YAML. The interface and interaction
  with ``OrderedDict`` should be 100% consistent with the behavior of past ``dict``
  objects - just now their order will be preserved when on Python versions before
  3.7.

Bug Fixes
-----------------

* #71: Modified default ``to_str()`` serializer function to coerce values to strings.
* #73: Corrected a variety of mismatches in the default serializer/deserializer
  functions relating to ``datetime.timedelta`` objects and SQLAlchemy ``Interval``
  and ``DATETIME`` type objects.
* #75: Corrected a bug that may have introduced errors in applications using
  Python 3.7, SQLAlchemy 1.3+, and relying on ``AssociationProxy`` constructions
  in their models.
* Updated the ``requirements.txt`` (which does not actually indicate utilization
  dependencies, and instead indicates development dependencies) to upgrade
  a number of libraries that had recently had security vulnerabilities
  discovered.


-----------

Release 0.4.0
=========================================

.. image:: https://travis-ci.com/insightindustry/sqlathanor.svg?branch=v.0.4.0
  :target: https://travis-ci.com/insightindustry/sqlathanor
  :alt: Build Status (Travis CI)

.. image:: https://codecov.io/gh/insightindustry/sqlathanor/branch/v.0.4.0/graph/badge.svg
  :target: https://codecov.io/gh/insightindustry/sqlathanor
  :alt: Code Coverage Status (Codecov)

.. image:: https://readthedocs.org/projects/sqlathanor/badge/?version=v.0.4.0
  :target: http://sqlathanor.readthedocs.io/en/latest/?badge=v.0.4.0
  :alt: Documentation Status (ReadTheDocs)

Bug Fixes
-----------------

* #63: Fixed error handling for when SQLAlchemy returns ``UnsupportedCompilationError`` on
  certain data types.

New Features
-----------------

* #61: Added ``display_name`` attribute configuration option to re-write attribute names
  on serialization / de-serialization.
* #62: Added support for multiple named configuration sets when using the meta
  configuration pattern.

Other Changes
------------------

* Upgraded PyYAML version in ``requirements.txt``.

-----------

Release 0.3.1
=========================================

.. image:: https://travis-ci.com/insightindustry/sqlathanor.svg?branch=v.0.3.1
  :target: https://travis-ci.com/insightindustry/sqlathanor
  :alt: Build Status (Travis CI)

.. image:: https://codecov.io/gh/insightindustry/sqlathanor/branch/v.0.3.1/graph/badge.svg
  :target: https://codecov.io/gh/insightindustry/sqlathanor
  :alt: Code Coverage Status (Codecov)

.. image:: https://readthedocs.org/projects/sqlathanor/badge/?version=v.0.3.1
  :target: http://sqlathanor.readthedocs.io/en/latest/?badge=v.0.3.1
  :alt: Documentation Status (ReadTheDocs)

Bug Fixes
-----------------

* #58: Fixed problem where ``None`` values are mistakenly serialized to empty lists.
* #57: Fixed problem where ``on_serialize`` functions were ignored for relationships.
* #56: Fixed problem where relationships were not properly deserialized.

Other Changes
------------------

* #26: Added Python 3.7 to test matrix.
* Removed some unnecessary print statements.

-----------

Release 0.3.0
=========================================

.. image:: https://travis-ci.com/insightindustry/sqlathanor.svg?branch=v.0.3.0
  :target: https://travis-ci.com/insightindustry/sqlathanor
  :alt: Build Status (Travis CI)

.. image:: https://codecov.io/gh/insightindustry/sqlathanor/branch/v.0.3.0/graph/badge.svg
  :target: https://codecov.io/gh/insightindustry/sqlathanor
  :alt: Code Coverage Status (Codecov)

.. image:: https://readthedocs.org/projects/sqlathanor/badge/?version=v.0.3.0
  :target: http://sqlathanor.readthedocs.io/en/latest/?badge=v.0.2.2
  :alt: Documentation Status (ReadTheDocs)

New Features
-----------------

* #35: Added ``BaseModel.dump_to_csv()``
* #35: Added ``BaseModel.dump_to_json()``
* #35: Added ``BaseModel.dump_to_yaml()``
* #35: Added ``BaseModel.dump_to_dict()``
* #34: Added ``BaseModel.configure_serialization()``
* #42: Added support for the programmatic generation of declarative model classes.
* #41: Added support for the programmatic generation of ``Table`` objects.
* #51: All ``*from_<format>()`` methods and functions now accept Path-like objects
  as inputs to load serialized data from a file.

Other Changes
---------------

* #43: Refactored declarative classes and functions.
* #50: Updated `Validator-Collection <https://validator-collection.readthedocs.io/en/latest>`_
  dependency.

-----------

Release 0.2.2
=========================================

.. image:: https://travis-ci.com/insightindustry/sqlathanor.svg?branch=v.0.2.2
  :target: https://travis-ci.com/insightindustry/sqlathanor
  :alt: Build Status (Travis CI)

.. image:: https://codecov.io/gh/insightindustry/sqlathanor/branch/v.0.2.2/graph/badge.svg
  :target: https://codecov.io/gh/insightindustry/sqlathanor
  :alt: Code Coverage Status (Codecov)

.. image:: https://readthedocs.org/projects/sqlathanor/badge/?version=v.0.2.2
  :target: http://sqlathanor.readthedocs.io/en/latest/?badge=v.0.2.2
  :alt: Documentation Status (ReadTheDocs)

Bugs Fixed
------------

* #36: Fixed error in documentation
  (``flask_sqlathanor.initialize_flask_sqlathanor()`` initially documented as
  ``flask_sqlathanor.initialize_sqlathanor()``).

Other Changes
---------------

* #32: Added Code of Conduct.

-----------

Release 0.2.1
=========================================

.. image:: https://travis-ci.com/insightindustry/sqlathanor.svg?branch=v.0.2.1
  :target: https://travis-ci.com/insightindustry/sqlathanor
  :alt: Build Status (Travis CI)

.. image:: https://codecov.io/gh/insightindustry/sqlathanor/branch/v.0.2.1/graph/badge.svg
  :target: https://codecov.io/gh/insightindustry/sqlathanor
  :alt: Code Coverage Status (Codecov)

.. image:: https://readthedocs.org/projects/sqlathanor/badge/?version=v.0.2.1
  :target: http://sqlathanor.readthedocs.io/en/latest/?badge=v.0.2.1
  :alt: Documentation Status (ReadTheDocs)

Bugs Fixed
------------

* #30: Tweaked function signature for ``declarative_base()`` to make ``cls`` a
  keyword argument.

-----------

Release 0.2.0
=========================================

.. image:: https://travis-ci.com/insightindustry/sqlathanor.svg?branch=v.0.2.0
  :target: https://travis-ci.com/insightindustry/sqlathanor
  :alt: Build Status (Travis CI)

.. image:: https://codecov.io/gh/insightindustry/sqlathanor/branch/v.0.2.0/graph/badge.svg
  :target: https://codecov.io/gh/insightindustry/sqlathanor
  :alt: Code Coverage Status (Codecov)

.. image:: https://readthedocs.org/projects/sqlathanor/badge/?version=v.0.2.0
  :target: http://sqlathanor.readthedocs.io/en/latest/?badge=v.0.2.0
  :alt: Documentation Status (ReadTheDocs)

Features Added
----------------

* #21: Added support for `SQLAlchemy Automap Extension`_.
* #27: Added support for programmatically modifying serialization/de-serialization
  configuration after model definition.

------------------

Release 0.1.1
=========================================

.. image:: https://travis-ci.com/insightindustry/sqlathanor.svg?branch=v.0.1.1
  :target: https://travis-ci.com/insightindustry/sqlathanor
  :alt: Build Status (Travis CI)

.. image:: https://codecov.io/gh/insightindustry/sqlathanor/branch/v.0.1.1/graph/badge.svg
  :target: https://codecov.io/gh/insightindustry/sqlathanor
  :alt: Code Coverage Status (Codecov)

.. image:: https://readthedocs.org/projects/sqlathanor/badge/?version=v.0.1.1
  :target: http://sqlathanor.readthedocs.io/en/latest/?badge=v.0.1.1
  :alt: Documentation Status (ReadTheDocs)

* #22: Added unit tests testing support for `SQLAlchemy Declarative Reflection`_.
* #23: Added documentation for **SQLAthanor** usage with `SQLAlchemy Declarative Reflection`_.
* #24: Added documentation comparing/contrasting to alternative serialization/deserialization
  libraries.
* Fixed project URLs in ``setup.py`` for display on PyPi.

------------------

Release 0.1.0
=========================================

.. image:: https://travis-ci.com/insightindustry/sqlathanor.svg?branch=v.0.1.0
  :target: https://travis-ci.com/insightindustry/sqlathanor
  :alt: Build Status (Travis CI)

.. image:: https://codecov.io/gh/insightindustry/sqlathanor/branch/v.0.1.0/graph/badge.svg
  :target: https://codecov.io/gh/insightindustry/sqlathanor
  :alt: Code Coverage Status (Codecov)

.. image:: https://readthedocs.org/projects/sqlathanor/badge/?version=v.0.1.0
  :target: http://sqlathanor.readthedocs.io/en/latest/?badge=v.0.1.0
  :alt: Documentation Status (ReadTheDocs)

* First public release

.. _SQLAlchemy Declarative Reflection: http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/table_config.html#using-reflection-with-declarative
.. _SQLAlchemy Automap Extension: http://docs.sqlalchemy.org/en/latest/orm/extensions/automap.html
