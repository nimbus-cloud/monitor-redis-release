#!/usr/bin/env python

import sys
import time
from decimal import Decimal
import math

egg_path='/var/vcap/packages/python_2.7.13/lib/python2.7/site-packages/redis-2.10.6-py2.7.egg'
sys.path.append(egg_path)
import redis

master_ts = 0
slave_ts = 0

STATE_OK = 0
STATE_WARNING = 1

host = "<%= p('redis_replication.host') %>"
port = "<%= p('redis_replication.port') %>"
password = "<%= p('redis_replication.password') %>"
max_sec_accepted_behind_master_critical = "<%= p('redis_replication.warning_threshold') %>"
max_sec_accepted_behind_master_warning = 1
user = "<%= p('redis_replication.user') %>"
user_password = "<%= p('redis_replication.user_password') %>"

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
        r_conn_master.set('user', user)
        r_conn_master.set('user_password', user_password)
        master_ts = r_conn_master.get('user')
        print "Setting ts: %s" % master_ts
    except Exception as e:
        print "Error when trying to write to master: %s" % e
        sys.exit(STATE_WARNING)
    return master_ts

def getts ():
    try:
        # get the value of the delay test key from slave
        slave_ts = r_conn_slave.get('user')
        print "Getting ts: %s" % slave_ts
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
