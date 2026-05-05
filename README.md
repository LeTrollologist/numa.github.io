# Numa's Space

Numa's Space is a handcrafted static web experience built as a personal, dreamy dashboard for studying, relaxing, playing, sketching, planning, and stargazing. The project is designed to run directly from GitHub Pages or any static file host without a build step.

The main entry point is `index.html`, with companion pages for the planner, sketchbook, grove, and custom 404 page. Styling, layout, animation, and most application logic are embedded directly in the HTML files, while shared optimization and analytics behavior lives in small standalone JavaScript files.

## Live Site

The project is configured around this GitHub Pages URL:

```text
https://letrollologist.github.io/numa.github.io/
```

Primary pages:

```text
https://letrollologist.github.io/numa.github.io/index.html
https://letrollologist.github.io/numa.github.io/planner.html
https://letrollologist.github.io/numa.github.io/sketch.html
https://letrollologist.github.io/numa.github.io/grove.html
```

## Features

- Personal home dashboard with animated atmosphere, world clocks, music controls, and a soft celestial visual style.
- StudyBuddy tools for tasks, notes, study timing, streaks, goals, and local progress tracking.
- Pong-style minigame with difficulty controls and score history.
- Dreamland and stargazing sections with rich visual effects and astronomy-inspired content.
- Interactive moon phase display and sky-themed UI elements.
- Standalone planner in `planner.html`.
- Standalone drawing/sketchbook experience in `sketch.html`.
- Standalone grove/garden scene in `grove.html`.
- Custom animated `404.html`.
- Service worker caching for core offline assets.
- Mobile, low-power, and iOS/WebKit optimization helpers.
- Lightweight analytics ping for page/session metadata.

## Project Structure

```text
.
|-- index.html                  # Main Numa's Space app
|-- planner.html                # Standalone constellation planner
|-- sketch.html                 # Standalone sketchbook/drawing tool
|-- grove.html                  # Standalone grove/garden scene
|-- 404.html                    # Custom not-found page
|-- test.html                   # Experimental/test sketchbook page
|-- service-worker.js           # Offline cache for core pages/assets
|-- analytics.js                # Page/session metadata uplink
|-- compute-optimizer.js        # Shared rendering/performance optimizer
|-- mobile-optimizer.js         # Mobile and battery optimization layer
|-- apple-optimizer.js          # iOS/WebKit safe-area, motion, and tap helpers
|-- *.jpg / *.png / *.webm      # Local visual/media assets
```

Some executable installer files are present in the working directory. They are not required to run the static site and should not be deployed as website assets unless intentionally needed.

## How To Run Locally

Because this is a static site, there is no package install or build command required.

The simplest option is to open `index.html` directly in a browser.

For behavior closer to GitHub Pages, especially for the service worker and root-relative favicon/manifest paths, run a local static server from the project root:

```powershell
python -m http.server 8000
```

Then visit:

```text
http://localhost:8000/index.html
```

You can also open the companion pages directly:

```text
http://localhost:8000/planner.html
http://localhost:8000/sketch.html
http://localhost:8000/grove.html
```

## Deployment

This project is suitable for GitHub Pages.

1. Commit the static files to the repository.
2. In GitHub, open the repository settings.
3. Go to Pages.
4. Select the branch that contains `index.html`.
5. Use the repository root as the Pages source.
6. Save and wait for GitHub Pages to publish.

No bundler, transpiler, package manager, or backend deployment is required for the front-end app.

## Important Files

### `index.html`

The main application. It contains the home dashboard, navigation, music player, study tools, status diagnostics, minigame, dream/stargazing views, and most visual systems.

It loads:

```html
<script src="compute-optimizer.js"></script>
<script src="mobile-optimizer.js"></script>
<script src="apple-optimizer.js"></script>
```

### `planner.html`

A standalone planner page with the same visual language as the main site. It uses the shared optimization scripts and analytics script.

### `sketch.html`

A standalone sketchbook/drawing page. It includes JSZip from a CDN:

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
```

This means ZIP/export-related functionality requires network access unless JSZip is vendored locally.

### `grove.html`

A standalone ambient grove/garden page. It uses shared optimization and analytics helpers.

### `service-worker.js`

Caches core project files:

```js
const ASSETS = [
  'index.html',
  'sketch.html',
  'grove.html',
  'planner.html',
  'mobile-optimizer.js',
  'apple-optimizer.js',
];
```

If new required assets are added, include them in this list so they are available offline.
