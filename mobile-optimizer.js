/**
 * mobile-optimizer.js
 * Unorthodox Mobile & Battery Optimizations
 * Intercepts rendering to save battery and prevent thermal throttling on phones.
 */

(function() {
    // Check if the user is on a mobile device
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth <= 768;
    
    if (!isMobile) return; // Only apply these aggressive hacks on mobile

    console.log("📱 Mobile Optimizer Engine Initialized");

    // ==========================================
    // 1. DYNAMIC CANVAS SUB-SAMPLING (Retina Hack)
    // ==========================================
    // Intercept Canvas Width/Height setters to lower internal resolution
    const origWidthDescr = Object.getOwnPropertyDescriptor(HTMLCanvasElement.prototype, 'width');
    const origHeightDescr = Object.getOwnPropertyDescriptor(HTMLCanvasElement.prototype, 'height');

    function applySubSampling(canvas, val, descriptor, property) {
        // Only scale the heavy background canvases, leave Minigame (Pong) untouched for physics accuracy
        if (canvas.id === 'stars') {
            canvas.style[property] = val + 'px'; // Keep visual size 100%
            descriptor.set.call(canvas, Math.floor(val * 0.75)); // Drop actual pixels by 25%
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
    // 2. THE "BLIND RENDER" ASSASSIN
    // ==========================================
    // Don't draw the background sky if it's covered by a solid background (StudyBuddy/Dreamland)
    const originalFill = CanvasRenderingContext2D.prototype.fill;
    const originalClearRect = CanvasRenderingContext2D.prototype.clearRect;

    function isCanvasCovered(ctx) {
        if (ctx.canvas.id === 'stars') {
            // Sky canvas is invisible whenever one of these pages/modes is active:
            // - Study mode: solid gradient covers the sky
            // - Dreamland: solid dark background
            // - Stargazer: its own canvas fills the screen on top of the sky
            if (document.body.classList.contains('studyMode') ||
                document.getElementById('page-dreamland').classList.contains('active') ||
                document.getElementById('page-stargazer').classList.contains('active')) {
                return true;
            }
        }
        return false;
    }

    CanvasRenderingContext2D.prototype.fill = function(...args) {
        if (isCanvasCovered(this)) return; // Abort GPU command
        return originalFill.apply(this, args);
    };

    CanvasRenderingContext2D.prototype.clearRect = function(...args) {
        if (isCanvasCovered(this)) return; // Abort GPU command
        return originalClearRect.apply(this, args);
    };

    // ==========================================
    // 3. ADAPTIVE FRAME DROPPER (Battery Saver)
    // ==========================================
    // Intentionally drops 1 out of every 3 frames on mobile to cap at ~40fps
    const originalRAF = window.requestAnimationFrame;
    let frameCounter = 0;

    window.requestAnimationFrame = function(callback) {
        return originalRAF(function(time) {
            frameCounter++;
            // Skip the 3rd frame to save battery, EXCEPT if playing Pong
            if (frameCounter % 3 === 0 && document.getElementById('page-minigame').classList.contains('active') === false) {
                // Instantly re-queue the frame without executing the heavy drawing logic
                window.requestAnimationFrame(callback);
                return; 
            }
            callback(time);
        });
    };

    // ==========================================
    // 4. LOW-TIER DEVICE GLASS DOWNGRADE
    // ==========================================
    // If the phone has 4GB of RAM or less, or <= 4 CPU cores, reduce blur radius.
    const ram = navigator.deviceMemory || 4;
    const cores = navigator.hardwareConcurrency || 4;

    if (ram <= 4 || cores <= 4) {
        console.log("📱 Low-end device detected: Downgrading Glassmorphism");
        const lowEndStyles = document.createElement('style');
        lowEndStyles.innerHTML = `
            /* Massive blurs kill cheap phone GPUs. Cap them at 6px. */
            #nav-bar, .glass-card, .contact-card, #mob-overlay, .status-card, #studyPanel .study-inner {
                backdrop-filter: blur(6px) !important;
                -webkit-backdrop-filter: blur(6px) !important;
                background: rgba(8, 8, 18, 0.88) !important; /* Make slightly darker to compensate for less blur */
            }
        `;
        document.head.appendChild(lowEndStyles);
    }

})();
