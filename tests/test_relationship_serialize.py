# -*- coding: utf-8 -*-

"""
******************************************
tests.test_relationship_serialize
******************************************

Tests how relationships are serialized. Based on a reported bug in
`Github #57 <https://github.com/insightindustry/sqlathanor/issues/57>`_

"""
# pylint: disable=line-too-long

import pytest

from sqlathanor import declarative_base, Column, relationship

from sqlalchemy import create_engine, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


def serialize_address(input):
    raise RuntimeError('error was raised successfully!')


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
                             on_serialize = serialize_address,
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


@pytest.mark.parametrize('max_nesting, error', [
    (2, RuntimeError),
    (0, RuntimeError),
])
def test_relationship_on_serialize(max_nesting, error):
    engine = create_engine('sqlite:///')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind = engine)
    session = Session()

    scott = User(name='scott')
    scott.addresses = [Address(email='scott@example.com'),
                       Address(email='scott@example.org')]
    session.add(scott)
    session.commit()

    if not error:
        result = scott.to_dict(max_nesting = max_nesting)
    else:
        with pytest.raises(error):
            scott.to_dict(max_nesting = max_nesting)
