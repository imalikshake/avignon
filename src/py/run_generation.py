
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
from io_utils import read_data, get_dfs, init_folders
from layout_utils import put_text_wrap, get_coords
from video_utils import run_ebsynth, join_videos, reverse_video
import argparse
import random

sys.path.append('.')

def get_style(input_file, out_dir, segments, joined_df, grid_rows=6, grid_cols=2, fsize_max=20, fsize_min=3, fstroke_max=40, 
              colour_max=140, ratio_max=7.91, show=False):
    input_image = load_image(input_file)
    
    height = input_image.shape[0]
    width = input_image.shape[1]

    blank_image = np.ones((height, width, 3), np.uint8) 
    blank_image.fill(0)

    cell_width = width // 2
    cell_height = height // 6

    r_sum = joined_df['ratio'].sum()
    r_truth = 7.91
    r_ratio = r_sum/r_truth
    r_ratio = max(r_ratio,0.85)
    r_ratio = min(r_ratio,1.75)

    for segment in segments:
        seg_joined_df = joined_df[joined_df['question number'] == segment]
        i_row, i_col = get_coords(segment, rows=grid_rows, cols=grid_cols)
    
        x = i_col * cell_width - 50
        y = i_row * cell_height 

        adj_x = x
        adj_y = y + cell_height
        
        for index, row in seg_joined_df.iterrows():
            text = row['question'].replace("sex", '')
            ratio = row['ratio']
            put_text_wrap(img=blank_image, 
                        text=text, 
                        org=(adj_x, adj_y-300),  
                        font=cv2.FONT_HERSHEY_SIMPLEX, 
                        font_scale=max(15 * ratio, 2), 
                        color=(10, 5, 10), 
                        thickness=int(max((ratio*8),1)), 
                        line_spacing=int((1/ratio)*100), 
                        max_width=500)

        for index, row in seg_joined_df.iterrows():
            text = row['numbers']
            ratio = row['ratio']
            green = colour_max * ratio /3
            # print(blue)
            blue = 255 *0*(1-ratio)
            red = 255 * 0.5*(1-ratio)
            cv2.putText(img=blank_image,
                text=text,
                org=(adj_x,adj_y),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=max(fsize_max*ratio,fsize_min),
                color=(red,green,blue),
                thickness=int(max(fstroke_max*(ratio),fsize_min)))
            

    temp_file_path = os.path.join(out_dir, os.path.basename(input_file))
    s_image = iu.overlay(blank_image,input_image)
    s_image = iu.edges(s_image,min_g=1,max_g=4)
    s_image = cv2.cvtColor(s_image, cv2.COLOR_GRAY2BGR)
    s_image = iu.overlay(input_image, s_image, 0.7*r_ratio)
    s_image = iu.overlay(blank_image, s_image, 0.3*r_ratio)
    s_image = iu.adjust_brightness_contrast(s_image, brightness=50, contrast=50)
    if show:
        show_image(s_image, fig_size=(10,5))
    save_image(temp_file_path, s_image)
    return temp_file_path
    
def generate_frames(input_files, joined_df, temp_dir, output_dir, question_segments=12, frames_per_segment=50):
    segments = []
    for i in range(0,question_segments):
        gen_style = False
        segments.append(i)
        for j in range(i*frames_per_segment,(i*frames_per_segment)+frames_per_segment, 1):
            file_idx = j
            input_file = input_files[file_idx]
            temp_file = os.path.join(temp_dir, os.path.basename(input_files[file_idx]))
            mask_file = input_files[file_idx]
            
            temp_file = get_style(input_file=input_file, out_dir=temp_dir, segments=segments, joined_df=joined_df)
            
            if not gen_style:
                style_file = temp_file
                gen_style = True

            start_time = time.time()
            output_file = run_ebsynth(uniformity=1,
                                      style=style_file, 
                                      guide_2=None, 
                                      guide_1_weight=1000000, 
                                      guide_2_weight=100000, 
                                      input_file=temp_file, 
                                      guide_1=mask_file, 
                                      out_dir=output_dir)
            
            elapsed_time = time.time() - start_time
            print("Elapsed time: {:.2f} seconds".format(elapsed_time))
            
            out_image = load_image(output_file)
            out_image = iu.adjust_brightness_contrast(out_image, brightness=10, contrast=10)
            hsv_image = cv2.cvtColor(out_image, cv2.COLOR_BGR2HSV)
            saturation_factor = 1.8 
            hsv_image[..., 1] = hsv_image[..., 1] * saturation_factor
            result_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
            save_image(output_file, result_image)
        
def generate_video(output_files, output_video_path, question_segments=12, frames_per_segment=50, frames_per_image=3, 
                   interpolation_factor=0.5, cvt=None, skip_percentage=0,kernel_sizes=[1,3,5],):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_video = cv2.VideoWriter(output_video_path, fourcc, 30, (1080, 1920))  
    do_blur = 0
    for i in range(0, question_segments):  
        for j in range(i*frames_per_segment, (i+1)*frames_per_segment):
            current_frame = load_image(output_files[j], cvt=cvt) 
            next_frame =  load_image(output_files[min(len(output_files)-1,j+1)], cvt=cvt) 

            interpolated_frame = cv2.addWeighted(current_frame, interpolation_factor, next_frame, 1 - interpolation_factor, 0)

            filter_n = (1/12)*(i+1)
            filter_n = max(filter_n, 0.25)
            interpolated_frame = (filter_n*interpolated_frame.astype(np.float32)).astype(np.uint8)
            
            random_number = random.randint(0,100)
            if random_number < skip_percentage:
                do_blur = do_blur + 3

            if do_blur:
                 # Adjust the kernel size based on the desired blur effect
                kernel_size = (kernel_sizes[min(len(kernel_sizes)-1,do_blur)], kernel_sizes[min(len(kernel_sizes)-1,do_blur)]) 
                interpolated_frame = cv2.GaussianBlur(interpolated_frame, kernel_size, 0)
                do_blur = do_blur - 1

            for _ in range(frames_per_image):
                output_video.write(interpolated_frame)

    output_video.release()

def main(args):
    project_dir = args.project_dir
    input_dir = os.path.join(project_dir, "input")
    output_dir = os.path.join(project_dir, "output")
    temp_dir = os.path.join(project_dir, "temp")
    questions_dir = os.path.join(project_dir, "questions")
    frames_per_segment = args.frames_per_segment
    audience_filename = args.audience_filename
    
    print("Initialising folders...")
    init_folders([temp_dir, output_dir])
    
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
                    frames_per_segment=frames_per_segment)

    video_forward_path = os.path.join(project_dir, "forward.mp4")
    video_reverse_path = os.path.join(project_dir, "reverse.mp4")
    video_loop_path = os.path.join(project_dir, "loop.mp4")
    
    print("Generating video...")
    output_files = read_data(output_dir)
    generate_video(output_files, video_forward_path)
    
    print("Reversing video...")
    reverse_video(video_forward_path, video_reverse_path)
    
    print("Looping video...")
    join_videos(video_forward_path, video_reverse_path, video_loop_path)
    
    print("Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data gen. for theatre.")
    parser.add_argument("-pd", "--project_dir", type=str, help="Input dir path.")
    parser.add_argument("-fps", "--frames_per_segment", type=int, default=50, help="Frames per segment.")
    parser.add_argument("-csv", "--audience_filename", type=str, default="q_and_a_audience.csv", help="CSV for audience data")

    args = parser.parse_args()

    main(args)