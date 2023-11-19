from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_json import mutable_json_type
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_json import mutable_json_type

import memgpt.config as cfg

SqlalBase = declarative_base()

class AgentTable(SqlalBase):
    __tablename__ = 'memgpt_agent'
    id = Column(Integer, primary_key=True)
    data = Column(mutable_json_type(dbtype=JSONB, nested=True))


class Sqlal:
    """
    sqlalchemy interface
    """
    persistence_session = None

    @classmethod
    def init(cls):
        if cls.persistence_session is None:
            config = cfg.MemGPTConfig.load()
            persistence_engine = create_engine(config.persistence_storage_uri)
            SqlalBase.metadata.create_all(persistence_engine)  # Create the table if it doesn't exist
            cls.persistence_session = sessionmaker(bind=persistence_engine)()

    @classmethod
    def load_agent_data(cls, name):
        cls.init()
        q = cls.persistence_session.query(AgentTable).filter(AgentTable.data['name'].astext == name)
        doc = q.first()
        return doc.data

    @classmethod
    def save_agent_data(cls, data):
        cls.init()
        q = cls.persistence_session.query(AgentTable).filter(AgentTable.data['name'].astext == data['name'])
        doc = q.first()
        if doc is None:
            doc = AgentTable(data=data)
            cls.persistence_session.add(doc)
        doc.data = data
        cls.persistence_session.commit()

    @classmethod
    def test(cls):
        sq.save_agent_data({'foo': "bar", 'name': "baz"})
        result = sq.load_agent_data("baz")
        print("RESULT:", result)

if __name__ == "__main__":
    sq = Sqlal()
    sq.test()
