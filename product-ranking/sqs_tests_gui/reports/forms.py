import datetime

from django import forms


class ReportDateForm(forms.Form):
    date = forms.DateField(initial=datetime.datetime.today)
