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


#region ==================== APP: EXIT

def app_exit(*messages):
    for message in messages:
        print(message)
        if message != "":
            print("")
    input("App will close. ")
    sys.exit()

#endregion


#region ==================== SETUP

os.system("title %s" % "Image Resizer")
Image.MAX_IMAGE_PIXELS = None

#endregion


#region ==================== INPUTS

drop_inputs = []

if len(sys.argv) == 1:
    app_exit(
        "This app expects an image file or a folder that contains images.",
        "Drag and drop images and/or a folder of images on this file.",
    )

for arg in sys.argv[1:]:
    drop_inputs.append(Path(arg))

MIN_BOUND_BOX_SIZE       = 100
MAX_BOUND_BOX_SIZE       = 16000
DEFAULT_BOUND_BOX_WIDTH  = 2000
DEFAULT_BOUND_BOX_HEIGHT = 2000
DEFAULT_IMAGE_QUALITY    = 75

print("Dimensions of the images will be limited to a specific area.")

print("")
input_image_width = input("Enter a width in pixels (%d-%d, [%s]): " % (MIN_BOUND_BOX_SIZE, MAX_BOUND_BOX_SIZE, DEFAULT_BOUND_BOX_WIDTH))

if input_image_width == "":
    input_image_width = str(DEFAULT_BOUND_BOX_WIDTH)

RE_INT = re.compile(r'^([1-9]\d*|0)$')
if re.match(RE_INT, input_image_width) is None:
    app_exit("", "Invalid value. Enter an integer in the range of %d-%d" % (MIN_BOUND_BOX_SIZE, MAX_BOUND_BOX_SIZE))

input_image_width = int(input_image_width)

if (MIN_BOUND_BOX_SIZE <= input_image_width <= MAX_BOUND_BOX_SIZE) is False:
    app_exit("", "Invalid range. Integer needs to be in the range of %d-%d" % (MIN_BOUND_BOX_SIZE, MAX_BOUND_BOX_SIZE))

print("")
input_image_height = input("Enter a height in pixels (%d-%d, [%s]): " % (MIN_BOUND_BOX_SIZE, MAX_BOUND_BOX_SIZE, DEFAULT_BOUND_BOX_HEIGHT))

if input_image_height == "":
    input_image_height = str(DEFAULT_BOUND_BOX_HEIGHT)

RE_INT = re.compile(r'^([1-9]\d*|0)$')
if re.match(RE_INT, input_image_height) is None:
    app_exit("", "Invalid value. Enter an integer in the range of %d-%d" % (MIN_BOUND_BOX_SIZE, MAX_BOUND_BOX_SIZE))

input_image_height = int(input_image_height)

if (MIN_BOUND_BOX_SIZE <= input_image_height <= MAX_BOUND_BOX_SIZE) is False:
    app_exit("", "Invalid range. Integer needs to be in the range of %d-%d" % (MIN_BOUND_BOX_SIZE, MAX_BOUND_BOX_SIZE))


print("")
input_image_quality = input("Enter a quality (10-95, [%s]): " % DEFAULT_IMAGE_QUALITY)

if input_image_quality == "":
    input_image_quality = str(DEFAULT_IMAGE_QUALITY)

if re.match(RE_INT, input_image_quality) is None:
    app_exit("", "Invalid value. Enter an integer in the range of 10-95")

input_image_quality = int(input_image_quality)

if (10 <= input_image_quality <= 95) is False:
    app_exit("", "Invalid range. Integer needs to be in the range of 10-95")

input_convert_jpeg = None
ALLOWED_CONVERT_JPEG_ANSWERS = ["y", "yes", "n", "no", ""]

print("")
input_convert_jpeg = input("Do you want to convert to jpeg, if they are not already so? (yes, [no]): ")

if input_convert_jpeg.lower() not in ALLOWED_CONVERT_JPEG_ANSWERS:
    app_exit("Invalid value. Enter yes or no.")

input_convert_jpeg = True if input_convert_jpeg.lower() in ["y", "yes"] else False

#endregion


#region ==================== FUNCS

def generate_new_file_name(file):
    name = file.name + " (%dpx, %dpx, %dqty)" % (input_image_width, input_image_height, input_image_quality)
    path = file.get_parent_path().path + file.sep + name + "." + file.extension
    return name, path

def generate_new_folder_name(folder):
    name = folder.name + " (%dpx, %dpx, %dqty)" % (input_image_width, input_image_height, input_image_quality)
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
    
    img.thumbnail((input_image_width, input_image_height), Image.Resampling.LANCZOS)
    
    pil_format = None
    if input_convert_jpeg:
        pil_format = "JPEG"
    img.save(target_img_path, format=pil_format, quality=input_image_quality)

#endregion


#region ==================== APP: RESIZE (FIT)

sw_start = time.time()

allowed_img_extensions = ["jpg", "jpeg", "bmp", "png", "tif"]

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

app_exit(
    "",
    "Total elapsed time: %d minutes %d seconds"
    % (
        math.floor(sw_elapsed / 60),
        round(sw_elapsed % 60)
    )
)

#endregion
