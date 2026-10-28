# 🌌 Numa's Space

Disclaimer: I am not affiliated with Numa, this website and project was made strictly as a gift to be a study aid and her privacy should be respected. 

A personal web app featuring celestial and twilight-forest themes, study tools, a digital garden, a vector sketchpad, and a multi-timezone converter. Built with vanilla web technologies and designed to run entirely in the browser with offline PWA support. 

This web app is considered completed, and as such there will be no new features added. The theme will remain the same and no changes will be made to the two existing themes on the PWA/SPA and the peripheral pages. There will only be casual maintenance done on existing features.

**[Live Site](https://letrollologist.github.io/numa.github.io/)**

---

## Features

- **Celestial Lounge (`index.html`)**: Study timers, ambient audio, dynamic starry sky canvas, and retro Pong mini-game with optional local/P2P multiplayer.
- **Stargazer**: Interactive night sky viewer mapping bright stars and constellation lines based on real astronomical coordinates and local sidereal time.
- **The Grove (`grove.html`)**: A relaxing virtual garden where you plant seeds, track growth cycles, and toggle ambient themes (Ember, Moonlit, Mist).
- **Sketchbook (`sketch.html`)**: Vector drawing tool with smoothing, grid toggles, layer management, and SVG export.
- **Planner (`planner.html`)**: Simple schedule and task organizer with a clean dark interface.
- **Time Converter (`converter.html`)**: Multi-timezone converter synchronizing UK, Dubai, Cara 🌸, and IST with interactive sliders, 24-hour timeline view, shared waking-hours overlap calculator, and target alignment countdown.
- **Offline / PWA**: Full Progressive Web App support via service worker for caching and home screen installation.

---

## Performance & Device Support

The app includes lightweight client-side scripts to keep animations smooth on mobile and desktop:

- `compute-optimizer.js`: Manages background task scheduling to prevent frame drops during canvas draws.
- `mobile-optimizer.js`: Adjusts particle count and canvas scaling based on device capability.
- `apple-optimizer.js`: Fixes iOS Safari dynamic viewport height (`100vh`) and composition layer quirks.

---

## Getting Started

### Local Setup

Because the app uses a Service Worker for offline support, run it through a local HTTP server rather than opening files directly with `file://`.

```bash
# Clone the repository
git clone https://github.com/LeTrollologist/numa.github.io.git
cd numa.github.io

# Start a local server (e.g. using Python or Node)
python -m http.server 8080
# or: npx http-server -p 8080

# Open in browser
# http://localhost:8080
```

---

## File Structure

```
numa.github.io/
├── index.html              # Main dashboard, Stargazer sky map, timers, mini-game
├── grove.html              # Virtual garden
├── planner.html            # Daily planner & tasks
├── sketch.html             # Vector sketchpad
├── converter.html          # Timezone converter (UK, Dubai, Cara, IST)
├── install.html            # PWA install guide
├── credits.html            # Credits and acknowledgements
├── service-worker.js       # Offline cache management
├── compute-optimizer.js    # Task scheduling helper
├── mobile-optimizer.js     # Mobile scaling helper
├── apple-optimizer.js      # iOS Safari viewport fixes
├── archived_tools/         # Offline data scripts (astronomy / star catalogue tools)
└── favicon/                # App icons & manifest assets
```

---
