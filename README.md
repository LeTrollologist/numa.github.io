# 🌌 Numa's Space

<div align="center">

[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](#)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)](#)
[![JavaScript](https://img.shields.io/badge/ES6_JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](#)
[![PWA](https://img.shields.io/badge/PWA_Ready-5A0FC8?style=for-the-badge&logo=pwa&logoColor=white)](#)
[![GitHub Pages](https://img.shields.io/badge/GitHub_Pages-181717?style=for-the-badge&logo=github&logoColor=white)](#)

A personal Progressive Web App ecosystem featuring celestial study tools, interactive creative playgrounds, atmospheric gardens, and multi-timezone synchronization — all rendered client-side with premium performance across every device.

**[Live Site 🚀](https://letrollologist.github.io/numa.github.io/)**

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Architecture](#-repository-architecture)
- [Modules](#-interactive-modules)
- [Optimization Engines](#-client-side-optimization-engines)
- [PWA & Offline Support](#-pwa--offline-support)
- [Getting Started](#-getting-started)
- [License](#-license--security)

---

## 🌠 Overview

Numa's Space is a fully client-side SPA (Single Page Application) designed as a personal productivity and creative environment. It blends celestial aesthetics with functional study tools, real-time canvas rendering, and offline-first architecture — all without a backend.

Key highlights:

- **Zero backend** — everything runs in the browser
- **PWA installable** — works offline, adds to home screen
- **Cross-device optimized** — custom rendering engines for mobile, desktop, and iOS Safari
- **Modular** — each sector (Grove, Planner, Sketchbook, etc.) is a self-contained experience

---

## 🗂 Repository Architecture

```mermaid
graph TD
    A[index.html — Core SPA] --> B[grove.html — The Grove]
    A --> C[planner.html — Constellation Planner]
    A --> D[sketch.html — Sketchpad]
    A --> E[converter.html — Time Aligner]
    end

    subgraph PWA ["PWA Offline Infrastructure"]
        SW[service-worker.js v1.3] -->|Cache-first strategy| A
        SW -->|Cache-first strategy| B
        SW -->|Cache-first strategy| C
        SW -->|Cache-first strategy| E
    end

    subgraph Engines ["Client Optimization Pipeline"]
        CO[compute-optimizer.js — Threading]
        MO[mobile-optimizer.js — Hardware Adaptation]
        AO[apple-optimizer.js — WebKit/iOS Support]
    end

    A -.->|Loads| Engines
```

---

## 🎨 Interactive Modules

### 🌌 Core SPA — Celestial Study Lounge
The central hub. Features a glassmorphic UI with particle animations, timelapse sky backgrounds, custom Pomodoro-style study timers, and ambient music integration.

### 🌿 The Grove — Atmospheric Garden
An interactive magical garden with dynamic lighting modes (Ember, Moonlit, Mist). Tends virtual seeds through day/night care cycles, tracks progress in a garden ledger, and rewards growth with a gold coin economy. Firefly animations complete the atmosphere.

### ✍️ Sketchbook — Vector Sketchpad
A smooth HTML5 Canvas drawing tool with a high-density grid overlay. Supports Bézier path smoothing for fluid strokes, a layer system, and SVG vector export for lossless output at any resolution.

### ✨ Planner — Constellation Scheduler
A cosmic task and schedule manager built around a glass-panel UI with Great Vibes typography. Tracks daily chores, star-themed to-do lists, and progress indicators in a visually cohesive calendar view.

### ⏰ Time Aligner — Multi-Zone Sync
A dual-timeline world clock with three visual themes. Synchronized sliders calculate awake/sleep overlap between two time zones, making it ideal for coordinating across regions.

---

## ⚡ Client-Side Optimization Engines

Numa's Space achieves smooth 60 FPS rendering across low-spec phones and high-DPI desktops through three purpose-built optimization scripts:

### `compute-optimizer.js` — Multi-Threading
Offloads intensive particle and canvas draw calculations from the main UI thread using browser thread pooling, preventing jank during complex animations.

### `mobile-optimizer.js` — Hardware Adaptability
Detects available system memory and device class at runtime. Dynamically reduces canvas resolution, particle count, and effect complexity to prevent thermal throttling on constrained hardware.

### `apple-optimizer.js` — WebKit / iOS Support
Addresses Safari-specific rendering issues:
- Corrects the `100vh` dynamic viewport height bug caused by Safari's collapsible toolbar
- Overrides WebKit composition layers to ensure glassmorphic panels and dynamic scroll behave correctly on iOS hardware

---

## 📡 PWA & Offline Support

Numa's Space is a full Progressive Web App powered by `service-worker.js`.

| Feature | Detail |
| :--- | :--- |
| **Caching strategy** | Cache-first with `Promise.allSettled` network fallback |
| **Cache version** | `hollow-grove-v1.3` — aggressive versioning evicts stale assets on deploy |
| **Client takeover** | New service worker immediately claims all open tabs on activation |
| **Compatibility** | Works across local preview (`localhost`) and GitHub Pages production |

To install: open the live site in a supported browser and use **"Add to Home Screen"** or the browser's install prompt.

---

## 🚀 Getting Started

### Prerequisites

- A modern browser (Chrome, Firefox, Safari, Edge)
- [Node.js](https://nodejs.org/) (optional, for local dev server)

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/LeTrollologist/numa.github.io.git
cd numa.github.io

# 2. Start a local server
npx http-server -p 8080

# 3. Open in browser
# http://localhost:8080
```

> **Note:** A local server is required (not `file://`) for the service worker and PWA features to initialize correctly.

---

## 📁 File Structure

```
numa.github.io/
├── index.html              # Core SPA entry point
├── grovein.html            # The Grove module
├── planner.html            # Constellation Planner
├── sketchin.html           # Sketchpad
├── converter.html          # Time Aligner
├── service-worker.js       # PWA offline caching
├── compute-optimizer.js    # Thread pooling engine
├── mobile-optimizer.js     # Hardware adaptability engine
├── apple-optimizer.js      # WebKit/iOS fixes
├── SECURITY.md
└── LICENSE.md
```

---

## 📄 License & Security

| | |
|:---|:---|
| **License** | MIT — see [LICENSE.md](license.md) |
| **Security** | Vulnerability reporting guidelines in [SECURITY.md](security.md) |
