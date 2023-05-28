import cv2
import subprocess
import os
def run_ebsynth(style, input_file, guide_1, out_dir, uniformity=1,patch_size=3, pyramid_levels=1, search_vote_iters=1, patch_match_iters=1, guide_1_weight=100, guide_2_weight=0.01, guide_2=None):
    output_file = os.path.splitext(os.path.basename(input_file))[0]
    if guide_2:
        command = f"ebsynth -style {style} \
                -guide {guide_1}  {input_file} -weight {guide_1_weight} \
                -guide {guide_2} {input_file} -weight {guide_2_weight} \
                -output {out_dir}/{output_file}.png \
                -uniformity {uniformity} -patchsize {patch_size} -pyramidlevels {pyramid_levels} -searchvoteiters {search_vote_iters} -patchmatchiters {patch_match_iters} "
    else:
        command = f"ebsynth -style {style} \
                -guide {guide_1}  {input_file} -weight {guide_1_weight} \
                -output {out_dir}/{output_file}.png \
                -uniformity {uniformity} -patchsize {patch_size} -pyramidlevels {pyramid_levels} -searchvoteiters {search_vote_iters} -patchmatchiters {patch_match_iters} "

    subprocess.call(command, shell=True)
    return f"{out_dir}/{output_file}.png"

def reverse_video(input_path, output_path):
    # Open the video file
    video = cv2.VideoCapture(input_path)

    # Get video properties
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Create a VideoWriter object to write the reversed video
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Specify the codec (e.g., XVID, mp4v, etc.)
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    # Read and write video frames in reverse order
    frames = []
    while True:
        ret, frame = video.read()
        if not ret:
            break
        frames.append(frame)

    for frame in reversed(frames):
        out.write(frame)

    # Release the video objects
    video.release()
    out.release()

def join_videos(video1_path, video2_path, output_path):
    # Open the first video
    video1 = cv2.VideoCapture(video1_path)
    fps1 = video1.get(cv2.CAP_PROP_FPS)
    frame_width1 = int(video1.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height1 = int(video1.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Open the second video
    video2 = cv2.VideoCapture(video2_path)
    fps2 = video2.get(cv2.CAP_PROP_FPS)
    frame_width2 = int(video2.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height2 = int(video2.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Ensure both videos have the same frame size and FPS
    if frame_width1 != frame_width2 or frame_height1 != frame_height2:
        raise ValueError("Videos must have the same frame size")
    if fps1 != fps2:
        raise ValueError("Videos must have the same FPS")

    # Create an output video writer
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    output_video = cv2.VideoWriter(output_path, fourcc, fps1, (frame_width1, frame_height1))

    # Read and write frames from the first video
    while True:
        ret, frame = video1.read()
        if not ret:
            break
        output_video.write(frame)

    # Read and write frames from the second video
    while True:
        ret, frame = video2.read()
        if not ret:
            break
        output_video.write(frame)

    # Release the video objects and writer
    video1.release()
    video2.release()
    output_video.release()
    