from django.contrib import admin

# Register your models here.

from .models import SubmitXMLItem, ErrorText, ItemMetadata


admin.site.register(SubmitXMLItem)
admin.site.register(ErrorText)
admin.site.register(ItemMetadata)