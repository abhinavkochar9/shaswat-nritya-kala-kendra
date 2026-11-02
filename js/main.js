// EDIT: contact details used by the enquiry form and WhatsApp button.
const SITE = {
  email: "snigdha.tripathi26@icloud.com",
  // WhatsApp number in international format, digits only (e.g. "919876543210").
  // While empty, the WhatsApp button stays as a placeholder link.
  whatsapp: "",
  whatsappGreeting: "Namaste Snigdha ji, I'd like to know more about your dance classes.",
};

// ---------- Header state ----------
const header = document.querySelector(".site-header");
const onScroll = () => header.classList.toggle("is-scrolled", window.scrollY > 24);
onScroll();
window.addEventListener("scroll", onScroll, { passive: true });

// ---------- Hero background video ----------
// Starts only when motion is welcome, pauses off-screen, and the button
// lets visitors stop it (WCAG 2.2.2).
const heroVideo = document.querySelector(".hero__video");
const heroPause = document.querySelector(".hero__pause");

if (heroVideo && heroPause) {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const icon = heroPause.querySelector("use");
  const label = heroPause.querySelector(".hero__pause-label");
  let userPaused = reduceMotion;

  const sync = () => {
    const paused = heroVideo.paused;
    heroPause.setAttribute("aria-pressed", String(paused));
    icon.setAttribute("href", paused ? "#i-play" : "#i-pause");
    label.textContent = paused ? "Play video" : "Pause video";
  };
  const play = () => heroVideo.play().catch(() => {});

  heroPause.addEventListener("click", () => {
    userPaused = !heroVideo.paused;
    userPaused ? heroVideo.pause() : play();
  });
  heroVideo.addEventListener("play", sync);
  heroVideo.addEventListener("pause", sync);

  let inView = true;
  if (!userPaused) play();
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(([entry]) => {
      inView = entry.isIntersecting;
      if (userPaused) return;
      inView ? play() : heroVideo.pause();
    }).observe(heroVideo);
  }
  // Browsers pause muted video in hidden tabs; pick it back up when the tab returns.
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden && inView && !userPaused) play();
  });
  sync();
}

// ---------- Mobile menu ----------
const toggle = document.querySelector(".nav__toggle");
const menu = document.getElementById("site-menu");

function setMenu(open) {
  toggle.setAttribute("aria-expanded", String(open));
  toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  document.body.classList.toggle("menu-open", open);
}

toggle.addEventListener("click", () => setMenu(toggle.getAttribute("aria-expanded") !== "true"));
menu.addEventListener("click", (e) => { if (e.target.closest("a")) setMenu(false); });
document.addEventListener("keydown", (e) => { if (e.key === "Escape") setMenu(false); });
window.matchMedia("(min-width: 961px)").addEventListener("change", () => setMenu(false));

// ---------- Reveal on scroll ----------
const revealEls = document.querySelectorAll(".reveal");
if ("IntersectionObserver" in window) {
  const io = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      entry.target.classList.add("is-visible");
      io.unobserve(entry.target);
    }
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
  revealEls.forEach((el) => io.observe(el));
} else {
  revealEls.forEach((el) => el.classList.add("is-visible"));
}

// ---------- Active nav link ----------
// Every section is watched, so the highlight clears over sections that have no nav link.
const navLinks = [...document.querySelectorAll('.nav__links a[href^="#"]')];
const navSections = document.querySelectorAll("main section[id]");

if ("IntersectionObserver" in window) {
  const navIO = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      const id = `#${entry.target.id}`;
      navLinks.forEach((a) => a.classList.toggle("is-active", a.getAttribute("href") === id));
    }
  }, { rootMargin: "-45% 0px -50% 0px" });
  navSections.forEach((s) => navIO.observe(s));
}

// ---------- Videos (load the player only on click) ----------
document.querySelectorAll(".yt").forEach((el) => {
  const id = el.dataset.ytId;
  const src = el.dataset.videoSrc;
  const button = el.querySelector(".yt__play");

  if (src) {
    if (el.dataset.poster) el.style.backgroundImage = `url("${el.dataset.poster}")`;
    button.setAttribute("aria-label", `Play video: ${el.dataset.title || "video"}`);
    button.addEventListener("click", () => {
      const video = document.createElement("video");
      video.src = src;
      if (el.dataset.poster) video.poster = el.dataset.poster;
      video.controls = true;
      video.autoplay = true;
      video.playsInline = true;
      el.replaceChildren(video);
    });
    return;
  }

  if (!id) {
    el.classList.add("yt--empty");
    button.disabled = true;
    button.setAttribute("aria-label", "Video coming soon");
    return;
  }

  el.style.backgroundImage = `url("https://i.ytimg.com/vi/${encodeURIComponent(id)}/hqdefault.jpg")`;
  button.setAttribute("aria-label", `Play video: ${el.dataset.title || "video"}`);
  button.addEventListener("click", () => {
    const iframe = document.createElement("iframe");
    iframe.src = `https://www.youtube-nocookie.com/embed/${encodeURIComponent(id)}?autoplay=1&rel=0`;
    iframe.title = el.dataset.title || "Video";
    iframe.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
    iframe.allowFullscreen = true;
    el.replaceChildren(iframe);
  });
});

// ---------- Gallery lightbox ----------
const lightbox = document.getElementById("lightbox");
const lbStage = lightbox.querySelector(".lightbox__stage");
const lbCaption = lightbox.querySelector(".lightbox__caption");
const galleryItems = [...document.querySelectorAll(".gallery__item")];
let lbIndex = 0;

function showItem(index) {
  lbIndex = (index + galleryItems.length) % galleryItems.length;
  const item = galleryItems[lbIndex];
  const img = item.querySelector("img");

  if (img) {
    const full = document.createElement("img");
    full.src = img.dataset.full || img.currentSrc || img.src;
    full.alt = img.alt;
    lbStage.replaceChildren(full);
  } else {
    lbStage.replaceChildren(item.querySelector(".frame").cloneNode(true));
  }
  lbCaption.textContent = item.querySelector("figcaption")?.textContent ?? "";
}

galleryItems.forEach((item, i) => {
  item.querySelector(".gallery__open").addEventListener("click", () => {
    showItem(i);
    lightbox.showModal();
  });
});

lightbox.querySelector(".lightbox__close").addEventListener("click", () => lightbox.close());
lightbox.querySelector(".lightbox__prev").addEventListener("click", () => showItem(lbIndex - 1));
lightbox.querySelector(".lightbox__next").addEventListener("click", () => showItem(lbIndex + 1));
lightbox.addEventListener("click", (e) => { if (e.target === lightbox) lightbox.close(); });
lightbox.addEventListener("keydown", (e) => {
  if (e.key === "ArrowLeft") showItem(lbIndex - 1);
  if (e.key === "ArrowRight") showItem(lbIndex + 1);
});

// ---------- WhatsApp ----------
document.querySelectorAll("[data-whatsapp]").forEach((a) => {
  if (!SITE.whatsapp) return;
  a.href = `https://wa.me/${SITE.whatsapp}?text=${encodeURIComponent(SITE.whatsappGreeting)}`;
  a.target = "_blank";
  a.rel = "noopener";
});

// ---------- Enquiry form ----------
// Opens the visitor's email app with the enquiry filled in.
// Once the domain is live, this can be switched to a form service
// (Formspree / Web3Forms) so messages send directly from the page.
const form = document.getElementById("enquiry-form");
const status = form.querySelector(".form__status");

form.addEventListener("submit", (e) => {
  e.preventDefault();

  let valid = true;
  form.querySelectorAll("input, select, textarea").forEach((field) => {
    const ok = field.checkValidity();
    field.closest(".field").classList.toggle("is-invalid", !ok);
    if (!ok && valid) field.focus();
    valid &&= ok;
  });
  if (!valid) {
    status.textContent = "Please fill in the highlighted fields.";
    return;
  }

  const data = new FormData(form);
  const subject = `Enquiry: ${data.get("interest")} — ${data.get("name")}`;
  const body = [
    `Name: ${data.get("name")}`,
    `Email: ${data.get("email")}`,
    `Phone: ${data.get("phone") || "—"}`,
    `About: ${data.get("interest")}`,
    "",
    data.get("message"),
  ].join("\n");

  window.location.href = `mailto:${SITE.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  status.textContent = `If your email app didn't open, write to ${SITE.email}.`;
});

form.addEventListener("input", (e) => {
  const field = e.target.closest(".field");
  if (field && e.target.checkValidity()) field.classList.remove("is-invalid");
});

// ---------- Footer year ----------
document.getElementById("year").textContent = new Date().getFullYear();
