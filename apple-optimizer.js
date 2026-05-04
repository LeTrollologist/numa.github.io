/**
 * apple-optimizer.js
 * Premium iOS & WebKit Enhancement Engine v1.0
 * Targeting: iPhone Notch, Safe Areas, OLED, and ProMotion.
 */
(function() {
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || 
                  (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    
    if (!isIOS) return;

    console.log("🍎 Apple Optimizer v1.0 Initialized");

    // ==========================================
    // 1. SAFE AREA & NOTCH INJECTOR
    // ==========================================
    const injectSafeAreas = () => {
        const style = document.createElement('style');
        style.innerHTML = `
            :root {
                --sat: env(safe-area-inset-top);
                --sar: env(safe-area-inset-right);
                --sab: env(safe-area-inset-bottom);
                --sal: env(safe-area-inset-left);
            }

            /* Adjust fixed headers */
            header, .page-header, #nav-bar {
                padding-top: calc(var(--sat, 0px) + 10px) !important;
            }

            /* Adjust fixed footers/tabs */
            footer, .nav-tabs, .fab, #mob-overlay {
                padding-bottom: calc(var(--sab, 0px) + 10px) !important;
            }

            /* Force momentum scrolling */
            * {
                -webkit-overflow-scrolling: touch;
            }

            /* Prevent auto-zoom on input focus */
            input, textarea, select {
                font-size: 16px !important;
            }

            /* Retina Typography */
            body {
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }
        `;
        document.head.appendChild(style);
    };

    // ==========================================
    // 2. OLED TRUE BLACK DETECTION
    // ==========================================
    const applyOLEDTheme = () => {
        // iPhone X, XS, 11 Pro, 12, 13, 14, 15 (OLED Aspect Ratios)
        const isOLED = (window.devicePixelRatio >= 3);
        
        if (isOLED) {
            const style = document.createElement('style');
            style.innerHTML = `
                body, .main-container, #gameContainer {
                    background: #000000 !important;
                }
                .glass, .glass-card, .card {
                    background: rgba(20, 20, 30, 0.7) !important;
                    border-color: rgba(255, 255, 255, 0.08) !important;
                }
            `;
            document.head.appendChild(style);
            console.log("🍎 OLED Display Detected → True Black Mode Enabled");
        }
    };

    // ==========================================
    // 3. TAPTIC INTERACTION SIMULATOR
    // ==========================================
    const setupTapticFeel = () => {
        document.addEventListener('touchstart', (e) => {
            const target = e.target.closest('button, .btn, .nav-tab, .task-item, .mood-btn');
            if (target) {
                target.style.transition = 'transform 0.1s cubic-bezier(0,0,0.2,1)';
                target.style.transform = 'scale(0.96)';
            }
        }, { passive: true });

        document.addEventListener('touchend', (e) => {
            const target = e.target.closest('button, .btn, .nav-tab, .task-item, .mood-btn');
            if (target) {
                target.style.transform = 'scale(1)';
            }
        }, { passive: true });
    };

    // ==========================================
    // 4. PREVENT SYSTEM CONTEXT MENUS
    // ==========================================
    const preventCallouts = () => {
        const style = document.createElement('style');
        style.innerHTML = `
            .no-select, img, a, button {
                -webkit-touch-callout: none !important;
                -webkit-user-select: none !important;
            }
            canvas {
                touch-action: none;
            }
        `;
        document.head.appendChild(style);
    };

    // ==========================================
    // INITIALIZE
    // ==========================================
    injectSafeAreas();
    applyOLEDTheme();
    setupTapticFeel();
    preventCallouts();

    // Home Screen Web App specific
    if (window.navigator.standalone) {
        console.log("🍎 Running as Standalone Web App");
        document.body.classList.add('ios-pwa');
    }

})();
