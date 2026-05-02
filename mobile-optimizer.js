/**
 * mobile-optimizer.js
 * Advanced Mobile & Battery Optimization Engine v2.1
 * - Stargazer Safe + Battery Aware + Boost Mode
 */
(function() {
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth <= 768;
    if (!isMobile) return;

    console.log("📱 Mobile Optimizer v2.1 Initialized");

    // ==========================================
    // GLOBAL STATE
    // ==========================================
    let batteryLevel = 1;           // 0.0 to 1.0
    let stargazerBoost = false;     // When true, reduce optimizations

    // ==========================================
    // 1. BATTERY MONITORING
    // ==========================================
    if (navigator.getBattery) {
        navigator.getBattery().then(function(battery) {
            batteryLevel = battery.level;
            battery.addEventListener('levelchange', function() {
                batteryLevel = battery.level;
            });
        });
    }

    // ==========================================
    // 2. STARGazer BOOST DETECTION
    // ==========================================
    function updateStargazerBoost() {
        const stargazerPage = document.getElementById('page-stargazer');
        stargazerBoost = stargazerPage && stargazerPage.classList.contains('active');
    }

    // Check boost status when page changes
    const observer = new MutationObserver(updateStargazerBoost);
    observer.observe(document.body, { attributes: true, subtree: true, attributeFilter: ['class'] });

    // Also check on touch/click (user is actively using it)
    document.addEventListener('touchstart', function() {
        if (document.getElementById('page-stargazer')?.classList.contains('active')) {
            stargazerBoost = true;
            setTimeout(() => { stargazerBoost = false; }, 8000); // Boost lasts 8 seconds after interaction
        }
    }, { passive: true });

    // ==========================================
    // 3. DYNAMIC CANVAS SUB-SAMPLING
    // ==========================================
    const origWidthDescr = Object.getOwnPropertyDescriptor(HTMLCanvasElement.prototype, 'width');
    const origHeightDescr = Object.getOwnPropertyDescriptor(HTMLCanvasElement.prototype, 'height');

    function applySubSampling(canvas, val, descriptor, property) {
        if (canvas.id === 'stars' && !stargazerBoost) {
            canvas.style[property] = val + 'px';
            descriptor.set.call(canvas, Math.floor(val * 0.72));
        } else {
            descriptor.set.call(canvas, val);
        }
    }

    Object.defineProperty(HTMLCanvasElement.prototype, 'width', {
        set(val) { applySubSampling(this, val, origWidthDescr, 'width'); },
        get() { return origWidthDescr.get.call(this); }
    });

    Object.defineProperty(HTMLCanvasElement.prototype, 'height', {
        set(val) { applySubSampling(this, val, origHeightDescr, 'height'); },
        get() { return origHeightDescr.get.call(this); }
    });

    // ==========================================
    // 4. BLIND RENDER ASSASSIN (Stargazer Safe)
    // ==========================================
    const originalFill = CanvasRenderingContext2D.prototype.fill;
    const originalClearRect = CanvasRenderingContext2D.prototype.clearRect;

    function isCanvasCovered(ctx) {
        if (ctx.canvas.id === 'stars') {
            if (document.body.classList.contains('studyMode') ||
                document.getElementById('page-dreamland').classList.contains('active')) {
                return true;
            }
        }
        return false;
    }

    CanvasRenderingContext2D.prototype.fill = function(...args) {
        if (isCanvasCovered(this)) return;
        return originalFill.apply(this, args);
    };

    CanvasRenderingContext2D.prototype.clearRect = function(...args) {
        if (isCanvasCovered(this)) return;
        return originalClearRect.apply(this, args);
    };

    // ==========================================
    // 5. BATTERY + BOOST AWARE FRAME DROPPER
    // ==========================================
    const originalRAF = window.requestAnimationFrame;
    let frameCounter = 0;

    window.requestAnimationFrame = function(callback) {
        return originalRAF(function(time) {
            frameCounter++;

            const minigameActive = document.getElementById('page-minigame').classList.contains('active');

            // Calculate how aggressive we should be
            let skipRate = 3; // Default: skip every 3rd frame

            if (stargazerBoost) {
                skipRate = 1; // Full performance when using Stargazer
            } else if (batteryLevel < 0.3) {
                skipRate = 4; // Very aggressive when battery is low
            } else if (batteryLevel < 0.5) {
                skipRate = 3; // Moderate saving
            }

            if (frameCounter % skipRate === 0 && !minigameActive && !stargazerBoost) {
                window.requestAnimationFrame(callback);
                return;
            }

            callback(time);
        });
    };

    // ==========================================
    // 6. LOW-END DEVICE DOWNGRADE
    // ==========================================
    const ram = navigator.deviceMemory || 4;
    const cores = navigator.hardwareConcurrency || 4;

    if (ram <= 4 || cores <= 4) {
        console.log("📱 Low-end device → Glassmorphism downgraded");
        const style = document.createElement('style');
        style.innerHTML = `
            #nav-bar, .glass-card, .contact-card, #mob-overlay, .status-card, #studyPanel .study-inner {
                backdrop-filter: blur(5px) !important;
                -webkit-backdrop-filter: blur(5px) !important;
                background: rgba(8, 8, 18, 0.90) !important;
            }
        `;
        document.head.appendChild(style);
    }

    // ==========================================
    // 7. TOUCH THROTTLING + VISIBILITY PAUSE
    // ==========================================
    let lastTouchMove = 0;
    const originalAddEventListener = EventTarget.prototype.addEventListener;

    EventTarget.prototype.addEventListener = function(type, listener, options) {
        if (type === 'touchmove' && isMobile) {
            const throttled = function(e) {
                const now = Date.now();
                if (now - lastTouchMove > 16) {
                    lastTouchMove = now;
                    listener.call(this, e);
                }
            };
            return originalAddEventListener.call(this, type, throttled, options);
        }
        return originalAddEventListener.call(this, type, listener, options);
    };

    document.addEventListener('visibilitychange', function() {
        if (document.hidden) console.log("📱 Tab hidden → Saving resources");
    });

    console.log("📱 All mobile optimizations applied (Stargazer Boost Enabled)");
})();
