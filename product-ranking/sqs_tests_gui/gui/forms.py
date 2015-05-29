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


class ReadOnlyWidget(forms.widgets.Widget):
    def render(self, _, value, attrs=None):
        return '<b>%s</b>' % value


class JobForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(JobForm, self).__init__(*args, **kwargs)
        self.fields['task_id'].initial = self.fields['task_id'].initial + random.randint(10000, 99999)
        self.fields['spider'] = forms.ChoiceField(
            choices=generate_spider_choices())
        if self.instance and self.instance.pk:
            for field in self.fields.keys():
                self.fields[field].widget = ReadOnlyWidget()
            # TODO: remove save and 'save and continue editing' buttons if the form has instance
        # TODO: remove 'save and continue editing' button

    def clean(self, *args, **kwargs):
        data = self.cleaned_data
        product_url = data.get('product_url', '')
        product_urls = data.get('product_urls', '')
        search_term = data.get('search_term', '')
        if not product_url and not search_term and not product_urls:
            raise forms.ValidationError(
                'You should enter Product url OR search term OR product_urls')
        return data

    def clean_product_url(self, *args, **kwargs):
        data = self.cleaned_data
        product_url = data.get('product_url', '')
        if product_url:
            if not product_url.lower().startswith('http://'):
                if not product_url.lower().startswith('https://'):
                    raise forms.ValidationError('Invalid URL')
        return product_url

    def clean_product_urls(self, *args, **kwargs):
        data = self.cleaned_data
        product_urls = data.get('product_urls', '')
        if product_urls:
            for prod_url in product_urls.split('||||'):
                if not prod_url.lower().startswith('http://'):
                    if not prod_url.lower().startswith('https://'):
                        raise forms.ValidationError('Invalid URL: ' + prod_url)
        return product_urls

    class Meta:
        model = Job
        exclude = ['created', 'status', 'finished']