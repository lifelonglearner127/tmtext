# pip install flask-login
# pip install flask

import os
import time
import datetime
import sys
import string
import random
import tempfile
import json
import uuid

from flask import (Flask, request, flash, url_for, redirect, render_template,
                   session, send_file, jsonify)

import flask_login
from auth import user_loader, User, load_credentials

app = Flask(__name__)
CWD = os.path.dirname(os.path.abspath(__file__))

app.secret_key = '7946fe07cc4ef6572c24510e2bfb6c780c9c62e7a82e8a0fmastercategory'

CHECK_CREDENTIALS = False

login_manager = flask_login.LoginManager()
login_manager.user_callback = user_loader
login_manager.init_app(app)


def run_converter(input_type, output_type, input_file, mapping_file):
    log_fname = tempfile.NamedTemporaryFile(delete=False)
    log_fname.close()
    log_fname = log_fname.name

    converters_dir = os.path.join(CWD, 'converters')

    if not os.path.exists(converters_dir):
        converters_dir = '.'

    cmd = ('python {converters_dir}/amazon_to_walmart.py --input_type={input_type}'
           ' --output_type={output_type} --input_file={input_file} --mapping_file={mapping_file}'
           ' --log_file="{log_file}"')

    cmd_run = cmd.format(converters_dir=converters_dir, log_file=log_fname,
                         input_type=input_type, output_type=output_type,
                         input_file=input_file, mapping_file=mapping_file)

    print('------- Run converter ----------')
    print(cmd_run)
    print('--------------------------------')
    os.system(cmd_run)

    return log_fname


def upload_file_to_our_server(file):
    fname = file.filename.replace('/', '')
    while fname.startswith('.'):
        fname = fname[1:]
    fname2 = ''
    for c in fname:
        if (c in string.ascii_lowercase or c in string.ascii_uppercase
                or c in string.digits or c in ('.', '_', '-')):
            fname2 += c
        else:
            fname2 += '-'
    fname = fname2
    if not os.path.exists(os.path.join(CWD, '_uploads')):
        os.makedirs(os.path.join(CWD, '_uploads'))
    tmp_local_file = os.path.join(CWD, '_uploads', fname)
    if os.path.exists(tmp_local_file):
        while os.path.exists(tmp_local_file):
            f_name, f_ext = tmp_local_file.rsplit('.', 1)
            f_name += str(random.randint(1, 9))
            tmp_local_file = f_name + '.' + f_ext
    file.save(tmp_local_file)
    return os.path.abspath(tmp_local_file)


def parse_log(log_fname):
    if not os.path.exists(log_fname):
        return False, 'Could not find the conversion result.'
    has_error = False
    result_file = None
    file_name = 'result'
    with open(log_fname, 'r') as fh:
        msgs = [json.loads(m.strip()) for m in fh.readlines() if m.strip()]

        for msg in msgs:
            if msg['level'] == 'RESULT_FILE' and os.path.isfile(msg['msg']):
                result_file = msg['msg']
            if msg['level'] == 'FILE_NAME':
                file_name = msg['msg']
            if msg['level'] == 'ERROR':
                has_error = True

    is_success = True if not has_error else False

    return is_success, msgs, result_file, file_name


def process_form():
    input_type = request.form.get('input_type', None)
    input_file = request.files.get('input_file', None)
    mapping_file = request.files.get('mapping_file', None)
    output_type = request.form.get('output_type', None)

    if not input_type:
        return 'Choose input type'
    if not input_file:
        return 'Choose input file'

    # if not mapping_file:
    #     return 'Choose ID mapping file'

    if not output_type:
        return 'Choose output type'

    input_f = upload_file_to_our_server(input_file)
    if mapping_file:
        mapping_f = upload_file_to_our_server(mapping_file)
    else:
        mapping_f = ''

    log_fname = run_converter(input_type=input_type, output_type=output_type,
                              input_file=input_f, mapping_file=mapping_f)
    success, messages, result_file, file_name = parse_log(log_fname)

    return success, messages, result_file, file_name


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    _msgs = process_form()
    if isinstance(_msgs, (list, tuple)):
        success, messages, result_file, file_name = _msgs
    else:
        return _msgs

    if not success:
        result_response = """
            <h2>Status: <b>FAILED</b></h2>
            <h2>Log:</g2>
            <p>{messages}</p>
        """.format(messages='<br/>'.join([m.get('msg') for m in messages]))
        return result_response

    return send_file(result_file,
                     mimetype='application/force-download',
                     as_attachment=True,
                     attachment_filename=file_name)


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')
