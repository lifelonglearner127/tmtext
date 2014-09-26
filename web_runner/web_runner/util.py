import fcntl
import logging
import os
import select
import pickle
import zlib
import base64
import datetime


FINISH = 'finished'
UNAVAILABLE = 'unavailable'
RUNNING = 'running'
PENDING = 'pending'


def encode_ids(ids):
    return base64.urlsafe_b64encode(
        zlib.compress(
            pickle.dumps(ids, pickle.HIGHEST_PROTOCOL),
            zlib.Z_BEST_COMPRESSION))


def decode_ids(s):
    return pickle.loads(zlib.decompress(base64.urlsafe_b64decode(
        # Pyramid will automatically decode it as Unicode but it's ASCII.
        s.encode('ascii'))))


def get_request_status(req, jobids_status):
    """Return the status of a REST command or spider request

    Parameters:
      . req: dictionary structure representing a REST request. 
        The structure is the one returned by db.get_request and
        db.get_last_requests
      . jobids_status: Dictionary containing the status of each
        request as it is returned by 
        scrapyd.ScrapydInterface.scrapyd_interf.get_jobs
    """
    final_status = FINISH
    for jobid in req['jobids']:
        # Set the final status
        if not jobid in jobids_status:
            final_status = UNAVAILABLE
        else:
            current_status = jobids_status[jobid]['status']
            if current_status == RUNNING:
                if final_status != UNAVAILABLE:
                    final_status = RUNNING
            elif current_status == PENDING:
                if final_status not in (UNAVAILABLE, RUNNING):
                    final_status = PENDING
            elif current_status == FINISH:
                pass    # Default option
    
    return final_status


def string2datetime(string, format='%Y-%m-%d %H:%M:%S.%f'):
    """Convert a string to datetime.datetime"""

    try:
        date = datetime.datetime.strptime(string, format)
    except ValueError:
        date = None

    return date


def string_from_local2utc(string, format='%Y-%m-%d %H:%M:%S.%f'):
    """Convert a string with localtime to UTC"""
    try:
        offset = datetime.datetime.utcnow() - datetime.datetime.now()
        local_datetime = datetime.datetime.strptime(string, format)
        result_utc_datetime = local_datetime + offset 
        ret = result_utc_datetime.strftime(format)
    except ValueError:
        ret = None

    return ret


def dict_filter(source, items):
    '''Given a source dictionary, returns a new one with a subset of the original

    items is a list of list than conteins the info of the new dictionary 
    structure to be returned.  For example:
    source = {"queues": {
                        "product_ranking": {"running": 0, 
                                            "finished": 0, 
                                            "pending": 0
                                            }
                        }, 
              "scrapyd_projects": ["product_ranking"], 
              "scrapyd_alive": true,
            }
    items = [ ['name1', 'queues'], 
              ['name2', 'queues.product_ranking],
              ['name3', 'queues.product_ranking.running]
            ]

    The returned dictionary should be:
    {"name2": {"running": 0, 
               "finished": 0, 
               "pending": 0}, 
     "name3": 0, 
     "name1": { "product_ranking": {"running": 0, 
                                    "finished": 0, 
                                    "pending": 0}
              }
    }
    '''

    ret = {}

    for item in items:
        if len(item) <> 2:
            continue
        [name, props] = item
        try:
            ret[name] = reduce((lambda x, y: x.get(y)), props.split('.'), source)
        except:
            continue

    return ret

# vim: set expandtab ts=4 sw=4:
