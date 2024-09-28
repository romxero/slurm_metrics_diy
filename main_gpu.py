#!/usr/bin/env python3
import subprocess
import json
import time

from prometheus_client import Gauge, start_http_server
import datetime
from datetime import timedelta  

# get the current date and subtract 1 hour
# format the date properly for the fn
# mother commands : 
# This string grabs all nodes from slurm. scontrol show nodes | grep NodeName | cut -d ' ' -f 1 | sed 's/NodeName=//g'
# grab the json from scontrol: scontrol show node {node} --json

# getting a list of nodes. Its a bit more lenient on the scheduler by doing this process in steps

def get_list_of_nodes():
    command = f"scontrol show nodes | grep NodeName | cut -d ' ' -f 1 | sed 's/NodeName=//g'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return [line.strip() for line in result.stdout.split('\n') if line.strip()]


# grab the node object
#for node in get_list_of_nodes():

def get_node_object(node):
    #print(node)
    command = f"scontrol show node {node} --json"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    slurm_node_object = json.loads(result.stdout)
    
    state = "" # initialize the state variable
    
    # grab these values from the node object
    _features = slurm_node_object['nodes'][0]['features']
    
    if 'gpu' in _features:    
        _state = slurm_node_object['nodes'][0]['state']
        _tres_used = slurm_node_object['nodes'][0]['tres_used']
        _gres = slurm_node_object['nodes'][0]['gres']
        _gres_used = slurm_node_object['nodes'][0]['gres_used']
        # if this is a gpu node then we can do some processing
    
        # conditional to see if the resource is idle or allocated    
        if 'IDLE' in _state:
            state = "idle"
        elif 'ALLOCATED' in _state:
            state = "allocated"
        else:
            state = "unknown"
        # make sure we work with the features here 
        if 'l4' in _features:
            features = "l4"
        elif 'h100' in _features:
            features = "h100"
        else:
            features = "unknown"
        
        # get the number of gpus
        num_gpus = int(_gres.replace('gpu:', ''))
        num_gpus_used = int(_gres_used.replace('gpu:', ''))
        # return the values
        #print(num_gpus, num_gpus_used, state, features)    
        return num_gpus, num_gpus_used, state, features
    else:
        return 0, 0, "unknown", "unknown"



if __name__ == '__main__':
    
    #main metric name: slurm_job_wait_time
    slurm_gpu_metrics_h100_idle = Gauge('slurm_gpu_metrics_h100_idle', 'Slurm gpu usage metrics of idle h100')
    slurm_gpu_metrics_l4_idle = Gauge('slurm_gpu_metrics_l4_idle', 'Slurm gpu usage metrics of idle l4s')
    
    slurm_gpu_metrics_h100_allocated = Gauge('slurm_gpu_metrics_h100_allocated', 'Slurm gpu usage metrics of allocated h100')
    slurm_gpu_metrics_l4_allocated = Gauge('slurm_gpu_metrics_l4_allocated', 'Slurm gpu usage metrics of allocated l4s')
    
    slurm_gpu_metrics_h100_total = Gauge('slurm_gpu_metrics_h100_total', 'Slurm gpu usage metrics of total h100')
    slurm_gpu_metrics_l4_total = Gauge('slurm_gpu_metrics_l4_total', 'Slurm gpu usage metrics of total l4s')
    
    # Start the Prometheus HTTP server on port 8010
    start_http_server(8010)
    while True:
        l4_idle_list = []
        h100_idle_list = []
        l4_allocated_list = []
        h100_allocated_list = []
        l4_total_list = []
        h100_total_list = []
    
        node_list = get_list_of_nodes()
        
        for node in node_list:
    
            num_gpus, num_gpus_used, state, features = get_node_object(node)

            if state == "idle":
                if features == "h100":
                    h100_idle_list.append(num_gpus)
                elif features == "l4":
                    l4_idle_list.append(num_gpus)
            elif state == "allocated":
                if features == "h100":
                    if num_gpus_used < num_gpus:
                        idle_diff = num_gpus - num_gpus_used
                        
                        h100_idle_list.append(idle_diff)
                        h100_allocated_list.append(num_gpus_used)
                    else:
                        h100_allocated_list.append(num_gpus_used)
                elif features == "l4":
                    if num_gpus_used < num_gpus:
                        idle_diff = num_gpus - num_gpus_used
                        
                        l4_idle_list.append(idle_diff)
                        l4_allocated_list.append(num_gpus_used)
                    else:
                        l4_allocated_list.append(num_gpus_used)
            if features == "h100":
                h100_total_list.append(num_gpus)
            elif features == "l4":
                l4_total_list.append(num_gpus)
            
            #time.sleep(2) # sleep for 2 seconds so we don't mess with the scheduler too much
        
        # set the metrics
        slurm_gpu_metrics_h100_idle.set(sum(h100_idle_list))
        slurm_gpu_metrics_l4_idle.set(sum(l4_idle_list))
        slurm_gpu_metrics_h100_allocated.set(sum(h100_allocated_list))
        slurm_gpu_metrics_l4_allocated.set(sum(l4_allocated_list))  
        slurm_gpu_metrics_h100_total.set(sum(h100_total_list))
        slurm_gpu_metrics_l4_total.set(sum(l4_total_list))
        # Sleep for 30 sec
        time.sleep(30)

