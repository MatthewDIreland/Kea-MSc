###############################################################################
# Assign Sessions
###############################################################################

# This code takes an input .csv which contains filepaths and associated species tags 
# and groups photos into sessions of animal activity. 
# It also makes folders containing samples of photos for tagging, plusas two folders 
# each containing on image per session: using either the maximum AI confidence tag of a session
# to select a photo to represent it, or the first photo of a session.

from datetime import datetime, timedelta
from pathlib import Path
from PIL import Image # pip install pillow
import csv
import ffmpeg # pip install ffmpeg-python
import os
import re
import sys
import shutil
import random

# Processing command line options
input_csv1 = sys.argv[1]
input_csv2 = sys.argv[2]
output_csv1 = sys.argv[4] 
output_csv2 = sys.argv[5] 

# Daylight savings table
year2017 = ("2016:09:25 02:00:00", "2017:04:02 03:00:00")
year2018 = ("2017:09:24 02:00:00", "2018:04:01 03:00:00")
year2019 = ("2018:09:30 02:00:00", "2019:04:07 03:00:00")
year2020 = ("2019:09:29 02:00:00", "2020:04:05 03:00:00")
year2021 = ("2020:09:27 02:00:00", "2021:04:04 03:00:00")
year2022 = ("2021:09:26 02:00:00", "2022:04:03 03:00:00")
year2023 = ("2022:09:25 02:00:00", "2023:04:02 03:00:00")
year2024 = ("2023:09:24 02:00:00", "2024:04:07 03:00:00")
daylight_savings_ranges = [year2017, year2018, year2019, year2020, year2022, year2023, year2024]

# Define a function to convert datetimes to seconds
epoch = datetime(2000, 1, 1)
def date_to_seconds(date_str):
    try:
        date_format = "%Y:%m:%d %H:%M:%S"
        date_object = datetime.strptime(date_str, date_format)
        seconds = (date_object - epoch).total_seconds()
        return int(seconds)
    except ValueError:
        date_format = "%Y-%m-%d %H:%M:%S"
        date_object = datetime.strptime(date_str, date_format)
        seconds = (date_object - epoch).total_seconds()
        return int(seconds)
    
# Define a function to convert seconds to datetimes
def seconds_to_date(seconds):
    base_date = datetime(2000, 1, 1)
    target_date = base_date + timedelta(seconds=seconds)
    return target_date.strftime("%Y:%m:%d %H:%M:%S")

# Define a function which converts dates of run footage into New Zealand Standard Time
def to_nz_standard_time(date_string, date_of_first_photo_in_run):
    x = [row for row in daylight_savings_ranges if date_of_first_photo_in_run >= row[0] and date_of_first_photo_in_run <= row[1]]
    if len(x) > 0:
        #print("x is", x)
        #print("converting", date_string, "cos this photo...", date_of_first_photo_in_run)
        date = datetime.strptime(date_string, "%Y:%m:%d %H:%M:%S")
        date = date - timedelta(hours=1)
        date_string = date.strftime("%Y:%m:%d %H:%M:%S")
        #print("converted to ", date_string)
    return date_string

###############################################################################
# These loops import classification and alignment data.
###############################################################################

print("Importing classifiation and alignment data...")

data_list = []
with open(input_csv1, 'r', newline='') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        data_list.append(row)
header = data_list[0] # Split header off data list
data_list = data_list[1:]
columns = len(header)

if columns == 3:
    AI_confidence = True
    c_fileName = 0
    c_species = 1
    c_confidence = 2
    c_dateTime = 3
    c_timeSource = 4
    c_timeSeconds = 5
    c_run = 6
elif columns == 1:
    AI_confidence = False
    c_fileName = 0
    c_dateTime = 1
    c_timeSource = 2
    c_timeSeconds = 3
    c_run = 4
else:
    print("Expected one column or three columns, not", columns, "(see instructions.txt for help).")
    sys.exit(1)

# Import alignment data
alignment_dict = {}
with open(input_csv2, 'r', newline='') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        folder = os.path.dirname(row[0])
        alignment_dict[folder] = int(row[1])

###############################################################################
# This loop extracts time metadata and adds it to a new column.
###############################################################################

print("Extracting time metadata and adding it to a new column...")

list_length = len(data_list)
for r in range(0, list_length):
    if r % 1000 == 0:
        print(str(r) + "...")
    file = data_list[r][0] # Reconstruct path
    base_name = os.path.basename(file)
    base_name_upper = base_name.upper()
    try:
        image_object = Image.open(file)
    except Exception as e:
        print("Cannot open file, it's probably corrupted", e)
        mod_time = os.path.getmtime(file)
        create_date = str(datetime.fromtimestamp(mod_time))
        time_source = "Photo modify date, can't open file"
        data_list[r].append(create_date)
        data_list[r].append(time_source)
        continue
    exif_info = image_object._getexif()
    if exif_info is None:
        # If path ends with _frames reconstruct path video path
        if "_FRAME_" in base_name_upper: 
            folder = data_list[r][0][:data_list[r][0].rfind('\\')]
            video_folder_name = str(folder).replace("_frames", "")
            base_name_no_extension = os.path.splitext(base_name)[0]
            video_base_name = base_name_no_extension.split("_frame_", 1)[0]
            video_base_name = re.sub(r'_(?=[^_]*$)', '.', video_base_name) # Changes the "_" to a "."
            video_path = video_folder_name + "\\" + video_base_name
            try:
                video_metadata = ffmpeg.probe(video_path)['streams']
                create_date = video_metadata[0]["tags"]["creation_time"]
                time_source = "Parent video metadata"
            except Exception as e:
                if ".AVI" in video_path.upper(): # If working off frames split out of .MP4 versions of .AVI file make the file path point to .AVI files.
                    video_path = video_path[:-4]
                mod_time = os.path.getmtime(video_path)
                create_date = str(datetime.fromtimestamp(mod_time))
                time_source = "Parent video modify date"
            create_date = create_date[0:19]
            create_date = create_date.replace("-", ":")
            create_date = create_date.replace("T", " ")
            data_list[r].append(create_date)
            data_list[r].append(time_source)
        else: # .JPG file has no exif info and is not a file from a split video.
            data_list[r].append("NA") 
            data_list[r].append("No time found") 
            continue # Skip this iteration as there is no time information to be gained (at least that I know of).
    else:         
        create_date = str(exif_info.get(36867, None))
        if create_date is None:
            print(file, "is missing a create date")
            mod_time = os.path.getmtime(file)
            create_date = str(datetime.fromtimestamp(mod_time))
            time_source = "Photo modify date"
        else: 
            time_source = "Photo metadata"
        data_list[r].append(create_date)
        data_list[r].append(time_source)

###############################################################################
# This loop makes a new column with dates converted to seconds.
###############################################################################

print("Making a new column with dates converted to seconds...")
        
list_length = len(data_list)
for r in range(0, list_length):
    folder = os.path.dirname(data_list[r][0])
    adjustment = alignment_dict.get(folder, 0)
    seconds = date_to_seconds(data_list[r][c_dateTime]) + adjustment
    file_name = data_list[r][c_fileName]
    frame_position = file_name.find("_frame_")
    if frame_position != -1:
        frame_position += 7
        no = int(file_name[frame_position : len(file_name) - 4])
        seconds += no - 1
    data_list[r].append(seconds)
    data_list[r][c_dateTime] = seconds_to_date(seconds)

##############################################################################
# This loop labels all photos and videos with the monitoring runs they're in.
##############################################################################

print("Labelling all photos and videos with the monitoring runs they're in...")

run = 1

list_length = len(data_list)
for r in range(0, list_length):
    # Prevent overflow error
    if r == list_length - 1:
        data_list[r].append(run)
        break
    if Path(data_list[r][c_fileName]).parent.parent.absolute() == Path(data_list[r + 1][c_fileName]).parent.parent.absolute():
        data_list[r].append(run)
    else:
        data_list[r].append(run)
        run += 1

data_list = sorted(data_list, key=lambda x: x[c_timeSeconds])
data_list = sorted(data_list, key=lambda x: x[c_run])

###############################################################################
# This loop assigns photos to sessions.
###############################################################################

print("Assigning photos to sessions...")

cutoff_time = 840
first_file = "?"
max_confidence = -1.0
max_species = "?"
max_file = "?"
total_photos = 0
start_time = data_list[0][c_timeSeconds]
date_first_photo_in_run = data_list[0][c_dateTime]
session_list = []
session_photo_list = []
        
output_list = []

list_length = len(data_list)
for r in range(0, list_length):
    if AI_confidence:
        species = data_list[r][c_species]
        species_confidence = float(data_list[r][c_confidence])
    current_run = data_list[r][c_run]
    current_time = data_list[r][c_timeSeconds]
    current_date_new = to_nz_standard_time(seconds_to_date(current_time), date_first_photo_in_run)
    data_list[r].append(current_date_new)
    current_photo = data_list[r][c_fileName]
    session_photo_list.append(current_photo)
    total_photos += 1
    if AI_confidence:
        if species_confidence > max_confidence:
            max_confidence = species_confidence
            max_species = species
            max_file = data_list[r][c_fileName]
    if first_file == "?":
        first_file = data_list[r][c_fileName]
    if r == len(data_list) - 1:
        end_time = current_time
        start_date_new = to_nz_standard_time(seconds_to_date(start_time), date_first_photo_in_run)
        end_date_new = to_nz_standard_time(seconds_to_date(end_time), date_first_photo_in_run)
        session_seconds = end_time - start_time
        if AI_confidence:
            output_row = [current_run, first_file, max_file, max_species, max_confidence, start_date_new, end_date_new, session_seconds, total_photos]
        else:
            output_row = [current_run, first_file, start_date_new, end_date_new, session_seconds, total_photos]
        output_list.append(output_row)
        session_list.append(session_photo_list)
        break
    next_run = data_list[r + 1][c_run]
    next_time = data_list[r + 1][c_timeSeconds]
    if next_time > current_time + cutoff_time or next_run != current_run:
        end_time = current_time
        start_date_new = to_nz_standard_time(seconds_to_date(start_time), date_first_photo_in_run)
        end_date_new = to_nz_standard_time(seconds_to_date(end_time), date_first_photo_in_run)
        session_seconds = end_time - start_time 
        if AI_confidence:
            output_row = [current_run, first_file, max_file, max_species, max_confidence, start_date_new, end_date_new, session_seconds, total_photos]
        else:
            output_row = [current_run, first_file, start_date_new, end_date_new, session_seconds, total_photos]
        output_list.append(output_row)
        session_list.append(session_photo_list)
        session_photo_list = []
        start_time = next_time
        first_file = "?"
        max_confidence = -1.0
        max_species = "?"
        max_file = "?"
        total_photos = 0
    if next_run != current_run:
        date_first_photo_in_run = data_list[r + 1][c_dateTime]

###############################################################################
# Write copy of input file with adjusted/corrected date/time information.
###############################################################################

print("Writing " + output_csv1)

header.append("FileDateTime")
header.append("TimeSource")
header.append("TimeInSeconds")
header.append("Run")
header.append("DateTimeNZST")

with open(output_csv1, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    for row in data_list:
        writer.writerow(row)

###############################################################################
# These loops copy the selected files into folder(s) for manual tagging.
###############################################################################

destination_folder = "SessionFirstAndMax"

i = 0 
prefix = "FirstSessionPhotos"
print("Copying the photos selected by the first in each session into a folder for manual tagging...")
for row in output_list:
    i += 1
    if i % 1000 == 0:
        print(str(i) + "...")
    file_path = row[1]
    file_name = os.path.basename(file_path)
    internal_or_external = os.path.basename(Path(file_path).parent.parent.parent.absolute())
    if internal_or_external != "INTERNAL":
        internal_or_external = "EXTERNAL"
    directories = file_path.split(os.path.sep)
    burrow_year = directories[3]
    new_folder_path = destination_folder + "\\" + burrow_year + "\\" + internal_or_external
    new_file_path = new_folder_path + "\\" + prefix + "_" + str(i) + "_" + file_name
    row.append(new_file_path)
    os.makedirs(new_folder_path, exist_ok = True)
    shutil.copy2(file_path, new_file_path)

if AI_confidence:
    print("Copying the photos selected using AI information (highest confidence) into a folder for manual tagging...")
    i = 0 
    prefix = "MaxSessionPhotos"
    print("Copying max in session photos")
    for row in output_list:
        i += 1
        if i % 1000 == 0:
            print(str(i) + "...")
        file_path = row[2]
        file_name = os.path.basename(file_path)
        internal_or_external = os.path.basename(Path(file_path).parent.parent.parent.absolute())
        if internal_or_external != "INTERNAL":
            internal_or_external = "EXTERNAL"
        directories = file_path.split(os.path.sep)
        burrow_year = directories[3]
        new_folder_path = destination_folder + "\\" + burrow_year + "\\" + internal_or_external
        new_file_path = new_folder_path + "\\" + prefix + "_" + str(i) + "_" + file_name
        row.append(new_file_path)
        os.makedirs(new_folder_path, exist_ok = True)
        shutil.copy2(file_path, new_file_path)

###############################################################################
# This loop copies all photos in a sample of sessions into a folder for manual tagging
###############################################################################

print("Copying all photos in a sample of sessions into a folder for manual tagging...")

random.seed(42)
sample_size = min(100, len(session_list))
random_sessions = random.sample(session_list, sample_size)
s = 0
for session_photos in random_sessions:   
    s += 1
    i = 0 
    for file_path in session_photos:
        i += 1
        file_name = os.path.basename(file_path)
        destination_folder = "SampleSessions/" + str(s)
        new_file_path = destination_folder + "/" + str(i) + "_" + file_name
        os.makedirs(destination_folder, exist_ok = True)
        shutil.copy2(file_path, new_file_path)   

###############################################################################
# This loop copies a sample of photos, broken down by AI tag (if possible) into a folder for manual tagging.
###############################################################################

# random.seed(42)
# if AI_confidence:
#     print("Copying a sample of photos, broken down by AI tag into a folder for manual tagging...")
#     species_list = [row[c_species] for row in data_list]
#     species_set = set(species_list)
#     for species in species_set:
#         species_rows = [row for row in data_list if row[c_species] == species]
#         sample_size = min(100, len(species_rows))
#         random_photos = random.sample(species_rows, sample_size)
#         i = 0    
#         for row in random_photos:
#             i += 1
#             file_path = row[0]
#             file_name = os.path.basename(file_path)
#             destination_folder = "SamplePhotos/" + species
#             new_file_path = destination_folder + "/" + str(i) + "_" + file_name
#             os.makedirs(destination_folder, exist_ok = True)
#             shutil.copy2(file_path, new_file_path)

###############################################################################
# Write session output file.
###############################################################################

print("Writing session data...")

if AI_confidence:
    session_header = ["Run", "FirstFile", "MaxFile", "MaxSpecies", "MaxConfidence", "SessionStartTime", "SessionEndTime", "SessionSeconds", "PhotosInSession", "FirstPhotoCopy", "MaxPhotoCopy"]
else:   
    session_header = ["Run", "FirstFile", "SessionStartTime", "SessionEndTime", "SessionSeconds", "PhotosInSession", "FirstPhotoCopy"]

with open(output_csv2, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(session_header)
    for row in output_list:
        writer.writerow(row)
print("Done!")
