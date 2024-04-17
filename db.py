from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, declarative_base

# Creamos el engine
engine = create_engine('sqlite:///database/crm.db', connect_args={'check_same_thread': False})

# Creamos la sesión, lo que nos permite realizar transacciones dentro de nuestra BD.
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()






