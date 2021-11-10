# -*- coding: utf-8 -*-
"""

Description :
    Synchronization of folders with logging at file and console

@author: Panagiotis Nikolaou

call example:
    python Task2.py --sourceDir C:/Users/Panos/Desktop/original --destinationDir C:/Users/Panos/Desktop/temp --interval 10 --logDir C:/Users/Panos/Desktop/log.txt

"""

import os
import shutil
import logging
import time
import sys
import argparse

# define the command parameters
parser = argparse.ArgumentParser(description='My script')
parser.add_argument('--sourceDir', help="Source folder")
parser.add_argument('--destinationDir', help="Destination folder")
parser.add_argument('--interval', type=int, help="Time interval")
parser.add_argument('--logDir', help="Log file")
args = parser.parse_args(sys.argv[1:])
srcDir = args.sourceDir
dstDir = args.destinationDir
interval = args.interval
logDir = args.logDir

# import logging
logging.root.handlers = []
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO, filename=logDir)

# create logger
logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to console_handler
console_handler.setFormatter(formatter)

# add console_handler to logger
logger.addHandler(console_handler)

# set up logging to console
console = logging.StreamHandler(sys.stdout)

console.setLevel(logging.ERROR)

# set a format which is simpler for console use
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# 'application' code
logger.debug('debug message')
logger.info('info message')
logger.warning('warn message')
logger.error('error message')
logger.critical('critical message')


def get_list_of_files(dir_name: str) -> list:
    # create a list of file and sub directories 
    # names in the given directory 
    list_of_files = os.listdir(dir_name)
    all_files = list()
    # Iterate over all the entries
    for entry in list_of_files:
        # Create full path
        full_path = os.path.join(dir_name, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(full_path):
            all_files = all_files + get_list_of_files(full_path)
        else:
            all_files.append(full_path)

    return all_files


def update() -> None:
    source_directory = srcDir
    before = dict([(f, None) for f in get_list_of_files(source_directory)])
    while 1:
        time.sleep(int(interval))
        after = dict([(f, None) for f in get_list_of_files(source_directory)])
        added = [f for f in after if not f in before]
        removed = [f for f in before if not f in after]
        if added:
            logger.info(f"Created: {added}")
            sync()
        if removed:
            logger.info(f"Removed: {removed}")
            sync()
        before = after


def sync() -> None:
    try:
        logger.info("Begin sync")
        check_if_root_dirs_exist(srcDir, dstDir)
        sync_dirs(srcDir, dstDir)
        sync_files(srcDir, dstDir)
        logger.info("End sync with success")
    except Exception as e:
        logger.error(e)
        logger.error("End sync with failure!")


def check_if_root_dirs_exist(root_dir_src: str, root_dir_dst: str) -> None:
    if not os.path.exists(root_dir_src) and not os.path.isdir(root_dir_src):
        raise Exception(root_dir_src + " doesn't exist")
    if not os.path.exists(root_dir_dst) and not os.path.isdir(root_dir_dst):
        raise Exception(root_dir_dst + " doesn't exist")


def sync_dirs(root_dir_src: str, root_dir_dst: str) -> None:
    for root1, dirs1, files1 in os.walk(root_dir_src):
        for relative_path_src in dirs1:
            full_path_src = os.path.join(root1, relative_path_src)
            full_path_dst = full_path_src.replace(root_dir_src, root_dir_dst)
            if os.path.exists(full_path_dst) and os.path.isdir(full_path_dst):
                continue
            if os.path.exists(full_path_dst) and os.path.isfile(full_path_dst):
                raise Exception("Cannot perform dir sync." + str(full_path_dst) + " should be a dir, not a file!")
            # Case 1 : dest dir does not exit
            shutil.copytree(full_path_src, full_path_dst)
            logging.info(f"Directory {str(full_path_dst)} copied from {str(full_path_src)}")
            continue
    for root2, dirs2, files2 in os.walk(root_dir_dst):
        for relative_path_dst in dirs2:
            full_path_dst = os.path.join(root2, relative_path_dst)
            full_path_src = full_path_dst.replace(root_dir_dst, root_dir_src)
            if os.path.exists(full_path_src) and os.path.isdir(full_path_src):
                continue
            if os.path.exists(full_path_src) and os.path.isfile(full_path_src):
                raise Exception("Cannot perform dir sync." + str(full_path_src) + " should be a dir, not a file!")
            # Case 3 : destination dir exists but not src dir, so we need to copy it
            shutil.rmtree(full_path_dst)
            logging.info(f"Directory {str(full_path_dst)} removed")
            continue


def sync_files(root_dir_src: str, root_dir_dst: str) -> None:
    for root1, dirs1, files1 in os.walk(root_dir_src):
        for file1 in files1:
            full_path_src = os.path.join(root1, file1)
            full_path_dst = full_path_src.replace(root_dir_src, root_dir_dst)
            # Case 1 : the file does not exist in destination dir
            if not os.path.exists(full_path_dst):
                shutil.copy2(full_path_src, full_path_dst)
                logging.info(f"File {str(full_path_dst)} copied from {str(full_path_src)}")
                continue
            # Case 2 : src file is more recent than destination file
            src_file_last_modification_time = round(os.path.getmtime(full_path_src))
            dst_file_last_modification_time = round(os.path.getmtime(full_path_dst))
            if src_file_last_modification_time > dst_file_last_modification_time:
                os.remove(full_path_dst)
                shutil.copy2(full_path_src, full_path_dst)
                logging.info(f"File {str(full_path_dst)} synchronized from {str(full_path_src)}")
                continue
            # Case 3 : destination file is more recent than src file
            if src_file_last_modification_time < dst_file_last_modification_time:
                os.remove(full_path_src)
                shutil.copy2(full_path_dst, full_path_src)
                logging.info(f"File {str(full_path_src)} synchronized from {str(full_path_dst)}")
                continue
    # Case 4 : file only exists in destination dir but not in src it should be deleted
    for root2, dirs2, files2 in os.walk(root_dir_dst):
        for file2 in files2:
            full_path_dst = os.path.join(root2, file2)
            full_path_src = full_path_dst.replace(root_dir_dst, root_dir_src)
            if os.path.exists(full_path_src):
                continue
            os.remove(full_path_dst)
            logging.info(f"File {str(full_path_src)} removed from {str(full_path_dst)}")


if __name__ == '__main__':
    # check the parameters from command line
    args = sys.argv
    try:
        check_srcDir = args[1]
        check_dstDir = args[2]
        check_interval = args[3]
        check_logDir = args[4]
    except IndexError:
        print("No correct parameters have been included")
        exit()
    # sync directories and files
    sync()
    # wait for changes in folders
    update()
