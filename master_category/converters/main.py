import argparse
import jinja2
import os

from template_to_googlemanufacturer import generate_google_manufacturer_xml
from amazon_to_walmart import generate_amazon_to_walmart

from helper import logging_info

CWD = os.path.dirname(os.path.abspath(__file__))

templateLoader = jinja2.FileSystemLoader(searchpath=CWD+'/templates/')
templateEnv = jinja2.Environment(loader=templateLoader)


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
    input_type = namespace.input_type
    output_type = namespace.output_type

    if input_type == 'template' and output_type == 'googlemanufacturer':
        generate_google_manufacturer_xml(input_file)
    elif input_type == 'amazon' and output_type == 'walmart':
        generate_amazon_to_walmart(input_file)
    else:
        generate_error()


def generate_error():
    logging_info('This type of conversion does not exist.', 'ERROR')


if __name__ == '__main__':
    main()
