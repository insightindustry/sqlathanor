# -*- coding: utf-8 -*-

# The lack of a module docstring for this module is **INTENTIONAL**.
# The module is imported into the documentation using Sphinx's autodoc
# extension, and its member function documentation is automatically incorporated
# there as needed.

import sqlalchemy

try:
    from sqlalchemy.ext.automap import automap_base as SA_automap_base
    SUPPORTS_AUTOMAP = True
except ImportError:
    SUPPORTS_AUTOMAP = False
    SA_automap_base = bool

from validator_collection import checkers

from sqlathanor import BaseModel
from sqlathanor.errors import SQLAlchemySupportError


def automap_base(declarative_base = None,
                 **kwargs):
    """Produce a declarative automap base.

    This function produces a new base class that is a product of the
    :class:`AutomapBase <sqlalchemy:sqlalchemy.ext.automap.AutomapBase>` class
    as well as a declarative base that you supply.

    If no declarative base is supplied, then the **SQLAthanor** default
    :class:`BaseModel <sqlathanor.declarative.BaseModel>` will be used, to provide
    serialization/de-serialization support to the resulting automapped base class.

    :param declarative_base: The declarative base class that is to be combined with
      the :class:`AutomapBase <sqlalchemy:sqlalchemy.ext.automap.AutomapBase>` class
      to construct the resulting automapped :term:`model class`. To ensure that
      **SQLAthanor** :term:`serialization`/:term:`de-serialization` functionality
      is provided to your automapped model class, make sure that the value provided
      is produced by
      :func:`sqlathanor.declarative_base() <sqlathanor.declarative.declarative_base>`
      or otherwise inherits from :class:`sqlathanor.declarative.BaseModel`. If
      ``None``, will default to :class:`sqlathanor.declarative.BaseModel`.
    :type declarative_base: The declarative base model to combine with the automapped
      :term:`model class` produced.

    :param kwargs: Passed to
      :func:`declarative_base() <sqlalchemy:sqlalchemy.ext.declarative.declarative_base>`
    :type kwargs: keyword arguments

    :returns: A :class:`AutomapBase <sqlalchemy:sqlalchemy.ext.automap.AutomapBase>`
      that can reflect your database schema structure with auto-generated
      declarative models that support **SQLAthanor** serialization/de-serialization.
    :rtype: :class:`AutomapBase <sqlalchemy:sqlalchemy.ext.automap.AutomapBase>`

    :raises SQLAlchemySupportError: if called in an environment where `SQLAlchemy`_
      is installed with a version less than 0.9.1 (which introduces automap support).

    """
    # pylint: disable=redefined-variable-type

    if not SUPPORTS_AUTOMAP:
        raise SQLAlchemySupportError(
            'automap is only available in SQLAlchemy v.0.9.1 and higher, ' + \
            'but you are using %s. Please upgrade.' % sqlalchemy.__version__
        )

    if declarative_base is None:
        cls = BaseModel
    elif isinstance(declarative_base, BaseModel) or declarative_base == BaseModel:
        cls = declarative_base
    elif isinstance(declarative_base, tuple):
        for item in declarative_base:
            if item == BaseModel or isinstance(item, BaseModel):
                cls = declarative_base
                break
    else:
        cls = kwargs.pop('cls', None)
        if cls is None and checkers.is_iterable(declarative_base):
            class_list = [BaseModel]
            class_list.extend([x for x in declarative_base])
        elif cls is None and not checkers.is_iterable(declarative_base):
            class_list = [BaseModel, declarative_base]
        elif checkers.is_iterable(cls) and checkers.is_iterable(declarative_base):
            class_list = [BaseModel]
            class_list.extend([x for x in cls])
            class_list.extend([x for x in declarative_base])
        elif cls is not None and checkers.is_iterable(declarative_base):
            class_list = [BaseModel, cls]
            class_list.extend([x for x in declarative_base])
        elif cls is not None and not checkers.is_iterable(declarative_base):
            class_list = [BaseModel, cls, declarative_base]

        for item in class_list[1:]:
            if item == BaseModel or isinstance(item, BaseModel):
                class_list = class_list[1:]
                break

        cls = tuple(x for x in class_list)

    automapped_base = SA_automap_base(declarative_base = cls, **kwargs)

    return automapped_base
