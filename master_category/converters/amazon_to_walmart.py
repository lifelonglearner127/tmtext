import argparse

from lxml import html, etree

import csv
import xlrd
from openpyxl import Workbook
from openpyxl.compat import range
from openpyxl.utils import get_column_letter
import jinja2
import os
import json
import uuid
import subprocess

CWD = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = None

templateLoader = jinja2.FileSystemLoader( searchpath=CWD+'/templates/' )

templateEnv = jinja2.Environment( loader=templateLoader )


def logging_info(msg, level='INFO'):
    """ We're using JSON which is easier to parse """
    global LOG_FILE
    with open(LOG_FILE, 'a') as fh:
        fh.write(json.dumps({'msg': msg, 'level': level})+'\n')

    print('CONVERTER LOGGING : [%s] %s' % (level, msg))


def get_result_file_name():
    if not os.path.exists(os.path.join(CWD, '_results')):
        os.makedirs(os.path.join(CWD, '_results'))
    filename = os.path.join(CWD, '_results', str(uuid.uuid4()))
    return filename


def write_to_file(content):
    filename = get_result_file_name()
    with open(filename, 'w') as result:
        result.write(content)

    return filename


def check_extension(filename, extensions):
    name, file_extension = os.path.splitext(filename)
    return file_extension in extensions


def generate_google_manufacturer_xml(input_file):
    available_extensions = ['.csv']
    items = []
    context = {}

    if not check_extension(input_file, available_extensions):
        logging_info('The file extension should be %s.'
                     % (','.join(available_extensions)), 'ERROR')
        return

    try:
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
    except Exception as e:
        logging_info(str(e), 'ERROR')
        return

    context['items'] = items

    template = templateEnv.get_template('GoogleManufacturer.html')
    output_content = template.render(context)

    filename = write_to_file(output_content)

    logging_info(filename, 'RESULT_FILE')
    logging_info('google-manufacturer.xml', 'FILE_NAME')


def generate_amazon_to_walmart(input_file, mapping_file):
    available_extensions = ['.xls']
    available_mapping_extensions = ['.csv']

    # check file extensions
    if not check_extension(input_file, available_extensions):
        logging_info('The file extension should be %s.'
                     % (','.join(available_extensions)), 'ERROR')
        return

    if not check_extension(mapping_file, available_mapping_extensions):
        logging_info('The mapping file extension should be %s.'
                     % (','.join(available_mapping_extensions)), 'ERROR')
        return

    template = templateEnv.get_template('walmart_long_description.html')

    def create_walmart_description(bullet1, bullet2, bullet3, bullet4, bullet5):
        context = {"bullets": []}
        context["bullets"] += [bullet1] if bullet1 != "" else []
        context["bullets"] += [bullet2] if bullet2 != "" else []
        context["bullets"] += [bullet3] if bullet3 != "" else []
        context["bullets"] += [bullet4] if bullet4 != "" else []
        context["bullets"] += [bullet5] if bullet5 != "" else []
        
        return template.render(context)

    def convert_file(source_file):
        name, ext = os.path.splitext(source_file)
        dst_file = name + '-cvt' + ext
        cmd_run = [
            '/usr/bin/unoconv',
            '-d',
            'spreadsheet',
            '--output',
            dst_file,
            '--format',
            'xls',
            source_file
        ]
        try:
            my_env = os.environ.copy()
            my_env["PATH"] = "/usr/bin:" + my_env["PATH"]
            subprocess.call(cmd_run, env=my_env)
        except Exception as e:
            logging_info('CONVERSION : ' + str(e))
        return dst_file

    mapper = {}
    # read mapping file
    try:
        with open(mapping_file, 'rU') as csvfile:
            csvfile.readline()
            reader = csv.reader(csvfile)
            for item in reader:
                if len(item) >= 4 and item[1] != '':
                    mapper[item[1]] = item
    except Exception as e:
        logging_info(str(e), 'ERROR')
        return

    logging_info('START CONVERSION')

    # xlrd could not read xls file that generated by PHPExcel
    # so we make file conversion
    repeat_cnt = 0
    input_file_c = ''
    while True:
        input_file_c = convert_file(input_file)
        repeat_cnt += 1
        if os.path.isfile(input_file_c):
            break
        if repeat_cnt > 3:
            input_file_c = ''
            break
    logging_info('END CONVERSION')

    if input_file_c == '':
        logging_info('Could not convert xml file', 'ERROR')
        return
    
    try:
        wb = xlrd.open_workbook(filename=input_file_c)
    except Exception as e:
        logging_info(str(e), 'ERROR')
        return

    item_sheet = wb.sheet_by_name('Item_Sheet')

    items = []
    # Read data from amazone form
    for idx, row in enumerate(item_sheet.get_rows()):
        if idx > 4:
            if row[4].value in mapper:
                try:
                    data = {
                        "upc": u"",
                        "gstn": u"",
                        "tool_id": unicode(mapper[row[4].value][3], "utf-8"),
                        "title": row[6].value,
                        "short_desc": row[30].value,
                        "shelf_desc": u"",
                        "long_desc": create_walmart_description(
                            row[31].value, row[32].value, row[33].value, row[34].value, row[35].value),
                        "ingredients": row[37].value,
                        "directions": row[38].value,
                        "warnings": row[39].value,
                    }

                    items.append(data)
                except:
                    pass

    wb = Workbook()
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
                    item["shelf_desc"],
                    item["short_desc"],
                    item["directions"],
                    item["ingredients"],
                    item["warnings"],
                    ])

    filename = get_result_file_name()
    wb.save(filename=filename)

    logging_info(filename, 'RESULT_FILE')
    logging_info('WalmartBulkContentUpload.xlsx', 'FILE_NAME')


def generate_error():
    logging_info('This type of conversion does not exist.', 'ERROR')


def main():
    global LOG_FILE, OUTPUT_DIR, ID

    parser = argparse.ArgumentParser(description='test',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--input_type', type=str, required=True,
                        help="Enter input type\n"
                             "Defined types\n"
                             " - amazon\n"
                             " - template\n")
    parser.add_argument('--output_type', type=str, required=True,
                        help="Enter output type\n"
                             "Defined types\n"
                             " - walmart\n"
                             " - googlemanufacturer\n")
    parser.add_argument('--input_file', type=str, required=True,
                        help="File to upload")
    parser.add_argument('--mapping_file', type=str, required=True,
                        help="File to map")
    parser.add_argument('--log_file', type=str, required=True,
                        help="filename for output logging")

    namespace = parser.parse_args()


    LOG_FILE = namespace.log_file
    input_file = namespace.input_file
    mapping_file = namespace.mapping_file
    input_type = namespace.input_type
    output_type = namespace.output_type

    if input_type == 'template' and output_type == 'googlemanufacturer':
        logging_info('[Start Google Manufacturer]')
        generate_google_manufacturer_xml(input_file)
        logging_info('[End Google Manufacturer]')
    elif input_type == 'amazon' and output_type == 'walmart':
        logging_info('[START Amazon to Walmart]')
        generate_amazon_to_walmart(input_file, mapping_file)
        logging_info('[END Amazon to Walmart]')
    else:
        generate_error()

    return


if __name__ == '__main__':
    main()
