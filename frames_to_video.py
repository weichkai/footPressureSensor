"""
This script generates an animation from multiple frames.

Command Line Arguments:
    python frames_to_video.py
    
Usage:
    After running "viz_generate_frames.py" and generating all the frames, please use this file to create an animation
    Remember to customize the folder paths in lines 22 and 23
"""
from moviepy.editor import ImageSequenceClip
import os


def create_video_from_frames(frame_folder, output_file, fps=25):
    frame_files = [os.path.join(frame_folder, f) for f in sorted(os.listdir(frame_folder)) if f.endswith('.png')]
    clip = ImageSequenceClip(frame_files, fps=fps)
    clip.write_videofile(output_file, codec='libx264')


frame_folder = 'frames/nrshoes_stone2'
output_file = 'nrshoes_stone2.mp4'
# frame_folder = 'frames/fullsoul_stone1'
# output_file = 'fullsoul_stone1.mp4'
create_video_from_frames(frame_folder, output_file, fps=25)
