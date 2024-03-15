###############################################################################
# Align Times Part Two
###############################################################################

# This code is the second of two scripts that aligns times. 
# It takes an output file produced in the first scipt and altered by the user 
# and standardises the offset times in that file by specified folders.

import sys
import csv

# Import .csv file
input_csv = sys.argv[1]
output_csv1 = sys.argv[2]

data_list = []
with open(input_csv, 'r', newline='') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        data_list.append(row)


# Loop down data_list, identifying blocks where the run folder is the same.
# Then get the value in each block that have been chosen in the .csv
# The subtract that value from each value in the block
i = 0
block_start = 0
block_end = 0
while i < len(data_list):
    # print("i is:", i, second_list[i])
    # If parent folder is the same then add one to block end and start again and increment i
    if (data_list[i][2] == data_list[block_start][2]):
        i += 1
        block_end = i
        if block_end != len(data_list):
            continue
    # This loop finds the time to use as a reference in each block
    o = block_start
    selected_offset = 0
    while o < block_end:  
        if(data_list[o][3] == "TRUE"):
            selected_offset = int(data_list[o][1])
        o += 1
    w = block_start
    # Thus loop standardises the offsets 
    while w != block_end:
        print(data_list[w])
        data_list[w][1] = int(data_list[w][1]) - selected_offset
        w += 1
    block_start = block_end
    i = block_start


with open(output_csv1, mode='w', newline='') as file:
    writer = csv.writer(file)  # Create a CSV writer
    for row in data_list:
        writer.writerow(row)




