# ls w.*png | while read A; do
# ebsynth -style result_w.0001.png -guide w.0001.png $A -weight 2 -weight 1 -output eb_$A
# done

counter=-1
threshold=450

ebsynth -style ~/frames_s/testimony724.jpg -guide ~/frames_r/testimony724.jpg  ~/frames_s/testimony120.jpg -weight 1 \
    -output test/1.png -uniformity 1200 -patchsize 3 -pyramidlevels 5 -searchvoteiters 5 -patchmatchiters 1

ebsynth -style ~/frames_s/testimony624.jpg -guide ~/frames_r/testimony624.jpg  ~/frames_s/testimony121.jpg -weight 1 \
    -guide ~/frames_s/testimony724.jpg  ~/frames_s/testimony121.jpg -weight 0.5 \
    -guide ~/frames_r/testimony724.jpg  ~/frames_r/testimony121.jpg -weight 0.5 \
    -output test/2.png -uniformity 1200 -patchsize 3 -pyramidlevels 5 -searchvoteiters 5 -patchmatchiters 1
ebsynth -style ~/frames_s/testimony524.jpg -guide ~/frames_r/testimony524.jpg  ~/frames_s/testimony122.jpg -weight 1 \
    -guide ~/frames_s/testimony624.jpg  ~/frames_s/testimony122.jpg -weight 0.5 \
    -guide ~/frames_r/testimony624.jpg  ~/frames_r/testimony122.jpg -weight 0.5 \
    -output test/3.png -uniformity 1200 -patchsize 3 -pyramidlevels 5 -searchvoteiters 5 -patchmatchiters 1