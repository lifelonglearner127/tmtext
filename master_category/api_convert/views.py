from django.views.generic import View, TemplateView
from django.http import HttpResponse
from django.template import loader

from django.conf import settings
from django.utils.encoding import smart_str

from lxml import html, etree

import csv
import xlrd
from openpyxl import Workbook
from openpyxl.compat import range
from openpyxl.utils import get_column_letter

import uuid


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
                tree_bullets = \
                    tree_description.xpath("//*[contains(@id,'feature-bullets')]//ul/"
                                           "li[not(contains(@class,'hidden'))]")
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


class AmazonToWalmartView(View):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('walmart_long_description.html')
        def create_walmart_description(bullet1, bullet2, bullet3, bullet4, bullet5):
            context = {
                "bullet1": bullet1 if bullet1 != "" else None,
                "bullet2": bullet2 if bullet2 != "" else None,
                "bullet3": bullet3 if bullet3 != "" else None,
                "bullet4": bullet4 if bullet4 != "" else None,
                "bullet5": bullet5 if bullet5 != "" else None,
            }
            return template.render(context, request)

        filename = settings.BASE_DIR + \
                   settings.MEDIA_URL + \
                   'amazon_to_walmart/Amazon-HPC-Template-Export-2016-10-25(22-26-50).xls'

        wb = xlrd.open_workbook(filename = filename)
        item_sheet = wb.sheet_by_name('Item_Sheet')

        items = []
        # Read data from amazone form
        for idx, row in enumerate(item_sheet.get_rows()):
            if idx > 3:
                data = {
                    "tool_id": row[4].value,
                    "title": row[6].value,
                    "short_desc": row[30].value,
                    "long_desc": create_walmart_description(
                        row[31].value, row[32].value, row[33].value, row[34].value, row[35].value),
                    "ingredients": row[37].value,
                    "directions": row[38].value,
                    "warnings": row[38].value,
                }
                if row[16].value == "UPC":
                    data["upc"] = row[17].value
                    data["gstn"] = ""
                elif row[16].value == "GSTN":
                    data["upc"] = ""
                    data["gstn"] = row[17].value
                else:
                    data["upc"] = ""
                    data["gstn"] = ""

                items.append(data)

        wb = Workbook()
        dest_filename = 'empty_book.xlsx'
        ws1 = wb.active
        ws1.title = "Sheet1"

        # Create header
        ws1.append(["GTIN-14",
                    "UPC",
                    "Tool ID",
                    "Product Name",
                    "Long Description",
                    "Shelf Description (Optional)",
                    "Short Description",
                    "Usage Directions (optional)",
                    "Ingredients (optional)",
                    "Caution Warnings Allergens (optional)"])
        # write product info
        for item in items:
            ws1.append([item["gstn"],
                        item["upc"],
                        item["tool_id"],
                        item["title"],
                        item["long_desc"],
                        "",
                        item["short_desc"],
                        item["ingredients"],
                        item["directions"],
                        item["warnings"],])

        temp_filename = filename = settings.BASE_DIR + \
                   settings.MEDIA_URL + \
                   "tmp/" + str(uuid.uuid4()) + ".xlsx"
        wb.save(filename = temp_filename)

        fp = open(temp_filename, 'rb')
        response = HttpResponse(fp.read())
        fp.close()
        response['Content-Type'] = 'application/vnd.ms-excel'
        # response['Content-Type'] = 'application/force-download'
        response['Content-Disposition'] = 'attachment; filename=WalmartBulkContentUpload.xlsx'
        return response

