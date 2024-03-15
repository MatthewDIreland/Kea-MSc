###############################################################################
# Fnd Suspicious Dates
###############################################################################

# This code finds all camera runs that have a difference between the earliest and last photo taken of 100 or more days.
# As burrow cameras usually have thier batteries checked around a month basis, a duration of 100 is definitely suspicious.
# Any cameras runs found by this script must be checked manually to see if the dates on them are legitimate
# Illegitamate dates often occur at the start or end of a camera run when field works are adjusting the date. 


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
        
# Find suspicious dates
burrow_run_days = []
burrow_run_list = sorted(list(set([str(Path(row[c_filename]).parent.parent) for row in data_list])))
date_format = "%Y:%m:%d %H:%M:%S"
for burrow_run in burrow_run_list:
    print(burrow_run)
    mini_list = [row for row in data_list if str(Path(row[c_filename]).parent.parent) == burrow_run]
    mini_list = sorted(mini_list, key=lambda x: x[c_date])
    start_date = datetime.strptime(mini_list[0][c_date], date_format).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = datetime.strptime(mini_list[len(mini_list) - 1][c_date], date_format).replace(hour=0, minute=0, second=0, microsecond=0)
    day_difference = (end_date - start_date).days
    if abs(day_difference) > 100:
        print(burrow_run, day_difference, start_date, end_date)
        burrow_run_days.append((burrow_run, day_difference, start_date, end_date))

# Write output csv
with open(output_csv, mode='w', newline='') as file:
    writer = csv.writer(file)  # Creates a CSV writer
    writer.writerow(("Burrow Run", "Day difference", "Start date", "End date"))
    writer.writerows(burrow_run_days)
