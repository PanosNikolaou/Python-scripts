# -*- coding: utf-8 -*-
"""

Description :
    Process monitoring for CPU, memory, open handles
    logging and store to pandas dataframe

@author: Panagiotis Nikolaou

call example:
    python CPU process monitoring.py --launchProcess "C:\Program Files\7-Zip\7zFM.exe" --interval 15

"""

import platform
import psutil
import time
import os
import signal
import pandas as pd
import argparse
import sys


# parse the args from command line
# launch process and time interval should be defined in command line
parser = argparse.ArgumentParser(description='Task 1 script')
parser.add_argument('--launchProcess', help="launch process")
parser.add_argument('--interval', type=int, help="Time interval")
args = parser.parse_args(sys.argv[1:])
launchProcess = args.launchProcess
interval = args.interval
processes_dataFrame_list = pd.DataFrame()


def get_process_details(launch_process: str) -> dict:
    # os detection
    detected_os = platform.system()
    # launch the process
    p = psutil.Popen([launch_process])
    # create a dictionary for process details
    process_details = {}
    # create process object from pid
    launched_process = psutil.Process(pid=p.pid)

    # if it is windows [cpu_usage,wset,private,open_handles]
    if "Windows" in detected_os:
        with launched_process.oneshot():
            # get the cpu percent consumption
            try:
                process_cpu_usage = launched_process.cpu_percent(interval=4)
            except psutil.AccessDenied:
                process_cpu_usage = 0
            # get the working set
            try:
                process_wset = launched_process.memory_info().wset
            except psutil.AccessDenied:
                process_wset = 0
            # get private bytes
            try:
                process_private_bytes = launched_process.memory_info().private
            except psutil.AccessDenied:
                process_private_bytes = 0
            # get open handles
            try:
                process_open_handles = len(launched_process.open_files())
            except psutil.AccessDenied:
                process_open_handles = 0
            # append the process details to the dictionary
            process_details.append({
                'cpu_usage': process_cpu_usage,
                'wset': process_wset,
                'private_bytes': process_private_bytes,
                'open_handles': process_open_handles
            })

            os.kill(p.pid, signal.SIGTERM)

    # if it is Linux [cpu_usage,rss,vms,open_handles]
    if "Linux" in detected_os:

        with launched_process.oneshot():
            # get the cpu percent consumption
            try:
                process_cpu_usage = launched_process.cpu_percent(interval=4)
            except psutil.AccessDenied:
                process_cpu_usage = 0
            # get the rss
            try:
                process_wset = launched_process.memory_info().rss
            except psutil.AccessDenied:
                process_wset = 0
            # get the vms
            try:
                process_private_bytes = launched_process.memory_info().vms
            except psutil.AccessDenied:
                process_private_bytes = 0
            # get the file descriptors
            try:
                process_file_descriptors = len(launched_process.open_files())
            except psutil.AccessDenied:
                process_file_descriptors = 0
            # append the process details to the dictionary
            process_details.append({
                'cpu_usage': process_cpu_usage,
                'rss': process_wset,
                'vms': process_private_bytes,
                'file_descriptors': process_file_descriptors
            })

    # kill the process
    os.kill(p.pid, signal.SIGTERM)

    return process_details


def convert_to_dataframe(processes: dict) -> pd.DataFrame:
    # Convert dictionary to pandas dataframe
    df = pd.DataFrame(processes)
    return df


if __name__ == '__main__':
    # check the parameters from command line
    args = sys.argv
    try:
        check_launchProcess = args[1]
        check_interval = args[2]
    except IndexError:
        print("No correct parameters have been included")
        exit()
    while True:
        # get the details of the process
        process = get_process_details(launchProcess)
        # convert to dataframe
        process_dataframe = convert_to_dataframe(process)
        # appends the measurements for the period to the overall measurements
        processes_dataFrame_list = processes_dataFrame_list.append(process_dataframe)
        # wait for the time interval
        time.sleep(interval)
