from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# import twitter.models
from settings import DATABASE

engine = create_engine(DATABASE, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

# this is used to initialize the database when tables have been cleared or to initialize
# a clean database during restarts
def init_db():
    # TODO: this needs to be optimized and made more user friendly. this does not always
    # create a new database and maybe creating the file itself would be a good option
    import twitter.models
    Base.metadata.create_all(bind=engine)
