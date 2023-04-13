import moviepy.editor as mp


def resize_video(video_path: str, output_path: str, height: int = 360):
    clip = mp.VideoFileClip(video_path)
    clip_resized = clip.resize(height=height)
    clip_resized.write_videofile(output_path)

