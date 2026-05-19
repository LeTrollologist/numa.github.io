# 🌌 Numa's Space

<div align="center">

[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](#)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)](#)
[![JavaScript](https://img.shields.io/badge/ES6_JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](#)
[![PWA](https://img.shields.io/badge/PWA_Ready-5A0FC8?style=for-the-badge&logo=pwa&logoColor=white)](#)
[![GitHub Pages](https://img.shields.io/badge/GitHub_Pages-181717?style=for-the-badge&logo=github&logoColor=white)](#)

A personal Web Application and Progressive Web App ecosystem featuring deep interactive elements, creative playgrounds, study engines, and celestial alignments.

[**Live Site 🚀**](https://letrollologist.github.io/numa.github.io/)
</div>

---

## 🌌 Repository Architecture

```mermaid
graph TD
    A[index.html - Core SPA] --> B[grovein.html - The Grove]
    A --> C[planner.html - Constellation Planner]
    A --> D[sketchin.html - Sketchpad]
    A --> E[converter.html - Time Aligner]
    
    subgraph PWA Layer [PWA Offline Infrastructure]
        SW[service-worker.js v1.3] -->|Caches Assets| A
        SW -->|Caches Assets| B
        SW -->|Caches Assets| C
        SW -->|Caches Assets| E
    end
    
    subgraph Engine Optimizers [Client Optimization Pipeline]
        CO[compute-optimizer.js]
        MO[mobile-optimizer.js]
        AO[apple-optimizer.js]
    end
    
    A -.->|Ingests| Engine Optimizers
```

---

## 🎨 Interactive Sectors (Modules)

| Sector | Concept | Visuals & System | Features |
| :--- | :--- | :--- | :--- |
| **🌌 The Core SPA** | Celestial Study Lounge | Glassmorphism, particles, smooth twilight animations | Custom study timers, timelapse backgrounds, music integration |
| **🌿 The Grove** | Magical Atmospheric Garden | Ember, Moonlit, Mist interactive lighting nodes | Dynamic seed care cycles, garden ledger, gold coin ledger, fireflies |
| **✍️ Sketchbook** | Smooth Vector Sketchpad | HTML5 Canvas, high-density grids | Bézier path smoothing, SVG vector export, layer system |
| **✨ Planner** | Constellation Scheduler | Cosmic glass panels, Great Vibes typography | Dynamic chore tracking, daily star schedules, progress indicators |
| **⏰ Time Aligner** | Multi-Zone Celestial Sync | Tri-Theme dual timelines | Dual slider synchronization, awake/sleep overlap calculations |

---

## ⚡ Client-Side Optimization Engines

To run premium rendering and real-time canvas layers on both low-spec mobile devices and high-DPI desktop machines, **Numa's Space** leverages three custom optimization engines:

1. **`compute-optimizer.js` (Multi-Threading & Thread Pooling)**
   * Manages tasks asynchronously.
   * Leverages browser thread pooling to isolate complex particle and cosmic drawing calculations away from the main UI thread, keeping interface frame rates locked at 60 FPS.
2. **`mobile-optimizer.js` (Hardware Adaptability)**
   * Detects system memory thresholds and device parameters.
   * Dynamically downsizes canvas scales, adjusts particle counts, and scales down resolution modifiers in real time to prevent thermal throttling on low-spec mobile units.
3. **`apple-optimizer.js` (WebKit/iOS Hardware Support)**
   * Tailors layout heights specifically to counteract mobile Safari’s dynamic viewport height (`100vh` scrolling bug).
   * Overrides WebKit composition layers to bypass CPU bottlenecks, ensuring dynamic scrolling and glassmorphic panels glide flawlessly on iOS hardware.

---

## 🛠️ PWA Offline Support & Cache Eviction

This workspace operates as a full PWA (Progressive Web App) managed by `service-worker.js`.
* **Caching Strategy**: Leverages a reliable cache-first strategy with safe network fallback rules using `Promise.allSettled` to support local preview environments and Production GitHub Pages hosting seamlessly.
* **Aggressive Versioning**: Utilizing custom versioned cache bounds (`CACHE_NAME = 'hollow-grove-v1.3'`), a push immediately sweeps deprecated browser assets, evicts stale layers, and claims active client tabs instantly.

---

## 🚀 Setting Up Locally

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/LeTrollologist/numa.github.io.git
   cd numa.github.io
   ```
2. **Launch Local Server**:
   Any standard static file hosting tool works. If using Node.js:
   ```bash
   npx http-server -p 8080
   ```
3. **Visit Numa's Space**:
   Open `http://localhost:8080` in your web browser.

---

## 📄 Licensing & Security

* **Security**: Standard reporting guidelines are available inside [SECURITY.md](security.md).
* **License**: Governed under the MIT License. See [LICENSE.md](license.md) for full terms.
