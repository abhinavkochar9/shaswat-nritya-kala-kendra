"""Track the dancer through a video with SAM 3 (text prompt) and save one mask per frame.

Usage: python sam3_track.py <video.mp4> <out.npz> [--prompt person] [--chunk 360]
Output npz: masks = packbits(bool[T, H, W], axis=-1), shape, scores (best object score per frame).
"""
import argparse
import time

import cv2
import numpy as np
import torch
from transformers import Sam3VideoModel, Sam3VideoProcessor

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("out")
ap.add_argument("--prompt", default="person")
ap.add_argument("--chunk", type=int, default=360)
args = ap.parse_args()

cap = cv2.VideoCapture(args.video)
frames = []
while True:
    ok, f = cap.read()
    if not ok:
        break
    frames.append(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
T, H, W = len(frames), *frames[0].shape[:2]
print(f"{T} frames {W}x{H}", flush=True)

proc = Sam3VideoProcessor.from_pretrained("facebook/sam3")
model = Sam3VideoModel.from_pretrained("facebook/sam3", dtype=torch.bfloat16).to("cuda").eval()

masks = np.zeros((T, H, W), bool)
scores = np.zeros(T, np.float32)
n_obj = np.zeros(T, np.int16)
t0 = time.time()

# Overlapping chunks keep memory bounded; the overlap frames are re-detected, so seams stay consistent.
overlap = 8
start = 0
while start < T:
    end = min(T, start + args.chunk)
    clip = frames[start:end]
    sess = proc.init_video_session(video=clip, inference_device="cuda", processing_device="cpu",
                                   video_storage_device="cpu", dtype=torch.bfloat16)
    proc.add_text_prompt(sess, [args.prompt])
    with torch.inference_mode():
        for mo in model.propagate_in_video_iterator(inference_session=sess, max_frame_num_to_track=len(clip)):
            r = proc.postprocess_outputs(sess, mo)
            i = start + int(mo.frame_idx)
            n = len(r["object_ids"])
            n_obj[i] = n
            if not n:
                continue
            m = r["masks"].cpu().numpy().astype(bool)
            sc = r["scores"].float().cpu().numpy()
            # The dancer is the only person on stage: keep the largest confident object.
            areas = m.reshape(n, -1).sum(1) * (sc > 0.3)
            k = int(areas.argmax())
            masks[i] = m[k]
            scores[i] = sc[k]
    sess.reset_inference_session()
    del sess
    torch.cuda.empty_cache()
    print(f"frames {start}-{end - 1} done, {time.time() - t0:.0f}s", flush=True)
    if end == T:
        break
    start = end - overlap

np.savez_compressed(args.out, masks=np.packbits(masks, axis=-1), shape=np.array([T, H, W]),
                    scores=scores, n_obj=n_obj)
print(f"saved {args.out}; empty frames: {(n_obj == 0).sum()}, multi-object frames: {(n_obj > 1).sum()}, "
      f"min score {scores[n_obj > 0].min() if (n_obj > 0).any() else 0:.2f}", flush=True)
