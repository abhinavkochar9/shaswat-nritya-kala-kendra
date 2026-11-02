"""Replace the curtain/banner behind the dancer with a hazy theatre backdrop, keeping her
(SAM 3 mask) and the real stage floor, and write the slowed hero loop.

Usage:
  python compose_hero.py preview <video> <masks.npz> <out_dir> <side_hex> [frame ...]   # JPEG stills
  python compose_hero.py render  <video> <masks.npz> <out.mp4> <poster.jpg> <side_hex>  # full loop
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

W, H = 1280, 720
SHIFT_X = int(0.14 * W)      # move her (and the stage) right so the left side is free for text
STEP = 2                     # 120 fps source, every 2nd frame at 30 fps = half speed
SMOOTH = 2                   # temporal mask smoothing radius (source frames)
XFADE_S = 1.0                # loop crossfade length (seconds)
FPS = 30
SEAM_BAND = (585, 670)       # rows where the curtain meets the stage floor
FRONT_OFFSET = 57            # stage front edge sits this far below the seam

Y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
X = np.linspace(0, 1, W, dtype=np.float32)[None, :]
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255


def smoothstep(e0, e1, v):
    t = np.clip((v - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def fbm(w, h, seed, octaves=6, base=3):
    """Fractal value noise in [0, 1] — soft, cloud-like."""
    rng = np.random.default_rng(seed)
    out, amp, total = np.zeros((h, w), np.float32), 1.0, 0.0
    for o in range(octaves):
        gw = base * 2 ** o + 1
        gh = max(2, int(gw * h / w) + 1)
        g = Image.fromarray(rng.random((gh, gw)).astype(np.float32))
        out += np.asarray(g.resize((w, h), Image.BICUBIC), np.float32) * amp
        total += amp
        amp *= 0.5
    out /= total
    return (out - out.min()) / (out.max() - out.min())


class Backdrop:
    """Dark theatre: warm key glow behind her, drifting haze lit by the key and a
    coloured side lamp, a soft beam from above."""

    def __init__(self, side_color, seam):
        cx = 0.51 + SHIFT_X / W
        fy = seam / H

        def blob(x0, y0, rx, ry, k):
            return np.exp(-(((X - x0) / rx) ** 2 + ((Y - y0) / ry) ** 2) * k)[..., None]

        top, low = hex_rgb("#0B0302"), hex_rgb("#1E0706")
        self.base = (top + (low - top) * (np.clip(Y / fy, 0, 1) ** 1.4)[..., None]) * np.ones((1, W, 1), np.float32)
        self.key = blob(cx, 0.46, 0.30, 0.50, 1.4)
        self.side = blob(1.03, 0.38, 0.30, 0.55, 1.2)
        self.wash = blob(0.28, 0.10, 0.30, 0.35, 1.5)
        beam_w = 0.05 + 0.13 * Y
        self.beam = (np.exp(-((X - cx) / beam_w) ** 2) * np.clip(1.15 - Y / fy, 0, 1))[..., None]
        self.amber, self.deep, self.side_c = hex_rgb("#F08A3A"), hex_rgb("#C2281F"), hex_rgb(side_color)
        self.s1 = fbm(W + 360, H + 260, seed=11)
        self.s2 = fbm(W + 360, H + 260, seed=23, base=4)

    def render(self, n):
        o1, o2 = int(n * 0.22), int(n * 0.14)
        a = self.s1[60:60 + H, o1:o1 + W]
        b = self.s2[200 - o2 // 2:200 - o2 // 2 + H, 300 - o2:300 - o2 + W]
        h1 = (np.clip((a - 0.38) * 2.4, 0, 1) ** 1.3)[..., None]
        h2 = (np.clip((b - 0.42) * 2.6, 0, 1) ** 1.3)[..., None]
        light = (self.amber * self.key * 0.60 + self.deep * self.key * 0.22
                 + self.side_c * self.side * 0.50 + self.amber * self.wash * 0.10)
        haze = light * (0.32 + 0.95 * h1) + self.side_c * self.side * h2 * 0.45
        haze = haze + self.amber * self.beam * (0.08 + 0.25 * h1)
        img = 1 - (1 - self.base) * (1 - np.clip(haze, 0, 1))  # screen
        return img, h1


def finish(img):
    """Vignette + dither so dark gradients survive H.264."""
    vr = np.sqrt(((X - 0.55) / 0.8) ** 2 + ((Y - 0.5) / 0.75) ** 2)[..., None]
    img = img * (1 - 0.5 * np.clip(vr, 0, 1) ** 2.4)
    noise = (np.random.default_rng(7).random((H, W, 1), np.float32) - 0.5) * (2.5 / 255)
    return np.clip(img + noise, 0, 1)


def blur(a, radius):
    return np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius)),
                      np.float32) / 255


def shift(a, dx, mirror=False):
    out = np.zeros_like(a)
    out[:, dx:] = a[:, :W - dx]
    if mirror:
        out[:, :dx] = a[:, :dx][:, ::-1]
    return out


def frame_reader(video):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", video, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE)
    while True:
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        yield np.frombuffer(buf, np.uint8).reshape(H, W, 3)


class Masks:
    def __init__(self, path):
        z = np.load(path)
        self.packed, self.T = z["masks"], int(z["shape"][0])

    def get(self, i):
        i = min(max(i, 0), self.T - 1)
        m = np.unpackbits(self.packed[i], axis=-1, count=W).astype(np.float32)
        # Keep only her: the heaviest run of occupied columns (drops slivers SAM picks up at the frame edge).
        cols = m.sum(0)
        occupied = np.where(cols > 0)[0]
        if len(occupied):
            runs = np.split(occupied, np.where(np.diff(occupied) > 30)[0] + 1)
            best = max(runs, key=lambda r: cols[r].sum())
            keep = np.zeros(W, bool)
            keep[best[0]:best[-1] + 1] = True
            m[:, ~keep] = 0
        return m

    def smooth(self, i):
        return np.mean([self.get(j) for j in range(i - SMOOTH, i + SMOOTH + 1)], axis=0)


def find_seam(rgb, mask):
    """Row where the dark curtain foot meets the floor, measured off the dancer."""
    y0, y1 = SEAM_BAND
    lum = rgb[y0:y1].astype(np.float32).mean(2)
    keep = mask[y0:y1] < 0.5
    rows = np.where(keep.sum(1) > 50, (lum * keep).sum(1) / np.maximum(keep.sum(1), 1), 255)
    dark = int(np.argmin(rows))
    below = np.where(rows[dark:] > rows[dark] + 60)[0]   # first clearly lit floor row
    return y0 + dark + (int(below[0]) if len(below) else 8)


class SeamTracker:
    def __init__(self):
        self.v = None

    def __call__(self, raw):
        self.v = raw if self.v is None else 0.85 * self.v + 0.15 * raw
        return self.v


def composite(rgb_u8, alpha, backdrop, n, seam):
    rgb = rgb_u8.astype(np.float32) / 255
    a = np.clip((blur(alpha, 1.0) - 0.08) / 0.84, 0, 1)

    # Her: pull the blue curtain spill out of her edges only (keeps the purple dupatta intact), warm slightly.
    edge = ((a > 0.02) & (a < 0.9))[..., None]
    her = rgb.copy()
    her[..., 2] = np.where(edge[..., 0], np.minimum(rgb[..., 2], np.maximum(rgb[..., 0], rgb[..., 1])), rgb[..., 2])
    her = np.clip(her * np.array([1.06, 0.98, 0.90], np.float32), 0, 1)

    # The real stage: darker overall, a pool of light around her feet, front edge in shadow.
    stage = rgb * np.array([1.0, 0.92, 0.80], np.float32)
    her, a = shift(her, SHIFT_X), shift(a, SHIFT_X)
    stage = shift(stage, SHIFT_X, mirror=True)
    cols = np.where(a[int(seam):int(seam) + 40].sum(0) > 0.5)[0]
    px = (cols.min() + cols.max()) / 2 if len(cols) else W * (0.51 + SHIFT_X / W)
    pool = np.exp(-(((XX - px) / 230) ** 2 + ((YY - seam - 25) / 55) ** 2))
    gain = 0.38 + 0.62 * pool
    gain *= 1 - 0.55 * smoothstep(seam + FRONT_OFFSET - 4, seam + FRONT_OFFSET + 6, YY)
    stage = stage * gain[..., None]

    bg, haze = backdrop.render(n)
    floor_w = smoothstep(seam - 7, seam + 5, YY)[..., None]
    out = bg * (1 - floor_w) + stage * floor_w

    # Haze drifts a little over the back of the floor to blend the seam.
    spill = (np.exp(-np.clip(YY - seam, 0, None) / 18) * (YY > seam - 7))[..., None]
    out = 1 - (1 - out) * (1 - np.clip(backdrop.amber * backdrop.key * haze * spill * 0.5, 0, 1))

    # Warm halo behind her so she reads as lit by the haze.
    halo = blur(a, 28)[..., None] * (1 - floor_w)
    out = 1 - (1 - out) * (1 - backdrop.amber * halo * 0.35)

    # A touch more contrast on her, then let the haze light wrap onto her edges.
    her = np.clip((her - 0.5) * 1.08 + 0.5, 0, 1)
    wrap = (np.clip((1 - blur(a, 5)) * a * 1.6, 0, 1) * 0.45)[..., None]
    lit = 1 - (1 - her) * (1 - np.stack([blur(out[..., c], 8) for c in range(3)], -1))
    her = her * (1 - wrap) + lit * wrap

    a3 = a[..., None]
    return finish(out * (1 - a3) + her * a3)


def to_u8(img):
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


def initial_seam(video, masks):
    for i, rgb in enumerate(frame_reader(video)):
        return find_seam(rgb, masks.get(i))


def main():
    mode, video, masks_path = sys.argv[1:4]
    masks = Masks(masks_path)
    seam0 = initial_seam(video, masks)
    print(f"{masks.T} mask frames, stage seam at y={seam0}", flush=True)
    track = SeamTracker()

    if mode == "preview":
        out_dir, side = Path(sys.argv[4]), sys.argv[5]
        out_dir.mkdir(parents=True, exist_ok=True)
        backdrop = Backdrop(side, seam0)
        wanted = {int(f) for f in sys.argv[6:]} or {0, 600, 1200, 1800}
        for i, rgb in enumerate(frame_reader(video)):
            seam = track(find_seam(rgb, masks.get(i)))
            if i in wanted:
                img = composite(rgb, masks.smooth(i), backdrop, i // STEP, seam)
                Image.fromarray(to_u8(img)).save(out_dir / f"{side.strip('#')}-f{i:04d}.jpg", quality=90)
                print(f"frame {i}: seam {seam:.1f}", flush=True)
            if i >= max(wanted):
                break
        return

    out_mp4, poster, side = sys.argv[4], sys.argv[5], sys.argv[6]
    backdrop = Backdrop(side, seam0)
    raw = str(Path(masks_path).parent / "_hero_raw.mp4")
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", raw],
        stdin=subprocess.PIPE)
    n = 0
    for i, rgb in enumerate(frame_reader(video)):
        seam = track(find_seam(rgb, masks.get(i)))
        if i % STEP:
            continue
        enc.stdin.write(to_u8(composite(rgb, masks.smooth(i), backdrop, n, seam)).tobytes())
        n += 1
        if n % 100 == 0:
            print(f"{n} frames", flush=True)
    enc.stdin.close()
    enc.wait()

    # Seamless loop: drop the first second and crossfade the clip's tail into it.
    dur = n / FPS
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", raw, "-filter_complex",
         f"[0]trim=start={XFADE_S},setpts=PTS-STARTPTS,fps={FPS}[a];"
         f"[0]trim=end={XFADE_S},setpts=PTS-STARTPTS,fps={FPS}[b];"
         f"[a][b]xfade=transition=fade:duration={XFADE_S}:offset={dur - 2 * XFADE_S},format=yuv420p",
         "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "24", "-profile:v", "high", "-movflags", "+faststart",
         out_mp4], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "2", "-i", out_mp4, "-frames:v", "1", "-q:v", "3", poster],
                   check=True)
    print(f"wrote {out_mp4} ({n} frames, {dur - XFADE_S:.1f}s loop)")


if __name__ == "__main__":
    main()
