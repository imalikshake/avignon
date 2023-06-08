
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
                    frames_per_segment=50, starting_segment=0, sampling_n=1):
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
    for i in range(starting_segment, question_segments):
        # Variable to track if style generation has been done
        gen_style = False
        
        # Add the segment number to the list
        # segments.append(i)
        segments = range(0, i+1)
        # Iterate over the frames in the segment
        for j in range(i * frames_per_segment, (i * frames_per_segment) + frames_per_segment, sampling_n):
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
            if not gen_style:
                style_file = temp_file
                gen_style = True
            
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
            save_image(output_file, result_image)

        
def generate_video(output_files, output_video_path, question_segments=12, frames_per_segment=50, 
                   frames_per_image=3, interpolation_factor=0.5, cvt=None, skip_percentage=0, 
                   kernel_sizes=[1, 3, 5], apply_progression=False):
    """
    Generate a video from the output frames.

    Parameters:
    - output_files: List of output frame file paths.
    - output_video_path: Path to save the output video.
    - question_segments: Number of question segments. Default is 12.
    - frames_per_segment: Number of frames per segment. Default is 50.
    - frames_per_image: Number of frames to generate from each interpolated image. Default is 3.
    - interpolation_factor: Interpolation factor for blending adjacent frames. Default is 0.5.
    - cvt: Conversion code for image loading. Default is None.
    - skip_percentage: Percentage of frames to skip. Default is 0.
    - kernel_sizes: List of kernel sizes for Gaussian blur. Default is [1, 3, 5].

    Returns:
    - None
    """

    # Define the fourcc code for the output video codec
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # Create a VideoWriter object to write the output video
    output_video = cv2.VideoWriter(output_video_path, fourcc, 30, (1080, 1920))

    # Variable to control the blurring effect
    do_blur = 0

    # Iterate over the question segments
    for i in range(len(output_files)):

        # Load the current frame and the next frame
        current_frame = load_image(output_files[i], cvt=cvt)
        next_frame = load_image(output_files[min(len(output_files) - 1, i + 1)], cvt=cvt)

        # Interpolate between the current and next frame
        interpolated_frame = cv2.addWeighted(current_frame, interpolation_factor, next_frame,
                                                1 - interpolation_factor, 0)

        if apply_progression:
        # Apply a filter to the interpolated frame
            j = i // question_segments
            filter_n = (1 / 12) * (j + 1)
            filter_n = max(filter_n, 0.25)
            interpolated_frame = (filter_n * interpolated_frame.astype(np.float32)).astype(np.uint8)

        # Generate a random number to determine if blurring should be applied
        random_number = random.randint(0, 100)
        if random_number < skip_percentage:
            do_blur = do_blur + 3

        if do_blur:
            # Adjust the kernel size based on the desired blur effect
            kernel_size = (kernel_sizes[min(len(kernel_sizes) - 1, do_blur)],
                            kernel_sizes[min(len(kernel_sizes) - 1, do_blur)])
            interpolated_frame = cv2.GaussianBlur(interpolated_frame, kernel_size, 0)
            do_blur = do_blur - 1

        # Write multiple frames from the interpolated frame
        for _ in range(frames_per_image):
            output_video.write(interpolated_frame)

    # Release the VideoWriter object
    output_video.release()

def main(args):
    input_project_dir = args.input_project_dir
    output_project_dir = args.output_project_dir
    input_dir = os.path.join(input_project_dir, "input")
    questions_dir = os.path.join(input_project_dir, "questions")
    output_dir = os.path.join(output_project_dir, "output")
    temp_dir = os.path.join(output_project_dir, "temp")
    frames_per_segment = args.frames_per_segment
    audience_filename = args.audience_filename
    starting_segment = args.starting_segment
    sampling_n = args.sampling_n
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
                    starting_segment=starting_segment,
                    sampling_n=sampling_n
                    )

    video_forward_path = os.path.join(output_project_dir, "forward.mp4")
    video_reverse_path = os.path.join(output_project_dir, "reverse.mp4")
    video_loop_path = os.path.join(output_project_dir, "loop.mp4")
    
    print("Generating video...")
    output_files = read_data(output_dir)
    generate_video(output_files, video_forward_path, 
                   question_segments=question_segments, 
                   frames_per_segment=frames_per_segment)
    
    print("Reversing video...")
    reverse_video(video_forward_path, video_reverse_path)
    
    print("Looping video...")
    join_videos(video_forward_path, video_reverse_path, video_loop_path)
    
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
    parser.add_argument("-n", "--starting_segment",
                        type=int, default=0,
                        help="Starting segment for decoding.")    
    parser.add_argument("-s", "--sampling_n", 
                        type=int, default=1,
                        help="Sampling number for frames.")    
    parser.add_argument

    args = parser.parse_args()

    main(args)