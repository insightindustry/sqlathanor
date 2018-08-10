# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

from sqlalchemy.ext.declarative import declarative_base as SA_declarative_base
from validator_collection import checkers

from sqlathanor.declarative.base_model import BaseModel

# pylint: disable=no-member

def declarative_base(cls = BaseModel, **kwargs):
    """Construct a base class for declarative class definitions.

    The new base class will be given a metaclass that produces appropriate
    :class:`Table <sqlalchemy:sqlalchemy.schema.Table>` objects and makes the
    appropriate :func:`mapper <sqlalchemy:sqlalchemy.orm.mapper>` calls based on the
    information provided declaratively in the class and any subclasses of the class.

    :param cls: Defaults to :class:`BaseModel` to provide serialization/de-serialization
      support.

      If a :class:`tuple <python:tuple>` of classes, will include :class:`BaseModel`
      in that list of classes to mixin serialization/de-serialization support.

      If not :obj:`None <python:None>` and not a :class:`tuple <python:tuple>`, will mixin
      :class:`BaseModel` with the value passed to provide
      serialization/de-serialization support.
    :type cls: :obj:`None <python:None>` / :class:`tuple <python:tuple>` of
      classes / class object

    :param kwargs: Additional keyword arguments supported by the original
      :func:`sqlalchemy.ext.declarative.declarative_base() <sqlalchemy:sqlalchemy.ext.declarative.declarative_base>`
      function
    :type kwargs: keyword arguments

    :returns: Base class for declarative class definitions with support for
      serialization and de-serialization.

    """
    if isinstance(cls, tuple):
        class_list = [x for x in cls]
        class_list.insert(0, BaseModel)
        cls = (x for x in class_list)
    elif checkers.is_iterable(cls):
        class_list = [BaseModel]
        class_list.extend(cls)
        cls = (x for x in class_list)

    return SA_declarative_base(cls = cls, **kwargs)


def as_declarative(**kw):
    """Class decorator for :func:`declarative_base`.

    Provides a syntactical shortcut to the ``cls`` argument
    sent to :func:`declarative_base`, allowing the base class
    to be converted in-place to a "declarative" base:

    .. code-block:: python

        from sqlathanor import as_declarative

        @as_declarative()
        class Base(object):
            @declared_attr
            def __tablename__(cls):
                return cls.__name__.lower()

            id = Column(Integer,
                        primary_key = True,
                        supports_csv = True)

        class MyMappedClass(Base):
            # ...

    .. tip::

      All keyword arguments passed to :func:`as_declarative` are passed
      along to :func:`declarative_base`.

    .. seealso::

      * :func:`declarative_base() <declarative_base>`
    """
    def decorate(cls):
        kw['cls'] = cls
        kw['name'] = cls.__name__
        return declarative_base(**kw)

    return decorate
