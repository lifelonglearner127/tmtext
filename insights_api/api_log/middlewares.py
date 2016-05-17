import time
from models import Query
from django.contrib.auth.models import AnonymousUser


class LogQueryInformation():

    def process_request(self, request):
        request.session['time'] = time.time()

    def process_response(self, request, response):
        path = request.get_full_path()
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        if '/admin/' not in path:
            data = {'remote_address': request.META['REMOTE_ADDR'],
                    'request_method': request.method,
                    'request_path': path,
                    'request_body': request.body,
                    'response_status': response.status_code,
                    'user': user,
                    'run_time': time.time() - request.session['time']}
            Query(**data).save()

        return response
