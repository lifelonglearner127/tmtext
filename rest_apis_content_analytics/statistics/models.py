import datetime

from django.db import models
from django.contrib.auth.models import User


def process_check_feed_response(user, check_results_output, date, check_auth=True):
    if check_auth and not user.is_authenticated():
        return
    multi_item = not(check_results_output.get('itemsReceived', 0) == 1)
    for item in check_results_output.get('itemDetails', {}).get('itemIngestionStatus', []):
        if not 'ingestionStatus' in item:
            print('No ingestionStatus found!')
            continue
        if item['ingestionStatus'].lower() not in ('success', 'received'):
            stat_xml_item(user, 'session', 'failed', multi_item,
                          date=date,
                          error_text=str(item.get('ingestionErrors')),
                          upc=item.get('sku'),
                          feed_id=check_results_output.get('feedId'))
            print('Stat item created, status: FAILED')
        else:
            stat_xml_item(user, 'session', 'successful', multi_item,
                          date=date,
                          upc=item.get('sku'),
                          feed_id=check_results_output.get('feedId'))
            print('Stat item created, status: SUCCESS')


def stat_xml_item(user, auth, status, multi_item, date, error_text=None, upc=None, feed_id=None):
    item = SubmitXMLItem.objects.create(user=user, auth=auth, when=date, status=status,
                                        multi_item=multi_item)
    if error_text:
        item.error_text = error_text
    if upc and feed_id:
        item.metadata = {'upc': upc, 'feed_id': feed_id}
    return item


def _filter_qs_by_date(qs, field_name, date):
    args = {
        field_name+'__year': date.year,
        field_name+'__month': date.month,
        field_name+'__day': date.day
    }
    return qs.filter(**args)


class SubmitXMLItem(models.Model):
    _status = (
        'successful',
        'failed'
    )
    _auth_types = (
        'session',  # user submit item via web site
        'basic'  # user used some code to submit item and used Basic authentication
    )

    user = models.ForeignKey(User, db_index=True)
    auth = models.CharField(max_length=15, choices=[(a, a) for a in _auth_types])
    status = models.CharField(max_length=20, choices=[(c, c) for c in _status],
                              db_index=True)
    when = models.DateTimeField(default=datetime.datetime.now, db_index=True)
    multi_item = models.BooleanField(default=False)  # if multiple items have been merged into one

    def __unicode__(self):
        return u'%s, %s => %s' % (self.user, self.when, self.status)

    @property
    def metadata(self):
        item_metadata = ItemMetadata.objects.filter(item=self)
        if not item_metadata:
            return
        return item_metadata[0]

    @metadata.setter
    def metadata(self, upc_and_feed_id_dict):
        if self.metadata:
            return
        ItemMetadata.objects.create(item=self, upc=upc_and_feed_id_dict.get('upc', None),
                                    feed_id=upc_and_feed_id_dict.get('feed_id', None))

    @property
    def error_text(self):
        item_text = ErrorText.objects.filter(item=self)
        if not item_text:
            return
        return item_text[0].text

    @error_text.setter
    def error_text(self, text):
        if self.error_text:
            return
        ErrorText.objects.create(item=self, text=text)

    @classmethod
    def failed_xml_items(cls, request):
        return cls.objects.filter(user=request.user, status='failed').order_by(
            '-when').distinct()

    @classmethod
    def successful_xml_items(cls, request):
        return cls.objects.filter(user=request.user, status='successful').order_by(
            '-when').distinct()

    @classmethod
    def today_all_xml_items(cls, request):
        return _filter_qs_by_date(
            cls.objects.filter(user=request.user),
            'when', datetime.datetime.today()
        ).order_by('-when').distinct()

    @classmethod
    def today_successful_xml_items(cls, request):
        return _filter_qs_by_date(
            cls.objects.filter(user=request.user, status='successful'),
            'when', datetime.datetime.today()
        ).order_by('-when').distinct()


class ErrorText(models.Model):
    item = models.ForeignKey(SubmitXMLItem, unique=True)
    text = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u'[%s]' % self.item


class ItemMetadata(models.Model):
    item = models.ForeignKey(SubmitXMLItem, unique=True, related_name='item_metadata')
    upc = models.CharField(max_length=20, blank=True, null=True)
    feed_id = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        return u'[%s], upc=>%s, feed_id=>%s' % (self.item, self.upc, self.feed_id)