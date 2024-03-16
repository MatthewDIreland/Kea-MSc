###############################################################################
# Score Colour
###############################################################################

#### no results from corrupted files (empty files)
#### ignore certain folders (autolure, unknown date folders) AUTOLURE UNKNOWN 
#### would be nice if it could flag lonely folders also


# This script calculates the average amount of colour per pixel in a crop of the top right of images.
# This script takes a crop to speed up processing. If you find this script's results inaccurate you 
# could change the size/shape/position of the crop (or use the entirety of each image).
# This script only calculates color scores for the first image in each 5 minute block in each monitoring run to speed up processing.

# Trail cameras usually record the time an image or video was taken in that file's metadata, as well as in a watermark added to the image or video itself. 
# However sometimes this information is incorrect (time information set incorrectly or reset due to a camera malfunction). 
# When manually tagging images, incorrect times can be found when images clearly taken at night (trail cameras take greyscale footage in the dark)
#  have watermarks suggesting the sun in up. This code sums up the absolute differences between B and G values and G and R values for each pixel 
# in a crop of each image; B G and R are exactly equal in truly grey pixels.

# RUNTIME INSTRUCTIONS
# This script should be run with two arguments after the name of this script on the command line: the full path of the folder to score the 
# colour of images inside, and the name of the output .csv file. 

# Imports required packages.
import os
import numpy as np
import sys
from pathlib import Path
from PIL import Image
import re
import ffmpeg
from datetime import datetime
import shutil
# from PIL import ExifTags

# Gets the full paths of the input folder and output file from the command line.
input_folder = sys.argv[1]
output_file = sys.argv[2]
output_folder = sys.argv[3]

start_time = datetime.now()
Count = 0
minutes_floor_previous = -1
hour_previous = -1
folder_previous = "unmatchable?"

def colour_score(image_object, image_path):
    try:
        box = (0, 0, 100, 10)
        # this crops the images from the top left corner, which avoids counting pixels of the watermark,
        # which (for some reason) are not greyscale, even though most appear so. This cropping also speeds up 
        # the code considerably, so much  that Image.open becomes the major bottleneck
        sampled_region = image_object.crop(box)
        image = np.array(sampled_region)
        h, w, c = image.shape
        pixel_count = float(h*w)
        image = image.astype(np.int16)
        differences = np.diff(image, axis=2)
        differences = np.absolute(differences)
        return differences.sum()/pixel_count
    except Exception as e:
        print(e, "Corrupted file: " + image_path)
        return 'NA'

# if os.path.exists(output_file):
#     raise Exception("Output file already exists, will not overwrite it.")
def get_file_names(root_folder):
    file_names = []
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            file_names.append(os.path.join(root, file))
    return file_names

# Checks if a folder belongs to a parent folder which has no other children folders
def get_lonely_status(child_folder_path):
    parent_folder_path = os.path.dirname(child_folder_path)
    parent_folder_contents = os.listdir(parent_folder_path)
    folders_in_parent = [item for item in parent_folder_contents if os.path.isdir(os.path.join(parent_folder_path, item))]
    return len(folders_in_parent) == 1

bad_files = []
lonely_dict = dict()
file_names = get_file_names(input_folder)
file_names = [file for file in file_names if file.upper().endswith(".JPG")]
file_names = [file for file in file_names if "AUTOLURE" not in file]
file_names = [file for file in file_names if "UNKNOWN" not in file]
file_count = len(file_names)
print(file_count,".jpg files found.")

with open(output_file, "w", buffering = 100000) as o:
    o.write("SourceFile,TimeSource,CreateDate,ColourScore,LonelyFolder\n")
    for file in file_names:
        Count = Count + 1
        time_source = "NA"
        if Count%200 == 0:
            print(str(100*Count//file_count) + "%... ", flush=True, end='')
        base_name = os.path.basename(file)
        base_name_upper = base_name.upper()
        folder = Path(file).parent.absolute()

        # This method using Image.open from Pillow is slightly faster than using imread from cv2
        try:
            image_object = Image.open(file)
        except Exception as e:
            print("Cannot open file, is probably corrupted", e)
            bad_files.append(file)
            mod_time = os.path.getmtime(file)
            create_date = str(datetime.fromtimestamp(mod_time))
            time_source = "Photo modify date, can't open file"
            continue
        # DateTime = 306 (when a conforming app last modified the image or its metadata. Most apps do not update it (contrary to the exif standard)
        # DateTimeOriginal = 36867 (when the shutter fired, this is what we are interested in)
        # DateTimeDigitized = 36868 (when the image finished conversion from analog to digital)
        
        exif_info = image_object._getexif()
        if(exif_info is None):
            # Reconstruct parent video path        
            if(base_name_upper.endswith("_FRAME_1.JPG")):
                video_folder_name = str(folder).replace("_frames", "")
                base_name_no_extension = os.path.splitext(base_name)[0]
                video_base_name = base_name_no_extension.replace("_frame_1", "")
                # Changes the "_" to a "."
                video_base_name = re.sub(r'_(?=[^_]*$)', '.', video_base_name)
                #print(video_base_name)
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
            else:
                # .JPG file has no exif info and is not a file from a split video so skip this iteration as it is useless.
                continue
        else:         
            create_date = str(exif_info.get(36867, None))
            if create_date is None:
                print(file, "is missing a create date")
                mod_time = os.path.getmtime(file)
                create_date = str(datetime.fromtimestamp(mod_time))
                time_source = "Photo modify date"
            else: 
                time_source = "Photo metadata"
        
        time_of_day = datetime.strptime(create_date, "%Y:%m:%d %H:%M:%S").time()
        hour = time_of_day.hour
        minutes = time_of_day.minute
        minutes_floor = minutes - minutes%5
        if minutes_floor != minutes_floor_previous or hour != hour_previous or folder != folder_previous:
            o.write(file + ",")
            o.write(time_source + ",")
            o.write(create_date + ",")
            o.write(str(colour_score(image_object, file)) + ",")
            lonely_status = lonely_dict.get(folder)
            if lonely_status is None:
                lonely_status = get_lonely_status(folder)
                lonely_dict[folder] = lonely_status
            o.write(str(lonely_status))
            o.write("\n")
            minutes_floor_previous = minutes_floor
            hour_previous = hour
            folder_previous = folder

end_time = datetime.now()
time_elapsed = end_time - start_time

print("\nTime elapsed:",  "{:.2f}".format(time_elapsed.total_seconds()), "seconds")
print("Processed", Count, "images")
print("Images processed per second:", "{:.2f}".format(Count/time_elapsed.total_seconds()))
print("Time taken per image:", "{:.5f}".format(time_elapsed.total_seconds()/Count), "seconds")

os.makedirs(output_folder, exist_ok = True)
print("Copying " + str(len(bad_files)) + " bad files...")
i = 0
for file in bad_files:
    if i % 100 == 0:
        print(str(i)) 
    i += 1
    shutil.copy2(file, output_folder + "/" + str(i) + "_" + os.path.basename(file))
