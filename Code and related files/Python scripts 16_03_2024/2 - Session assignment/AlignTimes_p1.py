###############################################################################
# Align Times Part One
###############################################################################

# This code is the first of two scripts that aligns times. It takes an input .csv 
# which contains paired rows of photos taken at the same time and calculates the values
# by which the times in photos taken by different cameras in the same run need to be adjusted
# to have the times aligned. It outputs a csv file which must be manually reviewed, adding
# a coloumn where one subfolder in each run will be assigned the value "TRUE" as the standard 
# photos shoudl be aligned by, and the others set to "FALSE". This script outputs two .csv files 
# but only the second is needed.

import csv
import sys
import os
from pathlib import Path
from datetime import datetime
import numpy as np
from PIL import Image
import re
import ffmpeg

# Define a function to convert dates to seconds
def date_to_seconds(date_str):
    try:
        date_format = "%Y:%m:%d %H:%M:%S"
        date_object = datetime.strptime(date_str, date_format)
        seconds = (date_object - datetime(2000, 1, 1)).total_seconds()
        return int(seconds)
    except ValueError:
        return None

# Import .csv file
input_csv = sys.argv[1]
output_csv1 = sys.argv[2]
output_csv2 = sys.argv[3]
# output_csv3 = sys.argv[4]

data_list = []
with open(input_csv, 'r', newline='') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        data_list.append(row)

# Split header off data list to add back after processing
header = data_list[0]
data_list = data_list[1:]
list_length = len(data_list)

# Define a function which converts time to seconds
def time_to_seconds(time_string):
    # Convert the time string to a datetime object
    time_format = "%Y:%m:%d %H:%M:%S"
    datetime_object = datetime.strptime(time_string, time_format)
    seconds = (datetime_object - datetime(1970, 1, 1)).total_seconds()
    return round(seconds, 0)

# Go through labelling imaages
# Loop down the list 
##############################################################################
for r in range(0, list_length):
    # print(r)
# Extract time metadata then put it into a new row
# Reconstruct path
    if data_list[r][2] == "TRUE":
        # print(r + 2)
        file = data_list[r][0] + "\\" + data_list[r][1] + "\\" + data_list[r][3]
        # print(file)
    # If path ends with _frames recronstruct path video path
        # Get the frame number subtract one and add it to the time
        base_name = os.path.basename(file)
        base_name_upper = base_name.upper()
        try:
            image_object = Image.open(file)
        except Exception as e:
            print("Cannot open file, is probably corrupted")
            # print(e)
            continue
        exif_info = image_object._getexif()
        if(exif_info is None):
            # Reconstruct parent video path        
            if "_FRAME_" in base_name_upper:
                folder = data_list[r][0] + "\\" + data_list[r][1]
                video_folder_name = str(folder).replace("_frames", "")
                base_name_no_extension = os.path.splitext(base_name)[0]
                video_base_name = base_name_no_extension.split("_frame_", 1)[0]
                # Changes the "_" to a "."
                video_base_name = re.sub(r'_(?=[^_]*$)', '.', video_base_name)
                # print(video_base_name)
                video_path = video_folder_name + "\\" + video_base_name
                # print(video_folder_name)
                # print(base_name_no_extension)
                # print(video_base_name)
                # print(video_path)
                #get metadata for that video
                try:
                    video_metadata = ffmpeg.probe(video_path)['streams']
                    # video_metadata = subprocess.run(["ffprobe.exe", video_path])
                    # print(video_metadata)
                    create_date = video_metadata[0]["tags"]["creation_time"]
                    time_source = "Parent video metadata"
                except Exception as e:
                    # print(video_path, e, "This error may be due to missing date/time information")
                    # Make the file path points to .AVI files if working off frames split out of .MP4 versions of .AVI files. 
                    if ".AVI" in video_path.upper():
                        video_path = video_path[:-4]
                    mod_time = os.path.getmtime(video_path)
                    create_date = str(datetime.fromtimestamp(mod_time))
                    time_source = "Parent video modify date"
                create_date = create_date[0:19]
                create_date = create_date.replace("-", ":")
                create_date = create_date.replace("T", " ")
                data_list[r].append(create_date)
                data_list[r].append(time_source)
            else:
                # .JPG file has no exif info and is not a file from a split video so skip this iteration as it is useless.
                data_list[r].append("NO TIME")
                continue
        else:         
            create_date = str(exif_info.get(36867, None))
            if create_date is None:
                print(file, "is missing a create date")
                mod_time = os.path.getmtime(video_path)
                create_date = str(datetime.datetime.fromtimestamp(mod_time))
                time_source = "Photo modify date"
            else: 
                time_source = "Photo metadata"
            data_list[r].append(create_date)
            data_list[r].append(time_source)

# data_list.insert(0, header)
# Export .csv file
# Open the file for writing with 'newline' parameter to prevent extra blank lines
# with open(output_csv3, mode='w', newline='') as file:
#     writer = csv.writer(file)  # Create a CSV writer
#     for row in data_list:
#         writer.writerow(row)
# # Write output csv

# This code reorders the dataframe into the proper format for the next loop
i = 0
second_list = []
run_count = 1
while i < len(data_list):
    if data_list[i][2] == "TRUE":
        # print(data_list[i][1])
        run_folder1 = data_list[i][0] + "\\" + data_list[i][1] 
        run_folder2 = data_list[i + 1][0] + "\\" + data_list[i + 1][1]
        file_path1 = run_folder1 + "\\" + data_list[i][3]
        file_path2 = run_folder2 + "\\" + data_list[i + 1][3]
        # These offsets need to have the times in the photos in each folder added to them
        offset1 = int(data_list[i][4]) + int(date_to_seconds(data_list[i][5]))
        offset2 = int(data_list[i+1][4]) + int(date_to_seconds(data_list[i+1][5]))
        # print("hello", i, offset1, offset2, offset2-offset1)
        # #debugging
        # if offset1 == offset2:
        #     print("something sus at row:", i)
        output_row = [run_count, file_path1, offset1, file_path2, offset2, run_folder1, run_folder2]
        second_list.append(output_row)
        if i + 2 < len(data_list) and data_list[i][0] != data_list[i+2][0]:
            run_count += 1
        i += 1
    i += 1


# Define a function to solve the alignment of all the subfolders in a folder
# Calculate offset between A and the first match with A (call it B)
# Repeat this until there are no more matched with A
# Now do the same thing with B, this is possible now we have a new value for B, which is it's offset from A
# Repeat until all folders in run have been processed.
def solve_alignment(in_list, reference_folder, secs_diff = 0, level = 1):
    debug = reference_folder.find("E:\\Kahurangi\\2021-2022\\Nest1~Cobb nest\\Cavity1a~Sam Creek cavity\\H 15_10_2021_to_22_10_2021") != -1
    # print("Reference folder", reference_folder)
    # print("Reference time", reference_time)
    # print("Level", level)
    out_list = []
    if debug:
        print("Level", level, "\nList", len(in_list), in_list, "\n", "reference_folder", reference_folder, "\n")
    if len(in_list) == 0:
        return(out_list)
    for r in range(0, len(in_list)):
        # print("r", r)
        # print("Inlist r", in_list[r])
        filepath1 = in_list[r][1]
        filepath2 = in_list[r][3]
        runfolder1 = in_list[r][5]
        runfolder2 = in_list[r][6]
        if level == 1 and r == 0:
            out_list.append([filepath1, 0])
        # print(in_list[r])
        if debug:
            print("Level", level, "r", r, "seconds difference", secs_diff, "\nrunfolder1", runfolder1, "\nrunfolder2", runfolder2, "\nref folder", reference_folder)
        if runfolder1 == reference_folder or runfolder2 == reference_folder:
            # If the values are the wrong way around swap them so that the correct letter and time is first
            if runfolder2 == reference_folder:
                in_list[r][1:3], in_list[r][3:5], in_list[r][5], in_list[r][6] = in_list[r][3:5], in_list[r][1:3], in_list[r][6], in_list[r][5]
                # print("flipped")
                filepath1, filepath2 = filepath2, filepath1
                runfolder1, runfolder2 = runfolder2, runfolder1
            # Calculate time difference from reference
            # e.g. if A is the referece then is A - B

            # In non-recursive second loop if reference time is from the same folder 
            # as old reference time then change reference time to be new value of current folder
            # if #this is the second or more time around the loop:
            reference_time = int(in_list[r][2])
            new_diff = reference_time - int(in_list[r][4]) + secs_diff
            if debug:
                print("Level", level, "difference to write or CARRY", new_diff, "r:", r, "\n")
        # print("differernce:", new_diff, "reference time:", reference_time, "subtract_time:", - int(in_list[r][4]))
            # Write results to difflist
            result = [filepath2, new_diff] 
            out_list.append(result)
            # Set values for next iteration
            # Set the new reference folder to be the folder that was just compared to the previous reference folder
            new_reference_folder = runfolder2
            # Set the time to be the new time with the time difference from the old reference folder added to it
            # print("reference_time", reference_time)
            # print("minus", int(in_list[r][4]))
            # Remove reference folder from new list and call function recursively
            out_list.extend(solve_alignment([item for item in in_list if reference_folder not in item], new_reference_folder, new_diff, level + 1))     
    return out_list


# Loop through "second list", splitting it into chunks to call solve_alignment on.
i = 0
block_start = 0
block_end = 0
data_all = []
while i < len(second_list):
    # print("i is:", i, second_list[i])
    # If parent folder is the same then add one to block end and start again and increment i
    if (second_list[i][0] == second_list[block_start][0]):
        i += 1
        block_end = i
        if block_end != len(second_list):
            continue
    # If parent folder is different call solve alignment
    subfolder = second_list[block_start][5]
    data = solve_alignment(second_list[block_start: block_end], subfolder)
    data_all.extend(data)
    block_start = block_end
    i = block_start

# Loop over data, adding run information:
run_no = 1
i = 0
while i < len(data_all):
    print(data_all[i])
    # break if reached the end of the data
    if i + 1 == len(data_all):
        data_all[i].append(run_no)
        break
    # Declare variables to be the folder path in row indices i and i + 1
    run_folder1 = data_all[i][0][:data_all[i][0].rfind("\\")]
    run_folder1 = run_folder1[:run_folder1.rfind("\\")]
    print("run no", run_no, "folder1", run_folder1)
    run_folder2 = data_all[i+1][0][:data_all[i+1][0].rfind("\\")]
    run_folder2 = run_folder2[:run_folder2.rfind("\\")]
    print("run no", run_no, "folder2", run_folder1)

    data_all[i].append(run_no)
    # If run folders are different dont increment run_no for next iteration
    if run_folder1 != run_folder2:
        run_no += 1
    # increment i
    i += 1

with open(output_csv1, mode='w', newline='') as file:
    writer = csv.writer(file)  # Create a CSV writer
    for row in second_list:
        writer.writerow(row)


# data_list.insert(0, header)
# Export .csv file
# Open the file for writing with 'newline' parameter to prevent extra blank lines
with open(output_csv2, mode='w', newline='') as file:
    writer = csv.writer(file)  # Create a CSV writer
    for row in data_all:
        writer.writerow(row)
# Write output csv
