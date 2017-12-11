#!/usr/bin/python

# Redis Slave Connectivity Check

import os, sys, json
sys.path.insert(0, '/var/vcap/packages/python-2.7/lib/python2.7/site-packages')
sys.path.insert(0, '/var/vcap/packages/python3/lib/python3.4/site-packages')
import redis

***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***

host = "<%= p('redis_slave.host') %>"
port = "<%= p('redis_slave.port') %>"
password = "<%= p('redis_slave.password') %>"

def conn_redis():
    global host, port, password
    try:
        conn = redis.StrictRedis(host, port, db=0, password=password)
        conn.ping()
    except redis.ConnectionError:
        print "Unknown: Redis connection is failed."
        sys.exit(1)
    return conn

def valid_redis():
    r = conn_redis()
    i = r.info()
    r_out = json.loads(json.dumps(i))
    r_role = r_out["role"]
    if r_role != 'slave':
      print 'Unknown: target redis server must be a slave!'
      sys.exit(1)

if __name__ == '__main__':
    valid_redis()

def check_redis():
    r = conn_redis()
    i = r.info()
    r_out = json.loads(json.dumps(i))
    r_link = r_out["master_link_status"]
    r_iosec = r_out["master_last_io_seconds_ago"]
    if r_link != 'up' and r_iosec == -1:
       print 'Critical: slave redis server is failed to connect master.It is down!'
       sys.exit(1)
    else:
       print 'OK: slave redis is connected properly to master'
       sys.exit(0)

if __name__ == '__main__':
    check_redis()
