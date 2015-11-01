import os
import sys
import re


CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CWD, '..', 'product-ranking'))
sys.path.append(os.path.join(CWD, '..'))
from product_ranking.items import SiteProductItem
from sqs_tests_gui.gui.forms import generate_spider_choices


def get_sc_fields():
    """ Returns all possible Ranking spiders fields """
    return SiteProductItem.__dict__['fields'].keys()


def test_run_to_dirname(test_run, base_path='/tmp/_test_runs/'):
    if not isinstance(test_run, int):
        test_run = test_run.pk
    return base_path + 'test_run_%i' % test_run


def dirname_to_test_run(path):
    from product_ranking_branch_tests.tests_app.models import TestRun
    match = re.search(r'test_run_(\d+)', path)
    if not match:
        return
    return TestRun.objects.get(pk=int(match.group(1)))