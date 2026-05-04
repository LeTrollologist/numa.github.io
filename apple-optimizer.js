/**
 * apple-optimizer.js
 * Premium iOS & WebKit Enhancement Engine v1.1
 * Targets: Dynamic Safe Areas, Keyboard, OLED, ProMotion, Battery, Interaction
 */
(function() {
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || 
                  (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    
    if (!isIOS) return;

    console.log("🍎 Apple Optimizer v1.1 Initialized");

    // ==========================================
    // 1. DYNAMIC SAFE AREAS & KEYBOARD
    // ==========================================
    const setupSafeAreas = () => {
        const style = document.createElement('style');
        style.id = 'apple-dynamic-styles';
        style.innerHTML = `
            :root {
                --sat: env(safe-area-inset-top, 0px);
                --sar: env(safe-area-inset-right, 0px);
                --sab: env(safe-area-inset-bottom, 0px);
                --sal: env(safe-area-inset-left, 0px);
                --keyboard-h: 0px;
            }

            header, .page-header, #nav-bar {
                padding-top: calc(var(--sat) + 10px) !important;
            }

            /* Adjust bottom elements for both Notch and Keyboard */
            footer, .nav-tabs, .fab, #mob-overlay, .statusbar {
                padding-bottom: calc(var(--sab) + var(--keyboard-h) + 10px) !important;
            }

            /* Prevent system bounce on the main body */
            body {
                overscroll-behavior: none;
            }
        `;
        document.head.appendChild(style);

        // Handle Keyboard / Visual Viewport changes
        if (window.visualViewport) {
            window.visualViewport.addEventListener('resize', () => {
                const keyboardHeight = window.innerHeight - window.visualViewport.height;
                document.documentElement.style.setProperty('--keyboard-h', `${Math.max(0, keyboardHeight)}px`);
            });
        }
    };

    // ==========================================
    // 2. BATTERY & MOTION AWARENESS
    // ==========================================
    const setupBatteryAndMotion = async () => {
        const updateMotion = (isLow) => {
            document.documentElement.setAttribute('data-reduce-motion', isLow);
        };

        if (navigator.getBattery) {
            try {
                const battery = await navigator.getBattery();
                const check = () => updateMotion(battery.level <= 0.2 && !battery.charging);
                battery.addEventListener('levelchange', check);
                battery.addEventListener('chargingchange', check);
                check();
            } catch(e) {}
        }
        
        const style = document.createElement('style');
        style.innerHTML = `
            @media (prefers-reduced-motion: reduce) {
                *, ::before, ::after {
                    animation-delay: -1ms !important;
                    animation-duration: 1ms !important;
                    animation-iteration-count: 1 !important;
                    background-attachment: initial !important;
                    scroll-behavior: auto !important;
                    transition-duration: 0s !important;
                    transition-delay: 0s !important;
                }
            }
            [data-reduce-motion="true"] * {
                animation-duration: 0.1s !important;
                transition-duration: 0.1s !important;
            }
        `;
        document.head.appendChild(style);
    };

    // ==========================================
    // 3. PROMOTION & GPU OPTIMIZATION
    // ==========================================
    const setupProMotion = () => {
        const style = document.createElement('style');
        style.innerHTML = `
            /* Surgical layer promotion */
            #app, .main, #gameContainer, canvas, .sidebar {
                will-change: transform;
                -webkit-backface-visibility: hidden;
                backface-visibility: hidden;
            }
            /* Native iOS timing for ProMotion displays */
            .glass, .card, .btn, .nav-tab {
                transition-timing-function: cubic-bezier(0.23, 1, 0.32, 1);
            }
        `;
        document.head.appendChild(style);
    };

    // ==========================================
    // 4. REFINED TAPTIC & INTERACTION
    // ==========================================
    const setupInteractions = () => {
        const selector = 'button, .btn, .nav-tab, .task-item, .mood-btn, .interactive';
        
        // Visual Taptic Feel
        document.addEventListener('touchstart', (e) => {
            const target = e.target.closest(selector);
            if (target) {
                target.style.transition = 'transform 0.08s cubic-bezier(0,0,0.2,1)';
                target.style.transform = 'scale(0.95)';
            }
            
            // Audio Engine Warmup
            if (window.AudioContext || window.webkitAudioContext) {
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                if (ctx.state === 'suspended') ctx.resume();
            }
        }, { passive: true });

        document.addEventListener('touchend', (e) => {
            const target = e.target.closest(selector);
            if (target) target.style.transform = 'scale(1)';
        }, { passive: true });

        // Hardening
        const style = document.createElement('style');
        style.innerHTML = `
            .no-select, img, a, button, canvas {
                -webkit-touch-callout: none !important;
                -webkit-user-select: none !important;
                user-select: none !important;
            }
            input, textarea, select { font-size: 16px !important; }
            * { -webkit-overflow-scrolling: touch; }
        `;
        document.head.appendChild(style);
    };

    // ==========================================
    // 5. OLED THEME SYNC
    // ==========================================
    const applyRetinaPolishing = () => {
        const isOLED = (window.devicePixelRatio >= 3);
        if (isOLED) {
            const style = document.createElement('style');
            style.innerHTML = `
                body, .main-container, #gameContainer { background: #000000 !important; }
                .glass, .glass-card, .card, .sidebar { 
                    background: rgba(15, 15, 25, 0.8) !important; 
                    backdrop-filter: blur(25px) saturate(180%) !important;
                }
            `;
            document.head.appendChild(style);
        }
    };

    // INITIALIZE
    setupSafeAreas();
    setupBatteryAndMotion();
    setupProMotion();
    setupInteractions();
    applyRetinaPolishing();

    if (window.navigator.standalone) document.body.classList.add('ios-pwa');
})();
