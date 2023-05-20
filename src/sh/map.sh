ls w.*png | while read A; do
gmic $A _fx_stylize starrynight +fx_stylize 1,6,0,0,0.5,2,3,0.5,0.1,3,3,0,0.7,1,0,1,0,5,5,7,1,30,1,2,1.85,0 output[2] result_$A
done