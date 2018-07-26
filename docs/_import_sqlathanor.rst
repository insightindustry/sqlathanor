Since **SQLAthanor** is a :term:`drop-in replacement`, you should import it using
the same elements as you would import from :doc:`SQLAlchemy <sqlalchemy:orm/tutorial>`:

.. tabs::

  .. tab:: Using SQLAlchemy

    The code below is a pretty standard set of ``import`` statements when
    working with `SQLAlchemy`_ and its
    :doc:`Declarative ORM <sqlalchemy:orm/extensions/declarative/index>`.

    They're provided for reference below, but do **not** make use of
    **SQLAthanor** and do **not** provide any support for :term:`serialization`
    or :term:`de-serialization`:

    .. code-block:: python

      from sqlalchemy.ext.declarative import declarative_base, as_declarative
      from sqlalchemy import Column, Integer, String          # ... and any other data types

      # The following are optional, depending on how your data model is designed:
      from sqlalchemy.orm import relationship
      from sqlalchemy.ext.hybrid import hybrid_property
      from sqlalchemy.ext.associationproxy import association_proxy

  .. tab:: Using SQLAthanor

    To import **SQLAthanor**, just replace the relevant `SQLAlchemy`_ imports
    with their **SQLAthanor** counterparts as below:

    .. code-block:: python

      from sqlathanor import declarative_base, as_declarative
      from sqlathanor import Column
      from sqlathanor import relationship             # This import is optional, depending on
                                                      # how your data model is designed.

      from sqlalchemy import Integer, String          # ... and any other data types

      # The following are optional, depending on how your data model is designed:
      from sqlalchemy.ext.hybrid import hybrid_property
      from sqlalchemy.ext.associationproxy import association_proxy

    .. tip::

      Because of its many moving parts, `SQLAlchemy`_
      splits its various pieces into multiple modules and forces you to use many
      ``import`` statements.

      The example above maintains this strategy to show how **SQLAthanor** is a
      1:1 drop-in replacement. But obviously, you can import all of the items you
      need in just one ``import`` statement:

      .. code-block:: python

        from sqlathanor import declarative_base, as_declarative, Column, relationship

  .. tab:: Using Flask-SQLAlchemy

    **SQLAthanor** is designed to work with `Flask-SQLAlchemy`_ too! However,
    you need to:

    #. Import the :class:`FlaskBaseModel <sqlathanor.flask_sqlathanor.FlaskBaseModel>`
       class, and then supply it as the ``model_class`` argument when initializing
       `Flask-SQLAlchemy`_.
    #. Initialize **SQLAthanor** on your ``db`` instance using
       :func:`initialize_flask_sqlathanor <sqlathanor.flask_sqlathanor.initialize_flask_sqlathanor>`.

    .. code-block:: python

      from sqlathanor import FlaskBaseModel, initialize_flask_sqlathanor
      from flask_sqlalchemy import SQLAlchemy

      db = SQLAlchemy(model_class = FlaskBaseModel)
      db = initialize_flask_sqlathanor(db)

    And that's it! Now **SQLAthanor** serialization functionality will be supported
    by:

    * Flask-SQLAlchemy's :class:`db.Model <flask_sqlalchemy:models>`
    * Flask-SQLAlchemy's :func:`db.relationship() <flask_sqlalchemy:one-to-many-relationships>`
    * Flask-SQLAlchemy's
      :class:`db.Column <flask_sqlalchemy:flask_sqlalchemy.SQLAlchemy.Column>`

    .. seealso::

      For more information about working with `Flask-SQLAlchemy`_, please review
      their `detailed documentation <http://flask-sqlalchemy.pocoo.org/>`_.

As the examples provided above show, importing **SQLAthanor** is very straightforward,
and you can include it in an existing codebase quickly and easily. In fact, your code
should work **just as before**. Only now it will include new functionality to
support serialization and de-serialization.

The table below shows how `SQLAlchemy`_ classes and functions map to their
**SQLAthanor** replacements:

.. list-table::
  :widths: 50 50
  :header-rows: 1

  * - `SQLAlchemy`_ Component
    - **SQLAthanor** Analog
  * - :func:`declarative_base() <sqlalchemy:sqlalchemy.ext.declarative.declarative_base>`

      .. code-block:: python

        from sqlalchemy.ext.declarative import declarative_base

    - :func:`declarative_base() <sqlathanor.declarative.declarative_base>`

      .. code-block:: python

        from sqlathanor import declarative_base

  * - :func:`@as_declarative <sqlalchemy:sqlalchemy.ext.declarative.as_declarative>`

      .. code-block:: python

        from sqlalchemy.ext.declarative import as_declarative

    - :func:`@as_declarative <sqlathanor.declarative.as_declarative>`

      .. code-block:: python

        from sqlathanor import as_declarative

  * - :class:`Column <sqlalchemy:sqlalchemy.schema.Column>`

      .. code-block:: python

        from sqlalchemy import Column

    - :class:`Column <sqlathanor.schema.Column>`

      .. code-block:: python

        from sqlathanor import Column

  * - :func:`relationship() <sqlalchemy:sqlalchemy.orm.relationship>`

      .. code-block:: python

        from sqlalchemy import relationship

    - :class:`relationship() <sqlathanor.schema.relationship>`

      .. code-block:: python

        from sqlathanor import relationship

  * - :func:`ext.automap.automap_base() <sqlalchemy:sqlalchemy.ext.automap.automap_base>`

      .. code-block:: python

        from sqlalchemy.ext.automap import automap_base

    - :func:`automap.automap_base() <sqlathanor.automap.automap_base>`

      .. code-block:: python

        from sqlathanor.automap import automap_base
