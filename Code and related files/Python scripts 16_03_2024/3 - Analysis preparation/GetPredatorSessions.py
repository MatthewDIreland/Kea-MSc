###############################################################################
# Get Predator Sessions
###############################################################################
# Note that this script is currently set to extract only max session photos - to change this see later comment

import csv
import os
import random
import shutil
import sys
import string

input_csv1 = sys.argv[1] # ImageDataCorrectedDateTimes.csv
input_csv2 = sys.argv[2] # AssignedSessions.csv
input_csv3 = sys.argv[3] # NEW_ALL_DATA_TAGGING.csv (Timelapse output with added columns)
output_base = sys.argv[4] # base folder for copied images

print("reading")
image_table = []
with open(input_csv1, 'r', newline='') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        image_table.append(row)
header = image_table[0] # Split header off data list
image_table = image_table[1:]

c_timeSeconds = 5
c_run = 6

print("sorting")
image_table = sorted(image_table, key=lambda x: x[c_timeSeconds])
image_table = sorted(image_table, key=lambda x: x[c_run])


print("Loading session data CSV...")
session_table = []
with open(input_csv2, 'r', newline='') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        session_table.append(row)
session_table = session_table[1:] # drop header
session_c_FirstPhotoCopy = 9

session_dict = dict()
for row in session_table:
    first_photo_copy = row[session_c_FirstPhotoCopy];
    first_photo_pos = first_photo_copy.find("FirstSessionPhotos_")
    if first_photo_pos != -1:
        session_id = int(first_photo_copy[first_photo_pos:].split("_")[1])
        session_dict[session_id] = row

session_c_FirstFile = 1
session_c_MaxFile = 2
session_c_PhotosInSession = 8
session_c_SessionImageNames = 11
session_id = 1
image_index = 0
total_images_in_all_sessions = 0

for row in session_table:
    first_session_file = row[session_c_FirstFile]
    max_session_file = row[session_c_MaxFile]
    images_in_session = int(row[session_c_PhotosInSession])
    print("session", session_id, "has", images_in_session, "images", "starting at ImageData.csv row", image_index + 2)
    image_file_names = []
    total_images_in_all_sessions += images_in_session
    i = images_in_session
    while i > 0:
        image_file_name = image_table[image_index][0]
        image_file_names.append(image_file_name)
        image_index += 1
        i -= 1
    row.append(image_file_names) # at index session_c_SessionImageNames
    if len(image_file_names) != images_in_session:
        raise Exception("file count mismatch for session", session_id, "PhotosInSession", images_in_session, "LengthOfList", len(image_file_names))
    if not (first_session_file in image_file_names):
        raise Exception("first_session_file missing from image_file_names for session", session_id)
    if not (max_session_file in image_file_names):
        raise Exception("max_session_file missing from image_file_names for session", session_id)
    session_id += 1

print("total images in all sessions:", total_images_in_all_sessions)

print("Loading analysis data CSV...")
analysis_table = []
with open(input_csv3, 'r', newline='') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        analysis_table.append(row)

analysis_c_File = 1
analysis_c_Animal = 5

random.seed(42)
# Swap the below lines depending on whether you want to extract first or max sessions photos
# analysis_rows = [row for row in analysis_table if row[analysis_c_File].startswith("FirstSessionPhotos_") and row[analysis_c_Animal] == "empty"]
animal_list = ["cat", "rat", "stoat", "possum", "mouse", "weka"]

for animal in animal_list:
    #all rows
    #all rows in 1 remove to be only animal
    #all rows in 2 remove to be only animal
    #add rows together

    analysis_rows = [row for row in analysis_table if (row[analysis_c_File].startswith("MaxSessionPhotos_") or row[analysis_c_File].startswith("FirstSessionPhotos_")) and row[analysis_c_Animal] == animal]
   #Filter analysis rows to remoe duplicates #canot do as the names not hte same here cos therse are the name of ccopies

    # Use a list comprehension to filter out sublists with duplicate values at index 2
    unique_values = set()
    filtered_list = [sublist for sublist in analysis_rows if sublist[2] not in unique_values and not unique_values.add(sublist[2])]

    # sample_size = min(100, len(analysis_rows))
    # print("Selecting " + str(sample_size) + " random sessions...")
    analysis_session_ids = [int(row[analysis_c_File].split("_")[1]) for row in analysis_rows]
    # random_sample_list_of_session_ids = random.sample(analysis_session_ids, len(analysis_rows)) #len(amalysisrows?)
    # random_sample_list_of_session_ids.sort()
    random_sample_list_of_session_ids = analysis_session_ids.sort()
    print("Random Session IDs", random_sample_list_of_session_ids)
    random_sample_set_of_session_ids = set(random_sample_list_of_session_ids)
    random_sample_of_analysis_rows = [row for row in analysis_rows if int(row[analysis_c_File].split("_")[1]) in random_sample_set_of_session_ids]
    random_sample_of_analysis_rows.sort(key=lambda x: int(row[analysis_c_File].split("_")[1]))

    total_images_to_copy = 0
    for analysis_row in random_sample_of_analysis_rows:
        session_id = int(analysis_row[analysis_c_File].split("_")[1])
        # session_row = session_table[session_id - 1]
        session_row = session_dict.get(session_id)
        if session_row is None:
            # continue
            raise Exception("Cannot find session", session_id)
        # print("--------------------------------------------------")
        # print("analysis_row", analysis_row)
        # print("    session_id", session_id)
        # print("    session_row", session_row)
        image_file_names = session_row[session_c_SessionImageNames]
        session_images_to_copy = len(image_file_names)
        total_images_to_copy += session_images_to_copy
    print("number of images to copy:", total_images_to_copy)

    correlation_list = []
    empty_sessions_folder = output_base + "\\EmptySessions"
    os.makedirs(empty_sessions_folder, exist_ok = True)
    print("first session to copy:", random_sample_of_analysis_rows[0])
    for analysis_row in random_sample_of_analysis_rows:
        session_id = int(analysis_row[analysis_c_File].split("_")[1])
        # session_row = session_table[session_id - 1]
        session_row = session_dict.get(session_id)
        if session_row is None:
            # continue
            raise Exception("Cannot find session", session_id)
        # print("--------------------------------------------------")
        # print("analysis_row", analysis_row)
        # print("    session_id", session_id)
        # print("    session_row", session_row)
        image_file_names = session_row[session_c_SessionImageNames]
        # print("image_file_names:", image_file_names)
        session_images_to_copy = len(image_file_names)
        print("session", session_id, "has", session_images_to_copy, "images to copy")
        empty_session_folder = output_base + "\\EmptySessions\\" + str(session_id)
        os.makedirs(empty_session_folder, exist_ok = True)
        i = 0
        for image_file in image_file_names:
            print("image_file:", image_file)
            i += 1
            characters = string.ascii_letters + string.digits  # You can customize this if you want specific characters
            random_string = ''.join(random.choice(characters) for _ in range(6))

            copy_to_file = empty_session_folder + "\\" + str(i) + "_" + string + "_" + os.path.basename(image_file)
            print("   copy to:", copy_to_file)
            correlation_list.append((copy_to_file, image_file))
            shutil.copy2(image_file, copy_to_file)

    correlation_file = output_base + "\\EmptySessions\\correlation.csv"
    with open(correlation_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(("EmptySessionImage", "OriginalImageFile"))
        for row in correlation_list:
            writer.writerow(row)



