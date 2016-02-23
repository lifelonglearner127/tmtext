import json

from .models import SubmissionHistory


def get_submission_history(request):
    if request.user.is_authenticated():
        return SubmissionHistory.objects.filter(user=request.user)


def get_submission_history_as_json(request):
    subm_history = get_submission_history(request)
    if not subm_history:
        return {}
    return {
        'submission_history_as_json': json.dumps({
            s.feed_id: {'all_statuses': s.get_statuses(), 'ok': s.all_items_ok()}
            for s in subm_history
        })
    }