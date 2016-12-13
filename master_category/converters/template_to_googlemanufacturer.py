import os
from lxml import html
import csv
import xlrd

from helper import check_extension, logging_info, write_to_file, convert_xls_file

#-------- define column names ------------
UPC = 'UPC'
MPN = 'MPN'
BRAND = 'Brand Name'
TITLE = 'Item Name'
GTIN = 'GTIN'
DESC = 'Description'
L_DESC = 'Long Description'
#-----------------------------------------


def convert_upc_to_gtin(upc):
    s_upc = u''
    if type(upc) == str or type(upc) == unicode:
        s_upc = upc
    elif type(upc) == float:
        s_upc = u'%.f' % upc
    gtin_code = u''
    if len(s_upc) == 12:
        gtin_code = s_upc
    if len(s_upc) == 8:
        gtin_code = u'0000' + s_upc
    return gtin_code


def generate_bullets(desc):
    if desc == '':
        return []

    tree_description = html.fromstring(desc)
    #--------- Description / CSV
    tree_bullets = \
        tree_description.xpath("//*[contains(@id,'feature-bullets')]//ul/"
                               "li[not(contains(@class,'hidden'))]")
    try:
        bullet_points = [b.text_content().strip() for b in tree_bullets if b.text_content().strip() != '']
    except Exception as e:
        bullet_points = []
        logging_info('Bullet parse error')
    if len(tree_bullets) > 0:
        return bullet_points

    #--------- Long Description / Amazon
    tree_bullets = \
        tree_description.xpath("//ul/li")
    try:
        bullet_points = [b.text_content().strip() for b in tree_bullets if b.text_content().strip() != '']
    except Exception as e:
        bullet_points = []
        logging_info('Bullet parse error')
    if len(tree_bullets) > 0:
        return bullet_points

    #--------- Long Description / Walmart
    tree_bullets = \
        tree_description.xpath("//p")
    try:
        bullet_points = [b.text_content().strip() for b in tree_bullets if b.text_content().strip() != '']
    except Exception as e:
        bullet_points = []
        logging_info('Bullet parse error')
    if len(tree_bullets) > 0:
        return bullet_points

    return [desc]


def generate_google_manufacturer_xml(template_env, input_file):
    available_extensions = ['.csv', '.xls']
    items = []
    context = {}

    if not check_extension(input_file, available_extensions):
        logging_info('The file extension should be %s.'
                     % (','.join(available_extensions)), 'ERROR')
        return

    try:
        name, file_extension = os.path.splitext(input_file)
        ci = {}
        # The ci will take column index like this
        # {
        #     'MPN': -1,    # The column index of the MPN field
        #     'Brand Name': -1,
        #     'Item Name': -1,
        #     'GTIN': -1,
        #     'Description': -1,
        #     'Long Description': -1
        # }
        if file_extension == '.csv':
            with open(input_file, 'rU') as csvfile:
                reader = csv.reader(csvfile)
                for idx, item in enumerate(reader):
                    if idx == 0:
                        for i, c in enumerate(item):
                            ci[c] = i
                    else:
                        data = {
                            'id': item[ci[MPN]] if ci[MPN] > -1 else '',
                            'brand': item[ci[BRAND]] if ci[BRAND] > -1 else '',
                            'title': item[ci[TITLE]] if ci[TITLE] > -1 else '',
                            'gtin': item[ci[GTIN]] if ci[GTIN] > -1 else '',
                            'mpn': item[ci[MPN]] if ci[MPN] > -1 else '',
                            'description': item[ci[DESC]] if ci[DESC] > -1 else '',
                            'bullet_points': item[ci[L_DESC]] if ci[L_DESC] > -1 else '',
                        }
                        data['bullet_points'] = generate_bullets(data['bullet_points'])

                        if data['gtin'] == '':
                            if ci[UPC] > -1 and item[ci[UPC]] != '':
                                data['gtin'] = convert_upc_to_gtin(item[ci[UPC]])
                        items.append(data)
        else:    # .xls file
            logging_info('START CONVERSION')
            # xlrd could not read xls file that generated by PHPExcel
            # so we make file conversion
            input_file_c = convert_xls_file(input_file)
            logging_info('END CONVERSION')

            if input_file_c == '':
                raise Exception('Could not convert xml file')

            wb = xlrd.open_workbook(filename=input_file_c)
            item_sheet = wb.sheet_by_name('Sheet1')

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
                    if data['gtin'] == '':
                        if ci[UPC] > -1 and row[ci[UPC]] != '':
                            data['gtin'] = convert_upc_to_gtin(row[ci[UPC]].value)
                    items.append(data)
    except Exception as e:
        logging_info(str(e), 'ERROR')
        return

    context['items'] = items

    template = template_env.get_template('GoogleManufacturer.html')
    output_content = template.render(context).encode('utf-8')

    filename = write_to_file(output_content)

    logging_info(filename, 'RESULT_FILE')
    logging_info('google-manufacturer.xml', 'FILE_NAME')