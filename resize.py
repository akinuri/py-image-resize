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
Image.MAX_IMAGE_PIXELS = None

from pprint import pprint

import math
import time

sw_start = time.time()

os.system("title " + "Resizing Images")


#region ==================== INPUT

drop_input = None

if len(sys.argv) > 1:
    drop_input = Path(sys.argv[1])
else:
    print("This program expects a folder that contains images.")
    print("Drag and drop the images folder on this file.")
    input("\nProgram will close.")
    sys.exit()

if drop_input.type != "Folder":
    print("The input item is not a folder.")
    input("\nProgram will close.")
    sys.exit()

#endregion


#region ==================== DUPLICATE

duplicate_path = drop_input.get_parent_path().path + drop_input.sep + drop_input.name + " (resized)"

# TODO: copy/create only the folder
# TODO: copy and resize files one by one
# TODO: what to do if the folder already exists?

shutil.copytree(drop_input.path, duplicate_path)

target_path = duplicate_path

#endregion


#region ==================== FIND

root_node        = Node(target_path)
image_extensions = ["jpg", "jpeg", "bmp", "png", "tif"]
images           = root_node.get_children(extensions=image_extensions, deep=True)

images_count = str(len(images))
index_length = len(images_count)

print(str(images_count) + " images are found.")

#endregion


#region ==================== RESIZE

size = (1920*4, 1920*4)
quality = 80 # 1-95, def=75

for i, image_node in enumerate(images):
    
    if image_node.extension != "jpg":
        new_path = image_node.parent.path + "\\" + image_node.name + ".jpg"
        os.rename(image_node.path, new_path)
        image_node.path = new_path
    
    img = Image.open(image_node.path)
    
    orientation = None
    exif = img.getexif()
    for tag_id in exif:
        tag = TAGS.get(tag_id, tag_id)
        if tag == "Orientation":
            data = exif.get(tag_id)
            if isinstance(data, bytes):
                data = data.decode()
            orientation = data
    
    # http://sylvana.net/jpegcrop/exif_orientation.html
    if orientation != None:
        angle = 0
        if orientation == 6:
            angle = -90
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
    
    img.save(image_node.path, quality=quality)
    
    print("("+ str_pad_left(i+1, index_length, "0") + "/" + images_count + ") " + image_node.path)

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


input("\nProgram will close.")