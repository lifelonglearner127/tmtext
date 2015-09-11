# TODO: bestsellers check

import os
import sys
import datetime
import zipfile
import subprocess
import tempfile

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils.timezone import now

CWD = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(CWD, '..', '..', '..', '..'))

from settings import MEDIA_ROOT
from gui.models import Job, get_data_filename, get_log_filename,\
    get_progress_filename


sys.path.append(os.path.join(CWD,  '..', '..', '..', '..', '..',
                             'deploy', 'sqs_ranking_spiders'))
import scrapy_daemon
from test_sqs_flow import download_s3_file, AMAZON_BUCKET_NAME, unzip_file
from list_all_files_in_s3_bucket import list_files_in_bucket, \
        AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY

LOCAL_AMAZON_LIST_CACHE = os.path.join(CWD, '_amazon_listing.txt')


def run(command, shell=None):
    """ Run the given command and return its output
    """
    out_stream = subprocess.PIPE
    err_stream = subprocess.PIPE

    if shell is not None:
        p = subprocess.Popen(command, shell=True, stdout=out_stream,
                             stderr=err_stream, executable=shell)
    else:
        p = subprocess.Popen(command, shell=True, stdout=out_stream,
                             stderr=err_stream)
    (stdout, stderr) = p.communicate()

    return stdout, stderr


def num_of_running_instances(file_path):
    """ Check how many instances of the given file are running """
    processes = 0
    output = run('ps aux')
    output = ' '.join(output)
    for line in output.split('\n'):
        line = line.strip()
        line = line.decode('utf-8')
        if file_path in line and not '/bin/sh' in line:
            processes += 1
    return processes


def list_amazon_bucket(bucket=AMAZON_BUCKET_NAME,
                       local_fname=LOCAL_AMAZON_LIST_CACHE):
    filez = list_files_in_bucket(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, bucket)
    # dump to a temporary file and replace the original one then
    tmp_file = tempfile.NamedTemporaryFile(mode='rb', delete=False)

    with open(tmp_file.name, 'w') as fh:
        for f in filez:
            fh.write(str(f)+'\n')
    if os.path.exists(local_fname):
        os.unlink(local_fname)
    os.rename(tmp_file.name, local_fname)


def get_filenames_for_task_id(task_id, server_name,
                              local_fname=LOCAL_AMAZON_LIST_CACHE):
    slug_server_name = scrapy_daemon.slugify(server_name)
    with open(local_fname, 'r') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if '____%s--%s____' % (slug_server_name, task_id) in line:
                if ',' in line:
                    line = line.split(',')[-1]
                line = line.replace('<', '').replace('>', '')
                yield line.strip()


def rename_first_file_with_extension(base_dir, new_fname, extension='.csv'):
    for filename in os.listdir(base_dir):
        if filename.lower().endswith(extension):
            os.rename(
                os.path.join(base_dir, filename),
                os.path.join(base_dir, new_fname)
            )
            return


def _unzip_local_file(fname, new_fname, ext):
    if zipfile.is_zipfile(fname):
        unzip_file(fname, unzip_path=fname)
        os.remove(fname)
        rename_first_file_with_extension(
            os.path.dirname(fname),
            new_fname,
            ext
        )


class Command(BaseCommand):
    help = 'Updates 10 random jobs, downloading their files if ready'

    def handle(self, *args, **options):
        if num_of_running_instances('update_jobs') > 1:
            print 'an instance of the script is already running...'
            sys.exit()
        jobs = Job.objects.filter(
            Q(status='pushed into sqs') | Q(status='in progress')
        ).order_by('?').distinct()[0:10]
        if jobs:
            list_amazon_bucket()  # get list of files from S3
        for job in jobs:
            # try to find the appropriate S3 file by task ID
            amazon_fnames = get_filenames_for_task_id(job.task_id,
                                                      job.server_name)
            if not isinstance(amazon_fnames, (list, tuple)):  # generator?
                amazon_fnames = list(amazon_fnames)
            amazon_data_file = [f for f in amazon_fnames if '.csv' in f]
            amazon_json_data_file = [f for f in amazon_fnames if '.jl' in f]
            amazon_log_file = [f for f in amazon_fnames if '.log' in f]
            amazon_progress_file = [f for f in amazon_fnames
                                    if '.progress' in f]

            amazon_data_file = amazon_data_file[0] if amazon_data_file else []
            amazon_json_data_file = amazon_json_data_file[0]\
                if amazon_json_data_file else []
            amazon_log_file = amazon_log_file[0] if amazon_log_file else []
            amazon_progress_file = amazon_progress_file[0]\
                if amazon_progress_file else []

            print
            print '=' * 79
            print 'Processing JOB', job.__dict__
            print 'Data file', amazon_data_file
            print 'Log file', amazon_log_file
            print 'Progress file', amazon_progress_file

            if amazon_progress_file:
                job.status = 'in progress'
                job.save()

            if amazon_progress_file:
                full_local_prog_path = MEDIA_ROOT + get_progress_filename(job)
                if not os.path.exists(os.path.dirname(full_local_prog_path)):
                    os.makedirs(os.path.dirname(full_local_prog_path))
                download_s3_file(AMAZON_BUCKET_NAME, amazon_progress_file,
                                 full_local_prog_path)
                _unzip_local_file(full_local_prog_path, 'progress.progress',
                                  '.progress')

            if amazon_log_file:
                full_local_log_path = MEDIA_ROOT + get_log_filename(job)
                if not os.path.exists(os.path.dirname(full_local_log_path)):
                    os.makedirs(os.path.dirname(full_local_log_path))
                download_s3_file(AMAZON_BUCKET_NAME, amazon_log_file,
                                 full_local_log_path)
                _unzip_local_file(full_local_log_path, 'log.log', 'log')
                with open(full_local_log_path, 'r') as fh:
                    cont = fh.read()
                    if not "'finish_reason': 'finished'" in cont:
                        job.status = 'failed'
                        job.save()
                        continue

            if amazon_data_file:
                print 'For job with task ID %s we found amazon fname [%s]' % (
                    job.task_id, amazon_data_file)
                full_local_data_path = MEDIA_ROOT + get_data_filename(job)
                if not os.path.exists(os.path.dirname(full_local_data_path)):
                    os.makedirs(os.path.dirname(full_local_data_path))
                download_s3_file(AMAZON_BUCKET_NAME, amazon_data_file,
                                 full_local_data_path)
                _unzip_local_file(full_local_data_path, 'data_file.csv', '.csv')
                if zipfile.is_zipfile(full_local_data_path):
                    unzip_file(full_local_data_path,
                               unzip_path=full_local_data_path)
                    os.remove(full_local_data_path)
                    rename_first_file_with_extension(
                        os.path.dirname(full_local_data_path),
                        'data_file.csv',
                        '.csv'
                    )

            if not amazon_data_file and amazon_json_data_file:  # CSV conversion failed?
                print 'For job with task ID %s we found amazon fname [%s]' % (
                    job.task_id, amazon_json_data_file)
                full_local_data_path = MEDIA_ROOT + get_data_filename(job)
                if not os.path.exists(os.path.dirname(full_local_data_path)):
                    os.makedirs(os.path.dirname(full_local_data_path))
                download_s3_file(AMAZON_BUCKET_NAME, amazon_json_data_file,
                                 full_local_data_path)
                _unzip_local_file(full_local_data_path, 'data_file.csv', '.csv')
                if zipfile.is_zipfile(full_local_data_path):
                    unzip_file(full_local_data_path,
                               unzip_path=full_local_data_path)
                    os.remove(full_local_data_path)
                    rename_first_file_with_extension(
                        os.path.dirname(full_local_data_path),
                        'data_file.csv',
                        '.csv'
                    )

            if amazon_data_file or amazon_json_data_file:
                if amazon_log_file:  # log file should exist for successful jobs
                    job.status = 'finished'
                    job.finished = now()
                    job.save()