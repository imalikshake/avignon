# Copy code
#!/bin/bash

folder_path='test3/output'
# # Path to the directory containing the image frames
# frames_directory="."

# # Output video file name
output_file="output.mp4"

# # Set the desired video codec, frame rate, and other encoding options
codec="libx264"
frame_rate=30
encoding_options="-crf 23 -preset medium"

# # Execute ffmpeg command to encode frames into video
ffmpeg -r "$frame_rate" -i $folder_path/%d.png  -pix_fmt yuv420p -c:v "$codec" $encoding_options "$output_file"
# ffmpeg -r "$frame_rate" -i %d.png -c:v "$codec" $encoding_options "$output_file"
# ffmpeg -y -i %d.png -r 4 result.mkv

# for file in *.jpg; do
#   if [[ -f "$file" ]]; then
#     # Extract the filename and extension
#     filename=$(basename "$file")
#     base="${filename%.*}"

#     # Rename the file
#     mv "$file" "$base.png"
#   fi
# done