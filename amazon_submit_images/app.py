# pip install flask-login
# pip install flask

import os
import time
import datetime
import sys
import string
import random
import tempfile

from flask import (Flask, request, flash, url_for, redirect, render_template,
                   session)

import flask.ext.login as flask_login
from auth import user_loader, User, load_credentials

app = Flask(__name__)
CWD = os.path.dirname(os.path.abspath(__file__))

app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KTSn  SKDk34k8**W$7SDfsdhSD4SDfggazsd'

login_manager = flask_login.LoginManager()
login_manager.user_callback = user_loader
login_manager.init_app(app)


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


def run_spider(username, password, local_file):
    log_fname = tempfile.NamedTemporaryFile(delete=False)
    log_fname.close()
    log_fname = log_fname.name

    spiders_dir = os.path.join(CWD, '..', 'product-ranking',
                               'product_ranking', 'spiders')
    cmd = ('python {spiders_dir}/submit_amazon_images.py --username={username}'
           ' --password={password} --zip_file={zip_file} --logging_file={log_file}')
    os.system(cmd.format(username=username, password=password, zip_file=local_file,
                         log_file=log_fname, spiders_dir=spiders_dir))
    return log_fname


def parse_log(log_fname):
    # TODO: error / success messages
    return 'ok', 'successfully uploaded'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('upload.html')

    username = request.form.get('username', None)
    password = request.form.get('password', None)
    file = request.files.get('file', None)

    if not username:
        return 'Enter username'
    if not password:
        return 'Enter password'
    if not file:
        return 'Select a file to upload'
    if not file.filename.lower().endswith('.zip'):
        return 'Please upload a zip file (ending with .zip)'

    time.sleep(1)  # against bruteforce attacks ;)

    for cred_login, cred_password in load_credentials():
        if username.strip() == cred_login.strip():
            if password.strip() == cred_password.strip():
                user = User()
                user.id = username
                flask_login.login_user(user)

                local_file = upload_file_to_our_server(file)
                log_fname = run_spider(username=username, password=password,
                                       local_file=local_file)
                status, messages = parse_log(log_fname)
                return 'Status: {status}<br/>Messages: {messages}'.format(
                    status=status, messages=messages)

    return 'Invalid login or password'


if __name__ == '__main__':
    app.run(debug=True)