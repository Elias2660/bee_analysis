#!/usr/bin/python3

# This Python code creates the counts.csv needed by the make_csv.py script.
# It runs ffprobe to count all the frames in a directory of h264 files, using 
# the parallel program to run ffprobe 60 copies at a time.
# It then cleans up the output of parallel to get a csv files of file, framecount
# to get a counts.csv file 

# Author: R. P. Marin

import sys 
import os
import subprocess

parallel_command = [  "/research/projects/grail/rmartin/bin/parallel","--jobs","60","--results","pcounts.csv","ffprobe","-v","error","-select_streams","v:0","-count_frames","-show_entries","stream=nb_read_frames","-of","csv=p=0",":::" ]

cleanup_shell_cmd = "awk -F, '{printf(\"%s,%s\\n\",$10,$11)} ' < pcounts.csv  | sed 's/V1/filename/g' | sed 's/Stdout/frames/g' | sed 's/\",\"/XYZ/g' | sed s/,//g | egrep 'frames|h264' | sed 's/\"//g' | sed 's/XYZ/,/g' | sed 's/frames/,frames/' > counts.csv"

def main():
    if len(sys.argv) == 2:
        dir = sys.argv[1]
    else:
        dir = "."

    # cd to the current directory 
    try:
        os.chdir(dir)
    except OSError as e:
        print(f"Error: {e}")

    # get a list of all the video files
    h264_files = [f for f in os.listdir() if f.endswith('.h264')]
    # append the list to the parallel command args
    
    for filename in h264_files:
        parallel_command.append(filename)

    print ("about to run ffprobe in parallel: ", parallel_command)
    # run the parallel command 
    process = subprocess.Popen(parallel_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # Decode the output and split it into lines
    parallel_output = stdout.decode('utf-8').splitlines()

    # run the cleanup command to generate the counts.csv that holds the frame count for each file
    print("about to run:", cleanup_shell_cmd)
    cleanup_result = subprocess.run(cleanup_shell_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    cleanup_output = cleanup_result.stdout.decode('utf-8')

# run the main program 
if __name__ == "__main__":
    main()

