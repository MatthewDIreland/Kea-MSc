###############################################################################
# Find Duplicates
###############################################################################

# Duplicates can get into footage, and in large datasets findings duplicates manually in infeasible.
# This code finds the paths of any duplicate folders and files in an input folder and writes them to a .txt file.
# While code finds duplicates automatically (removing duplicates must still be done manually).

# RUNTIME INSTRUCTIONS
# This script should be run with an additional argument after the name of this script on the command line: 
# the full path of the folder to look for duplicates inside.

# Imports required packages.
import sys
import os
from pathlib import Path

# Gets the full paths of the input folder and output file from the command line.
input_folder = sys.argv[1]
output_file = sys.argv[2]

TupleList = []
empty_file_list = []
suspicious_file_list = []
duplicate_folder_set = set()
empty_folder_set = set()
duplicate_file_pairs = []
duplicate_Count = 0
content_cache = dict()
skip_set = set()

def get_file_names(root_folder):
    file_names = []
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            file_names.append(os.path.join(root, file))
    return file_names

file_names = get_file_names(input_folder)
file_names = [file for file in file_names if file.upper().endswith(".JPG")]
file_count_1 = len(file_names)
print("Found " + str(file_count_1) + " .JPG files.")

for file in file_names:
    BaseName = os.path.basename(file)
    BaseNameUpper = BaseName.upper()
    ParentFolder = Path(file).parent.absolute()
    FileSize = os.path.getsize(file)
    if FileSize == 0:
        empty_file_list.append(file)
        empty_folder_set.add(ParentFolder)
    elif FileSize < 10000:
        suspicious_file_list.append(file)
    else:
        TupleList.append((file, FileSize, ParentFolder))

file_count_2 = len(TupleList)
print(str(file_count_2) + " .JPG files suitable for processing.")
TupleList.sort(key = lambda x : x[1])
size_map = {}
for tuple in TupleList:
    size_map[tuple[1]] = (0)
for tuple in TupleList:
    size = tuple[1]
    size_map[size] = size_map[size] + 1
sus_map = {key: value for key, value in size_map.items() if value > 1}
sus_map = dict(sorted(sus_map.items(), key=lambda item: item[1], reverse=True))
print(str(len(sus_map)) + " potential duplicate files.")
with open("Gibbely.txt", "wt") as Gobbley:
    # Gobbley.write(str(suspicious_file_list) + "\n")
    Gobbley.write("Potential Duplicate Map" + "\n\n")
    Gobbley.write(str(sus_map) + "\n")

print("Sorting complete, beginning file comparisons")
i = 0
n = len(TupleList)
while (i < n):
    first_pair = TupleList[i]
    first_filename = first_pair[0]
    if (first_filename in skip_set):
        i += 1
        continue
    # if i == 50000:
    #     break
    if i % 500 == 0:
        print(str(100 * i // file_count_2) + "%... ", flush = True, end ='')
    j = 0
    first_tuple_size = TupleList[i][1]
    while (i + j + 1 < n):
        if (first_tuple_size == TupleList[i + j + 1][1]):
            # j is the number of repeats in block (min 0).
            j = j + 1
        else:
            break
    if (j == 0):
        content_cache = dict()
        i += 1
        continue
    k = 1
    
    with open(first_filename, "rb") as file_1:
        # This equates (for .jpg files) to ~20,000*51 pixels.
        file_1.seek(first_tuple_size // 4096 * 2048)
        first_chunk = file_1.read(2048)
    while (k <= j):
        second_pair = TupleList[i + k]
        second_filename = second_pair[0]
        if (second_filename in skip_set):
            k += 1
            continue
        second_chunk = content_cache.get(second_filename)
        if second_chunk is None:
            with open(second_filename, "rb") as file_2:
                file_2.seek(first_tuple_size // 4096 * 2048)
                second_chunk = file_2.read(2048)
            content_cache[second_filename] = second_chunk
        if(first_chunk == second_chunk):
            skip_set.add(second_filename)
            duplicate_Count = duplicate_Count + 1
            first_folder = str(first_pair[2])
            second_folder = str(second_pair[2])
            duplicate_folder_set.add((first_folder, second_folder))
            duplicate_file_pairs.append((first_folder, second_folder, first_filename, second_filename))
        k = k + 1
    i += 1 

duplicate_folder_list = list(duplicate_folder_set)
duplicate_folder_list.sort(key = lambda x : x[0] + x[1]) 
duplicate_file_pairs.sort(key = lambda x : x[0] + x[1] + x[2] + x[3])
duplicate_file_pairs = [(item[2], item[3]) for item in duplicate_file_pairs]
empty_folder_list = list(empty_folder_set)
empty_folder_list.sort()
with open(output_file, "wt") as duplicate_hitlist:
    # List all folders containing duplicates and how many duplicates they contain.
    # List how many files they contain that aren't duplicates.
    duplicate_hitlist.write("In total " + str(file_count_2) + " .JPG files were processed.\n\n")
    duplicate_hitlist.write("Found " + str(duplicate_Count) + " duplicate files and " + str(len(empty_file_list)) + " empty files.\n\n")
    duplicate_hitlist.write(str(len(duplicate_folder_list)) + " folder(s) containing duplicate .JPG files:\n")
    duplicate_hitlist.write("\n".join(str(x) for x in duplicate_folder_list) + "\n\n")
    duplicate_hitlist.write("List of duplicate .JPG files:\n")
    duplicate_hitlist.write("\n".join(str(x) for x in duplicate_file_pairs) + "\n\n")
    duplicate_hitlist.write(str(len(duplicate_folder_list)) + " folder(s) containing empty .JPG files:\n")
    duplicate_hitlist.write("\n".join(str(x) for x in empty_folder_list) + "\n\n")
    duplicate_hitlist.write("List of empty .JPG files:\n")
    duplicate_hitlist.write("\n".join(str(x) for x in empty_file_list) + "\n")
print("Done! - found " + str(duplicate_Count) + " duplicate files.")