"""Create a small synthetic sample video for pipeline testing."""
from moviepy.editor import ColorClip
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'test_samples')
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PATH = os.path.join(OUT_DIR, 'sample.mp4')

def make_sample(path=OUT_PATH, duration=6, fps=24, size=(640,360)):
    clip = ColorClip(size, col=(255,0,0)).set_duration(duration)
    clip.write_videofile(path, fps=fps, codec='libx264', audio=False)
    clip.close()

if __name__ == '__main__':
    print('Creating sample video at', OUT_PATH)
    make_sample()
    print('Done')
