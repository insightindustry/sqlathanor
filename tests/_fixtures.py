# -*- coding: utf-8 -*-

"""
***********************************
tests._fixtures
***********************************

Fixtures used by the SQLAthanor test suite.

"""

import pytest

from sqlathanor import BaseModel as Base

from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, MetaData
from sqlalchemy.orm import relationship, clear_mappers

class State(object):
    """Class to hold incremental test state."""
    # pylint: disable=too-few-public-methods
    pass



@pytest.fixture
def state(request):
    """Return the :class:`State` object that holds incremental test state."""
    # pylint: disable=W0108
    return request.cached_setup(
        setup = lambda: State(),
        scope = "session"
    )

@pytest.fixture(scope = 'function')
def base_model(request):

    engine = create_engine('sqlite://')

    def finalizer():
        clear_mappers()
        Base.metadata.drop_all(engine)
        Base.metadata.clear()

    request.addfinalizer(finalizer)

    Base.metadata.create_all(engine)

    return Base


@pytest.fixture(scope = "function")
def model_single_pk(request, base_model):

    User = None
    Address = None

    class User(base_model):
        """Mocked class with a single primary key."""

        __tablename__ = 'users'

        id = Column('id',
                    Integer,
                    primary_key = True)
        name = Column('username',
                      String(50))
        addresses = relationship('Address', backref = 'user')

    class Address(base_model):
        """Mocked class with a single primary key."""

        __tablename__ = 'addresses'

        id = Column('id',
                    Integer,
                    primary_key = True)
        email = Column('email_address',
                       String(50))
        user_id = Column('user_id',
                         Integer,
                         ForeignKey('users.id'))

    return (User, Address)


@pytest.fixture(scope = "function")
def model_composite_pk(request, base_model):

    class User2(base_model):
        """Mocked class with a single primary key."""

        __tablename__ = 'users'

        id = Column('id',
                    Integer,
                    primary_key = True)
        id2 = Column('id2',
                     Integer,
                     primary_key = True)
        id3 = Column('id3',
                     Integer,
                     primary_key = True)
        name = Column('username',
                      String(50))
        addresses = relationship('Address2', backref = 'user')

    class Address2(base_model):
        """Mocked class with a single primary key."""

        __tablename__ = 'addresses'

        id = Column('id',
                    Integer,
                    primary_key = True)
        email = Column('email_address',
                       String(50))
        user_id = Column('user_id',
                         Integer,
                         ForeignKey('users.id'))

    return (User2, Address2)
