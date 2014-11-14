import sqlalchemy
from models import Crawler_List, Site, Session, Batch


session = Session()

for row in session.query(Site):
    new_row = Site(address="%s/add-on"%row.address)
    session.add(new_row)
    session.flush()
    session.commit()











