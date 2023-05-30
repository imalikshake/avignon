# Generative art for visualising data

## How it works:
Aggregated data as CSVs and input base frames are used to generate a stylised video.

## How to run it:

```
python run_generation.py --input_project_dir {Path to data folder}
                         --output_project_dir {Output directory
                         --audience_filename {Filename of audience's data}
                         --frames_per_segment {n}
```

+ The input project dir is structured with two folders: /input and /questions. /questions should contain the .csvs for the data and /input should contain the input frames. 
+ The output project dir is where all the output frames and videos will be saved.
+ --frames_per_segment indicates how many frames there are per question segment. 
+ --audience_filename is the filename of the aggregated audience data.

