import os
import tempfile
import cv2
import numpy as np

from project.app import run_pipeline


def create_test_video(path, seconds=2, fps=10):
    width, height = 320, 240
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(path, fourcc, fps, (width, height))
    for i in range(seconds * fps):
        img = np.zeros((height, width, 3), dtype='uint8')
        cv2.putText(img, f'Frame {i}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)
        writer.write(img)
    writer.release()


def test_run_pipeline_creates_outputs(tmp_path):
    tmpdir = tmp_path
    video_path = os.path.join(tmpdir, 'test.mp4')
    create_test_video(video_path, seconds=2, fps=10)
    outdir = os.path.join(tmpdir, 'out')
    os.makedirs(outdir, exist_ok=True)

    od = run_pipeline(video_path, outdir, max_scenes=2)
    assert os.path.isdir(od)
    assert os.path.exists(os.path.join(od, 'summary.txt'))
    assert os.path.exists(os.path.join(od, 'moderation_report.json'))
*** End Patch