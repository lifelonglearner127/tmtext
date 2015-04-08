import os
import sys
import random

from django import forms

from .models import Job


CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CWD, '..', '..', 'monitoring'))
SPIDERS_DIR = os.path.join(CWD, '..', '..', 'product_ranking', 'spiders')
from deploy_to_monitoring_host import find_spiders


def generate_spider_choices():
    result = []
    for spider in find_spiders(SPIDERS_DIR):
        if not spider:
            continue
        if len(spider) < 2:
            continue
        spider_name, spider_domain = spider[0], spider[1]
        if ',' in spider_domain:
            spider_domain = spider_domain.split(',')[0].strip()
        spider_domain = spider_domain.replace('www.', '')
        result.append([spider_name, spider_name + ' [%s]' % spider_domain])
    return sorted(result)


class JobForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(JobForm, self).__init__(*args, **kwargs)
        self.fields['task_id'].initial = self.fields['task_id'].initial + random.randint(10000, 99999)
        self.fields['spider'] = forms.ChoiceField(
            choices=generate_spider_choices)

    class Meta:
        model = Job
        exclude = ['created', 'status', 'finished']