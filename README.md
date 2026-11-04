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
- `assets/images/` — the round logo badge (`logo.webp`, `logo-160.webp`) and `share.jpg`, the logo image that
  link previews (WhatsApp etc.) show. `assets/favicon.png` and `apple-touch-icon.png` come from the same logo.
  Photos go here web-sized, with EXIF/GPS stripped.
- `assets/video/hero-loop.mp4` — the silent background loop in the hero: her performance clip at
  half speed, with the curtain and banner replaced by a hazy theatre backdrop (she and the real stage floor are
  kept). How it was made: `tools/hero-video/README.md`.
- `assets/video/performance.mp4` — the original clip with sound, in the Videos section.

## Still to fill in

The page only states what the Kendra has written about itself, plus the phone and email. Anything new
waits for her own words:

- Pictures. Her photos were taken off the site at the family's request (Nov 2026); they are sending other
  pictures. The Founder and Performances sections each hold an empty arch slot (marked `EDIT`), and the
  Gallery section is off until there are photos for it.
- YouTube / Instagram links if she wants them shown.
- Consent: any photo that shows children — check the parents are happy with it online.

## Swapping media

- **Gallery:** the section's markup is in commit `5ba0458` (between Performances and Videos). Bring it back,
  then per photo copy a `gallery__item` block and change `src`, `width`, `height`, `--ar` (width/height) and the caption.
  Add the Gallery link back to the header and footer, and renumber the section labels.
- **Video from YouTube:** put the ID (the part after `v=`) in `data-yt-id`.
- **Video file:** use `data-video-src` and `data-poster` like the featured video.

## Contact form

The form opens the visitor's email app with the message filled in. Once the site has a domain,
it can post to a form service (Formspree, Web3Forms) so messages send directly.

## Deploying

The draft is served by GitHub Pages from the `main` branch: push to `main` and it updates in a minute or two.
When her domain is ready, add it under the repository's Settings → Pages (or move to any static host) and
change `og:url` / `og:image` in `index.html` to the new address.
