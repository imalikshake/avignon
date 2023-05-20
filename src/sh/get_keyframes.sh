directory="test2/keyframes/"

# Output text file name
output_file="keyframes.txt"

# Scrape filenames from the directory and save them in a text file
# ls "$directory" > "$output_file"
# find "$directory" -type f -name "*.jpg" -o -name "*.png" | sed -E 's/.*\/([0-9]+)\..*/\1/' > "$output_file"
ls "$directory" | grep -Eo '[0-9]+' > "$output_file"