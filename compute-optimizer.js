/**
 * compute-optimizer.js
 * Pure Computational & Rendering Optimizations.
 */

(function() {
    console.log("⚡ Compute Optimizer Engine Initialized");

    // ==========================================
    // 1. INJECT HARDWARE ACCELERATION & CONTAINMENT
    // ==========================================
    const perfStyles = document.createElement('style');
    perfStyles.innerHTML = `
        /* A. GPU OFFLOADING */
        .petal, .glitter, .love-text, .page-title, .note, .click-heart {
            will-change: transform;
            transform: translateZ(0); 
            backface-visibility: hidden; 
            perspective: 1000px; 
        }

        /* Cache heavy glassmorphism blurs on the GPU */
        /* Note: backdrop-filter is not a valid will-change value — use transform only */
        .glass-card, #nav-bar, .dl-shell, .study-inner, .status-card {
            will-change: transform;
            transform: translateZ(0);
        }

        /* D. CELESTIAL BODIES — repositioned on each SunCalc update */
        #sunSvg, #moonSvg, #moonLabel {
            will-change: transform, left, top;
            transform: translateZ(0);
            backface-visibility: hidden;
        }

        /* B. CSS CONTAINMENT (Sandbox DOM recalculations) */
        .clock-box, .counter span, #timerDisplay, #score, .dl-cd {
            contain: layout paint style;
        }

        /* C. FONT OPTIMIZATION */
        #hud, .dashboard, .study-stats {
            text-rendering: optimizeSpeed;
            -webkit-font-smoothing: antialiased;
        }
    `;
    document.head.appendChild(perfStyles);

    // ==========================================
    // 2. CANVAS API OPTIMIZATION (Monkey Patch)
    // ==========================================
    const originalGetContext = HTMLCanvasElement.prototype.getContext;
    
    HTMLCanvasElement.prototype.getContext = function(type, attributes) {
        if (type === '2d') {
            attributes = Object.assign({}, attributes || {}, {
                desynchronized: true, 
                willReadFrequently: false 
            });
        }
        return originalGetContext.call(this, type, attributes);
    };

    // ==========================================
    // 3. PASSIVE SCROLLING (Thread Unblocking)
    // ==========================================
    const originalAddEventListener = EventTarget.prototype.addEventListener;
    
    EventTarget.prototype.addEventListener = function(type, listener, options) {
        if (['wheel', 'mousewheel', 'touchstart', 'touchmove'].includes(type) && this.id !== 'pongCanvas') {
            if (typeof options === 'boolean') {
                options = { capture: options, passive: true };
            } else if (!options) {
                options = { passive: true };
            } else if (typeof options === 'object' && options.passive === undefined) {
                options.passive = true;
            }
        }
        return originalAddEventListener.call(this, type, listener, options);
    };

})();
