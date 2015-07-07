from sqlalchemy import Column, ForeignKey, \
    String, Integer, SmallInteger, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

SEARCH_TERM = 'search_term'
URL_TERM = 'url_term'
TERM_TYPES = {
    SEARCH_TERM: 0,
    URL_TERM: 1
}


class Spider(Base):
    """
    Spider model class
    """
    __tablename__ = 'spider'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), index=True)

    def __repr__(self):
        return '<Spider %s>' % self.name


class Term(Base):
    """
    Search term model class
    """
    __tablename__ = 'term'
    id = Column(Integer, primary_key=True)
    type = Column(SmallInteger, default=TERM_TYPES[SEARCH_TERM])
    term = Column(String(300), index=True)  # if term is url, can be long

    def __repr__(self):
        return '<Term %s>' % self.term


class Run(Base):
    """
    Search run models class (consists of spider, term and run date)
    """
    __tablename__ = 'run'
    id = Column(Integer, primary_key=True)
    spider_id = Column(Integer, ForeignKey('spider.id'))
    term_id = Column(Integer, ForeignKey('term.id'))
    date = Column(DateTime, index=True)
    #
    spider = relationship('Spider', backref='runs')
    term = relationship('Term', backref='terms')

    def __repr__(self):
        return '<Run %s - %s (%s)>' % (
            self.spider.name, self.term.term, self.date)


engine = create_engine('mysql://root:root@localhost/test')

from sqlalchemy.orm import sessionmaker
sess = sessionmaker()
sess.configure(bind=engine)
# Base.metadata.create_all(engine)