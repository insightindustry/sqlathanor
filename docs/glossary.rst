**********
Glossary
**********

.. glossary::

  Object Relational Mapper (ORM)
    An **Object Relational Mapper** (ORM) is a software tool that makes it easier
    to write code that reads data from or writes data to a relational database.

    Fundamentally, it maps a class in your code to the tables and columns in the
    underlying database so that you can work with that class, rather than worrying
    about how to construct multiple (often related!) records directly in SQL.

    The `SQLAlchemy ORM <http://docs.sqlalchemy.org/en/latest/orm/tutorial.html>`_
    is one of the most powerful Python ORMs available, and also provides a great
    `Declarative <http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/index.html>`_
    system that makes their super-powerful ORM incredibly easy to use.

  Serialization
    Serialization is a process where a Python object (say a :term:`model instance`)
    is converted into a different format, typically more suited to transmission to
    or interpretation by some other program.

    Think of it this way: You've got a virtual representation of some information
    in your Python code. It's an object that you can work with in your Python code.
    But how do you give that information to some other application (like a web app)
    written in JavaScript? You serialize (translate) it into a format that other
    language can understand.

  De-Serialization
    De-Serialization - as you can probably guess - is the reverse of
    :term:`serialization`. It's the process whereby data is received in one format
    (say a JSON string) and is converted into a Python object (say a
    :term:`model instance`) that you can more easily work with in your Python code.

    Think of it this way: A web app written in JavaScript needs to ask your Python
    code to register a user. Your Python code will need to know that user's details
    to register the user. So how does the web app deliver that information to your
    Python code? It'll most typically send JSON - but your Python code will need
    to then de-serialize (translate) it from JSON into an object representation
    (your ``User`` object) that it can work with.

  Model Instance
    A model instance is an object representation of a database record in your
    Python code.

    It stores and exposes the record's data and (if you're using a robust
    :term:`ORM <Object Relational Mapper (ORM)>` like
    `SQLAlchemy <https://www.sqlalchemy.org>`_) exposes methods to modify that data.

    .. note::

      Throughout **SQLAthanor** we use the terms "model instance" and "record"
      interchangably.
