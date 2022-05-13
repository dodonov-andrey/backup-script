import argparse
import time
import shutil
import os
import logging


def get_files_list(path, ignore_ios_files=True):
    result = []
    for root, _, files in os.walk(path):
        if ignore_ios_files:
            files = [f for f in files if not f.startswith(".")]
        
        for f in files:
            # remove root for future comparison
            file_path = os.path.join(root, f).replace(path, "")
            
            result.append(file_path)
    return result


def synchronize_folders(source, destination):
    source_files_set = set(get_files_list(source))
    replica_files_set = set(get_files_list(destination))
    # make XOR operation for getting difference
    diff_files_set = source_files_set ^ replica_files_set
    
    for f in diff_files_set:
        # return root paths after comparison
        src_file = source + f
        dest_file = destination + f
        
        #  add file to replica folder if it exist in source
        if f in source_files_set:
            try:
                shutil.copy2(src_file, dest_file)
            except IOError:
                os.makedirs(os.path.dirname(dest_file))
                shutil.copy2(src_file, dest_file)
            
            logging.info(dest_file + " CREATED")
        # remove file from replica if it does not exist in source
        else:
            os.remove(dest_file)
            
            logging.info(dest_file + " REMOVED")


def validate_arguments(arguments):
    validation = True
    
    if not os.path.exists(arguments.source_folder):
        print("Provided source folder " + arguments.source_folder + " does not exist")
        validation = False
    
    if not arguments.log_file_path.endswith(".log"):
        print("Incorrect log file name: " + arguments.log_file_path)
        print("Log file should have .log extension")
        validation = False
    try:
        int(arguments.backup_interval)
    except ValueError:
        print("Provided interval " + arguments.backup_interval + " is not integer")
        validation = False
    
    if not validation:
        exit()


def parse_arguments():
    parser = argparse.ArgumentParser(description="This script make replication of source folder to replica folder")
    
    parser.add_argument("-s", "--source_folder", help="Path to source folder", required=True)
    parser.add_argument("-r", "--replica_folder", help="Path to replica folder", required=True)
    parser.add_argument("-i", "--backup_interval", help="Backup interval in seconds, should be integer", required=True)
    parser.add_argument("-l", "--log_file_path", help="Optional. Path to log file, should have .log extension. "
                                                      "Default value - replica.log", default="replica.log")
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    validate_arguments(args)
    logging.basicConfig(
                        format="%(asctime)s %(message)s",
                        level=logging.INFO,
                        datefmt="%d/%m/%Y %H:%M",
                        handlers=[logging.FileHandler(args.log_file_path), logging.StreamHandler()])
    
    while True:
        synchronize_folders(args.source_folder, args.replica_folder)
        time.sleep(int(args.backup_interval))
