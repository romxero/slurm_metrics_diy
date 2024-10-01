#!/usr/bin/env python3
import subprocess
from datetime import datetime, timedelta
import os
import math
from prometheus_client import start_http_server, Gauge
import time
import statistics
import json
#Mother command # sacctmgr show users -n -P | cut -d '|' -f 1

def get_slurm_users():
    command = "sacctmgr show users -n -P | cut -d '|' -f 1"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return [line.strip() for line in result.stdout.split('\n') if line.strip()]



def get_user_job_obj(user):
    command = f"squeue -h -a -u {user} -t R  --json"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return json.loads(result.stdout)



print(slurm_users)

if __name__ == '__main__':

    #file_system_utilization_exp = Gauge('file_system_utilization_exp', 'File system utilization in percent for /exp')
    #file_system_utilization_data = Gauge('file_system_utilization_data', 'File system utilization in percent for /data')
    slurm_users = get_slurm_users()
    print(slurm_users)

    # Start the Prometheus HTTP server on port 8012
    start_http_server(8012)
    while True:
        
        # Set the value of the Prometheus metric
        for user in slurm_users:
            exp_util = get_file_system_utilization('/exp')
            data_util = get_file_system_utilization('/data')
        
        #print(int(exp_util[0]))
        #print(int(data_util[0]))
        file_system_utilization_exp.set(exp_util[0])
        file_system_utilization_data.set(data_util[0])
        # Sleep for 30 sec
        time.sleep(30)






