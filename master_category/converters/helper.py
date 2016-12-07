import os
import json
import uuid

LOG_FILE = None
CWD = ''


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

