#!/usr/bin/env python3

import subprocess, sys
import argparse



'''
OPS445 Assignment 2
Program: duim.py 
Author: Yasir Ahmad
The python code in this file (duim.py) is original work written by
Yasir Ahmad. No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: Assignment2-VersionB

Date:2024/12/08 
'''

def parse_command_args():
    """
    Set up argparse for command-line arguments.

    Returns:
        Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="DU Improved -- See Disk Usage Report with bar charts",
                                     epilog="Copyright 2023")
    parser.add_argument("-l", "--length", type=int, default=20,
                        help="Specify the length of the graph. Default is 20.")
    parser.add_argument("-H", "--human-readable", action="store_true",
                        help="Display sizes in human-readable format (e.g., MiB, GiB).")
    parser.add_argument("target", nargs="?", help="Target directory to analyze.")
    return parser.parse_args()



def percent_to_graph(percent: int, total_chars: int) -> str:
    "returns a string: eg. '##  ' for 50 if total_chars == 4"
    """
    Convert a percentage into a bar graph string of specified total characters.

    Args:
        percent (int): The percentage value (0-100).
        total_chars (int): The total number of characters for the graph.

    Returns:
        str: Bar graph string composed of '=' for filled and ' ' for empty spaces.
    """
    if not (0 <= percent <= 100):
        raise ValueError("Percent must be between 0 and 100.")

    filled_chars = round((percent / 100) * total_chars)
    return '=' * filled_chars + ' ' * (total_chars - filled_chars)


def call_du_sub(location: str) -> list:
    "use subprocess to call `du -d 1 + location`, rtrn raw list"

    """
    Use subprocess to call `du -d 1 <location>` and return the raw list.

    Args:
        location (str): Target directory to check disk usage.

    Returns:
        list: List of strings containing the output of `du -d 1`.
    """
    try:
        process = subprocess.Popen(
            ['du', '-d', '1', location],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            error_lines = stderr.strip().split('\n')
            permission_errors = [line for line in error_lines if 'Permission denied' in line]
        if permission_errors:
            print("Warning: Permission denied for some directories. Skipping them.")


        # Clean the output
        return stdout.strip().split('\n')
    except Exception as e:
        print(f"Error: {e}")
        return []



def create_dir_dict(raw_dat: list) -> dict:
    """
    Convert raw 'du' data into a dictionary of directories and sizes.

    Args:
        raw_dat (list): List of strings from `call_du_sub`.

    Returns:
        dict: Dictionary with directory names as keys and sizes as values.
    """
    dir_dict = {}
    for entry in raw_dat:
        try:
            size, directory = entry.split(maxsplit=1)  # Split size and directory
            dir_dict[directory] = int(size)  # Convert size to integer
        except ValueError:
            continue  # Skip invalid entries
    return dir_dict



def bytes_to_human_r(kibibytes: int, decimal_places: int=2) -> str:
    "turn 1,024 into 1 MiB, for example"
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']  # iB indicates 1024
    suf_count = 0
    result = kibibytes 
    while result > 1024 and suf_count < len(suffixes):
        result /= 1024
        suf_count += 1
    str_result = f'{result:.{decimal_places}f} '
    str_result += suffixes[suf_count]
    return str_result

if __name__ == "__main__":
    args = parse_command_args()
    target_directory = args.target
    graph_length = args.length
    human_readable = args.human_readable

    try:
        # Validate the target directory
        if not os.path.isdir(target_directory):
            print(f"Error: {target_directory} is not a valid directory.")
            sys.exit(1)

        # Call call_du_sub to get raw data
        raw_data = call_du_sub(target_directory)

        # Debugging step: Print raw data
        print("Raw Data:", raw_data)

        # Call create_dir_dict to process the raw data
        dir_dict = create_dir_dict(raw_data)

        # Debugging step: Print directory dictionary
        print("Directory Dictionary:", dir_dict)

        # Calculate the total size for percentages
        total_size = sum(dir_dict.values())

        # Print the disk usage report
        print(f"{'Directory':<40} {'Size':>10} {'Usage':<}")
        for directory, size in dir_dict.items():
            # Convert size to human-readable if -H is specified
            size_display = bytes_to_human_r(size) if human_readable else f"{size} KiB"

            # Calculate percentage and generate graph
            percent = (size / total_size) * 100
            graph = percent_to_graph(percent, graph_length)

            # Print the formatted row
            print(f"{directory:<40} {size_display:>10} {graph:<}")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)



