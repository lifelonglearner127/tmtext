from django import template
from datetime import date, timedelta

register = template.Library()


@register.filter(name='split')
def split(value, arg):
    return value.split(arg)