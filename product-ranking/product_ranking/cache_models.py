import sys
import os

from sqlalchemy import Column, ForeignKey, \
    String, Integer, SmallInteger, Date, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


Base = declarative_base()

SEARCH_TERM = 'search_term'
URL_TERM = 'url_term'
URLS_TERM = 'urls_term'
TERM_TYPES = {
    SEARCH_TERM: 0,
    URL_TERM: 1,
    URLS_TERM: 2
}


class Spider(Base):
    """Spider model class
    """
    __tablename__ = 'spider'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), index=True)

    def __repr__(self):
        return '<Spider %s>' % self.name


class Term(Base):
    """Search term model class
    """
    __tablename__ = 'term'

    id = Column(Integer, primary_key=True)
    type = Column(SmallInteger, default=TERM_TYPES[SEARCH_TERM])
    term = Column(String(500), index=True)  # needs html-quoting
    # if term is url, can be long

    def __repr__(self):
        return '<Term %s>' % self.term


class Run(Base):
    """Search run model class (consists of spider, term and run date)
    """
    __tablename__ = 'run'

    id = Column(Integer, primary_key=True)
    spider_id = Column(Integer, ForeignKey('spider.id'))
    term_id = Column(Integer, ForeignKey('term.id'))
    date = Column(Date, index=True)

    spider = relationship('Spider', backref='runs')
    term = relationship('Term', backref='terms')

    def get_folder(self):
        """get path to the s3 cache folder for current run"""
        return '%s/%s/%s' % (self.spider.name, self.date, self.term.term)

    def __repr__(self):
        return '<Run for %s>' % self.date


# engine = create_engine('mysql://root:root@localhost/test', echo=True)
# use echo for debug purposes, to see produced sql queries
if os.path.exists('cache_models.db'):  # local mode with SQLite
    engine = create_engine('sqlite:///cache_models.db')
else:
    engine = create_engine(
        'postgresql://sccache:DetVoFremjokIrnEttat'
        '@sc-cache-map.cmuq9py90auz.us-east-1.rds.amazonaws.com/sccache'
    )

sess = sessionmaker()
sess.configure(bind=engine)
session = sess()


def create_tables():
    Base.metadata.create_all(engine)


def get_or_create(model, **kwargs):
    """SqlAlchemy implementation of Django's get_or_create.
    """
    global session
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance, True


def get_or_create_spider(name):
    return get_or_create(Spider, name=name)


def get_or_create_term(type, term):
    return get_or_create(Term, type=type, term=term)


def get_or_create_run(spider, term, date):
    return get_or_create(Run, spider_id=spider.id, term_id=term.id, date=date)


def _get_st_type():
    args_term = [a for a in sys.argv if 'searchterms_str' in a]
    args_url = [a for a in sys.argv if 'product_url' in a]
    args_urls = [a for a in sys.argv if 'products_url' in a]
    if args_term:
        return SEARCH_TERM
    if args_url:
        return URL_TERM
    if args_urls:
        return URLS_TERM


def create_db_cache_record(spider, date):
    from cache import _get_searchterms_str_or_product_url

    st = _get_searchterms_str_or_product_url()

    spider_db, is_created = get_or_create_spider(spider.name)
    term_db, is_created = get_or_create_term(type=TERM_TYPES[_get_st_type()],
                                             term=st)
    run_db, is_created = get_or_create_run(spider=spider_db, term=term_db,
                                           date=date)


def list_db_cache(spider=None, term=None, date=None):
    """ Get cache data, spider -> date -> searchterm
    supports strings for spider (as name) and for terms(as term)
    :return: dict
    """
    global session
    query = session.query(Run)
    if spider:
        if isinstance(spider, Spider):
            query = query.join(Spider, Run.spider_id == spider.id)
        else:  # if spider is string
            query = query.join(Spider).filter(Spider.name == spider)
    if term:
        if isinstance(term, Term):
            query = query.join(Term, Run.term_id == term.id)
        else:  # if term is string
            query = query.join(Term).filter(Term.term == term)
    if date:
        query = query.filter(Run.date == date)
    runs = query.all()

    # TODO: possible alternative
    # get list of strings, representing s3 paths to the needed folders
    # cache_map = [run.get_folder() for run in runs]
    # return cache_map

    cache_map = {}
    for r in runs:
        spider = r.spider.name
        date = r.date
        searchterm = r.term.term
        if spider not in cache_map:
            cache_map[spider] = {}
        if date not in cache_map[spider]:
            cache_map[spider][date] = []
        if searchterm not in cache_map[spider][date]:
            cache_map[spider][date].append(searchterm)
    return cache_map


if __name__ == '__main__':
    create_tables()
    if 'clear_cache' in sys.argv:
        if raw_input('Delete all records? y/n: ').lower() == 'y':
            #TODO: this doesn't work because of constraints - fix
            session.query(Spider).delete()
            session.query(Run).delete()
            session.query(Term).delete()
            session.commit()
            print('Cleared')
        else:
            print('You did not type "y" - exit...')
    if 'list' in sys.argv:
        listing = list_db_cache()
        for spider in listing.keys():
            print
            print spider.upper(), '*'*50
            for date in listing[spider].keys():
                print ' '*4, date, '-'*20
                for searchterm in listing[spider][date]:
                    print ' '*8, searchterm