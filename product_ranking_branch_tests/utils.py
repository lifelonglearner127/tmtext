import os
import sys


CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CWD, '..', 'product-ranking'))
from product_ranking.items import SiteProductItem
from sqs_tests_gui.gui.forms import generate_spider_choices


def get_sc_fields():
    """ Returns all possible Ranking spiders fields """
    return SiteProductItem.__dict__['fields'].keys()