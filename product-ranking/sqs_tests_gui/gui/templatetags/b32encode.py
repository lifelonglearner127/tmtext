import base64

from django import template
from datetime import date, timedelta

register = template.Library()


@register.filter(name='b32encode')
def _b32_encode(val):
    return base64.b32encode(val)