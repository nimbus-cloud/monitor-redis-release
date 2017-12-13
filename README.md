monitor-redis-release

This release contains 2 monit checks which are to be deployed on the master node.

Check 1:
checks if the slave is connected to the master node
Check 2:
checks if the replication between master and slave is working by creating a dummy key
Manifests

Redis Slave Check

The required variables in manifests are

slave host/ip
slave port
slave password
Redis Replication Check

The required variables in manifests are

slave host/ip
slave port
slave password
Warning threshold (time in seconds it takes for replication to occur)
Dependancy

The checks are written in python and use the python module 'redis'. 
