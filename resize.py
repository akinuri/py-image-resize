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

#endregion


#region ==================== SETUP

os.system("title %s" % "Resizing Images")
Image.MAX_IMAGE_PIXELS = None
sw_start = time.time()

#endregion


#region ==================== INPUT

drop_input = None

if len(sys.argv) > 1:
    drop_input = Path(sys.argv[1])
else:
    print("This program expects a folder that contains images.")
    print("Drag and drop the images folder on this file.")
    print("")
    input("Program will close.")
    sys.exit()

if drop_input.type != "Folder":
    print("The input item is not a folder.")
    print("")
    input("Program will close.")
    sys.exit()

DEFAULT_IMAGE_SIZE = 5000
DEFAULT_IMAGE_QUALITY = 75
MIN_IMAGE_SIZE = 768
MAX_IMAGE_SIZE = 12800

print("Dimensions of the images will be limited to a specific area, a square.")
input_image_size = input("Enter a size in pixels (%d-%d, the default is %s): " % (MIN_IMAGE_SIZE, MAX_IMAGE_SIZE, DEFAULT_IMAGE_SIZE))

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

input_image_quality = input("Enter a quality (10-95, the default is %s): " % DEFAULT_IMAGE_QUALITY)

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

#endregion


#region ==================== TARGET

target_dir      = drop_input.name + " (%dpx, %dqty)" % (input_image_size, input_image_quality)
target_dir_path = drop_input.get_parent_path().path + drop_input.sep + target_dir
target_dir_deleted = False

if os.path.isdir(target_dir_path):
    print("The output folder \"%s\" already exists." % target_dir)
    delete_choice = input("Do you want to delete it? ([yes], no): ")
    if delete_choice not in ["", "yes", "no"]:
        print("You provided an invalid choice.")
        print("")
        print("Program will close.")
        input()
        sys.exit()
    if delete_choice == "no":
        print("You chose not to delete the already existing output folder.")
        print("")
        print("Program will close.")
        input()
        sys.exit()
    shutil.rmtree(target_dir_path)
    target_dir_deleted = True

os.mkdir(target_dir_path)

#endregion


#region ==================== FIND

root_node        = Node(drop_input.path)
image_extensions = ["jpg", "jpeg", "bmp", "png", "tif"]
images           = root_node.get_children(extensions=image_extensions, deep=True)

images_count = str(len(images))
index_length = len(images_count)

if target_dir_deleted:
    print("")
print(str(images_count) + " images are found.")

#endregion


#region ==================== RESIZE

size = (input_image_size, input_image_size)
quality = input_image_quality

for i, image_node in enumerate(images):
    
    img_path = Path(image_node.path)
    target_img_path = image_node.path.replace(
        str_wrap(drop_input.name, img_path.sep),
        str_wrap(target_dir, img_path.sep),
    )
    
    # if image_node.extension != "jpg":
    #     new_path = image_node.parent.path + "\\" + image_node.name + ".jpg"
    #     os.rename(image_node.path, new_path)
    #     image_node.path = new_path
    
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
    
    img.thumbnail(size, Image.Resampling.LANCZOS)
    
    img.save(target_img_path, quality=quality)
    
    print(
        "(%s/%s) %s"
        % (
            str_pad_left(i+1, index_length, "0"),
            images_count,
            target_img_path
        )
    )

#endregion


#region ==================== DURATION

sw_end = time.time()
sw_elapsed = sw_end - sw_start
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