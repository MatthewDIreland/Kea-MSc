###############################################################################
# Cross Reference
###############################################################################

# This script adds the correct (adjusted) times to the Timelapse data so that photos in Timelapse can be ordered by the correct times.
# It also adds various other important columns

import sys
import csv
from pathlib import Path

input_csv1 = sys.argv[1] # TimelapseData.csv (Timelapse output)
input_csv2 = sys.argv[2] # AssignedSessions.csv
output_csv = sys.argv[3] # AnalysisData.csv

data_list = []
with open(input_csv1, 'r', newline='') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        data_list.append(row)

AI_confidence = len([row for row in data_list if row[1].startswith("Max")]) > 0

cross_ref_dict = dict()
with open(input_csv2, 'r', newline='') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        first_photo = row[1]
        if AI_confidence:
            max_photo = row[2]
            ai_tag = row[3]
            real_start_time_nzst = row[5]
            session_duration = row[7]
        else:
            max_photo = "NA"
            ai_tag = "NA"
            real_start_time_nzst = row[5]
            session_duration = row[7]
        copied_file = row[9]
        cross_ref_dict[copied_file] = (ai_tag, first_photo, max_photo, real_start_time_nzst, session_duration)
        copied_file = row[10]
        cross_ref_dict[copied_file] = (ai_tag, first_photo, max_photo, real_start_time_nzst, session_duration)

i = 1
source = "?"
for row in data_list:
    if i == 1:
        row.append("AI_tag")
        row.append("PhotoSource")
        row.append("OriginalFile")
        row.append("FirstPhotoNZST")
        row.append("SortingColumn")
        row.append("SessionDurationSeconds")
    else:
        copied_file = row[2] + "\\" + row[1]
        if row[1].startswith("FirstSessionPhotos"):
            ai_tag, first_photo, max_photo, real_start_time_nzst, session_duration = cross_ref_dict[copied_file]
            original_photo = first_photo
            source = "First"
        elif row[1].startswith("MaxSessionPhotos"):
            ai_tag, first_photo, max_photo, real_start_time_nzst, session_duration = cross_ref_dict[copied_file]
            original_photo = max_photo
            source = "Max"
        else:
            original_photo = "unknown"
            real_start_time_nzst = "NA"
            source = "?"
            ai_tag = "NA"
            session_duration = "NA"
        row.append(ai_tag)
        row.append(source)
        row.append(original_photo)
        row.append(real_start_time_nzst)
        row.append(real_start_time_nzst + " " + source)
        row.append(session_duration)
    i += 1

with open(output_csv, mode='w', newline='') as file:
    writer = csv.writer(file)  # Create a CSV writer
    for row in data_list:
        writer.writerow(row)


