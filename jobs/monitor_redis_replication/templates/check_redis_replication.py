#!/usr/bin/env python

import sys
import time
from decimal import Decimal
import math

REPL_DELAY_TEST_KEY = 'REPL_DELAY_TEST_KEY'
master_ts = 0
slave_ts = 0

STATE_OK = 0
STATE_WARNING = 1

try:
    sys.path.insert(0, '/var/vcap/packages/python-2.7/lib/python2.7/site-packages')
    import redis
except ImportError:
    print ("WARNING: need to install redis python library." +
           "easy_install redis")
    sys.exit(STATE_WARNING)


***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***

host = "<%= p('redis_replication.host') %>"
port = "<%= p('redis_replication.port') %>"
password = "<%= p('redis_replication.password') %>"
max_sec_accepted_behind_master_critical = "<%= p('redis_replication.warning_threshold') %>"
max_sec_accepted_behind_master_warning = 1

r_conn_slave = redis.StrictRedis(host=host, port=port, password=password)

def setts ():
    try:
        info_slave_dic = r_conn_slave.info()
        # get master's connection details:
        master_host = info_slave_dic['master_host']
        master_port = info_slave_dic['master_port']
    except Exception as e:
        print "Error when trying to get master's connection details: %s" % e
        sys.exit(STATE_WARNING)
    try:
        r_conn_master = redis.StrictRedis(host=master_host, port=master_port, password=password)
        # set a timestamp on master as value for the delay test key
        r_conn_master.delete(REPL_DELAY_TEST_KEY)
        master_ts = str(time.time())
        r_conn_master.set(REPL_DELAY_TEST_KEY, master_ts)
        #print "Setting ts: %s" % master_ts
    except Exception as e:
        print "Error when trying to write to master: %s" % e
        sys.exit(STATE_WARNING)
    return master_ts

def getts ():
    try:
        # get the value of the delay test key from slave
        slave_ts = str(r_conn_slave.get(REPL_DELAY_TEST_KEY))
        #print "Getting ts: %s" % slave_ts
    except Exception as e:
        print "Error when trying to read from slave: %s" % e
        sys.exit(STATE_WARNING)
    return slave_ts

if __name__ == '__main__':
    master_ts = setts()
    start_time = time.time()
    timeout = time.time() + float(max_sec_accepted_behind_master_critical) + 2
    while True:
        slave_ts = getts()
        if ( time.time() > timeout ):
            print "Warning - Could not measure replication time. Slave may be %s seconds behind master (> %s sec)." % (timeout, max_sec_accepted_behind_master_warning)
            sys.exit(STATE_WARNING)
        elif ( slave_ts == master_ts ):
            end_time = time.time()
            break
    delay = Decimal(end_time) - Decimal(start_time)
    seconds_behind_master = math.ceil(delay*10000)/10000

    if ( max_sec_accepted_behind_master_warning <= seconds_behind_master < max_sec_accepted_behind_master_critical ):
        print "Warning - Replication is slow: slave is %s seconds behind master (> %s sec)." % (seconds_behind_master, max_sec_accepted_behind_master_warning)
        sys.exit(STATE_WARNING)

    print "Replication is OK. Slave is %s seconds behind master (< %s sec)." % (seconds_behind_master, max_sec_accepted_behind_master_warning)
    sys.exit(STATE_OK)
