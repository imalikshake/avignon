
input_file="keyframes.txt"
keyframe_folder="test2/keyframes_s/"


counter=-1

skip=49
declare -a lines

# Read the lines from the file into the array
while IFS= read -r line; do
  lines+=("$line")
done < "$input_file"

# Access the array elements
# for line in "${lines[@]}"; do
#   echo "$line"
# done

array_i=0
cap_f=${lines[array_i] }
echo $cap_f
# exit 1
cap_p=-1
# while IFS= read -r line; do
# echo "Processing line: $line"
ls test2/video/testimony*jpg | while read A; do
    ((counter++))
    if [[ $counter -gt $skip ]]; then
        if [[ $array_i -eq 0 ]]; then
            if [[ $counter -lt $cap_f ]]; then
                ebsynth -style test2/keyframes_s/testimony$cap_f.jpg -guide test2/keyframes_s/testimony$cap_f.jpg  $A -weight 1  \
                -output test2/output/$counter.png -uniformity 1200 -patchsize 3 -pyramidlevels 5 -searchvoteiters 5 -patchmatchiters 1
            else
                ((array_i++))
                cap_p=$cap_f
                cap_f=${lines[array_i]}
                ebsynth -style test2/keyframes_s/testimony$cap_f.jpg -guide test2/keyframes_s/testimony$cap_f.jpg  $A -weight 1  \
                -output test2/output/$counter.png -uniformity 1200 -patchsize 3 -pyramidlevels 5 -searchvoteiters 5 -patchmatchiters 1
            fi
        else
            if [[ $counter -lt $cap_f ]]; then
                ebsynth -style test2/keyframes_s/testimony$cap_f.jpg -guide test2/keyframes_s/testimony$cap_f.jpg  $A -weight 1  \
                -guide test2/keyframes_s/testimony$cap_p.jpg  $A -weight 10  \
                -output test2/output/$counter.png -uniformity 1200 -patchsize 3 -pyramidlevels 5 -searchvoteiters 5 -patchmatchiters 1
            else
                ((array_i++))
                cap_p=$cap_f
                cap_f=${lines[array_i]}
                ebsynth -style test2/keyframes_s/testimony$cap_f.jpg -guide test2/keyframes_s/testimony$cap_f.jpg  $A -weight 1  \
                -guide test2/keyframes_s/testimony$cap_p.jpg  $A -weight 10  \
                -output test2/output/$counter.png -uniformity 1200 -patchsize 3 -pyramidlevels 5 -searchvoteiters 5 -patchmatchiters 1
            fi
        fi
    else
        echo "skip"
    fi
done
# done < "$input_file"   


