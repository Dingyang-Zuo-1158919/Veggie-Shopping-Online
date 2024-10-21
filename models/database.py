from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine('mysql+mysqlconnector://root:ZDYzdy123@localhost/final_pj')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


