#!/bin/bash

# Specify the source and destination directories
source_dir="../../projects/graphite/graphite_original/"
destination_dir="../../projects/graphite/graphite_original_jpg/"

# Convert PNG files to JPG and save them in the destination directory
for file in "$source_dir"/*.png; do
  filename=$(basename "$file")
  new_filename="${filename%.png}.jpg"
  convert "$file" "$destination_dir/$new_filename"
done