from django.contrib import admin

# Register your models here.

from .models import SubmitXMLItem, ErrorText, ItemMetadata


class ErrorTextInline(admin.TabularInline):
    model = ErrorText


class ItemMetadataInline(admin.TabularInline):
    model = ItemMetadata


@admin.register(SubmitXMLItem)
class SubmitXMLItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'auth', 'status', 'when', 'multi_item']
    list_filter = ['user', 'auth', 'status', 'when', 'multi_item']

    inlines = [ItemMetadataInline, ErrorTextInline]

    ordering = ['-when']