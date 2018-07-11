from sqlathanor.declarative import BaseModel
from sqlathanor.schema import relationship, Column

class FlaskBaseModel(BaseModel):
    """Base class that establishes shared methods, attributes, and properties.

    Designed to be supplied as a ``model_class`` when initializing
    :doc:`Flask-SQLAlchemy <flask_sqlalchemy:index>`.

    .. seealso::

      For detailed explanation of functionality, please see
      :class:`BaseModel <sqlathanor.declarative.BaseModel>`.

    """
    pass

def initialize_flask_sqlathanor(db):
    """Initialize **SQLAthanor** contents on a `Flask-SQLAlchemy`_ instance.

    :param db: The
      :class:`flask_sqlalchemy.SQLAlchemy <flask_sqlalchemy:flask_sqlalchemy.SQLAlchemy>`
      instance.
    :type db: :class:`flask_sqlalchemy.SQLAlchemy <flask_sqlalchemy:flask_sqlalchemy.SQLAlchemy>`

    :returns: A mutated instance of ``db`` that replaces `SQLAlchemy`_ components and
      their `Flask-SQLAlchemy`_ flavors with **SQLAthanor** analogs while maintaining
      `Flask-SQLAlchemy`_ and `SQLAlchemy`_ functionality and interfaces.
    :rtype: :class:`flask_sqlalchemy.SQLAlchemy <flask_sqlalchemy:flask_sqlalchemy.SQLAlchemy>`

    :raises ImportError: if called when `Flask-SQLAlchemy`_ is not installed
    :raises ValueError: if ``db`` is not an instance of
      :class:`flask_sqlalchemy.SQLAlchemy <flask_sqlalchemy:flask_sqlalchemy.SQLAlchemy>`

    """
    from flask_sqlalchemy import _wrap_with_default_query_class, SQLAlchemy

    if not isinstance(db, SQLAlchemy):
        raise ValueError('db must be an instance of flask_sqlalchemy.SQLAlchemy')

    db.Column = Column
    db.relationship = _wrap_with_default_query_class(relationship, db.Query)

    return db
