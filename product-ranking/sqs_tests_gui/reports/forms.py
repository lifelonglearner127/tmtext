import datetime

from django import forms


class ReportDateForm(forms.Form):
    date = forms.DateField(auto_now_add=True)
