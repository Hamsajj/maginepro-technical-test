import unittest
from video_utils import *
import os
import moviepy.editor as mp

SAMPLE_VIDEO = "./files/small_video.mp4"


def test_resize_video():
    assert os.path.isfile(SAMPLE_VIDEO), "assert file exists"
    output_path = "./test_resize_video_output.mp4"
    resized_height = 120
    resize_video(SAMPLE_VIDEO, output_path, height=resized_height)
    assert os.path.isfile(output_path), "output should be created"
    resized_clip = mp.VideoFileClip(output_path)
    assert resized_clip.h == resized_height, "output should be resized"
    os.remove(output_path)