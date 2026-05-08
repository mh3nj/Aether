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
| Ctrl+L | Logs |
| Ctrl+Z | Undo |
| Ctrl+Y / Ctrl+Shift+Z | Redo |
| Ctrl+Shift+T | Toggle Dark/Light Theme |

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
│   ├── css/
│   ├── fonts/
│   └── logos/
├── presets/
└── requirements.txt
```

---

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

**Mohsen Jafari** – Creator, Developer, Designer

- Email: parsegan@proton.me
- Websites: parsegan.com, dahgan.com
- GitHub: @parsegan / @mh3nj
- LinkedIn: linkedin.com/in/parsegan

> Special thanks to the AI coding companion that co-wrote the code and helped debug every feature across all 12 merged tools.

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
