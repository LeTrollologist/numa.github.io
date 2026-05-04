/**
 * mobile-optimizer.js
 * Advanced Mobile & Battery Optimization Engine v3.0
 * Optimized for: Stargazer, Pong, Sketch, Grove, and Planner.
 */
(function() {
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth <= 768;
    if (!isMobile) return;

    console.log("📱 Mobile Optimizer v3.0 Initialized");

    // ==========================================
    // 1. POWER MANAGER (Battery & Charging)
    // ==========================================
    const PowerManager = {
        level: 1,
        isCharging: false,
        isLowPower: false,

        async init() {
            if (navigator.getBattery) {
                const battery = await navigator.getBattery();
                this.update(battery);
                battery.addEventListener('levelchange', () => this.update(battery));
                battery.addEventListener('chargingchange', () => this.update(battery));
            }
        },

        update(battery) {
            this.level = battery.level;
            this.isCharging = battery.charging;
            this.isLowPower = this.level < 0.2 && !this.isCharging;
            document.documentElement.setAttribute('data-battery-low', this.isLowPower);
        }
    };

    // ==========================================
    // 2. BOOST MANAGER (Context Awareness)
    // ==========================================
    const BoostManager = {
        activeContexts: new Set(),
        
        // Critical elements that must NEVER be throttled or downscaled
        WHITELIST: ['pongCanvas', 'cvs', 'sketchCanvas', 'garden-area'],

        init() {
            this.setupDetection();
        },

        setupDetection() {
            // Monitor active pages/modals
            const observer = new MutationObserver(() => this.update());
            observer.observe(document.body, { attributes: true, subtree: true, attributeFilter: ['class', 'style'] });
            
            // Interaction-based boost
            document.addEventListener('touchstart', (e) => {
                if (this.WHITELIST.some(id => e.target.id === id || e.target.closest('#' + id))) {
                    this.applyTemporaryBoost(8000);
                }
            }, { passive: true });
        },

        update() {
            const stargazer = document.getElementById('page-stargazer');
            const minigame = document.getElementById('page-minigame');
            
            if (stargazer?.classList.contains('active')) this.activeContexts.add('stargazer');
            else this.activeContexts.delete('stargazer');

            if (minigame?.classList.contains('active')) this.activeContexts.add('minigame');
            else this.activeContexts.delete('minigame');
        },

        applyTemporaryBoost(ms) {
            this.activeContexts.add('interaction');
            clearTimeout(this.boostTimeout);
            this.boostTimeout = setTimeout(() => this.activeContexts.delete('interaction'), ms);
        },

        isBoosted() {
            return this.activeContexts.size > 0 || PowerManager.isCharging;
        }
    };

    // ==========================================
    // 3. VISUAL MANAGER (Canvas & CSS)
    // ==========================================
    const VisualManager = {
        init() {
            this.patchCanvas();
            this.applyStyles();
        },

        patchCanvas() {
            const origWidth = Object.getOwnPropertyDescriptor(HTMLCanvasElement.prototype, 'width');
            const origHeight = Object.getOwnPropertyDescriptor(HTMLCanvasElement.prototype, 'height');

            const applyScaling = (canvas, val, descriptor) => {
                const isStars = canvas.id === 'stars';
                const isWhitelisted = BoostManager.WHITELIST.includes(canvas.id);
                
                if (isStars && !BoostManager.isBoosted()) {
                    // background stars can be low-res
                    descriptor.set.call(canvas, Math.floor(val * 0.7));
                } else {
                    descriptor.set.call(canvas, val);
                }
            };

            Object.defineProperty(HTMLCanvasElement.prototype, 'width', {
                set(val) { applyScaling(this, val, origWidth); },
                get() { return origWidth.get.call(this); }
            });

            Object.defineProperty(HTMLCanvasElement.prototype, 'height', {
                set(val) { applyScaling(this, val, origHeight); },
                get() { return origHeight.get.call(this); }
            });
        },

        applyStyles() {
            if (navigator.deviceMemory <= 4) {
                const style = document.createElement('style');
                style.innerHTML = `
                    #nav-bar, .glass-card, .status-card, .sidebar, .page-header {
                        backdrop-filter: blur(4px) !important;
                        -webkit-backdrop-filter: blur(4px) !important;
                        background: rgba(10, 10, 25, 0.92) !important;
                    }
                `;
                document.head.appendChild(style);
            }
        }
    };

    // ==========================================
    // 4. EVENT MANAGER (Symmetric Throttling)
    // ==========================================
    const EventManager = {
        wrappedListeners: new WeakMap(),

        init() {
            this.patchEvents();
        },

        patchEvents() {
            const originalAdd = EventTarget.prototype.addEventListener;
            const originalRemove = EventTarget.prototype.removeEventListener;
            const self = this;

            EventTarget.prototype.addEventListener = function(type, listener, options) {
                if (type === 'touchmove' && typeof listener === 'function') {
                    const wrapped = function(e) {
                        if (!this._lastMove || Date.now() - this._lastMove > 16) {
                            this._lastMove = Date.now();
                            listener.call(this, e);
                        }
                    };
                    self.wrappedListeners.set(listener, wrapped);
                    return originalAdd.call(this, type, wrapped, options);
                }
                return originalAdd.call(this, type, listener, options);
            };

            EventTarget.prototype.removeEventListener = function(type, listener, options) {
                const wrapped = self.wrappedListeners.get(listener);
                return originalRemove.call(this, type, wrapped || listener, options);
            };
        }
    };

    // ==========================================
    // 5. FRAME ENGINE (RAF Patch)
    // ==========================================
    const FrameEngine = {
        frameCounter: 0,

        init() {
            const originalRAF = window.requestAnimationFrame;
            window.requestAnimationFrame = (callback) => {
                return originalRAF((time) => {
                    this.frameCounter++;
                    
                    // Logic: Skip frames only if NOT boosted AND (Battery Low OR intentionally saving)
                    let skipRate = 1;
                    if (!BoostManager.isBoosted()) {
                        if (PowerManager.level < 0.15) skipRate = 3;
                        else if (PowerManager.level < 0.4) skipRate = 2;
                    }

                    if (this.frameCounter % skipRate !== 0) {
                        window.requestAnimationFrame(callback);
                        return;
                    }

                    callback(time);
                });
            };
        }
    };

    // ==========================================
    // INITIALIZE
    // ==========================================
    PowerManager.init();
    BoostManager.init();
    VisualManager.init();
    EventManager.init();
    FrameEngine.init();

})();

