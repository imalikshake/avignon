#!/bin/bash

# Specify the input text file containing number ranges
input_file="kframes3.txt"

# Specify the source and destination directories
source_dir="test3/video_o/"
destination_s_dir="test3/keyframes_s"
destination_f_dir="test3/keyframes_f"

# Read the input file line by line
while IFS="-" read -r start_num end_num; do
    # Copy the file using the first number
    source_file="${source_dir}/testimony${start_num}.jpg"
    destination_file="${destination_s_dir}/testimony${start_num}.jpg"
    cp "$source_file" "$destination_file"
    
    # Copy the file using the second number
    source_file="${source_dir}/testimony${end_num}.jpg"
    destination_file="${destination_f_dir}/testimony${end_num}.jpg"
    cp "$source_file" "$destination_file"
done < "$input_file"