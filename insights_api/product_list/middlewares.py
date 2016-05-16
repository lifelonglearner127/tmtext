import time
from models import Query


class LogQueryInformation():

    def process_request(self, request):
        request.session['time'] = time.time()

    def process_response(self, request, response):
        data = {'remote_address': request.META['REMOTE_ADDR'],
                'request_method': request.method,
                'request_path': request.get_full_path(),
                'request_body': request.body,
                'response_status': response.status_code,
                'run_time': time.time() - request.session['time']}

        Query(**data).save()
        return response
