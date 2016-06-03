import datetime

from .models import SubmitXMLItem


def _filter_qs_by_date(qs, field_name, date):
    args = {
        field_name+'__year': date.year,
        field_name+'__month': date.month,
        field_name+'__day': date.day
    }
    return qs.filter(**args)


def _failed_xml_items(request):
    return SubmitXMLItem.objects.filter(user=request.user, status='failed').order_by('-when').distinct()


def _successful_xml_items(request):
    return SubmitXMLItem.objects.filter(user=request.user, status='successful').order_by('-when').distinct()


def _today_all_xml_items(request):
    return _filter_qs_by_date(
        SubmitXMLItem.objects.filter(user=request.user),
        'when', datetime.datetime.today()
    ).order_by('-when').distinct()


def _today_successful_xml_items(request):
    return _filter_qs_by_date(
        SubmitXMLItem.objects.filter(user=request.user, status='successful'),
        'when', datetime.datetime.today()
    ).order_by('-when').distinct()


def stats_walmart_xml_items(request):
    if not request.user.is_authenticated():
        return {}
    return {
        'stats_all_walmart_xml_items': SubmitXMLItem.objects.filter(user=request.user).order_by('-when').distinct(),
        'stats_failed_walmart_xml_items': _failed_xml_items(request),
        'stats_successful_walmart_xml_items': _successful_xml_items(request),
        'stats_today_all_xml_items': _today_all_xml_items(request),
        'stats_today_successful_xml_items': _today_successful_xml_items(request),
    }