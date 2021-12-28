## Implement a system which manages multiple sports, events, markets, and selections.

### System Requirements

- A sport may have multiple events
- An event may have multiple markets
- A market may have multiple selections
- When all the selections of a particular market are inactive, the market becomes inactive
- When all the markets of an event are inactive, the event becomes inactive
- When all the events of an sport are inactive, the sport becomes inactive
- Sports, events, markets, and selections need to be persistently stored

## A simple command-line application demonstrating the following functionalities:

Creating sports, events, markets or selections

Updating sports, events, markets or selections

Deleting sports, events, markets, or selections

Searching for sports, events, markets, or selections

### The system should be able to combine N filters with an AND expression

Filters may be more or less complex

Examples of Filters:

All (sports/events/markets) with a name satisfying a particular regex

All (sports/events/markets) with a minimum number of active (events/markets/selections) higher than a threshold

### A sport contains the following elements:

- Name
- Display Name
- Slug (url friendly version of name)
- Order
- Active (Either true or false)

### An event contains the following elements:

- Name
- Event Type (Either preplay or inplay)
- Sport
- Status (Preplay, Inplay or Ended)
- Slug (url friendly version of name)
- Active (Either true or false)

### A market contains the following elements:

- Name
- Display Name
- Order
- Active (Either true or false)
- Schema (integer value which controls how market is displayed)
- Columns (number of columns used in display)

### A selection contains the following elements:

- Name
- Event
- Market
- Price (Decimal value, to 2 decimal places)
- Active (Either true or false)
- Outcome (Unsettled, Void, Lose, Place, Win)

## Documents

ER Diagram [docs/er_diagram.drawio.png]

DFD [docs/dfd.drawio.png]

ADD Delete Selection [docs/add_delete_selection.drawo.png]

## How to install

You need python >= 3.8 [https://www.python.org/downloads/]

Install pip [https://pip.pypa.io/en/stable/installation/]

Extract the application

Go to application root

Run `pip install -r requirements.txt` [hope all lib required will be installed other if anything miss need to run `pip install <lib name>`]

## How to run the tests

`python test_app.py`

## How to run

to get help

`python app.py -h`

to add an element

`python app.py -a '{"sport":{"name": "football", "display_name": "Football", "slug": "football", "order":1, "active": 0}}'`

to update an element

`python app.p -u '{"sport":{"id":1, "values": {"name": "football", "display_name": "Football", "slug": "football", "order":2}}}'`

to delete an element [it it does not have any active dep]

`python app.py -d '{"sport":{"id":1}}'`

to search all with a keyword

`python app.py -f '{"all": "foot"}'`

to search an element with a keyword

`python app.py -f '{"sport": "foot"}'`

to search all with more than a min number of active dep

`python app.py -f '{"active": "0"}'`

## How can be improved

So many things can be improved, if time and requirement permit to do so. Few of them

- All recursive check before update and delete operations
- make poetry build of this application to make it a python lib
- make a binary build with pyinstaller to make this a system utility
- Keep in a MVC eg. flask
- make it API based application
- more try catch block
- more tests
- create trigger to related update or insert record
- check order for all records and then allow to enter the order or create one as increment
