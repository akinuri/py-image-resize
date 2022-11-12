#region ==================== IMPORT

import os, sys

cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cwd + "\\_modules")

from string_helpers import *
from path import *
from node import *

import shutil

# pip install Pillow
from PIL import Image
from PIL import ImageCms
from PIL.ExifTags import TAGS

from pprint import pprint

import math
import time
import re

import pathlib

#endregion


#region ==================== SETUP

os.system("title %s" % "Image Resizer")
Image.MAX_IMAGE_PIXELS = None
sw_start = time.time()

#endregion


#region ==================== INPUTS

drop_inputs = []

if len(sys.argv) == 0:
    print("This program expects an image file or a folder that contains images.")
    print("Drag and drop images and/or a folder of images on this file.")
    print("")
    input("Program will close.")
    sys.exit()

for arg in sys.argv[1:]:
    drop_inputs.append(Path(arg))

DEFAULT_IMAGE_SIZE = 5000
DEFAULT_IMAGE_QUALITY = 75
MIN_IMAGE_SIZE = 768
MAX_IMAGE_SIZE = 12800

print("Dimensions of the images will be limited to a specific area, a square.")
input_image_size = input("Enter a size in pixels (%d-%d, [%s]): " % (MIN_IMAGE_SIZE, MAX_IMAGE_SIZE, DEFAULT_IMAGE_SIZE))

if input_image_size == "":
    input_image_size = str(DEFAULT_IMAGE_SIZE)

RE_INT = re.compile(r'^([1-9]\d*|0)$')
if re.match(RE_INT, input_image_size) is None:
    print("Invalid value. Enter an integer in the range of %d-%d" % (MIN_IMAGE_SIZE, MAX_IMAGE_SIZE))
    print("")
    input("Program will close.")
    sys.exit()

input_image_size = int(input_image_size)

if (MIN_IMAGE_SIZE <= input_image_size <= MAX_IMAGE_SIZE) is False:
    print("Invalid range. Integer needs to be in the range of %d-%d" % (MIN_IMAGE_SIZE, MAX_IMAGE_SIZE))
    print("")
    input("Program will close.")
    sys.exit()

input_image_quality = input("Enter a quality (10-95, [%s]): " % DEFAULT_IMAGE_QUALITY)

if input_image_quality == "":
    input_image_quality = str(DEFAULT_IMAGE_QUALITY)

if re.match(RE_INT, input_image_quality) is None:
    print("Invalid value. Enter an integer in the range of 10-95")
    print("")
    input("Program will close.")
    sys.exit()

input_image_quality = int(input_image_quality)

if (10 <= input_image_quality <= 95) is False:
    print("Invalid range. Integer needs to be in the range of 10-95")
    print("")
    input("Program will close.")
    sys.exit()

input_convert_jpeg = None
ALLOWED_CONVERT_JPEG_ANSWERS = ["", "y", "yes", "n", "no"]

input_convert_jpeg = input("Do you want to convert to jpeg, if it's not already so? (yes, [no]): ")

if input_convert_jpeg.lower() not in ALLOWED_CONVERT_JPEG_ANSWERS:
    print("Invalid value. Enter yes or no.")
    print("")
    input("Program will close.")
    sys.exit()

input_convert_jpeg = True if input_convert_jpeg.lower() in ["y", "yes"] else False

#endregion


#region ==================== RESIZE

allowed_img_extensions = ["jpg", "jpeg", "bmp", "png", "tif"]

def generate_new_file_name(file):
    name = file.name + " (%dpx, %dqty)" % (input_image_size, input_image_quality)
    path = file.get_parent_path().path + file.sep + name + "." + file.extension
    return name, path

def generate_new_folder_name(folder):
    name = folder.name + " (%dpx, %dqty)" % (input_image_size, input_image_quality)
    path = folder.get_parent_path().path + folder.sep + name
    return name, path

def resize_image(image_node, target_img_path):
    
    if input_convert_jpeg:
        target_img_path = target_img_path.get_parent_path().path + target_img_path.sep + target_img_path.name + ".jpg"
    else:
        target_img_path = target_img_path.path
    
    img = Image.open(image_node.path)
    
    orientation = None
    exif = img.getexif()
    for tag_id in exif:
        tag = TAGS.get(tag_id, tag_id)
        if tag == "Orientation":
            orientation = exif.get(tag_id)
    
    # http://sylvana.net/jpegcrop/exif_orientation.html
    if orientation != None:
        angle = 0
        if orientation == 6:
            angle = -90
        if orientation == 8:
            angle = -270
        if angle != 0:
            img = img.rotate(angle, expand=True)
    
    if img.mode == "CMYK":
        img = ImageCms.profileToProfile(
            img,
            cwd + "\\_modules\\Color_Profiles\\USWebCoatedSWOP.icc",
            cwd + "\\_modules\\Color_Profiles\\sRGB_Color_Space_Profile.icm",
            outputMode="RGB"
        )
    
    elif img.mode == "RGBA":
        img_new = Image.new('RGB', img.size, (255, 255, 255))
        img_new.paste(img, (0,0), mask=img)
        img = img_new
        
    else:
        img = img.convert("RGB")
    
    img.thumbnail((input_image_size, input_image_size), Image.Resampling.LANCZOS)
    
    pil_format = None
    if input_convert_jpeg:
        pil_format = "JPEG"
    img.save(target_img_path, format=pil_format, quality=input_image_quality)

images_count = 0
for drop_input in drop_inputs:
    if drop_input.type == "File":
        if drop_input.extension.lower() not in allowed_img_extensions:
            continue
        images_count += 1
    elif drop_input.type == "Folder":
        root_node = Node(drop_input.path)
        images    = root_node.get_children(extensions=allowed_img_extensions, deep=True)
        images_count += len(images)
print("")
print(str(images_count) + " images are found.")

index_length = len(str(images_count))
index = 0

print("")
for drop_input in drop_inputs:
    
    if drop_input.type == "File":
        
        if drop_input.extension.lower() not in allowed_img_extensions:
            continue
        
        new_name, new_path = generate_new_file_name(drop_input)
        
        if os.path.isfile(new_path):
            print("The output file \"%s\" already exists." % new_name)
            delete_choice = input("Do you want to delete it? ([yes], no): ")
            if delete_choice not in ["", "yes", "no"]:
                print("You provided an invalid choice.")
                print("")
                print("The file is skipped.")
                continue
            if delete_choice == "no":
                print("You chose not to delete the already existing output file.")
                print("")
                print("The file is skipped.")
                continue
            os.remove(new_path)
        
        resize_image(drop_input, Path(new_path))
        
        print(
            "(%s/%s) %s"
            % (
                str_pad_left(index+1, index_length, "0"),
                images_count,
                drop_input.path
            )
        )
        
        index += 1
        
    elif drop_input.type == "Folder":
        
        new_name, new_path = generate_new_folder_name(drop_input)
        
        if os.path.isdir(new_path):
            print("The output folder \"%s\" already exists." % new_name)
            delete_choice = input("Do you want to delete it? ([yes], no): ")
            if delete_choice not in ["", "yes", "no"]:
                print("You provided an invalid choice.")
                print("")
                print("The folder is skipped.")
                continue
            if delete_choice == "no":
                print("You chose not to delete the already existing output folder.")
                print("")
                print("The folder is skipped.")
                continue
            shutil.rmtree(new_path)
        
        root_node = Node(drop_input.path)
        images = root_node.get_children(extensions=allowed_img_extensions, deep=True)
        
        for image_node in images:
            img_path = Path(image_node.path)
            target_img_path = Path(
                image_node.path.replace(
                    str_wrap(drop_input.name, img_path.sep),
                    str_wrap(new_name, img_path.sep),
                ),
                "File",
            )
            pathlib.Path(target_img_path.get_parent_path().path).mkdir(parents=True, exist_ok=True)
            resize_image(image_node, target_img_path)
            print(
                "(%s/%s) %s"
                % (
                    str_pad_left(index+1, index_length, "0"),
                    images_count,
                    image_node.path
                )
            )
            index += 1

#endregion


#region ==================== DURATION

sw_end = time.time()
sw_elapsed = sw_end - sw_start
print("")
print(
    "Total elapsed time: %d minutes %d seconds"
    % (
        math.floor(sw_elapsed / 60),
        round(sw_elapsed % 60)
    )
)

#endregion


print("")
print("Program will close.")
input()