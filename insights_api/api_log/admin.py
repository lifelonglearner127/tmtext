from django.contrib import admin

# Register your models here.
from models import Query


class QueryAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('user', 'remote_address', 'request_method', 'request_path',
                    'request_body', 'response_status', 'date', 'run_time')

admin.site.register(Query, QueryAdmin)