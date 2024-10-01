#!/usr/bin/env python3
import subprocess
from datetime import datetime, timedelta
import os
import math
from prometheus_client import start_http_server, Gauge
import time
import statistics
import json


# below are fields that I want to grab from the gpu stats output 

#gpus,index,name,temperature.gpu,power.draw,memory.used,memory.total,processes[]
# this script will grab all active users on the cluster and check to see if 

# the list of partiitons with gpus to filter
gpu_partitions="a3,a3dev,a3high,a3low,a3mixed,a3mixedlow,g2dev" #partitions with gpus 

#    gpu_util = gpu['utilization.gpu']
#    gpu_mem = gpu['memory.used']
#    gpu_mem_total = gpu['memory.total'] 
#    gpu_temp = gpu['temperature.gpu']
#    gpu_power = gpu['power.draw']
#    gpu_name = gpu['name']

prometheus_label_list = ["user", "partition", "node", "jobid", "gpu_num", "gpu_name", "gpu_util", "gpu_used_mem", "gpu_total_mem","gpu_temp", "gpu_power"]


def get_slurm_running_users_on_gpu_partitions():
    command = f"squeue -p {gpu_partitions} -t r -o %u -h | sort -u"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
        raise Exception(f"Error executing command: {error}")
    return output.decode("utf-8").splitlines()


def get_slurm_running_users():
    command = f"squeue -t r -o %u -h | sort -u"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
        raise Exception(f"Error executing command: {error}")
    return output.decode("utf-8").splitlines()


def get_slurm_node_list(user):
    command = f"squeue -u {user} -t r -o %N -h"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
        raise Exception(f"Error executing command: {error}")
    return output.decode("utf-8").splitlines()

def get_slurm_node_list_on_gpu_partitions(user):
    command = f"squeue -p {gpu_partitions} -u {user} -t r -o %N -h"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
        raise Exception(f"Error executing command: {error}")
    return output.decode("utf-8").splitlines()


def get_slurm_node_list(user):
    command = f"squeue -u {user} -t r -o %N -h"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
        raise Exception(f"Error executing command: {error}")
    return output.decode("utf-8").splitlines()



def filter_node_list_with_scontrol_and_return_list(nodes):
    command = f"scontrol show node {nodes} | grep NodeName | cut -d ' ' -f 1 | sed 's/NodeName=//g'"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
        raise Exception(f"Error executing command: {error}")
    return output.decode("utf-8").splitlines()      


def grab_gpu_stats_from_node_ssh(node):
    command = f"ssh -T {node} /opt/conda/bin/gpustat --json"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
        raise Exception(f"Error executing command: {error}")
    return json.loads(output.decode("utf-8"))

def tmp_grab_gpu_stats_from_node_ssh(node):
    filtered_gpu_metric_object = {}
    gpu_metric_object = {}
    command = f"sudo -u clusteradmin ssh -T {node} /opt/conda/bin/gpustat --json"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
        raise Exception(f"Error executing command: {error}")
    return json.loads(output.decode("utf-8"))



def g_to_int_string(number):
    return f"G{number}"



def parse_slurm_node_list(squeue_piped_list):
    parsed_list = []
    for line in squeue_piped_list:
        node, partition, jobid = line.split('|')
        parsed_list.append({
            'nodes': node,
            'partition': partition,
            'jobid': jobid
        })
    return parsed_list


def get_slurm_node_list_on_gpu_partitions(user):
    command = f"squeue -p {gpu_partitions} -u {user} -t r -o '%N|%P|%i' -h"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
        raise Exception(f"Error executing command: {error}")
    return parse_slurm_node_list(output.decode("utf-8").splitlines())



def get_parsed_slurm_node_list(user, partition):
    node_list = get_slurm_node_list_on_gpu_partitions(user, partition)
    return parse_slurm_node_list(node_list)




#my_gpu_node_object = tmp_grab_gpu_stats_from_node_ssh('dojo-a3-ghpc-16')
#
#gpus_obj_list = my_gpu_node_object['gpus']
#
#for gpu in gpus_obj_list:
#    gpu_index = gpu['index']
#    gpu_util = gpu['utilization.gpu']
#    gpu_mem = gpu['memory.used']
#    gpu_mem_total = gpu['memory.total'] 
#    gpu_temp = gpu['temperature.gpu']
#    gpu_power = gpu['power.draw']
#    gpu_name = gpu['name']
#    print(gpu_index)
#    print(gpu_name)
#    print(gpu_util)
#    print(gpu_mem)
#    print(gpu_mem_total)
#    print(gpu_temp)
#    print(gpu_power)
#
#
#
#
#
#
#for _user in active_gpu_slurm_users:
#    _squeue_list = get_slurm_node_list_on_gpu_partitions(_user)
#    for _job_info_list in _squeue_list:
#        _node_list = filter_node_list_with_scontrol_and_return_list(_job_info_list['nodes'])
#        print(_user)
#        print(_job_info_list)
#        print(_node_list)
#        for _node in _node_list:
#            _gpu_stats = tmp_grab_gpu_stats_from_node_ssh(_node)
#            #print(_gpu_stats)
#            for gpu in _gpu_stats['gpus']:
#                gpu_index = gpu['index']
#                gpu_util = gpu['utilization.gpu']
#                gpu_mem = gpu['memory.used']
#                gpu_mem_total = gpu['memory.total'] 
#                gpu_temp = gpu['temperature.gpu']
#                gpu_power = gpu['power.draw']
#                gpu_name = gpu['name']
#                print(gpu_index)
#                print(gpu_name)
#                print(gpu_util)
#                print(gpu_mem)
#                print(gpu_mem_total)
#                print(gpu_temp)
#                print(gpu_power)
#





if __name__ == '__main__':

    user_gpu_utilization_metrics = Gauge('user_gpu_utilization_metrics', 'GPU utilization metrics for a user running jobs on the cluster', labelnames=prometheus_label_list)
    #file_system_utilization_data = Gauge('file_system_utilization_data', 'File system utilization in percent for /data')

    # Start the Prometheus HTTP server on port 8012
    start_http_server(8012)
    while True:
        active_gpu_slurm_users = get_slurm_running_users_on_gpu_partitions()
        for _user in active_gpu_slurm_users:
            _squeue_list = get_slurm_node_list_on_gpu_partitions(_user)
            for _job_info_list in _squeue_list:
                _node_list = filter_node_list_with_scontrol_and_return_list(_job_info_list['nodes'])
                #print(_user)
                #print(_job_info_list)
                #print(_node_list)
                for _node in _node_list:
                    _gpu_stats = tmp_grab_gpu_stats_from_node_ssh(_node)
                    #print(_gpu_stats)
                    for gpu in _gpu_stats['gpus']:
                        gpu_index = gpu['index']
                        gpu_util = gpu['utilization.gpu']
                        gpu_mem = gpu['memory.used']
                        gpu_mem_total = gpu['memory.total'] 
                        gpu_temp = gpu['temperature.gpu']
                        gpu_power = gpu['power.draw']
                        gpu_name = gpu['name']
                        #print(gpu_index)
                        #print(gpu_name)
                        #print(gpu_util)
                        #print(gpu_mem)
                        #print(gpu_mem_total)
                        #print(gpu_temp)
                        #print(gpu_power)
                        user_gpu_utilization_metrics.labels(user=_user, partition=_job_info_list['partition'], node=_node, jobid=_job_info_list['jobid'], gpu_num=gpu_index, gpu_name=gpu_name, gpu_util=gpu_util, gpu_used_mem=gpu_mem, gpu_total_mem=gpu_mem_total, gpu_temp=gpu_temp, gpu_power=gpu_power).set(gpu_util)
        # Sleep for 30 sec
        time.sleep(30)







