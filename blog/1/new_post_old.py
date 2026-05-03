#!/usr/bin/env python3
"""
SoloMinerClinic — Repair Blog Generator
Run: python new_repair_post.py
Outputs a ready-to-upload .html file.
"""

import re
from datetime import datetime
from pathlib import Path


# ── Helpers ────────────────────────────────────────────────────────────────

def ask(prompt, default=None):
    suffix = f" [{default}]" if default else ""
    val = input(f"{prompt}{suffix}: ").strip()
    return val if val else default

def ask_multiline(prompt):
    print(f"{prompt} (blank line to finish):")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    return " ".join(lines)

def ask_imgur_links():
    print("\nPaste Imgur image URLs one per line (blank line to finish):")
    print("  e.g. https://i.imgur.com/xxxxxxx.jpeg")
    urls = []
    while True:
        url = input(f"  Image {len(urls)+1}: ").strip()
        if not url:
            break
        if not url.startswith("http"):
            print("  ⚠  Doesn't look like a URL, skipping.")
            continue
        urls.append(url)
    return urls

def slugify(text):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text

def build_gallery_imgs(urls):
    if not urls:
        return '    <img src="https://i.imgur.com/PLACEHOLDER.jpeg" loading="lazy">\n'
    return "\n".join(
        f'    <img src="{u}" loading="lazy">' for u in urls
    ) + "\n"

def build_sections(sections):
    html = ""
    for title, body in sections:
        html += f"\n    <h2>{title}</h2>\n    <p>{body}</p>\n"
    return html


# ── HTML template ──────────────────────────────────────────────────────────

TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Doctor's Notes — {title} | SoloMinerClinic</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
:root {{
  --orange: #F7931A;
  --dark: #0D0D0D;
  --card: #161616;
  --border: rgba(255,255,255,0.08);
  --text: #F5F5F5;
  --muted: #9a9a9a;
  --white: #FFFFFF;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Inter', sans-serif; background: var(--dark); color: var(--text); }}

/* HEADER */
header {{
  position: sticky; top: 0;
  background: rgba(13,13,13,0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border);
}}
.header-title {{ text-align: center; padding: 1rem; }}
.header-title a {{
  font-family: 'Space Mono', monospace;
  color: var(--orange); text-decoration: none; font-size: 1.4rem;
}}

/* LAYOUT */
.blog-wrap {{ max-width: 760px; margin: 0 auto; padding: 2rem 1.2rem 4rem; }}

.blog-meta {{
  font-family: 'Space Mono', monospace;
  font-size: 0.75rem; color: var(--muted);
  margin-bottom: 1rem; letter-spacing: 0.1em;
}}
.blog-title {{
  font-size: clamp(1.8rem, 4vw, 2.4rem);
  font-weight: 600; margin-bottom: 1rem;
}}
.blog-sub {{ font-size: 1rem; color: var(--muted); margin-bottom: 2rem; line-height: 1.7; }}

/* LIGHTBOX */
.lightbox {{
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.95);
  display: none; justify-content: center; align-items: center;
  z-index: 999; cursor: zoom-out;
}}
.lightbox.open {{ display: flex; }}
.lightbox-img {{
  max-width: 95vw; max-height: 90vh;
  border-radius: 10px; object-fit: contain; cursor: default;
}}
.lightbox-close {{
  position: fixed; top: 16px; right: 22px;
  color: white; font-size: 2rem; cursor: pointer;
  line-height: 1; opacity: 0.7; transition: opacity 0.2s;
  background: none; border: none;
}}
.lightbox-close:hover {{ opacity: 1; }}

/* GALLERY */
.gallery-wrap {{ position: relative; margin: 2rem 0; }}
.arrow {{
  position: absolute; top: 50%; transform: translateY(-50%);
  background: rgba(0,0,0,0.6); border: 1px solid var(--border);
  color: white; font-size: 22px; padding: 8px 14px;
  cursor: pointer; z-index: 2; border-radius: 6px; line-height: 1;
  transition: background 0.2s;
}}
.arrow.left {{ left: 8px; }}
.arrow.right {{ right: 8px; }}
.arrow:hover {{ background: rgba(255,255,255,0.15); }}
.gallery {{
  display: flex; gap: 10px;
  overflow-x: auto; scroll-snap-type: x mandatory;
  padding-bottom: 8px; cursor: grab;
  -webkit-overflow-scrolling: touch;
}}
.gallery:active {{ cursor: grabbing; }}
.gallery::-webkit-scrollbar {{ display: none; }}
.gallery img {{
  flex: 0 0 85%; max-width: 85%;
  border-radius: 10px; border: 1px solid var(--border);
  scroll-snap-align: center; cursor: zoom-in;
  object-fit: cover; aspect-ratio: 4/3;
  user-select: none; -webkit-user-drag: none;
}}

/* CONTENT */
.blog-content {{ font-size: 1rem; line-height: 1.9; }}
.blog-content p {{ margin-bottom: 1.4rem; color: #ddd; }}
.blog-content h2 {{ margin-top: 2.5rem; margin-bottom: 0.8rem; font-size: 1.25rem; }}
.blog-back {{
  display: inline-block; margin-top: 3rem;
  font-size: 0.9rem; color: var(--orange); text-decoration: none;
}}
footer {{
  border-top: 1px solid var(--border);
  padding: 2rem; text-align: center;
  color: var(--muted); font-size: 0.8rem;
}}

@media (max-width: 600px) {{
  .gallery img {{ flex: 0 0 90%; max-width: 90%; }}
}}
</style>
</head>
<body>

<header>
  <div class="header-title">
    <a href="index.html">SoloMinerClinic</a>
  </div>
</header>

<div class="blog-wrap">

  <div class="blog-meta">REPAIR CASE · {date}</div>

  <h1 class="blog-title">{title}</h1>

  <div class="blog-sub">{subtitle}</div>

  <div class="gallery-wrap">
    <button class="arrow left" onclick="scrollGallery(-1)">&#8249;</button>
    <div class="gallery">
{gallery_imgs}    </div>
    <button class="arrow right" onclick="scrollGallery(1)">&#8250;</button>
  </div>

  <div class="blog-content">

    <p>{intro}</p>
{sections}
  </div>

  <a href="blog.html" class="blog-back">&#8592; Back to Doctor's Notes</a>

</div>

<footer>© {year} Solo Miner Clinic. All rights reserved.</footer>

<div id="lightbox" class="lightbox">
  <button class="lightbox-close">&times;</button>
  <img class="lightbox-img" src="" alt="">
</div>

<script>
document.addEventListener("DOMContentLoaded", () => {{
  const gallery  = document.querySelector('.gallery');
  const lightbox = document.getElementById('lightbox');
  const lbImg    = lightbox.querySelector('.lightbox-img');
  const closeBtn = lightbox.querySelector('.lightbox-close');
  let isDown = false, startX, scrollLeft, wasDragging = false;

  // Lightbox open/close
  function openLightbox(src) {{
    lbImg.src = src;
    lightbox.classList.add('open');
    document.body.style.overflow = 'hidden';
  }}
  function closeLightbox() {{
    lightbox.classList.remove('open');
    document.body.style.overflow = '';
  }}
  gallery.querySelectorAll('img').forEach(img => {{
    img.addEventListener('click', () => {{ if (!wasDragging) openLightbox(img.src); }});
  }});
  closeBtn.addEventListener('click', closeLightbox);
  lightbox.addEventListener('click', e => {{ if (e.target !== lbImg) closeLightbox(); }});
  document.addEventListener('keydown', e => {{ if (e.key === 'Escape') closeLightbox(); }});

  // Arrow scroll
  window.scrollGallery = dir =>
    gallery.scrollBy({{ left: dir * gallery.clientWidth * 0.85, behavior: 'smooth' }});

  // Mouse drag
  gallery.addEventListener('mousedown', e => {{
    isDown = true; wasDragging = false;
    startX = e.pageX - gallery.offsetLeft;
    scrollLeft = gallery.scrollLeft;
  }});
  gallery.addEventListener('mouseleave', () => {{ isDown = false; }});
  gallery.addEventListener('mouseup',    () => {{ isDown = false; }});
  gallery.addEventListener('mousemove', e => {{
    if (!isDown) return;
    e.preventDefault();
    const dx = (e.pageX - gallery.offsetLeft - startX) * 1.5;
    if (Math.abs(dx) > 4) wasDragging = true;
    gallery.scrollLeft = scrollLeft - dx;
  }});

  // Touch
  let touchStartX = 0;
  gallery.addEventListener('touchstart', e => {{ touchStartX = e.touches[0].clientX; }}, {{ passive: true }});
  gallery.addEventListener('touchend', e => {{
    wasDragging = Math.abs(e.changedTouches[0].clientX - touchStartX) > 10;
    setTimeout(() => {{ wasDragging = false; }}, 100);
  }});
}});
</script>

</body>
</html>
"""


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print("=" * 52)
    print("  SoloMinerClinic — New Repair Blog Post")
    print("=" * 52)

    # Basic info
    today = datetime.now()
    date_default = today.strftime("%b %d %Y").upper()   # e.g. APR 18 2026

    title    = ask("\nPost title (e.g. 'VRM Failure — Patient Was at 100W')")
    subtitle = ask("Subtitle / one-liner (shown under title)")
    date_str = ask("Date", default=date_default)
    intro    = ask_multiline("\nIntro paragraph (what arrived, what was wrong)")

    # Sections (Diagnosis / Surgery / Recovery or custom)
    print("\n── Sections ──────────────────────────────────────")
    print("Default sections: Diagnosis, Surgery, Recovery")
    custom = ask("Use custom section names? (y/n)", default="n")

    sections = []
    if custom.lower() == "y":
        print("Enter section names one by one (blank to stop):")
        while True:
            sec_title = input("  Section name: ").strip()
            if not sec_title:
                break
            sec_body = ask_multiline(f"  {sec_title} text")
            sections.append((sec_title, sec_body))
    else:
        for name in ["Diagnosis", "Surgery", "Recovery"]:
            body = ask_multiline(f"\n{name}")
            sections.append((name, body))

    # Images
    print("\n── Images ────────────────────────────────────────")
    img_urls = ask_imgur_links()

    # Build output
    filename = slugify(title) + ".html"
    output_path = Path(filename)

    html = TEMPLATE.format(
        title        = title,
        subtitle     = subtitle,
        date         = date_str,
        year         = today.year,
        intro        = intro,
        gallery_imgs = build_gallery_imgs(img_urls),
        sections     = build_sections(sections),
    )

    output_path.write_text(html, encoding="utf-8")

    print("\n" + "=" * 52)
    print(f"  ✅  Saved: {filename}")
    print(f"  📷  Images: {len(img_urls)}")
    print(f"  📝  Sections: {len(sections)}")
    print("=" * 52)


if __name__ == "__main__":
    main()
