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
from sqlalchemy.ext.declarative import declarative_base

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

@pytest.yield_fixture
def base_model(request):

    engine = create_engine('sqlite://')

    BaseModel = declarative_base(cls = Base, metadata = MetaData())
    BaseModel.metadata.clear()
    BaseModel.metadata.create_all(engine)

    yield BaseModel

    clear_mappers()
    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.clear()


@pytest.fixture
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


@pytest.fixture
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
