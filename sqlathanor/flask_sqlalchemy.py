from sqlathanor.declarative import BaseModel

class FlaskBaseModel(BaseModel):
    """Base class that establishes shared methods, attributes, and properties.

    Designed to be supplied as a ``model_class`` when initializing
    :doc:`Flask-SQLAlchemy <flask_sqlalchemy:index>`.

    .. seealso::

      For detailed explanation of functionality, please see
      :class:`BaseModel <sqlathanor.declarative.BaseModel>`.

    """
    pass
