###############################################################################
# Update Folders
###############################################################################

# This code moves files in specifc folders up one level, and appends the name of the folder they were in to the end of their file name.
# When manually tagging images, it's useful to be able to go through all photos or videos taken by a single camera in a monitoring run in time order. 
# However, trail cameras will split images taken in a single monitoring run into subfolders when more than 9999 images have been taken.
# The nth image in each subfolder will be named identically. 
# If images are moved to a folder already containing images with the same name (in Windows) they (if not overwritten) will have (1) or 
# (2) etc. appended to their name. But as images are (usually) ordered left to right alphabetically, this does not result in images being arranged in time taken.

# RUNTIME INSTRUCTIONS
# This script should be run with an additional argument after the name of this script on the command line: the full path of the root folder
# (the folder that contains all folder that have SUBFOLDERS containing IMAGES to be pooled into a single folders)

# Imports required packages.
import os
import csv
import sys

# Gets the root folder from the command line.
root_folder = sys.argv[1]

# Defines a function which replaces the last occurrence of a specified character with another specified character.
def replace_last(input_string, x, y):
    if x not in input_string:
        return input_string
    last_occurrence_index = input_string.rfind(x)
    new_string = input_string[:last_occurrence_index] + y + input_string[last_occurrence_index + len(x):]
    return new_string

# Defines a function which gets all files names in a specified folder.
def get_directory_names(root_folder):
    directory_names = []
    for root, dirs, files in os.walk(root_folder):
        for directory in dirs:
            directory_names.append(os.path.join(root, directory))
    return directory_names

# Defines a function which writes all names in a list to a .csv file
def write_to_csv(directory_names, csv_filename):
    with open(csv_filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Directory Name'])  # Write header
        for directory_name in directory_names:
            csv_writer.writerow([directory_name])

directory_names = get_directory_names(root_folder)
censused_names = []

# This removes all folders from the folder list except those ending with the common extensions 
# used when cameras split photos or videos in a monitoring run into subfolders.
for item in directory_names:
    if item.endswith("BTCF") or item.endswith("IMAGE") or item.endswith("EK113"):
        censused_names.append(item)

# Pooled all items into folders
for item in censused_names:
    for original_path in os.listdir(item):
        original_path = item + "\\" + original_path
        newpath = replace_last(original_path, "\\", "_")
        print("Will move " + original_path + " to " + newpath)
        os.rename(original_path, newpath)