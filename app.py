"""
Command send to RCs.

Usage:
  app [-h]
  app [-v]
  app [-a <element>]
  app [-u <element>]
  app [-d <element>]
  app [-f <filter>]

Options:
  -h --help                       Sports bet application:
                                        app <option> <parameters>
                                  To create a element eg. sport or event or market or selection:
                                        app -a <element name>
                                  To update a element eg. sport or event or market or selection:
                                        app -u <element name>
                                  To delete a element eg. sport or event or market or selection:
                                        app -d <element name>
                                  To search:
                                        app -f <search filter name>

  -v --version                    Show version.

  -a                              With element name and all details in JSON format

  -u                              With element name and all details in JSON format

  -d                              With element name and all details in JSON format

  -f                              With serach filter conditions and all details in JSON format



"""

import time
import os
from os.path import exists
import sys
from pathlib import Path
import signal
from docopt import docopt
import re
import json
from sqlalchemy import create_engine, Column, Table, Column, Integer, String, MetaData, ForeignKey, text, delete, update
from sqlalchemy.orm import Session, relationship, session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

# Use the default method for abstracting classes to tables
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import DECIMAL, Boolean
from sqlalchemy import inspect, Index


Base = declarative_base()


class Sport(Base):
    """
    This class will handle all methods for command execution for sport
    """
    __tablename__ = 'sports'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False, unique=True)
    slug = Column(String(255), nullable=False, unique=True)
    order = Column(Integer)
    active = Column(Boolean, default=False)
    __table_args__ = (UniqueConstraint(
        'name', 'display_name', 'slug', name='_sports_uc'),)


class Event(Base):
    """
    This class will handle all methods for command execution for event
    """
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    sport_id = Column(Integer, ForeignKey('sports.id'))
    name = Column(String(255), nullable=False, unique=True)
    type = Column(Integer, nullable=False)
    status = Column(Integer)
    slug = Column(String(255), nullable=False, unique=True)
    active = Column(Boolean, default=False)
    __table_args__ = (UniqueConstraint('name', 'slug', name='_events_uc'),)


class Market(Base):
    """
    This class will handle all methods for command execution for market
    """
    __tablename__ = 'markets'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False, unique=True)
    order = Column(Integer)
    active = Column(Boolean, default=False)
    schema = Column(Integer, nullable=False)
    columns = Column(Integer)
    __table_args__ = (UniqueConstraint(
        'name', 'display_name', name='_markets_uc'),)


class MarketEvent(Base):
    """
    This class will handle all methods for command execution for selection
    """
    __tablename__ = 'marketevents'
    id = Column(Integer, primary_key=True)
    market_id = Column(Integer, ForeignKey('markets.id'))
    event_id = Column(Integer, ForeignKey('events.id'))
    active = Column(Boolean, default=False)


class Selection(Base):
    """
    This class will handle all methods for command execution for selection
    """
    __tablename__ = 'selections'
    id = Column(Integer, primary_key=True)
    marketevent_id = Column(Integer, ForeignKey('marketevents.id'))
    price = Column(DECIMAL(10, 2))
    name = Column(String(255), nullable=False, unique=True)
    outcome = Column(Integer)
    active = Column(Boolean, default=False)
    __table_args__ = (UniqueConstraint('name', name='_selections_uc'),)


def is_json(myjson):
    try:
        if isinstance(myjson, str):
            json.loads(myjson)
    except ValueError as e:
        return False

    return True


# Handle Ctrl + C interrupt
interrupted = False


def signal_handler(signal, frame):
    """
    Signal Handler to exit the program
    """
    global interrupted
    interrupted = True


signal.signal(signal.SIGINT, signal_handler)


def save_into_db(session, object) -> int:
    """
    It will save into database table

    Args:
        objects ([array]): [details of the object to be saved]

    Returns:
        [int]: [last inserted id]
    """
    session.add(object)

    # Commit changes to database
    session.commit()
    return object.id


def finds(session, obj, condition) -> String:
    """
    It will query and find all matched results
    """
    try:
        result = session.query(obj).filter(text(condition)).all()

    except MultipleResultsFound as e:
        print(e)
        # Deal with it
    except NoResultFound as e:
        print(e)
        # Deal with that as well

    return result


def find(session, obj, condition, join_obj=None) -> String:
    """
    It will query and find one
    """
    result = None
    try:
        if not join_obj:
            result = session.query(obj).filter(
                text(condition)).one_or_none()
        else:
            result = session.query(obj).join(join_obj).filter(
                text(condition)).one_or_none()

    except MultipleResultsFound as e:
        print(e)
        # Deal with it
    except NoResultFound as e:
        print(e)
        # Deal with that as well

    return result


def add(conn, session, args):
    parameters = []
    market_event_id = None

    if is_json(args['<element>']):
        parameters = json.loads(args['<element>'])
        new_id = None

        """
        {"sport":{"name": "football", "display_name": "Football", "slug": "football", "order":1, "active": 0}}

        {"event":{"sport_id":1, "name": "France vs England", "status": 0, "slug": "france_vs_england", "type":"0", "active": 0}}

        {"market":{"name": "full time result", "display_name": "Full Time Result", "order":"1", "schema":"2", "columns":"3", "active": 0}}

        {"selection":{"market_id":"1", "event_id":"1", "name": "France", "price": "1.85", "outcome": "win",  "active": 1}}
        """
        if 'sport' in parameters:
            new_sport = Sport(
                name=parameters['sport']['name'], display_name=parameters['sport']['display_name'],
                slug=parameters['sport']['slug'], order=parameters['sport']['order'],
                active=parameters['sport']['active'])
            new_id = save_into_db(session, new_sport)

        elif 'event' in parameters:
            # check sport id available or not
            sport = find(session, Sport,
                         "sports.id = " + parameters['event']['sport_id'])

            # sports data matched
            if sport:
                new_event = Event(sport_id=parameters['event']['sport_id'], name=parameters['event']['name'],
                                  type=parameters['event']['type'],
                                  slug=parameters['event']['slug'], status=parameters['event']['status'], active=1)
                new_id = save_into_db(session, new_event)

        elif 'market' in parameters:
            new_market = Market(name=parameters['market']['name'], display_name=parameters['market']['display_name'],
                                order=parameters['market']['order'], schema=parameters['market']['schema'],
                                columns=parameters['market']['columns'], active=0)
            new_id = save_into_db(session, new_market)

        elif 'selection' in parameters:
            market_event = find(
                session, MarketEvent,
                "(marketevents.market_id=" + parameters['selection']['market_id'] + ") & (marketevents.event_id=" +
                parameters['selection']['event_id'] + ") & (marketevents.active=1)")

            if market_event:
                market_event_id = market_event.id
            else:
                # add market event
                new_market_event = MarketEvent(
                    market_id=parameters['selection']['market_id'], event_id=parameters['selection']['event_id'],
                    active=1)
                market_event_id = save_into_db(session, new_market_event)

            new_selection = Selection(marketevent_id=market_event_id, name=parameters['selection']['name'],
                                      price=parameters['selection']['price'],
                                      outcome=parameters['selection']['outcome'], active=1)
            new_id = save_into_db(session, new_selection)

            # activate market
            stmt = update(Market).where(
                Market.id == parameters['selection']['market_id']).values(active=1)
            conn.execute(stmt)

            # activate event
            stmt = update(Event).where(
                Event.id == parameters['selection']['event_id']).values(active=1)
            conn.execute(stmt)

            # activate sport
            event_sport_details = find(
                session, Sport, "events.sport_id=" + parameters['selection']['event_id'], Event)
            if event_sport_details.active == 0:
                stmt = update(Sport).where(
                    Sport.id == event_sport_details.id).values(active=1)
                conn.execute(stmt)

        return new_id


def update_element(conn, session, args):
    """
    This will update details of an element
    """
    parameters = []
    market_event_id = None

    if is_json(args['<element>']):
        parameters = json.loads(args['<element>'])
        """
        {"sport":{"id":1, "values": {"name": "football", "display_name": "Football", "slug": "football", "order":1}}}

        {"event":{"id":1, "values": {"name": "France vs England", "status": 0, "slug": "france_vs_england", "type":"0"}}}

        {"market":{"id":1, "values": {"name": "full time result", "display_name": "Full Time Result", "order":"1", "schema":"2", "columns":"3"}}}

        {"selection":{"id":1, "values": {"market_id":"1", "event_id":"1", "name": "France", "price": "1.85", "outcome": "win"}}}
        """
        if 'sport' in parameters:
            stmt = update(Sport).where(
                Sport.id == parameters['sport']['id']).values(parameters['sport']['values'])
            conn.execute(stmt)

        elif 'event' in parameters:
            # for this version sport_id cant change for event
            # otherwise need to update all related changes in different places
            if 'sport_id' in parameters['event']['values']:
                return "Sport ID cant be change for a Event"

            stmt = update(Event).where(Event.id == parameters['event']['id']).values(
                parameters['event']['values'])
            conn.execute(stmt)

        elif 'market' in parameters:
            stmt = update(Market).where(Market.id == parameters['market']['id']).values(
                parameters['market']['values'])
            conn.execute(stmt)

        elif 'selection' in parameters:
            # existing selection
            selection = find(
                session, Selection,
                "selections.id=" + str(parameters['selection']['id']))

            if selection:
                # get selection related marketevent details
                marketevent = find(
                    session, MarketEvent,
                    "marketevents.id=" + str(selection.marketevent_id))
            else:
                return "Selection ID not found"

            if marketevent and (int(marketevent.market_id) != int(parameters['selection']['values']['market_id']) or int(marketevent.event_id) != int(parameters['selection']['values']['event_id'])):
                # find previous market event connected with any other selection
                selections_for_marketevent = finds(session, Selection, "(selections.marketevent_id=" + str(
                    selection.marketevent_id) + ") & (selections.id != " + str(parameters['selection']['id']) + ")")

                # if it is not connected with any selection then need to deactivate or delete
                if not selections_for_marketevent:
                    stmt = delete(MarketEvent).where(
                        MarketEvent.id == marketevent.id)
                    conn.execute(stmt)

            # find if already marketevent available for this market_id and event_id
            market_event = find(
                session, MarketEvent,
                "(marketevents.market_id=" + parameters['selection']['values']['market_id'] + ") & (marketevents.event_id=" +
                parameters['selection']['values']['event_id'] + ") & (marketevents.active=1)")

            if market_event:
                market_event_id = market_event.id
            else:
                # add new market event
                new_market_event = MarketEvent(
                    market_id=parameters['selection']['values']['market_id'], event_id=parameters['selection']['values']['event_id'],
                    active=1)
                market_event_id = save_into_db(session, new_market_event)

            # activate market
            stmt = update(Market).where(
                Market.id == parameters['selection']['values']['market_id']).values(active=1)
            conn.execute(stmt)

            # activate event
            stmt = update(Event).where(
                Event.id == parameters['selection']['values']['event_id']).values(active=1)
            conn.execute(stmt)

            # update the selection
            stmt = update(Selection).where(Selection.id == parameters['selection']['id']).values(
                {"marketevent_id": market_event_id, "name": parameters['selection']['values']['name'], "price": parameters['selection']['values']['price'], "outcome": parameters['selection']['values']['outcome']})
            conn.execute(stmt)

        return True


def delete_element(conn, session, args):
    """
    delete an element
    we can change it to update in active = 0 as well later
    """
    parameters = []

    if is_json(args['<element>']):
        parameters = json.loads(args['<element>'])
        """
        {"sport":{"id":1}}

        {"event":{"id":1}}

        {"market":{"id":1}}

        {"selection":{"id":1}}
        """
        if 'sport' in parameters:
            # if sport is use in any event can't delete
            events = finds(session, Event, "events.sport_id=" +
                           str(parameters['sport']['id']))

            if not events:
                stmt = delete(Sport).where(
                    Sport.id == parameters['sport']['id'])
                conn.execute(stmt)
            else:
                return False

        elif 'event' in parameters:
            # if event in marketevents then can't delete
            marketevents = finds(session, MarketEvent, "marketevents.event_id=" +
                                 str(parameters['event']['id']))

            if not marketevents:
                stmt = delete(Event).where(
                    Event.id == parameters['event']['id'])
                conn.execute(stmt)
            else:
                return False

        elif 'market' in parameters:
            # if market in marketevents then can't delete
            marketevents = finds(session, MarketEvent, "marketevents.market_id=" +
                                 str(parameters['market']['id']))

            if not marketevents:
                stmt = delete(Market).where(
                    Market.id == parameters['market']['id'])
                conn.execute(stmt)
            else:
                return False

        elif 'selection' in parameters:
            stmt = delete(Selection).where(
                Selection.id == parameters['selection']['id'])
            conn.execute(stmt)

        return True


def search(conn, session, args):
    """
    search with filter
    """
    {"all": "text"}
    {"sport": "text"}
    {"market": "text"}
    {"event": "text"}
    {"selection": "text"}
    {"active": "1"}

    if is_json(args['<filter>']):
        parameters = json.loads(args['<filter>'])
        result = None
        keyword = None

        if 'all' in parameters:
            keyword = parameters['all']

            sql = "select * from sports s \
                    left join events e on e.sport_id = s.id \
                    left join marketevents me on me.event_id = e.id \
                    left join markets m on me.market_id = m.id \
                    left join selections se on se.marketevent_id = me.id \
                    group by se.id \
                    having s.name like '%" + keyword + "%' or \
                    e.name like '%" + keyword + "%' or \
                    m.name like '%" + keyword + "%' or \
                    se.name like '%" + keyword + "%'"
            result = conn.execute(sql)

        elif 'sport' in parameters:
            sql = "select * from sports s \
                    where s.name like '%" + keyword + "%' or \
                    s.display_name like '%" + keyword + "%' or \
                    s.slug like '%" + keyword + "%'"
            result = conn.execute(sql)

        elif 'market' in parameters:
            sql = "select * from market m \
                    where m.name like '%" + keyword + "%' or \
                    m.display_name like '%" + keyword + "%'"
            result = conn.execute(sql)

        elif 'event' in parameters:
            sql = "select * from events e \
                    where e.name like '%" + keyword + "%' or \
                    e.slug like '%" + keyword + "%'"
            result = conn.execute(sql)

        elif 'selection' in parameters:
            sql = "select * from selections s \
                    where s.name like '%" + keyword + "%' or \
                    s.outcome like '%" + keyword + "%'"
            result = conn.execute(sql)

        elif 'active' in parameters:
            # minimum number of active child
            threshold = parameters['active']

            sql = "select 'sports' as 'type', s.id, s.name, count(e.id) as 'active_cnt' from sports s \
                inner join events e on e.sport_id = s.id \
                group by s.id \
                having e.active = 1 and count(e.id) > " + threshold + " \
                UNION \
                select 'events' as 'type', e.id, e.name, count(se.id) as 'active_cnt' from events e \
                inner join marketevents me on me.event_id = e.id \
                inner join selections se on se.marketevent_id = me.id \
                group by e.id \
                having se.active = 1 and count(se.id) > " + threshold + " \
                UNION \
                select 'markets' as 'type', m.id, m.name, count(se.id) as 'active_cnt' from markets m \
                inner join marketevents me on me.market_id = m.id \
                inner join selections se on se.marketevent_id = me.id \
                group by m.id \
                having se.active = 1 and count(se.id) > " + threshold + ""
            result = conn.execute(sql)

        return result


# starting point
def cli():
    """
    This is the cli or command line interface for send command to rc tool
    """
    args = docopt(__doc__, version='App 1.0', help=True)

    # Create DB connection with sqlite
    engine = create_engine("sqlite:///app.sqlite")
    conn = engine.connect()
    session = Session(bind=engine)
    inspector = inspect(engine)

    # create index
    sportnameindex = Index('sportnameindex', Sport.name)
    sportdisplaynameindex = Index('sportdisplaynameindex', Sport.display_name)
    sportactiveindex = Index('sportactiveindex', Sport.active)
    sportslugindex = Index('sportslugindex', Sport.slug)
    eventnameindex = Index('eventnameindex', Event.name)
    eventslugindex = Index('eventslugindex', Event.slug)
    eventactiveindex = Index('eventactiveindex', Event.active)
    marketnameindex = Index('marketnameindex', Market.name)
    marketdisplaynameindex = Index(
        'marketdisplaynameindex', Market.display_name)
    marketeventindex = Index('marketeventindex', MarketEvent.active)
    selectionnameindex = Index('selectionnameindex', Selection.name)
    selectionactiveindex = Index('selectionactiveindex', Selection.active)

    # Create metadata layer that abstracts our SQL DB
    Base.metadata.create_all(engine)

    # comment out following index creation lines first time
    # sportnameindex.create(bind=engine)
    # sportdisplaynameindex.create(bind=engine)
    # sportactiveindex.create(bind=engine)
    # sportslugindex.create(bind=engine)
    # eventnameindex.create(bind=engine)
    # eventslugindex.create(bind=engine)
    # eventactiveindex.create(bind=engine)
    # marketnameindex.create(bind=engine)
    # marketdisplaynameindex.create(bind=engine)
    # marketeventindex.create(bind=engine)
    # selectionnameindex.create(bind=engine)
    # selectionactiveindex.create(bind=engine)

    # call for create an element
    if args['-a'] and args['<element>'] != None:
        response = add(conn, session, args)
    elif args['-u'] and args['<element>'] != None:
        response = update_element(conn, session, args)
    elif args['-d'] and args['<element>'] != None:
        response = delete_element(conn, session, args)
    elif args['-f'] and args['<filter>'] != None:
        response = search(conn, session, args)
        for res in response:
            print(res)

        return response

    # call for update an element
    elif args['-u'] and args['-u']:
        return args['-u']

    # create the object for send command
    else:
        response = "No option provided"

    return response


"""
Following code is only for direct calling
So when you are building with poetry kindly comment the following part.
"""
if __name__ == "__main__":
    response = cli()
    print(response)
