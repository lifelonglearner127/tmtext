import os
from lxml import html
import csv
import xlrd

from helper import check_extension, logging_info, write_to_file

#-------- define column names ------------
MPN = 'MPN'
BRAND = 'Brand Name'
TITLE = 'Item Name'
GTIN = 'GTIN'
DESC = 'Description'
L_DESC = 'Long Description'
#-----------------------------------------


def generate_bullets(desc):
    return []


def generate_google_manufacturer_xml(input_file, templateEnv):
    available_extensions = ['.csv', '.xls']
    items = []
    context = {}

    if not check_extension(input_file, available_extensions):
        logging_info('The file extension should be %s.'
                     % (','.join(available_extensions)), 'ERROR')
        return

    try:
        name, file_extension = os.path.splitext(input_file)
        if file_extension == '.csv':
            with open(input_file, 'rU') as csvfile:
                csvfile.readline()
                reader = csv.reader(csvfile)
                for item in reader:
                    tree_description = html.fromstring(item[10])
                    tree_bullets = \
                        tree_description.xpath("//*[contains(@id,'feature-bullets')]//ul/"
                                               "li[not(contains(@class,'hidden'))]")
                    bullet_points = []
                    for bullet in tree_bullets:
                        bullet_points.append(bullet.text_content())

                    items.append({
                        'id': item[7],
                        'brand': item[17],
                        'title': item[9],
                        'gtin': item[1],
                        'mpn': item[7],                                 # This field should be redefined
                        'description': item[12],
                        'bullet_points': bullet_points,
                    })
        else:                               # .xls
            wb = xlrd.open_workbook(filename=input_file)
            item_sheet = wb.sheet_by_name('Sheet1')

            items = []
            ci = {}
            # The ci will take column index like this
            # {
            #     'MPN': -1,
            #     'Brand Name': -1,
            #     'Item Name': -1,
            #     'GTIN': -1,
            #     'Description': -1,
            #     'Long Description': -1
            # }

            for idx, row in enumerate(item_sheet.get_rows()):
                if idx == 0:
                    for i, c in enumerate(row):
                        ci[c.value] = i
                else:
                    data = {
                        'id': row[ci[MPN]].value if ci[MPN] > -1 else '',
                        'brand': row[ci[BRAND]].value if ci[BRAND] > -1 else '',
                        'title': row[ci[TITLE]].value if ci[TITLE] > -1 else '',
                        'gtin': row[ci[GTIN]].value if ci[GTIN] > -1 else '',
                        'mpn': row[ci[MPN]].value if ci[MPN] > -1 else '',
                        'description': row[ci[DESC]].value if ci[DESC] > -1 else '',
                        'bullet_points': row[ci[L_DESC]].value if ci[L_DESC] > -1 else '',
                    }
                    data['bullet_points'] = generate_bullets(data['bullet_points'])
                    items.append(data)
            pass
    except Exception as e:
        logging_info(str(e), 'ERROR')
        return

    context['items'] = items

    template = templateEnv.get_template('GoogleManufacturer.html')
    output_content = template.render(context)

    filename = write_to_file(output_content)

    logging_info(filename, 'RESULT_FILE')
    logging_info('google-manufacturer.xml', 'FILE_NAME')