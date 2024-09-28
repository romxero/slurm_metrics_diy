#!/usr/bin/env python3
import subprocess
from datetime import datetime, timedelta
import os
import math
from prometheus_client import start_http_server, Gauge
import time
import statistics

#Mother command df /exp --output="pcent" | sed -e 1d | sed 's/%//g' | xargs


def get_file_system_utilization(fs_location):
    command = f"df {fs_location} --output='pcent' | sed -e 1d | sed 's/%//g' | xargs"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return [line.strip() for line in result.stdout.split('\n') if line.strip()]



if __name__ == '__main__':

    file_system_utilization_exp = Gauge('file_system_utilization_exp', 'File system utilization in percent for /exp')
    file_system_utilization_data = Gauge('file_system_utilization_data', 'File system utilization in percent for /data')
    # Start the Prometheus HTTP server on port 8011

    start_http_server(8011)
    while True:
        
        # Set the value of the Prometheus metric
        exp_util = get_file_system_utilization('/exp')
        data_util = get_file_system_utilization('/data')
        
        #print(int(exp_util[0]))
        #print(int(data_util[0]))
        file_system_utilization_exp.set(exp_util[0])
        file_system_utilization_data.set(data_util[0])
        # Sleep for 30 sec
        time.sleep(30)












