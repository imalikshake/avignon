# ls w.*png | while read A; do
# ebsynth -style result_w.0001.png -guide w.0001.png $A -weight 2 -weight 1 -output eb_$A
# done

# style_path1='test3/video_o/testimony1080.jpg'
style_path='test3/test.jpg'
style_path2='test3/test3.jpg'
# style_path1='lines3.png'

out_folder='test3/output'
mask_folder='graphite'
in_folder='graphite_original'
# style_path='lines3.png'
# out_folder='test3/_output'
# in_folder='test3/video_o'
# mask_folder='test3/video_s'
# in_folder='test1/frames_s'
counter=-1
threshold=-1

ls $in_folder/*png | while read A; do
    filename=$(basename "$A")
    # Build the path to the corresponding file in the target folder
    mask_file="$mask_folder/$filename"
    ((counter++))
    if [[ $counter -gt $threshold ]]; then
        ebsynth -style $style_path2 \
        -guide $mask_file  $A -weight 100 \
        -guide $style_path $A -weight 0.01 \
        -output $out_folder/$counter.png \
        -uniformity 1 -patchsize 5 -pyramidlevels 1 -searchvoteiters 1 -patchmatchiters 1 
    else
        echo "skip"
    fi    
done

