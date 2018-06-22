# -*- coding: utf-8 -*-

"""
***********************************
tests._fixtures
***********************************

Fixtures used by the SQLAthanor test suite.

"""

import pytest

from sqlathanor import BaseModel as Base
from sqlathanor import Column, relationship

from sqlalchemy import Integer, String, ForeignKey, create_engine, MetaData
from sqlalchemy.orm import clear_mappers, Session, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy


from validator_collection import validators

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

        _hybrid = 1

        @hybrid_property
        def hybrid(self):
            return self._hybrid

        @hybrid.setter
        def hybrid(self, value):
            self._hybrid = value

        @hybrid_property
        def hybrid_differentiated(self):
            return self._hybrid

        @hybrid_differentiated.setter
        def hybrid_differentiated(self, value):
            self._hybrid = value

        keywords_basic = association_proxy('keywords_basic', 'keyword')

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

        _hybrid = 1
        @hybrid_property
        def hybrid(self):
            return self._hybrid

        @hybrid_property
        def hybrid_differentiated(self):
            return self._hybrid

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

    class User_Complex(BaseModel):
        """Mocked class with a single primary key with varied serialization support."""

        __tablename__ = 'users_complex'

        id = Column('id',
                    Integer,
                    primary_key = True,
                    supports_csv = True,
                    csv_sequence = 1,
                    supports_json = True,
                    supports_yaml = True,
                    supports_dict = True)
        name = Column('username',
                      String(50),
                      supports_csv = True,
                      csv_sequence = 2,
                      supports_json = True,
                      supports_yaml = True,
                      supports_dict = True)
        password = Column('password',
                          String(50),
                          supports_csv = (True, False),
                          csv_sequence = 3,
                          supports_json = (True, False),
                          supports_yaml = (True, False),
                          supports_dict = (True, False))
        hidden = Column('hidden_column',
                        String(50))

        addresses = relationship('Address_Complex',
                                 backref = 'user',
                                 supports_json = True,
                                 supports_yaml = (True, True),
                                 supports_dict = (True, False))

        _hybrid = 1

        @hybrid_property
        def hybrid(self):
            return self._hybrid

        @hybrid.setter
        def hybrid(self, value):
            self._hybrid = value

        @hybrid_property
        def hybrid_differentiated(self):
            return self._hybrid

        @hybrid_differentiated.setter
        def hybrid_differentiated(self, value):
            self._hybrid = value

        keywords_basic = association_proxy('keywords_basic',
                                           'keyword')

    class UserKeyword(BaseModel):
        __tablename__ = 'user_keywords'

        user_id = Column('user_id',
                         Integer,
                         ForeignKey('users.id'),
                         primary_key = True)
        keyword_id = Column('keyword_id',
                            Integer,
                            ForeignKey('keywords.id'),
                            primary_key = True)
        special_key = Column('special_key', String(50))

        user = relationship(User,
                            backref = backref('keywords_basic',
                                              cascade = 'all, delete-orphan'))

        keyword = relationship('Keyword')

        def __init__(self, keyword = None, user = None, special_key = None):
            self.user = user
            self.keyword = keyword
            self.special_key = special_key

    class UserKeyword_Complex(BaseModel):
        __tablename__ = 'user_keywords_complex'

        user_id = Column('user_id',
                         Integer,
                         ForeignKey('users_complex.id'),
                         primary_key = True)
        keyword_id = Column('keyword_id',
                            Integer,
                            ForeignKey('keywords.id'),
                            primary_key = True)
        special_key = Column('special_key', String(50))

        user = relationship(User_Complex,
                            backref = backref('keywords_basic',
                                              cascade = 'all, delete-orphan'))
        keyword = relationship('Keyword')

        def __init__(self, keyword = None, user = None, special_key = None):
            self.user = user
            self.keyword = keyword
            self.special_key = special_key

    class Keyword(BaseModel):
        __tablename__ = 'keywords'

        id = Column('id',
                    Integer,
                    primary_key = True)
        keyword = Column('keyword',
                         String(50),
                         supports_csv = True)

        def __init__(self, id, keyword):
            self.id = id
            self.keyword = keyword


    class Address_Complex(BaseModel):
        """Mocked class with a single primary key."""

        __tablename__ = 'addresses_complex'

        id = Column('id',
                    Integer,
                    primary_key = True)
        email = Column('email_address',
                       String(50),
                       supports_csv = True,
                       supports_json = True,
                       supports_yaml = True,
                       supports_dict = True,
                       on_serialize = validators.email,
                       on_deserialize = validators.email)
        user_id = Column('user_id',
                         Integer,
                         ForeignKey('users_complex.id'))


    BaseModel.metadata.create_all(db_engine)

    yield {
        'base_model': BaseModel,
        'model_single_pk': (User, Address),
        'model_composite_pk': (User2, Address2),
        'model_complex': (User_Complex, Address_Complex)
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


@pytest.fixture(scope = 'session')
def model_complex(request, tables):
    User = tables['model_complex'][0]
    Address = tables['model_complex'][1]

    return (User, Address)


@pytest.fixture
def instance_complex(request, model_complex):
    user_instance_values = {
        'id': 1,
        'name': 'test_username',
        'password': 'test_password',
        'hidden': 'hidden value'
    }
    address_instance_values = {
        'id': 1,
        'email': 'test@domain.com',
        'user_id': 1
    }
    user = model_complex[0]
    address = model_complex[1]

    user_instance = user(**user_instance_values)
    address_instance = address(**address_instance_values)

    instances = (user_instance, address_instance)
    instance_values = (user_instance_values, address_instance_values)

    return (instances, instance_values)
