from django.views.generic import View, TemplateView
from django.http import HttpResponse
from django.template import loader

import csv
from django.conf import settings
from lxml import html, etree

class GoogleManufacturerView(TemplateView):
    template_name = 'GoogleManufacturer.html'
    def get(self, request, *args, **kwargs):
        template = loader.get_template(self.template_name)
        items = []
        context = {}
        with open(settings.BASE_DIR +
                          settings.MEDIA_URL +
                          'google_manufacturer/Generic Template File.csv',
                  'rU') as csvfile:
            csvfile.readline()
            reader = csv.reader(csvfile)
            for item in reader:
                tree_description = html.fromstring(item[9])
                tree_bullets = tree_description.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
                bullet_points = []
                for bullet in tree_bullets:
                    bullet_points.append(bullet.text_content())

                items.append({
                    'id': item[6],
                    'brand': item[16],
                    'title': item[8],
                    'gtin': item[1] if item[0]=="" else item[0],
                    'mpn': '00150',                                 # This field should be redefined
                    'description': item[11],
                    'bullet_points': bullet_points,
                });

        context['items'] = items

        response = HttpResponse(template.render(context, request), content_type='text/xml')
        response['Content-Disposition'] = 'attachment; filename=google-manufacturer.xml'
        return response

