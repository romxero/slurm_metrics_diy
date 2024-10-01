#!/usr/bin/env python3
import subprocess
from datetime import datetime, timedelta
import os
import math
from prometheus_client import start_http_server, Gauge
import time
import statistics

# get the current date and subtract 1 hour
# format the date properly for the fn
# mother command : # sacct -a -X -S 2024-08-24T00:00:00  -o submit,start -P -n | grep -v -e "None" -e "Unknown" 



def get_job_info(start_date):
    command = f"sacct -a -X -S {start_date} -o submit,start -P -n | grep -v -e 'None' -e 'Unknown'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return [line.strip() for line in result.stdout.split('\n') if line.strip()]


def split_and_convert_to_datetime(input_string):
    """
    Split a string by '|' delimiter and convert the resulting parts to datetime objects.
    
    Args:
    input_string (str): A string containing datetime information separated by '|'
    
    Returns:
    tuple: A tuple of two datetime objects
    """
    # Split the input string by '|'
    parts = input_string.strip().split('|')
    
    # Check if we have exactly two parts
    if len(parts) != 2:
        raise ValueError("Input string must contain exactly two datetime strings separated by '|'")
    
    # Convert each part to a datetime object
    try:
        dt1 = datetime.strptime(parts[0], '%Y-%m-%dT%H:%M:%S')
        dt2 = datetime.strptime(parts[1], '%Y-%m-%dT%H:%M:%S')
    except ValueError as e:
        raise ValueError(f"Error parsing datetime: {e}")
    
    return dt1, dt2



def datetime_diff_seconds(dt1, dt2):
    """
    Calculate the difference between two datetime objects and return the result in seconds.
    
    Args:
    dt1 (datetime): The first datetime object
    dt2 (datetime): The second datetime object
    
    Returns:
    float: The difference in seconds
    """
    time_diff = dt2 - dt1
    return time_diff.total_seconds()


# start the processing of the job info

def get_slurm_wait_time(start_time):
    
    slurm_wait_time_list = []
    job_start_time_info = get_job_info(start_time)
    for job_info in job_start_time_info:
        try:
            submit_time, start_time = split_and_convert_to_datetime(job_info)
            time_difference = datetime_diff_seconds(submit_time, start_time)
            slurm_wait_time_list.append(time_difference)
            #print(f"Job submitted at: {submit_time}")
            #print(f"Job started at: {start_time}")
            #print(f"Time difference: {time_difference} seconds")
            #print("---")
        except ValueError as e:
            print(f"Error processing job info: {e}")
            print("---")
    return slurm_wait_time_list


if __name__ == '__main__':
    #main metric name: slurm_job_wait_time
    slurm_job_wait_time_mean = Gauge('slurm_job_wait_time_mean', 'Slurm job wait time in seconds')
    slurm_job_wait_time_median = Gauge('slurm_job_wait_time_median', 'Slurm job wait time in seconds')
    
    # Start the Prometheus HTTP server on port 8009
    start_http_server(8009)
    while True:
        # Generate a random number
        d = datetime.today() - timedelta(hours=1)
        current_start_date = d.strftime('%Y-%m-%dT%H:%M:%S')

        slurm_wait_time_list = get_slurm_wait_time(current_start_date)
        mean_wait_time = statistics.mean(slurm_wait_time_list)
        median_wait_time = statistics.median(slurm_wait_time_list)
        # Set the value of the Prometheus metric
        #slurm_job_wait_time.set(mean_wait_time)
        slurm_job_wait_time_mean.set(mean_wait_time)
        slurm_job_wait_time_median.set(median_wait_time)
        # Sleep for 30 sec
        time.sleep(30)


#print()
#print()






