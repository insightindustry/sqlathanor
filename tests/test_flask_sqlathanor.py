# -*- coding: utf-8 -*-

"""
******************************************
tests.test_flask_sqlathanor
******************************************

Tests that the Flask-SQLAlchemy integration works correctly.

"""
# pylint: disable=line-too-long

import pytest

from tests.fixtures import flask_app

from sqlathanor import FlaskBaseModel, initialize_flask_sqlathanor
from sqlathanor.schema import Column, RelationshipProperty

from sqlalchemy import Integer
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from flask_sqlalchemy.model import Model as FlaskModel

@pytest.mark.parametrize('cls, fails', [
    (FlaskBaseModel, False),
    (FlaskModel, True),
])
def test_initialize_flask_sqlathanor(flask_app, cls, fails):
    db = SQLAlchemy(app = flask_app, model_class = cls)

    if not fails:
        db = initialize_flask_sqlathanor(db)

    expected_result = not fails

    assert hasattr(db.Model, 'to_json') is expected_result

    relationship = db.relationship('test_relationship')
    assert isinstance(relationship, RelationshipProperty) is expected_result

    column = db.Column('test_column', Integer)
    assert isinstance(column, Column) is expected_result
