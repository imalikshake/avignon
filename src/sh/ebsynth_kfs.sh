# ls w.*png | while read A; do
# ebsynth -style result_w.0001.png -guide w.0001.png $A -weight 2 -weight 1 -output eb_$A
# done

input_file="keyframes.txt"

# style_path='test1/frames_s/testimony824.jpg'
style_path='lines3.png'
out_folder='test3'
in_folder='test2/video'
# in_folder='test1/frames_s'
counter=-1
threshold=-1

while IFS= read -r A; do
    ((counter++))
    if [[ $counter -gt $threshold ]]; then
        ebsynth -style $style_path -guide $style_path  $in_folder/testimony$A.jpg -weight 10  \
        -output $out_folder/$counter.png \
        -uniformity 100000 -patchsize 5 -pyramidlevels 5 -searchvoteiters 5 -patchmatchiters 2 
    else
        echo "skip"
    fi    
done  < "$input_file"

