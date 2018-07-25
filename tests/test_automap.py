# -*- coding: utf-8 -*-

"""
******************************************
tests.test_automap
******************************************

Tests for :doc:`Automap <sqlalchemy:sqlalchemy.ext.automap>` support.

"""

from sqlalchemy import create_engine
from sqlalchemy.orm import session
from sqlalchemy.ext.automap import AutomapBase

from sqlathanor.declarative import BaseModel
from sqlathanor.automap import automap_base

from tests.fixtures import existing_db


def test_automap_base(request, existing_db):

    Base = automap_base()

    engine = create_engine('sqlite:///%s' % existing_db)
    assert len(engine.table_names()) == 2

    Base.prepare(engine, reflect = True)

    assert len(Base.classes) == 2

    User = Base.classes.users
    Address = Base.classes.addresses

    assert hasattr(User, 'to_csv') == True
    assert hasattr(User, 'to_json') == True
    assert hasattr(User, 'to_yaml') == True
    assert hasattr(User, 'to_dict') == True
    assert hasattr(User, 'new_from_csv') == True

    assert hasattr(Address, 'to_csv') == True
    assert hasattr(Address, 'to_json') == True
    assert hasattr(Address, 'to_yaml') == True
    assert hasattr(Address, 'to_dict') == True
    assert hasattr(Address, 'new_from_csv') == True

    assert len(User.get_serialization_config(from_csv = True,
                                             to_csv = True,
                                             from_json = True,
                                             to_json = True,
                                             from_yaml = True,
                                             to_yaml = True,
                                             from_dict = True,
                                             to_dict = True)) == 0


def test_set_serialization(request, existing_db):

    Base = automap_base()

    engine = create_engine('sqlite:///%s' % existing_db)
    Base.prepare(engine, reflect = True)

    User = Base.classes.users
    Address = Base.classes.addresses

    User.set_attribute_serialization_config('col1',
                                            supports_csv = True,
                                            supports_json = True,
                                            supports_yaml = True,
                                            supports_dict = True)

    assert len(User.get_serialization_config(from_csv = True,
                                             to_csv = True,
                                             from_json = True,
                                             to_json = True,
                                             from_yaml = True,
                                             to_yaml = True,
                                             from_dict = True,
                                             to_dict = True)) == 1
