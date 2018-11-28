# -*- coding: utf-8 -*-

"""
******************************************
tests.test_relationship_deserialize
******************************************

Tests how relationships are deserialized. Based on a reported bug in
`Github #56 <https://github.com/insightindustry/sqlathanor/issues/56>`_

"""
# pylint: disable=line-too-long

import pytest

from sqlathanor import declarative_base, Column, relationship

from sqlalchemy import create_engine, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer,
                Sequence('user_id_seq'),
                primary_key = True,
                supports_dict = True,
                )

    name = Column(String,
                  supports_dict = True,
                  )

    addresses = relationship("Address",
                             backref = "user",
                             lazy = "joined",
                             supports_dict = True,
                             )

    def __repr__(self):
        return "<User(id='{0:s}', name='{1:s}')>".format(
            str(self.id),
            self.name,
            )


class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer,
                primary_key=True,
                supports_dict = True,
                )

    email = Column(String,
                   nullable=False,
                   supports_dict = True,
                   )

    user_id = Column(Integer,
                     ForeignKey('users.id'),
                     supports_dict = True,
                     )

    def __repr__(self):
        return "<Address(email='{0:s}')>".format(
            self.email,
            )

@pytest.fixture
def json_passes():
    return {
        'id': 1,
        'name': 'John Doe',
        'addresses': []
    }

@pytest.fixture
def json_fails():
    return {
        'id': 1,
        'name': 'John Doe',
        'addresses': [
            {
                'id': 2,
                'email': 'john@test.com',
                'user_id': 1
            },
            {
                'id': 3,
                'email': 'john2@test.com',
                'user_id': 1
            }
        ]
    }


@pytest.mark.parametrize('use_fails', [
    (False),
    (True),
])
def test_relationship_new_from_json(json_passes, json_fails, use_fails):
    engine = create_engine('sqlite:///')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind = engine)
    session = Session()

    if use_fails:
        input = json_fails
    else:
        input = json_passes

    result = User.new_from_dict(input)
    assert isinstance(result, User)
    print(result)
    
