# Hero video pipeline

How `assets/video/hero-loop.mp4` was made from the 120 fps phone clip.

1. **Downscale, keep every frame** (on the Mac):
   `ffmpeg -i IMG_0422.MOV -map 0:v:0 -an -vf "scale=1280:720,format=yuv420p" -c:v libx264 -crf 12 dance_720p120.mp4`
2. **Track her with SAM 3** (on a CUDA GPU with `transformers` and access to `facebook/sam3`; ~20 min for 2,287 frames on an 8 GB laptop GPU):
   `python sam3_track.py dance_720p120.mp4 dance_masks.npz --prompt person`
3. **Composite and loop** (on the Mac, a few minutes):
   `python3 compose_hero.py preview dance_720p120.mp4 dance_masks.npz prev "#2E9AB8" 240 1000`
   `python3 compose_hero.py render dance_720p120.mp4 dance_masks.npz hero-loop.mp4 hero-poster.jpg "#2E9AB8"`
   The last argument is the side-light colour in the haze (`#C8325A` gives an all-warm look).

The background above the stage line is replaced; she and the real stage floor are kept. The output is
half speed (every 2nd frame of 120 fps played at 30 fps) with a 1 s crossfade so it loops cleanly.

`../cutout.swift` lifts a person out of a still photo with Apple Vision (used for the `cutout-*.webp` images):
`swiftc -O cutout.swift -o cutout && ./cutout photo.jpg out/prefix`
