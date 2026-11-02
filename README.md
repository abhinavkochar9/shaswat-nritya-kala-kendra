# Shashwat Nritya Kala Kendra — website

Live draft: https://abhinavkochar9.github.io/shaswat-nritya-kala-kendra/

One-page static site for Shashwat Nritya Kala Kendra, the Kathak academy founded by Snigdha Tripathi. Plain HTML, CSS and JavaScript —
no build step. Open `index.html` through any static server, e.g.

```bash
python3 -m http.server 8791
```

## Files

- `index.html` — all content. The text comes from the Kendra's own write-up, kept in its words;
  spots that still need information have an `<!-- EDIT -->` comment.
- `css/styles.css` — palette and fonts are the variables at the top of the file.
- `js/main.js` — `SITE.email` (used by the enquiry form), hero video controls, gallery viewer.
- `assets/images/` — web-sized photos (EXIF/GPS stripped), transparent cut-outs (`cutout-*.webp`) and the
  round logo badge (`logo.webp`, `logo-160.webp`). `assets/favicon.png` and `apple-touch-icon.png` come from the same logo.
- `assets/video/hero-loop.mp4` — the silent background loop in the hero: her performance clip at
  half speed, with the curtain and banner replaced by a hazy theatre backdrop (she and the real stage floor are
  kept). How it was made: `tools/hero-video/README.md`.
- `assets/video/performance.mp4` — the original clip with sound, in the Videos section.

## Still to fill in

The page only states what the Kendra has written about itself, plus the phone and email. Anything new
waits for her own words:

- More photos and videos; higher-resolution originals of the student group photo and the certificate
  photo (the current ones are WhatsApp-compressed).
- YouTube / Instagram links if she wants them shown.
- Consent: the student group photo shows children — check the parents are happy with it online.

## Swapping media

- **Gallery photo:** copy an existing real `gallery__item` block, change `src`, `width`, `height`,
  `--ar` (width/height) and the caption.
- **Video from YouTube:** put the ID (the part after `v=`) in `data-yt-id`.
- **Video file:** use `data-video-src` and `data-poster` like the featured video.

## Contact form

The form opens the visitor's email app with the message filled in. Once the site has a domain,
it can post to a form service (Formspree, Web3Forms) so messages send directly.

## Deploying

The draft is served by GitHub Pages from the `main` branch: push to `main` and it updates in a minute or two.
When her domain is ready, add it under the repository's Settings → Pages (or move to any static host) and
change `og:url` / `og:image` in `index.html` to the new address.
