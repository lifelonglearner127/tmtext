from .models import SubmitXMLItem


def _failed_xml_items(request):
    return SubmitXMLItem.objects.filter(user=request.user, status='failed').order_by('-when')


def _successful_xml_items(request):
    return SubmitXMLItem.objects.filter(user=request.user, status='successful').order_by('-when')


def stats_walmart_xml_items(request):
    return {
        'stats_all_walmart_xml_items': SubmitXMLItem.objects.filter(user=request.user).order_by('-when'),
        'stats_failed_walmart_xml_items': _failed_xml_items(request),
        'stats_successful_walmart_xml_items': _successful_xml_items(request)
    }