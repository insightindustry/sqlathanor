"""
******************************************
tests.test_relationship_sererialize
******************************************

Tests display name when relationships are deserialized.

"""

import pytest

from sqlathanor import declarative_base, Column, relationship

from sqlalchemy import Integer, String, Sequence, ForeignKey

from validator_collection import validators, checkers

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


@pytest.mark.parametrize('email, error', [
    ('scott@example.com', None),
    (['scott@example.com', 'frank@example.com'], None),
])
def test_display_name_used_for_attribute_on_serialize(email, error):

    user = User()
    if checkers.is_string(email):
        user.addresses = [Address(email = email)]
        expected_string = '{"all-addresses": [{"email": "%s"}]}' % email
    else:
        user.addresses = [Address(email = x) for x in email]
        email_string = ''
        for x in email:
            email_string += '{"email": "%s"}, ' % x
        email_string = email_string[:-2]
        expected_string = '{"all-addresses": [%s]}' % email_string

    json_str = user.to_json(max_nesting=2)
    if not error:
        assert json_str == expected_string

@pytest.mark.parametrize('email_string, expected_result, error', [
    ('[{"email": "scott@example.com"}]', ["scott@example.com"], None),
    ('[{"email": "scott@example.com"}, {"email": "frank@example.com"}]', ["scott@example.com", "frank@example.com"], None),
    ('[{"email": "scott@example.com"},{"email": "frank@example.com"}]', ["scott@example.com", "frank@example.com"], None),
])
def test_display_name_used_for_attribute_on_deserialize(email_string, expected_result, error):
    input_string = '{"all-addresses": %s}' % email_string

    if not error:
        user_obj = User.new_from_json(input_string)
        assert len(user_obj.addresses) == len(expected_result)
        deserialized_emails = [x.email for x in user_obj.addresses]
        for email in expected_result:
            assert email in expected_result
        for address in user_obj.addresses:
            assert address.email in expected_result
    else:
        with pytest.raises(error):
            user_obj = User.new_from_json(input_string)
            assert len(user_obj.addresses) == len(expected_result)
            deserialized_emails = [x.email for x in user_obj.addresses]
            for email in expected_result:
                assert email in expected_result
            for address in user_obj.addresses:
                assert address.email in expected_result
