import unittest
from utils import *
import os
import moviepy.editor as mp

FILE_PATH = os.path.dirname(os.path.abspath(__file__))
SAMPLE_VIDEO = os.path.join(FILE_PATH, "./files/small_video.mp4")


def test_resize_video():
    """tests success path of resize_video"""
    assert os.path.isfile(SAMPLE_VIDEO), f"assert {SAMPLE_VIDEO} exists"
    output_path = os.path.join(FILE_PATH, "./test_resize_video_output.mp4")
    resized_height = 120
    resize_video(SAMPLE_VIDEO, output_path, height=resized_height, verbose=False)
    assert os.path.isfile(output_path), "output should be created"
    resized_clip = mp.VideoFileClip(output_path)
    assert resized_clip.h == resized_height, "output should be resized"
    os.remove(output_path)
