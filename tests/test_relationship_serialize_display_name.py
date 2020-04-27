"""
******************************************
tests.test_relationship_sererialize
******************************************

Tests display name when relationships are deserialized.

"""

from sqlathanor import declarative_base, Column, relationship

from sqlalchemy import Integer, String, Sequence, ForeignKey

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key = True)

    addresses = relationship("Address",
                             backref = "user",
                             lazy = "joined",
                             supports_json = True,
                             display_name = "all-addresses"
                             )


class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer,primary_key=True)

    email = Column(String,
                   nullable=False,
                   supports_json=True,
                   )

    user_id = Column(Integer, ForeignKey('users.id'))


def test_display_name_used_for_attribute():

    scott = User()
    email_com = 'scott@example.com'
    scott.addresses = [Address(email=email_com)]

    json_str = scott.to_json(max_nesting=2)

    assert json_str == '{"all-addresses": [{"email": "%s"}]}' % (email_com)
