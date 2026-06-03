<<<<<<< HEAD
# Aether v2.2

> a complete web dev toolkit. runs offline. sounds human now. built during internet restrictions in iran.

---

## what's new in v2.2

### video lazy loader
before v2.2, aether loaded every video on the page the moment you opened it. all of them. at once. your laptop fans had opinions about this.

now videos are placeholders until you scroll to them. the page loads fast. your RAM stays calm. the video loads exactly when you need it — not 3 minutes before.

**real numbers:**
| | v2.0 | v2.2 |
|--|------|------|
| load time (20 videos) | 4-6 seconds | ~1 second |
| RAM usage | 400-600MB | 80-120MB |
| laptop fan noise | yes | no |

### humanize code
v2.0 responses sounded like this:

> *"Based on the data provided, I am unable to fulfill this request as an AI language model."*

v2.2 sounds like this:

> *"Something went wrong — want me to check the config?"*

same accuracy. actual personality. there's a whole humanization layer now that strips robot phrases, adds contractions, breaks up walls of text, and adjusts tone based on context. serious question gets a serious answer. casual question gets a casual one.

---

## what aether actually is

a desktop app with 12 tools for web developers, SEO folks, and content creators. everything runs offline. nothing leaves your machine.

built in ~48 hours over 5 days. 18,000+ lines of code. started as 29 separate tools, merged into 12 that actually make sense together.

---

## the 12 tools

| tab | what it does |
|-----|-------------|
| Dashboard | real-time health score, recent activity, quick actions |
| Code Studio | format Python/JS/TS/HTML/CSS with before/after diff view |
| SEO Command | meta tags, hreflang, scoring, duplicate detection |
| Schema & Social | JSON-LD generator, OG preview, Twitter Card preview |
| Media Studio | favicon gen, WebP conversion, **video lazy loader** (new), image hints |
| Link Studio | bulk find/replace, broken link checker, orphan page detection |
| Accessibility Hub | alt text, WCAG checks, spell checker, heading hierarchy |
| Performance Lab | preload scanner, PageSpeed Insights, Core Web Vitals |
| Security & Backup | CSP generator, SRI hashes, timestamped backups |
| Analytics | keyword density, SEO score history |
| Batch Ops | bulk meta updates, robots.txt, sitemap.xml |
| Logs | full operation history, filters, CSV export |

---

## quick start

Quick Start (3 commands. I timed it.)
bash

# 1. Grab it
git clone https://github.com/mh3nj/aether.git

# 2. Run it (the bat does the rest)
./aether.bat        # - - -> Windows
./aether.sh         # - - -> Mac/Linux

That's it. No npm install, no docker pull, no "please wait 15 minutes while we download node_modules"


## requirements

- Python 3.11+ (or just use the .exe)
- 4GB RAM (8GB if you're the kind of person with 47 chrome tabs open)
- internet for first run, then go fully offline forever

---

## keyboard shortcuts

| shortcut | where it goes |
|----------|--------------|
=======
# Aether – Complete Web Development Toolkit

**Status:** Stable Release v2.0  
**Build Date:** May 8, 2026

A professional desktop application with **12 powerful merged tools** (originally 29 standalone features) for web developers, SEO specialists, and content creators – all in one offline, privacy-focused application.

---

## About Aether

Aether (pronounced "ee-ther") is a complete web development command center named after the classical element believed to fill the universe. Just as aether carries light across the cosmos, Aether carries your code to perfection through formatting, optimization, and validation.

### What Aether Helps You Do

- Format code – Python, JS, HTML, CSS, TypeScript with diff view
- Optimize SEO – Meta tags, Open Graph, Twitter Cards, hreflang
- Generate Schema – FAQ, Product, Article, Event, Recipe, HowTo, LocalBusiness, Video
- Optimize images – WebP conversion, smart lazy loading with blur-up previews
- Manage links – Bulk find/replace, broken link detection, internal link suggestions
- Improve accessibility – Alt text checker, WCAG compliance scans
- Boost performance – Preload scanner, PageSpeed Insights (Core Web Vitals)
- Secure your site – CSP & SRI security headers
- Backup & restore – Never lose work during bulk operations

**12 integrated tools** | **Dark/Light theme** | **100% offline** | **Zero telemetry**

---

## The 12 Tools (Merged from 29 Original Features)

| Tab | Description |
|-----|-------------|
| Dashboard | Command center with real-time metrics and quick actions |
| Code Studio | Code Formatter + CSS Optimizer (print + speech CSS) |
| SEO Command | SEO Optimizer + SEO Score + Duplicate Detector + Meta Refresh |
| Schema & Social | Schema Library + OG Preview + Breadcrumb Builder |
| Media Studio | Favicon Generator + WebP Converter + Lazy Load + Image Hints |
| Link Studio | Link Manager + Link Checker + Internal Links |
| Accessibility Hub | Accessibility Checker + Alt Checker + Spell Checker + Content Length |
| Performance Lab | Preload Scanner + PageSpeed Insights |
| Security & Backup | CSP Generator + SRI Hash + Backup & Restore |
| Analytics | Keyword Density + SEO Score History |
| Batch Ops | Batch Meta Updater + Robots & Sitemap |
| Logs | Complete operation history with filters and export |

---

## Getting Started

### Option 1: From Source (Python required)

```
git clone https://github.com/mh3nj/Aether.git
cd Aether
python -m venv venv
venv\Scripts\activate  (Windows)
# source venv/bin/activate  (Mac/Linux)
pip install -r requirements.txt
python main.py
```

### Option 2: Standalone Executable

Download from GitHub Releases. No Python installation required. Just unzip and run Aether.exe.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
>>>>>>> b31a27c329fd60a8d9841f698397eeb438ee1cc7
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
<<<<<<< HEAD
| Ctrl+H | Code Humanizer |
=======
>>>>>>> b31a27c329fd60a8d9841f698397eeb438ee1cc7
| Ctrl+L | Logs |
| Ctrl+Z | Undo |
| Ctrl+Y / Ctrl+Shift+Z | Redo |
| Ctrl+Shift+T | Toggle Dark/Light Theme |

<<<<<<< HEAD

---

## known issues (honestly)

- Windows Defender might yell at the .bat file. it's fine. it's just scared of things it doesn't recognize. aren't we all.
- first launch takes ~30 seconds while dependencies install. just that once.
- PageSpeed Insights needs internet. everything else doesn't.

---

## project structure

```
Aether/
├── main.py
=======
---

## Features In Detail

### Code Studio
- Format Python (Black), JavaScript/TypeScript/HTML/CSS (Prettier or jsbeautifier)
- Split-view before/after with diff highlighting
- Generate print-optimized CSS and speech-optimized CSS for screen readers

### SEO Command
- Edit all meta tags with real-time character counters (title: 50-60, description: 150-160)
- Generate hreflang tags for multi-language sites
- Score each page 0-100 with actionable recommendations
- Find duplicate titles, descriptions, and H1 tags
- Detect harmful meta refresh redirects

### Schema & Social
- Generate JSON-LD for 8 schema types (FAQ, Product, Article, Event, Recipe, HowTo, LocalBusiness, Video)
- Validate schema against Google's requirements
- Preview Open Graph and Twitter Card appearance
- Inject JSON-LD directly into any HTML file

### Media Studio
- Generate all favicon sizes (ICO + PNGs) from a single source image
- Bulk convert JPG/PNG to WebP with adjustable quality
- Smart lazy loading with blur-up WebP previews (no layout shift)
- Detect missing width/height attributes and oversized images

### Link Studio
- Bulk find/replace links across all HTML files (regex support)
- Check for broken internal and external links
- Find orphan pages and get internal link suggestions
- Preview changes before applying

### Accessibility Hub
- Check for missing alt text, html lang attribute, empty links, heading hierarchy, iframe titles, form labels
- Bulk fix missing alt attributes (with smart suggestions from filename or surrounding text)
- Spell checker for English content
- Analyze content length with word count guidelines

### Performance Lab
- Scan for preload opportunities (CSS, JS, fonts, hero images)
- Inject preload links into HTML files
- Run PageSpeed Insights tests (Mobile/Desktop)
- Get Core Web Vitals metrics (LCP, CLS, FID)

### Security & Backup
- Generate Content Security Policy (CSP) meta tags with presets
- Generate Subresource Integrity (SRI) hashes for CDN resources
- Create timestamped backups of entire projects
- Restore any previous backup with one click

### Analytics
- Analyze keyword density (detect under-optimization and keyword stuffing)
- Track SEO score history across pages

### Batch Ops
- Update meta tags across hundreds of files at once
- Generate robots.txt and sitemap.xml
- Generate image sitemaps and video sitemaps

### Logs
- Complete operation history with filters (by type, search)
- Export logs as CSV
- Mini-logs viewer in Dashboard shows recent activity

### Dashboard
- Real-time SEO health score
- Key metrics (pages analyzed, issues found, average score, fixes applied)
- Top issues and recent fixes
- Quick actions panel
- Recent activity log

---

## Project Structure

```
Aether/
├── main.py                 # Entry point
>>>>>>> b31a27c329fd60a8d9841f698397eeb438ee1cc7
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
│   ├── logs_tab.py
│   ├── sidebar.py
│   ├── undo_manager.py
│   ├── data_bridge.py
│   └── project_setup_wizard.py
├── assets/
<<<<<<< HEAD
=======
│   ├── css/
│   ├── fonts/
│   └── logos/
>>>>>>> b31a27c329fd60a8d9841f698397eeb438ee1cc7
├── presets/
└── requirements.txt
```

---

<<<<<<< HEAD
## dependencies

```
PySide6          # the UI
BeautifulSoup4   # HTML parsing
Pillow           # image stuff
requests         # for the bits that need internet
black            # python formatting (optional)
jsbeautifier     # js/html/css formatting
pyspellchecker   # spell checking (optional)
```

---

## development timeline

| day | hours | what got built |
|-----|-------|---------------|
| May 4 | ~10h | formatter, SEO, favicon, WebP, link manager, robots |
| May 5 | ~10h | schema, lazy load, OG preview, image hints, link checker, SEO score |
| May 6 | ~10h | alt checker, CSS optimizer, keyword density, security, performance |
| May 7 | ~10h | PageSpeed, backup, undo/redo, logs, tab merging, sidebar |
| May 8 | ~8h  | dark/light theme, docs, release |

**total: ~48 hours. 18,000+ lines. 35 features merged into 12.**

---

## author

**Mohsen Jafari**.

- GitHub: [mh3nj](https://github.com/mh3nj)
- Xing: [mh3nj](https://www.xing.com/profile/Mohsen_Jafari093223/)
- [Parsegan.com](https://parsegan.com) — logo design
- [Dahgan.com](https://dahgan.com) — land surveying / portfolio

---

## license

MIT. use it, fork it, sell it, print it on a shirt. just don't blame us if something breaks.

---

## the story behind this

this project was built during internet restrictions in iran.

no stack overflow. no npm docs. no youtube tutorials. just whatever was cached, whatever was local, and whatever could be figured out from first principles.

48 hours. 18,000 lines. 12 tools.

proof that creativity and persistence don't need a stable connection.

**Aether**
=======
## Requirements

- Python 3.11+
- PySide6 (Qt6 for Python)
- BeautifulSoup4
- Pillow
- requests
- black (optional)
- jsbeautifier
- pyspellchecker (optional)

---

## Development Timeline

| Phase | Duration | Key Achievements |
|-------|----------|------------------|
| Day 1 (May 4) | ~10 hours | Foundation: Formatter, SEO, Favicon, WebP, Link Manager, Robots |
| Day 2 (May 5) | ~10 hours | Expansion: Schema, Lazy Load, OG, Image Hints, Link Checker, SEO Score |
| Day 3 (May 6) | ~10 hours | Advanced: Alt Checker, CSS Optimizer, Keyword Density, Security, Performance |
| Day 4 (May 7) | ~10 hours | Integration: PageSpeed, Backup, Undo/Redo, Logs, Tab merging, Sidebar |
| Day 5 (May 8) | ~8 hours | Polish: Dark/Light theme fixes, Documentation, Release |

**Total:** ~48 hours | **Lines of code:** 18,000+ | **Tabs:** 12 merged (from 29 original)

---

## Author

**Mohsen Jafari** - Creator, Developer, Designer

- GitHub: [mh3nj](https://github.com/mh3nj)
- LinkedIn: [mh3nj](https://linkedin.com/in/mh3nj)
- Websites: [Parsegan.com](https://parsegan.com) (logo design), [Dahgan.com](https://dahgan.com) (land surveying/portfolio)

---

## License

MIT License – Free for personal and commercial use with attribution. Because web development tools should be accessible to everyone.

---

## Acknowledgments

- PySide6 team (Qt for Python)
- BeautifulSoup4, Pillow, Black, Prettier, jsbeautifier
- Google PageSpeed Insights API
- The open-source community

---

*This project was created during internet restrictions in Iran – proof that creativity and persistence know no boundaries.*

**Aether – The breathing light of code.**

---
>>>>>>> b31a27c329fd60a8d9841f698397eeb438ee1cc7
