# Aether – technical portfolio document

**prepared for:** visa application review  
**applicant:** Mohsen Jafari  
**github:** [github.com/mh3nj](https://github.com/mh3nj)  
**project repository:** [github.com/mh3nj/Aether](https://github.com/mh3nj/Aether)  
**document date:** june 4, 2026
**started this app:** may 4, 2026

---

## what is aether

Aether is a professional desktop application for web developers and SEO specialists. it consolidates 31 individual tools into 12 integrated tabs, all running fully offline on the user's machine.

the project was conceived, designed, and built entirely by Mohsen Jafari;solo;over the course of one month, under significant technical constraints due to internet restrictions in iran.

it is not a prototype or a concept. it is a complete, stable, working application used for real professional work.

**verified by cloning and running:**
```bash
git clone https://github.com/mh3nj/Aether.git
cd Aether
pip install -r requirements.txt
python main.py
```

---

## the problem it solves

building a website involves two distinct phases. the first is development;writing code, building layouts, implementing features. the second is post-launch optimization;SEO setup, meta tags, schema markup, image compression, accessibility checks, broken link detection, security headers, performance analysis.

the second phase is tedious, time-consuming, and typically requires switching between 10–15 different online tools, services, and manual processes. for a full-time web developer, this adds hours to every project.

Aether eliminates this entirely. every tool is in one place, works offline, and operates with automatic injection into the project's HTML files. a task that previously took hours can be completed in minutes.

---

## technical scope

| metric | value |
|--------|-------|
| total lines of code | 18,000+ (python, QSS, JSON) |
| original standalone features | 31 |
| merged into | 12 integrated tabs |
| development period | may 4 – june 4, 2026 |
| total active development hours | ~55 hours |
| platform | windows, mac, linux |
| primary language | python 3.9+ |
| UI framework | PySide6 (Qt6) |
| internet required | no;fully offline except PageSpeed API |

---

## the 12 tools

### dashboard
real-time SEO health score across the loaded project. key metrics: pages analyzed, issues found, average score, fixes applied. quick action panel and recent activity log. all data pulled live from the other 11 tabs.

### code studio
formats python (via Black), javascript, typescript, HTML, and CSS (via jsbeautifier or prettier). displays a split before/after view with line-by-line diff highlighting. also generates print-optimized CSS and speech-optimized CSS for screen readers.

### SEO command
full meta tag editor with real-time character counters (title: 50–60 characters, description: 150–160 characters). hreflang generator for multi-language sites. 0–100 page scoring with actionable recommendations. duplicate title/description/H1 detection. harmful meta refresh redirect detection.

### schema & social
generates valid JSON-LD markup for 8 schema types: FAQ, Product, Article, Event, Recipe, HowTo, LocalBusiness, Video. validates against google's structured data requirements. live Open Graph and Twitter Card preview. direct injection into HTML files.

### media studio
four capabilities in one tab:
- favicon generator;produces all required sizes (ICO + multiple PNGs) from a single source image
- WebP converter;bulk converts JPG/PNG to lossless WebP with automatic quality optimization
- smart image lazy loader;described in detail below
- smart video lazy loader;described in detail below

### link studio
bulk find and replace across all HTML files in a project, with regex support. broken link checker for both internal and external links. orphan page detection with internal link suggestions. preview of all changes before applying.

### accessibility hub
checks for: missing alt text, missing html lang attribute, empty links, broken heading hierarchy, missing iframe titles, unlabeled form elements. bulk fix for missing alt attributes with smart suggestions based on filename and surrounding content. spell checker. content length analysis with word count guidelines.

### performance lab
scans HTML files for preload opportunities (CSS, JS, fonts, hero images) and injects the appropriate preload link tags. PageSpeed Insights integration (mobile and desktop). Core Web Vitals reporting: LCP, CLS, FID.

### security & backup
content security policy (CSP) generator with common presets. subresource integrity (SRI) hash generator for CDN-hosted resources. timestamped full project backups. one-click restore to any previous backup.

### analytics
keyword density analysis across pages;detects both under-optimization and keyword stuffing. SEO score history tracking over time.

### batch ops
update meta tags across hundreds of HTML files simultaneously. generate robots.txt and sitemap.xml. generate image sitemaps and video sitemaps.

### code humanizer *(v2.2, early stage)*
lowercases all code comments across a project. removes common AI-generated phrasing patterns. batch operation across all files. this is the first phase of a larger planned system;the architecture and roadmap are complete, implementation is ongoing.

---

## two flagship features of v2.2

### smart image lazy loading with WebP preview pipeline

this is one of the more technically involved features in the application.

the standard approach to lazy loading images is to delay loading until the user scrolls to the image. aether goes further.

when processing a project, aether generates a preview version of every image;same dimensions, same format (WebP), but compressed to approximately 2KB regardless of the original file size. this is done using an automatic lossless compression algorithm that finds the optimal settings per image.

when a user visits a page, they see the tiny preview immediately;it loads in milliseconds and is displayed as a soft blur placeholder. in the background, the full-quality image downloads silently. the moment the download completes, the preview is replaced seamlessly with no layout shift and no visible pop-in.

every original image, regardless of its original format, is automatically converted to lossless WebP during this process;smaller file size, better quality, faster delivery.

the entire system;preview generation, WebP conversion, lazy load injection;is automatic. the developer points aether at their project folder and it handles everything.

### smart video lazy loading with parallel chunk downloading

video is the most bandwidth-expensive asset on most websites. the naive approach is to load all videos when the page loads, which is slow and wasteful;especially for users on mobile or limited data plans.

aether's smart video lazy loader works as follows:

when a video is off-screen, it is not loaded. a low-resolution crystalline placeholder is displayed instead. when the user scrolls to the video, aether begins downloading it in 5 parallel chunks simultaneously;similar to how advanced download managers (like ADM on android) work. the 5 chunks are downloaded concurrently and assembled seamlessly into one complete video, which then replaces the placeholder.

the result is significantly faster video start times compared to sequential downloading, with zero bandwidth wasted on videos the user never reaches.

| | standard loading | aether v2.2 |
|--|-----------------|-------------|
| load time (20 videos) | 4–6 seconds | ~1 second |
| RAM usage | 400–600MB | 80–120MB |
| videos loaded before scrolling | all | zero |
| bandwidth for unviewed videos | wasted | zero |

---

## development timeline

the initial version (v2.0) was built in 5 days. v2.2 followed over the subsequent month with two major feature additions and extensive testing.

### v2.0;may 4–8, 2026

| date | hours | work completed |
|------|-------|----------------|
| may 4 | ~10h | project architecture, formatter, SEO tools, favicon generator, WebP converter, link manager, robots.txt |
| may 5 | ~10h | schema generator, image lazy load, OG preview, image hints, link checker, SEO scorer, dark/light theme |
| may 6 | ~10h | alt text checker, CSS optimizer, keyword density, spell checker, security headers, performance scanner, batch meta updater |
| may 7 | ~10h | PageSpeed API integration, backup system, undo/redo, logs tab, tab merging (29 → 12), sidebar navigation |
| may 8 | ~8h | theme propagation fixes, cross-platform testing, documentation, v2.0 stable release |

**v2.0 total: ~48 hours across 5 days**

### v2.2;may 12 – june 4, 2026

| date | hours | work completed |
|------|-------|----------------|
| may 12 | ~1h | bug identification pass |
| may 15 | ~1.5h | real-world testing, additional bugs found |
| may 19 | ~3h | researching code humanization strategies, roadmap planning |
| may 21 | ~4h | smart video lazy loader architecture design |
| may 26 | ~2h | identifying the correct python approach for parallel chunk downloading |
| may 30 | ~6h | building and shipping the smart video lazy loader |
| june 1 | ~1h | edge case testing on video lazy load |
| june 2 | ~3h | standard video lazy load injection mode |
| june 3 | ~5h | code humanizer v1, final testing pass across all features |
| june 4 | ~2h | repository cleanup, v2.2 stable release |

**v2.2 additions: ~28.5 hours**

**combined total: ~55 hours. one month. one developer.**

---

## development context

this project was developed under significant constraints.

iran experienced widespread internet restrictions during this period, including whitelisting protocols that blocked access to github, PyPI, stack overflow, and most standard development resources. the majority of the work was completed offline;dependencies researched and downloaded during brief windows of connectivity, documentation consulted from locally cached copies, problems solved from first principles when no reference was available.

this affected not just convenience but fundamental development workflow. version control pushes, dependency management, and documentation access;things most developers do without thinking;required planning and timing around unpredictable connectivity windows.

the application was built anyway. it works. it is documented. it can be cloned and run by anyone.

---

## verification

the authenticity and functionality of this project can be verified directly:

1. clone the repository: `git clone https://github.com/mh3nj/Aether.git`
2. install dependencies: `pip install -r requirements.txt`
3. run the application: `python main.py`

the full application launches and operates exactly as documented. no binaries, no compiled executables required. every line of code is readable in the repository.

---

## technical challenges solved

| challenge | solution implemented |
|-----------|---------------------|
| dark theme not propagating to nested Qt widgets | implemented `update_theme()` method on every merged tab, called on theme toggle |
| FontAwesome unicode icons not rendering | resolved prefix format to `\ufxxx` with correct `\u` notation |
| sidebar text color incorrect on startup | added `sidebar.update_theme(is_dark)` call during initial `_set_theme_state` |
| dashboard not receiving live data from tabs | connected data bridge signals after dashboard instantiation |
| tab bar visible after programmatic hiding | used `self.tabs.tabBar().setHidden(True)` explicitly |
| BeautifulSoup scope issues | standardized import pattern across all tabs |

---

## about the author

**Mohsen Jafari** is a full-time web developer based in iran, with professional experience in frontend development, website design, and SEO implementation.

Aether was built to solve a real problem from his own professional workflow;the hours spent on post-launch SEO and optimization work that every web project requires. the result is a tool he uses himself, that he built himself, that works.

- github: [github.com/mh3nj](https://github.com/mh3nj)
- xing: [xing.com/profile/Mohsen_Jafari093223](https://www.xing.com/profile/Mohsen_Jafari093223/)
- logo design work: [parsegan.com](https://parsegan.com)
- portfolio: [dahgan.com](https://dahgan.com)

---

*this project was built during internet restrictions in iran. no stack overflow. no documentation access. no reliable connectivity. just whatever was cached, whatever could be reasoned through, and the determination to ship something real.*

*55 hours. 18,000+ lines. 31 features. 12 tools. one month. one developer.*

*proof that creativity and persistence don't need a stable connection.*
