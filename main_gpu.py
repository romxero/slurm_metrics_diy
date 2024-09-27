#!/usr/bin/env python3
import subprocess
import json

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
    print(node)
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
        print(num_gpus, num_gpus_used, state, features)    
        return num_gpus, num_gpus_used, state, features
    else:
        return 0, 0, "unknown", "unknown"




node_list = get_list_of_nodes()

for node in node_list:
    num_gpus, num_gpus_used, state, features = get_node_object(node)


