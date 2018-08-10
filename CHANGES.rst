-----------

Release 0.3.0
=========================================

.. image:: https://travis-ci.org/insightindustry/sqlathanor.svg?branch=v.0.3.0
  :target: https://travis-ci.org/insightindustry/sqlathanor
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

.. image:: https://travis-ci.org/insightindustry/sqlathanor.svg?branch=v.0.2.2
  :target: https://travis-ci.org/insightindustry/sqlathanor
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

.. image:: https://travis-ci.org/insightindustry/sqlathanor.svg?branch=v.0.2.1
  :target: https://travis-ci.org/insightindustry/sqlathanor
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

.. image:: https://travis-ci.org/insightindustry/sqlathanor.svg?branch=v.0.2.0
  :target: https://travis-ci.org/insightindustry/sqlathanor
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

.. image:: https://travis-ci.org/insightindustry/sqlathanor.svg?branch=v.0.1.1
  :target: https://travis-ci.org/insightindustry/sqlathanor
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

.. image:: https://travis-ci.org/insightindustry/sqlathanor.svg?branch=v.0.1.0
  :target: https://travis-ci.org/insightindustry/sqlathanor
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
