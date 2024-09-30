#!/usr/bin/env python3

import subprocess
import json



def get_slurm_running_users():
    command = "squeue -t r -o %u -h | sort -u"
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


def g_to_int_string(number):
    return f"G{number}"




