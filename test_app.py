from sqlalchemy.orm import session
import unittest
from sqlalchemy import create_engine, Column, Table, Column, Integer, String, MetaData, ForeignKey, text, delete, update
from sqlalchemy.orm import Session, relationship, session
import sqlalchemy

# Use the default method for abstracting classes to tables
from app import *


class SimpleTest(unittest.TestCase):
    conn = None
    session = None
    element_id = None
    # for the sake of time constraint not created test db

    def setUp(self) -> None:
        engine = create_engine("sqlite:///app.sqlite")
        self.conn = engine.connect()
        self.session = Session(bind=engine)
        return super().setUp()

    def test_add(self):
        args = {'--help': False,
                '--version': False,
                '-a': True,
                '-d': False,
                '-f': False,
                '-u': False,
                '<element>': '{"sport":{"name": "swiming", "display_name": "Swiming", "slug": "swiming", "order":1, "active": 0}}',
                '<filter>': None}
        self.__class__.element_id = add(self.conn, self.session, args)
        self.assertGreaterEqual(self.__class__.element_id, 1)

    def test_update(self):
        args = {'--help': False,
                '--version': False,
                '-a': False,
                '-d': False,
                '-f': False,
                '-u': True,
                '<element>': '{"sport":{"id": ' + str(self.__class__.element_id) + ', "values": {"name": "boxing", "display_name": "Boxing", "slug": "boxing", "order":2}}}',
                '<filter>': None}
        self.assertEqual(update_element(self.conn, self.session, args), True)

    def test_search(self):
        args = {'--help': False,
                '--version': False,
                '-a': False,
                '-d': False,
                '-f': True,
                '-u': False,
                '<element>': None,
                '<filter>': '{"all": "box"}'}
        response = search(
            self.conn, self.session, args)
        self.assertIsInstance(response, sqlalchemy.engine.cursor.LegacyCursorResult)

    def test_active(self):
        args = {'--help': False,
                '--version': False,
                '-a': False,
                '-d': False,
                '-f': True,
                '-u': False,
                '<element>': None,
                '<filter>': '{"active": "0"}'}
        response = search(
            self.conn, self.session, args)
        self.assertIsInstance(response, sqlalchemy.engine.cursor.LegacyCursorResult)

    def test_delete(self):
        args = {'--help': False,
                '--version': False,
                '-a': False,
                '-d': True,
                '-f': False,
                '-u': False,
                '<element>': '{"sport":{"id":' + str(self.__class__.element_id) + '}}',
                '<filter>': None}
        self.assertGreaterEqual(delete_element(
            self.conn, self.session, args), 1)


if __name__ == '__main__':
    unittest.main()
