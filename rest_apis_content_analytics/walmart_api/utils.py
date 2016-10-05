from django.conf import settings


def get_submission_history_cache_key_for_request_or_user(request_or_user):
    if hasattr(request_or_user, 'user'):  # we got request
        user = request_or_user.user
        if not user.is_authenticated():
            return
    else:  # we got user
        user = request_or_user
    return settings.SUBMISSION_HISTORY_CACHE_KEY + str(user.pk)


def get_stats_cache_key_for_request_or_user(request_or_user):
    if hasattr(request_or_user, 'user'):  # we got request
        user = request_or_user.user
        if not user.is_authenticated():
            return
    else:  # we got user
        user = request_or_user
    return settings.STATISTICS_CACHE_KEY + str(user.pk)
