import os
import sys

CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CWD, '..', 'product_ranking'))

from spiders import (push_simmetrica_event, USING_SIMMETRICA,
                     MONITORING_HOST, get_simmetrica_events,
                     return_average_for_last_days)