try:
    from simmetrica import Simmetrica
    USING_SIMMETRICA = True
except ImportError:
    USING_SIMMETRICA = False


MONITORING_HOST = '54.174.165.160'


def push_simmetrica_event(
        event_name, increment_by=1,
        host=MONITORING_HOST, port=6379, db=0, password=None
):
    """

    :param event_name: str, event, like "spider_opened"
    :param increment_by: int, increments event counter by this value
    :param host: Redis server host, default is MONITORING_HOST
    :param port: Redis server port, default is 6379
    :param db: Redis database, default is 0
    :param password: Redis password, default is None
    :return: True if the event has been pushed, None otherwise
    """
    global USING_SIMMETRICA
    if not USING_SIMMETRICA:
        return
    try:
        simm = Simmetrica(host=host, port=port, db=db, password=password)
        simm.push(event_name, increment=increment_by)
    except Exception, e:
        # in very rare cases, pushing fails (if using SocksiPy for ex).
        # TODO: implement command-line event addition
        return
    return True