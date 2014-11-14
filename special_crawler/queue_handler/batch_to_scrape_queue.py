# from models import Crawler_List, Site, Session, Batch
from dummy_list_set import CrawlerList
from sqs_connect import SQS_Queue
import json

# session = Session()


def main():
    # batch = select_batch(1)
    # sites = select_sites_from_batch(batch)
    # print(sites)
    sqs_scrape = SQS_Queue('test_scrape')

    load_queue(sqs_scrape)


def load_queue(sqs):
    crawler_list = CrawlerList()
    rows = crawler_list.get_rows()
    rows = [json.dumps(x) for x in rows]
    sqs.put(rows)


def select_sites_from_batch(batch):
    return batch.date

def select_batch(id):
    batch = session.query(Batch)\
                    .filter(Batch.id==id)
    return batch.all()[0]



if __name__ == "__main__":
    main()