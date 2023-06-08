
import os
import cv2
import numpy as np
import time
import sys
import glob
import pandas as pd
from image_utils import load_image, show_image, save_image
import image_utils as iu
import time
import argparse
import random
from io_utils import read_data, get_dfs, init_folders
from layout_utils import put_text_wrap, get_coords
from video_utils import run_ebsynth, join_videos, reverse_video


sys.path.append('.')

def generate_time_id():
    timestamp = str(int(time.time()))  # Get the current timestamp as an integer
    time_id = timestamp[-6:]           # Extract the last 6 digits
    
    return time_id

def get_style(input_file, out_dir, segments, joined_df, grid_rows=6, grid_cols=2, fsize_max=20, 
              fsize_min=3, fstroke_max=40, colour_max=140, r_truth=7.91, r_min=0.72, r_max=1.5, 
              show=False):
    """
    Generate the style image for the given input file.
    
    Parameters:
    - input_file: Path to the input file.
    - out_dir: Directory to save the output image.
    - segments: List of segment numbers to include in the style image.
    - joined_df: Joined dataframe of static and audience questions.
    - grid_rows: Number of rows in the grid. Default is 6.
    - grid_cols: Number of columns in the grid. Default is 2.
    - fsize_max: Maximum font size. Default is 20.
    - fsize_min: Minimum font size. Default is 3.
    - fstroke_max: Maximum font stroke. Default is 40.
    - colour_max: Maximum color value. Default is 140.
    - r_truth: Truth value for ratio calculation. Default is 7.91.
    - r_min: Minimum value for ratio. Default is 0.5.
    - r_max: Maximum value for ratio. Default is 1.5.
    - show: Whether to display the output image.
    
    Returns:
    - Path to the generated style image.
    """
    # Load input image
    input_image = load_image(input_file)
    
    # Get image dimensions
    height = input_image.shape[0]
    width = input_image.shape[1]

    # Create a blank image with the same dimensions as input image
    blank_image = np.ones((height, width, 3), np.uint8) 
    blank_image.fill(0)

    # Calculate cell dimensions for the grid
    cell_width = width // 2
    cell_height = height // 6

    # Calculate ratio for scaling text size
    r_sum = joined_df['ratio'].sum()
    r_sum_diff = joined_df['ratio_diff'].sum()
    r_ratio = r_sum / r_truth 
    r_ratio = max(r_ratio, r_min)
    r_ratio = min(r_ratio, r_max)
    # Iterate over each segment
    for segment in segments:
        seg_joined_df = joined_df[joined_df['question number'] == segment]
        i_row, i_col = get_coords(segment, rows=grid_rows, cols=grid_cols)
    
        x = i_col * cell_width
        y = i_row * cell_height 

        adj_x = x - 50
        adj_y = y + cell_height
        
        # Add text for each question in the segment
        for index, row in seg_joined_df.iterrows():
            text = row['question'].replace("sex", '')
            ratio = max(row['ratio'], 1e-5)
            print("ratio", ratio)
            put_text_wrap(img=blank_image, 
                          text=text, 
                          org=(adj_x, adj_y-300),  
                          font=cv2.FONT_HERSHEY_SIMPLEX, 
                          font_scale=max(15 * ratio, 2), 
                          color=(10, 5, 10), 
                          thickness=int(max((ratio*8), 1)), 
                          line_spacing=min(500,int((1/ratio)*100)), 
                          max_width=500)

        # Add numbers for each question in the segment
        for index, row in seg_joined_df.iterrows():
            text = row['numbers']
            ratio = max(row['ratio'], 1e-5)
            green = colour_max * ratio / 3
            blue = 255 * 0 * (1 - ratio)
            red = 255 * 0.5 * (1 - ratio)
            cv2.putText(img=blank_image,
                        text=text,
                        org=(adj_x, adj_y),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=max(fsize_max * ratio, fsize_min),
                        color=(red, green, blue),
                        thickness=int(max(fstroke_max * (ratio), fsize_min)))
            
    # Generate the style image by overlaying and adjusting the input and blank images
    temp_file_path = os.path.join(out_dir, os.path.basename(input_file))
    s_image = iu.overlay(blank_image, input_image)
    s_image = iu.edges(s_image, min_g=1, max_g=4)
    s_image = cv2.cvtColor(s_image, cv2.COLOR_GRAY2BGR)
    s_image = iu.overlay(input_image, s_image, min(0.7, max(0.3, 0.7 * r_ratio)))
    s_image = iu.overlay(blank_image, s_image, 0.3 * r_ratio)
    s_image = iu.adjust_brightness_contrast(s_image, brightness=50, contrast=50)
    s_image = iu.add_color_jitter(s_image, r_sum_diff*4)
    if show:
        show_image(s_image, fig_size=(10, 5))
    
    # Save the generated style image
    save_image(temp_file_path, s_image)
    
    return temp_file_path

def generate_frames(input_files, joined_df, temp_dir, output_dir, question_segments=12, 
                    frames_per_segment=50, frame_number=0):
    """
    Generate frames based on the input files and dataframes.

    Parameters:
    - input_files: List of input file paths.
    - joined_df: Joined dataframe of static and audience questions.
    - temp_dir: Directory to save temporary style images.
    - output_dir: Directory to save the output frames.
    - question_segments: Number of question segments. Default is 12.
    - frames_per_segment: Number of frames per segment. Default is 50.

    Returns:
    - None
    """
    # Create an empty list to store the segments
    segments = []
    
    # Iterate over the number of question segments
    i = frame_number // frames_per_segment

    style_i = i * frames_per_segment
    
    # Add the segment number to the list
    # segments.append(i)
    segments = range(0, i+1)
    # Iterate over the frames in the segment
    j = frame_number
    # Get the index of the input file
    file_idx = j
    
    # Get the input file, temp file, and mask file paths
    input_file = input_files[file_idx]
    temp_file = os.path.join(temp_dir, os.path.basename(input_files[file_idx]))
    mask_file = input_files[file_idx]
    
    # Generate the style image and get the path to it
    temp_file = get_style(input_file=input_file, out_dir=temp_dir, segments=segments, 
                            joined_df=joined_df)
    
    # Set the style file path if it hasn't been set already
    style_file = get_style(input_file=input_files[style_i], out_dir=temp_dir, segments=segments, 
                            joined_df=joined_df)

    
    # Start the timer
    start_time = time.time()
    
    # Run ebsynth to generate the output frame
    output_file = run_ebsynth(uniformity=1,
                                style=style_file,
                                guide_2=None,
                                guide_1_weight=1000000,
                                guide_2_weight=100000,
                                input_file=temp_file,
                                guide_1=mask_file,
                                out_dir=output_dir)
    
    # Calculate the elapsed time
    elapsed_time = time.time() - start_time
    print("Elapsed time: {:.2f} seconds".format(elapsed_time))
    
    # Load the output image
    out_image = load_image(output_file)
    
    # Adjust brightness and contrast of the output image
    out_image = iu.adjust_brightness_contrast(out_image, brightness=10, contrast=10)
    
    # Convert the image to HSV color space
    hsv_image = cv2.cvtColor(out_image, cv2.COLOR_BGR2HSV)
    
    # Increase the saturation of the image
    saturation_factor = 1.8
    hsv_image[..., 1] = hsv_image[..., 1] * saturation_factor
    
    # Convert the image back to BGR color space
    result_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
    
    # Save the output image
    save_image(output_file.split('.')[0]+"_"+generate_time_id()+".png", result_image)

def main(args):
    input_project_dir = args.input_project_dir
    output_project_dir = args.output_project_dir
    input_dir = os.path.join(input_project_dir, "input")
    questions_dir = os.path.join(input_project_dir, "questions")
    output_dir = os.path.join(output_project_dir, "output")
    temp_dir = os.path.join(output_project_dir, "temp")
    frames_per_segment = args.frames_per_segment
    audience_filename = args.audience_filename
    frame_number = args.frame_number
    print("Initialising folders...")
    init_folders([output_project_dir, temp_dir, output_dir])
    
    print("Initialising data...")
    input_files = read_data(input_dir)
    joined_df = get_dfs(questions_dir, 
                        static_filename="static_q_and_a.csv", 
                        audience_filename=audience_filename)

    question_segments = joined_df['question number'].max()+1
    
    print("Generating frames...")
    generate_frames(input_files=input_files,
                    joined_df=joined_df,
                    temp_dir=temp_dir,
                    output_dir=output_dir,
                    question_segments=question_segments,
                    frames_per_segment=frames_per_segment,
                    frame_number=frame_number)

    print("Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data gen. for theatre.")
    parser.add_argument("-i", "--input_project_dir", 
                        type=str, help="Input dir path.")
    parser.add_argument("-o", "--output_project_dir", 
                        type=str, help="Output dir path.")
    parser.add_argument("-f", "--frames_per_segment", 
                        type=int, default=50, 
                        help="Frames per segment.")
    parser.add_argument("-c", "--audience_filename", 
                        type=str, default="q_and_a_audience.csv",
                        help="CSV for audience data")
    parser.add_argument("-n", "--frame_number", 
                        type=int, default=0,
                        help="Frame to get.")

    args = parser.parse_args()

    main(args)