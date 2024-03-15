###############################################################################
# Get Monitoring Effort 
###############################################################################

# This script calculates the total number of days of monitoring of each burrow season, broken down by month

#Get monitoring effort
import sys
import csv
from datetime import datetime, timedelta
from pathlib import Path

# Import master data
input_csv = sys.argv[1] ### ImageDataCorrectedDateTimes.csv
output_csv = sys.argv[2]

data_list = []
with open(input_csv, 'r', newline='') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        data_list.append(row)
   
c_filename = 0
c_date = 7

# Split header off data list to add back after processing
header = data_list[0:1]
data_list = data_list[1:]

# Fix times
for row in data_list:
    replace = row[c_date].replace("-", ":")
    if row[c_date] != replace:
        print("altering", row[c_date], "to", replace)
        row[c_date] = replace

burrow_year_days = []
for camera in ["internal","external","combined"]:
    if camera  == "external":
        sub_list = [row for row in data_list if row[c_filename].find("INTERNAL") == -1]
    elif camera == "internal":
        sub_list = [row for row in data_list if row[c_filename].find("INTERNAL") != -1]
    else:
        sub_list = data_list
    # Assign camera runs
    burrow_run_days = []
    burrow_run_list = sorted(list(set([str(Path(row[c_filename]).parent.parent) for row in sub_list])))
    date_format = "%Y:%m:%d %H:%M:%S"
    for burrow_run in burrow_run_list:
        print(camera, burrow_run)
        mini_list = [row for row in sub_list if str(Path(row[c_filename]).parent.parent) == burrow_run]
        mini_list = sorted(mini_list, key=lambda x: x[c_date])
        # drop_list = [row for row in mini_list if row[c_date][5:10] == "01:01"]
        # if len(drop_list) > 0:
        #     drop_first = drop_list[0]   
        #     print("dropping", len(drop_list), "rows from", drop_first[c_date], "of", burrow_run)
        # mini_list = [row for row in mini_list if row[c_date][5:10] != "01:01"]
        start_date = datetime.strptime(mini_list[0][c_date], date_format).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = datetime.strptime(mini_list[len(mini_list) - 1][c_date], date_format).replace(hour=0, minute=0, second=0, microsecond=0)
        burrow_run_days.append((burrow_run, start_date, end_date))

  #########################################################porblem###
    burrow_year_list = sorted(list(set(['\\'.join(row[0].split('\\')[:4]) for row in burrow_run_days])))
    for burrow_year in burrow_year_list: ##################porblem2
        mini_list = [row for row in burrow_run_days if '\\'.join(row[0].split('\\')[:4]) == burrow_year]
        for month in range(1,13):
            days_in_month = 0
            for row in mini_list:
                start_date, end_date = row[1], row[2]
                d = start_date
                while d <= end_date:
                    if d.month == month:
                        days_in_month += 1
                    d = d + timedelta(days=1)
            burrow_year_days.append((camera, burrow_year, month, days_in_month))

# Write output csv
with open(output_csv, mode='w', newline='') as file:
    writer = csv.writer(file)  # Creates a CSV writer
    writer.writerow(("Camera", "Burrow year", "Month", "Days"))
    writer.writerows(burrow_year_days)


# # Fix nesting of internal
# for row in data_list:
#     if row[c_filename].find("INTERNAL") != -1:
#         print("altering", row[c_filename])
#         row[c_filename] = str(Path(row[c_filename]).parent)
#         print("altered to", row[c_filename])
