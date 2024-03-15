###############################################################################
# Split Videos
###############################################################################

# Videos cannot be tagged by AI classifiers (at least not those commonly used). So they must be split before running a classifier.
# Videos are also faster to process if scrolling (but not necessarily tagging) though footage manually.
# This code splits all videos into one photo per second, starting with the very first frame of video. 

# RUNTIME INSTRUCTIONS
# This script should be run with two additional arguments after the name of this script on the command line: the full path of the input folder, and the full path of the output file.
# If you are attempting to split long videos and encounter errors you may need to increase OPENCV_FFMPEG_READ_ATTEMPTS. Do this by running "set OPENCV_FFMPEG_READ_ATTEMPTS=X" in command prompt (without quotes), where X is 65536, for example.
# .AVI files are very problematic to process. This code fixes this issue by creating a .MP4 version of each .AVI file in the input folder.

# Imports required packages.
import ijson
import sys
import cv2
import os
from pathlib import Path
import subprocess
import math

# Gets the full paths of the input folder from the command line.
input_folder = sys.argv[1]
overwrite = sys.argv[2]
Count = 0

if overwrite == "y":
    print("Files will be overwritten")
if overwrite == "n":
    print("Files will not be overwritten")

# Defines a function which replaces the last occurance of the substring "old" with the substring "new" in target string
def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

# Defines a function which gets a list of all files in the input folder
def get_file_names(root_folder):
    file_names = []
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            file_names.append(os.path.join(root, file))
    return file_names

# Gets a list of all files in the input folder
file_names = get_file_names(input_folder)
for file in file_names:
    BaseName = os.path.basename(file)
    BaseNameUpper = BaseName.upper()
    ParentFolder = Path(file).parent.absolute()
    
    # Makes an .MP4 version of .AVI files
    if BaseNameUpper.endswith(".AVI"):
        output_file_path = file + ".MP4"
        try: 
            subprocess.run(["ffmpeg.exe", "-i", file, "-q:v", "1", "-c:a", "aac", "-c:v", "mpeg4", "-b:v", "100K", output_file_path])
            file = output_file_path
            BaseNameUpper = output_file_path.upper()
            BaseName = os.path.basename(file)
            ParentFolder = Path(file).parent.absolute()
        except Exception as e:
            print(e)
            continue
        
    if BaseNameUpper.endswith(".MP4") or BaseNameUpper.endswith(".MOV"):
        try: 
            Count = Count + 1
            print(file)
            print(Count)
            cap = cv2.VideoCapture(file)
            # Get the frames per second (fps) of the input video.
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps == 0:
                continue
            # Get the total number of frames in the video.
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            # print(str(math.floor((total_frames) / fps)))
            # Calculate the duration of the video in seconds.
            # This code is correct. Note well - do not alter it.
            duration = math.floor((total_frames - 1) / fps) + 1
            for second in range(duration):
                # Set the frame position based on the current second.
                frame_pos = int(second * fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                # Read the frame.
                ret, frame = cap.read()
                output_folder = f'{ParentFolder}_frames'
                BaseNameMod = rreplace(BaseName, ".", "_", 1)
                output_file_path = f'{ParentFolder}_frames/{BaseNameMod}_frame_{second + 1}.jpg'
                if os.path.exists(output_file_path) and overwrite == "n":
                    continue
                os.makedirs(output_folder, exist_ok = True)
                cv2.imwrite(output_file_path, frame)
            cap.release()
        except Exception as e:
            print(e)
print("Done!")