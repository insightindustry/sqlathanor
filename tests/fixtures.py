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
from sqlalchemy.orm import relationship, clear_mappers, Session
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

@pytest.fixture(scope = "session")
def db_engine(request):
    engine = create_engine('sqlite://')

    return engine

@pytest.yield_fixture(scope = 'session')
def tables(request, db_engine):
    BaseModel = declarative_base(cls = Base, metadata = MetaData())

    class User(BaseModel):
        """Mocked class with a single primary key."""

        __tablename__ = 'users'

        id = Column('id',
                    Integer,
                    primary_key = True)
        name = Column('username',
                      String(50))
        addresses = relationship('Address', backref = 'user')

    class Address(BaseModel):
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

    class User2(BaseModel):
        """Mocked class with a single primary key."""

        __tablename__ = 'users_composite'

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

    class Address2(BaseModel):
        """Mocked class with a single primary key."""

        __tablename__ = 'addresses_composite'

        id = Column('id',
                    Integer,
                    primary_key = True)
        email = Column('email_address',
                       String(50))
        user_id = Column('user_id',
                         Integer,
                         ForeignKey('users_composite.id'))

    BaseModel.metadata.create_all(db_engine)

    yield {
        'base_model': BaseModel,
        'model_single_pk': (User, Address),
        'model_composite_pk': (User2, Address2)
    }

    clear_mappers()
    BaseModel.metadata.drop_all(db_engine)
    BaseModel.metadata.clear()

@pytest.yield_fixture(scope = 'session')
def base_model(request, tables):
    BaseModel = tables['base_model']

    yield BaseModel


@pytest.yield_fixture
def db_session(request, db_engine, base_model):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind = connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture()
def model_single_pk(request, tables):
    User = tables['model_single_pk'][0]
    Address = tables['model_single_pk'][1]

    return (User, Address)


@pytest.fixture()
def instance_single_pk(request, model_single_pk):
    instance_values = {
        'id': 1,
        'name': 'Test Name'
    }
    user = model_single_pk[0]

    instance = user(**instance_values)

    return (instance, instance_values)


@pytest.fixture(scope = 'session')
def model_composite_pk(request, tables):
    User2 = tables['model_composite_pk'][0]
    Address2 = tables['model_composite_pk'][1]

    return (User2, Address2)


@pytest.fixture
def instance_composite_pk(request, model_composite_pk):
    instance_values = {
        'id': 1,
        'id2': 2,
        'id3': 3,
        'name': 'Test Name'
    }
    user = model_composite_pk[0]

    instance = user(**instance_values)

    return (instance, instance_values)
