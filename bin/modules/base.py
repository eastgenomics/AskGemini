from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session,sessionmaker,relationship
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

# set up the engine
ConnectionString = "mysql://ga_ro:readonly@sql01/genetics_ark_1_1_0"
# echo=True makes the sql commands issued by sqlalchemy get output to the console, useful for debugging
# engine = create_engine(ConnectionString, echo=True)
engine = create_engine(ConnectionString)
# bind the dbsession to the engine
DBSession.configure(bind=engine)
# now you can interact with the database if it exists
# import all your models then execute this to create any tables that don't yet exist.This does not handle migrations
Base.metadata.create_all(engine)