#!/bin/bash

image_folder="est"

# Check if ImageMagick is installed
if ! command -v mogrify &> /dev/null; then
    echo "ImageMagick is not installed. Please install it first."
    exit 1
fi

# Check if the image folder exists
if [ ! -d "$image_folder" ]; then
    echo "Image folder does not exist."
    exit 1
fi

# Rotate all images in the folder
mogrify -rotate -90 "$image_folder"/*.jpg "$image_folder"/*.jpeg "$image_folder"/*.png "$image_folder"/*.gif

echo "Images rotated successfully."