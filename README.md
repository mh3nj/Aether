# Aether v2.2

![Version](https://img.shields.io/badge/version-2)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.9+-yellow)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20mac%20%7C%20linux-lightgrey)
![Offline](https://img.shields.io/badge/works-offline-brightgreen)
![Size](https://img.shields.io/badge/size-10MB-blue)
![Built in Iran](https://img.shields.io/badge/built%20in-iran-red)
![GitHub Stars](https://img.shields.io/github/stars/mh3nj/Aether?style=social)

<img src="/assets/banner.webp" alt="Aether banner" />

> **12 tools. one app. fully offline. built solo in one month.**  
> everything a web developer or SEO specialist needs; without switching between 12 different tabs, services, or subscriptions.

---

## the problem this solves

if you've ever finished building a website and then spent hours on SEO setup, meta tags, schema generation, image optimization, broken link checks, accessibility scans;you know how much time that eats.

aether does all of it in one place. injection into your HTML. batch operations across hundreds of files. no cloud. no subscription. no data leaving your machine.

built by a full-time web developer who got tired of the same painful post-launch workflow.

---

## what's new in v2.2

two real features. not just a readme update.

### smart video lazy loader

the standard way to load videos on a page is to load all of them at once. this is a bad idea when you have more than two or three;your page slows down, RAM spikes, and users on mobile or limited data plans suffer.

aether's smart video lazy loader works differently. when a video is off-screen, it shows a low-resolution crystalline placeholder. when the user scrolls to it, aether starts downloading the video in **5 parallel chunks simultaneously**;similar to how advanced download managers work;then assembles them seamlessly and displays the video as one piece. faster start, smoother playback, no wasted bandwidth on videos the user never reaches.

for users in countries where internet costs money per megabyte, this matters a lot.

| | v2.0 | v2.2 |
|--|------|------|
| load time (20 videos) | 4–6 seconds | ~1 second |
| RAM usage | 400–600MB | 80–120MB |
| videos loaded before scrolling | all of them | zero |

### smart image lazy loader (upgraded)

same philosophy for images. when a high-resolution image is off-screen, aether generates a tiny WebP preview;same dimensions, same format, but compressed down to roughly 2KB regardless of the original file size. that preview loads almost instantly and is displayed as a soft blur placeholder.

while the user sees the preview, the full-quality image downloads silently in the background. the moment it's ready, it replaces the placeholder seamlessly;no layout shift, no pop-in.

every original image, regardless of format, is automatically converted to lossless WebP during this process. smaller file, better quality, faster load. the compression is tuned automatically to find the best lossless result.

### code humanizer

early stage, but functional. lowercases all comments across your codebase, removes the obvious AI-generated phrasing that makes code feel like it was written by a documentation bot. batch operation across files. the roadmap for this one goes much further;this is just the foundation.

`Ctrl+H` to open it.

---

## the 12 tools (31 features)

| tab | what's inside |
|-----|--------------|
| Dashboard | real-time SEO health score, key metrics, recent activity, quick actions |
| Code Studio | python/js/ts/html/css formatter with split before/after diff view, print CSS, speech CSS |
| SEO Command | meta tag editor, hreflang generator, 0–100 page scorer, duplicate detector, meta refresh checker |
| Schema & Social | JSON-LD for 8 schema types, OG preview, Twitter card preview, breadcrumb builder |
| Media Studio | favicon generator, WebP converter, smart image lazy loader, smart video lazy loader |
| Link Studio | bulk find/replace (regex), broken link checker, orphan page detection, internal link suggestions |
| Accessibility Hub | WCAG compliance, alt text fixer, spell checker, heading hierarchy checker |
| Performance Lab | preload scanner, PageSpeed Insights, Core Web Vitals (LCP, CLS, FID) |
| Security & Backup | CSP generator, SRI hash generator, timestamped backups, one-click restore |
| Analytics | keyword density analysis, SEO score history tracking |
| Batch Ops | bulk meta updates across hundreds of files, robots.txt, sitemap.xml, image & video sitemaps |
| Code Humanizer | lowercases comments, strips AI phrasing;more coming |
| Logs | full operation history, type filters, search, CSV export |

everything has automatic HTML injection. you point aether at your project folder and it handles the rest.

---

## screenshots

<div align="center">
  <table>
    <tr>
      <td align="center"><img src="/screenshots/screenshot01.png" width="100%" alt="Dashboard"><br/><sub>dashboard</sub></td>
      <td align="center"><img src="/screenshots/screenshot02.png" width="100%" alt="Code Studio"><br/><sub>code studio</sub></td>
    </tr>
    <tr>
      <td align="center"><img src="/screenshots/screenshot03.png" width="100%" alt="Media Studio"><br/><sub>media studio</sub></td>
      <td align="center"><img src="/screenshots/screenshot04.png" width="100%" alt="Code Humanizer"><br/><sub>code humanizer (new)</sub></td>
    </tr>
    <tr>
      <td align="center"><img src="/screenshots/screenshot05.png" width="100%" alt="Media Studio"><br/><sub>media studio</sub></td>
      <td align="center"><img src="/screenshots/screenshot06.png" width="100%" alt="Code Humanizer"><br/><sub>code humanizer (new)</sub></td>
    </tr>
    <tr>
      <td align="center"><img src="/screenshots/screenshot7.png" width="100%" alt="Dark Mode"><br/><sub>dark mode</sub></td>
      <td align="center"><img src="/screenshots/screenshot8.png" width="100%" alt="Light Mode"><br/><sub>light mode</sub></td>
    </tr>
  </table>
</div>

---

## getting started

### windows

download `aether-launcher.bat` and run it. that's it.

it will check your python version, clone the repo, set up a virtual environment, install dependencies, and launch aether;automatically. if something is missing it tells you exactly what and where to get it.

```
aether-launcher.bat
```

if Windows Defender flags it, click "more info" → "run anyway". it's a setup script, not malware;you can read every line of it before running.

### mac / linux

download `aether-launcher.sh`, make it executable, and run it:

```bash
chmod +x aether-launcher.sh
./aether-launcher.sh
```

same as the windows version;checks python, clones the repo, sets up the environment, launches aether.

### manual setup (if you prefer)

```bash
git clone https://github.com/mh3nj/Aether.git
cd Aether
python -m venv .venv

# windows:
.venv\Scripts\activate
# mac/linux:
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

### requirements

- python 3.9+
- 4GB RAM (8GB recommended if you tend to have a lot open)
- internet only for PageSpeed Insights;everything else is fully offline

---

## keyboard shortcuts

| shortcut | tab |
|----------|-----|
| Ctrl+1 | Dashboard |
| Ctrl+2 | Code Studio |
| Ctrl+3 | SEO Command |
| Ctrl+4 | Schema & Social |
| Ctrl+5 | Media Studio |
| Ctrl+6 | Link Studio |
| Ctrl+7 | Accessibility Hub |
| Ctrl+8 | Performance Lab |
| Ctrl+9 | Security & Backup |
| Ctrl+0 | Analytics |
| Ctrl+B | Batch Ops |
| Ctrl+H | Code Humanizer |
| Ctrl+L | Logs |
| Ctrl+Z | Undo |
| Ctrl+Y / Ctrl+Shift+Z | Redo |
| Ctrl+Shift+T | toggle dark/light theme |

---

## project structure

```
Aether/
├── main.py                      # run this
├── ui/
│   ├── dashboard_tab.py
│   ├── code_studio_tab.py
│   ├── seo_command_tab.py
│   ├── schema_social_tab.py
│   ├── media_studio_tab.py
│   ├── link_studio_tab.py
│   ├── accessibility_hub_tab.py
│   ├── performance_lab_tab.py
│   ├── security_backup_tab.py
│   ├── analytics_tab.py
│   ├── batch_ops_tab.py
│   ├── code_humanizer_tab.py
│   ├── logs_tab.py
│   ├── sidebar.py
│   ├── undo_manager.py
│   ├── data_bridge.py
│   └── project_setup_wizard.py
├── assets/
│   ├── css/
│   ├── fonts/
│   └── logos/
├── presets/
└── requirements.txt
```

---

## dependencies

```
PySide6          # UI framework (Qt6)
BeautifulSoup4   # HTML parsing
Pillow           # image processing
requests         # PageSpeed Insights API calls
black            # python code formatting (optional)
jsbeautifier     # js/html/css formatting
pyspellchecker   # spell checking (optional)
```

---

## known issues

- windows defender may flag the .bat launcher;it's a setup script, every line is readable before you run it
- first launch takes ~30 seconds while pip installs dependencies;only happens once
- PageSpeed Insights requires internet;all other features work fully offline
- the .sh script opens nano to edit your .env on first run;if you don't have an API key yet, just close it and it'll continue
- the fontawesome icons dont load properly which i'll fix it in next versions <3

---

## development timeline

this project was built over one month, solo, from scratch.

| date | hours | what got built |
|------|-------|----------------|
| may 4 | ~10h | project architecture, formatter, SEO tools, favicon generator, WebP converter, link manager, robots.txt |
| may 5 | ~10h | schema generator, image lazy load, OG preview, image hints, link checker, SEO scorer, dark/light theme |
| may 6 | ~10h | alt text checker, CSS optimizer, keyword density, spell checker, security headers, performance scanner, batch meta updater |
| may 7 | ~10h | PageSpeed API integration, backup system, undo/redo, logs tab, tab merging (29 → 12), sidebar navigation |
| may 8 | ~8h | theme propagation fixes, cross-platform testing, documentation, v2.0 stable release |
| may 12 | ~1h | bug fixes |
| may 15 | ~1.5h | real-world testing, more bugs found |
| may 19 | ~3h | researching code humanization strategies, drawing the roadmap |
| may 21 | ~4h | planning the smart video lazy loader architecture |
| may 26 | ~2h | finding the right python approach for parallel chunk downloading |
| may 30 | ~6h | building and shipping the smart video lazy loader |
| june 1 | ~1h | edge case testing on video lazy load |
| june 2 | ~3h | standard video lazy load injection |
| june 3 | ~5h | code humanizer v1, final testing pass |
| june 4 | ~2h | repo cleanup, v2.2 stable release |
| june 10 | ~1h | planning next features |

**total: ~77 hours. one month. solo. 18,000+ lines of code. 31 features across 12 tabs.**

---

## acknowledgments

- [PySide6](https://doc.qt.io/qtforpython/);Qt for Python
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/);HTML parsing
- [Pillow](https://python-pillow.org/);image processing
- [Black](https://black.readthedocs.io/);python formatter
- [jsbeautifier](https://beautifier.io/);js/html/css formatter
- [Google PageSpeed Insights API](https://developers.google.com/speed/docs/insights/v5/get-started)
- the open source community that made all of this possible

---

## author

**Mohsen Jafari**;designed, built, and shipped this. every line.

- github: [mh3nj](https://github.com/mh3nj)
- xing: [Mohsen Jafari](https://www.xing.com/profile/Mohsen_Jafari093223/)
- [parsegan.com](https://parsegan.com);logo design work
- [dahgan.com](https://dahgan.com);land surveying / portfolio

---

## license

MIT. use it, fork it, ship it, build on it. just don't blame us if something breaks.

---

## the story behind this

this project was built during a period of severe internet restrictions in iran.

no stack overflow. no access to npm documentation. no youtube tutorials. no reliable connection to the tools most developers take for granted. just whatever was cached locally, whatever could be reasoned through from first principles, and the determination to ship something real anyway.

55 hours of focused work. 18,000+ lines of code. 31 features. 12 tools. one month. one developer.

it works. it's useful. and it was built under conditions that would have stopped most projects before they started.

**Aether;the breathing light of code.**  
*— mh3nj*
