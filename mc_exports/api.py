import os
import xlrd
import csv

# We'll render HTML templates and access data sent by POST
# using the request object from flask. Redirect and url_for
# will be used to redirect the user once the upload is done
# and send_from_directory will help us to send/show on the
# browser the file that the user just uploaded
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from werkzeug import secure_filename

# Initialize the Flask application
app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = '/var/tmp/mc_exports/upload/'
app.config['EXPORT_FOLDER'] = '/var/tmp/mc_exports/export/'
# This is the path to the template file
app.config['TEMPLATE_MAPPING_FILE'] = '/var/tmp/mc_exports/Template Mapping File.xlsx'

# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['csv'])


# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def parse_input_file(file_path):
    with open(file_path, 'r') as f:
        results = [row for row in csv.DictReader(f.read().splitlines())]

    return results


def parse_template_file(file_path):
    template_mapping_info_json = {"column_name_list": [], "map_info_by_retailer": {}}
    workbook = xlrd.open_workbook(file_path)
    worksheet = workbook.sheet_by_index(0)

    # Change this depending on how many header rows are present
    # Set to 0 if you want to include the header data.
    offset = 0

    for i, row in enumerate(range(worksheet.nrows)):
        if i <= offset:  # (Optionally) skip headers
            for j, col in enumerate(range(worksheet.ncols)):
                template_mapping_info_json["column_name_list"].append(worksheet.cell_value(i, j).strip())
            continue

        r = {}

        for j, col in enumerate(range(worksheet.ncols)):
            r[worksheet.cell_value(0, j).strip()] = worksheet.cell_value(i, j).strip()

        template_mapping_info_json["map_info_by_retailer"][worksheet.cell_value(i, 0).strip().lower()] = r

    return template_mapping_info_json


def filter_input_data_by_template(input_data_info, template_mapping_info, retailer):
    retailer = retailer.strip().lower()
    results = []

    for index, row in enumerate(input_data_info):
        result_row = {}

        for column in row:
            if template_mapping_info["map_info_by_retailer"][retailer].get(column, None):
                if template_mapping_info["map_info_by_retailer"][retailer][column] == "*":
                    result_row[column] = row[column]
                else:
                    result_row[template_mapping_info["map_info_by_retailer"][retailer][column]] = row[column]

        results.append(result_row)

    return results


def generate_export_file(filtered_data, retailer):
    keys = filtered_data[0].keys()

    with open(os.path.join(app.config['EXPORT_FOLDER'], '{0}_mc_export.csv'.format(retailer)), 'wb') as export_file:
        dict_writer = csv.DictWriter(export_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(filtered_data)

    return '{0}_mc_export.csv'.format(retailer)


def make_error(status_code, sub_code, message, action):
    response = jsonify({
        'status': status_code,
        'sub_code': sub_code,
        'message': message,
        'action': action
    })
    response.status_code = status_code

    return response

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('index.html')


# Route that will process the file upload
@app.route('/mc_export', methods=['POST'])
def mx_export():
    # Get the name of the uploaded file
    file = request.files['file']
    retailer = request.args.get("retailer")

    if not file:
        return make_error(0, 0, 'Missing param: template file', 'Try again...')

    if not retailer:
        return make_error(0, 0, 'Missing param: retailer', 'Try again...')

    if not allowed_file(file.filename):
        return make_error(0, 0, 'Incorrect file type: the input file should be csv format.', 'Try again...')

    template_mapping_info = parse_template_file(app.config["TEMPLATE_MAPPING_FILE"])

    if not template_mapping_info or not template_mapping_info.get("map_info_by_retailer", None):
        return make_error(0, 0, 'Empty template map info', 'Try again...')

    # Make the filename safe, remove unsupported chars
    filename = secure_filename(file.filename)
    # Move the file form the temporal folder to
    # the upload folder we setup
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    input_data_info = parse_input_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    if retailer.strip().lower() not in template_mapping_info["map_info_by_retailer"]:
        return make_error(0, 0, 'Retailer doesn\'t exist in template mapping file', 'Try again...')

    filtered_data = filter_input_data_by_template(input_data_info, template_mapping_info, retailer)
    export_file_name = generate_export_file(filtered_data, retailer)

    # Redirect the user to the uploaded_file route, which
    # will basicaly show on the browser the uploaded file
    return send_from_directory(directory=app.config['EXPORT_FOLDER'],
                               filename=export_file_name,
                               as_attachment=True,
                               attachment_filename=export_file_name)

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("80"),
        debug=True
    )
