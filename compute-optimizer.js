/**
 * compute-optimizer.js
 * High-Performance Computational & Rendering Engine.
 * Implements unorthodox optimizations: Visibility Tracking, Idle Scheduling, and Hardware Scaling.
 */

(function() {
    console.log("⚡ Advanced Compute Optimizer Engine Initialized");

    const CONFIG = {
        MAX_IDLE_TIME: 16, // ms
        TARGET_FPS: 60,
        LOW_POWER_FPS: 30,
        VISIBILITY_SELECTORS: '.petal, .glitter, .love-text, .note, canvas:not(#pongCanvas)',
        CONTAINMENT_SELECTORS: '.clock-box, .counter span, #timerDisplay, #score, .dl-cd'
    };

    // ==========================================
    // 1. HARDWARE & CAPABILITY ENGINE
    // ==========================================
    const HardwareEngine = {
        cores: navigator.hardwareConcurrency || 4,
        memory: navigator.deviceMemory || 4,
        isLowEnd: (navigator.hardwareConcurrency || 4) <= 4,
        
        getOptimizationLevel() {
            if (this.isLowEnd) return 'aggressive';
            return 'balanced';
        }
    };

    // ==========================================
    // 2. VISIBILITY & CONTAINMENT ENGINE
    // ==========================================
    const VisibilityEngine = {
        observer: null,

        init() {
            this.injectStyles();
            this.setupObserver();
        },

        injectStyles() {
            const style = document.createElement('style');
            style.id = 'compute-perf-styles';
            style.innerHTML = `
                /* GPU Acceleration */
                ${CONFIG.VISIBILITY_SELECTORS} {
                    will-change: transform;
                    transform: translateZ(0);
                    backface-visibility: hidden;
                }

                /* Containment */
                ${CONFIG.CONTAINMENT_SELECTORS} {
                    contain: layout paint style;
                }

                /* Off-screen Optimization */
                .is-off-screen {
                    animation-play-state: paused !important;
                    visibility: hidden !important;
                }

                /* Speed-focused Text */
                #hud, .dashboard, .study-stats {
                    text-rendering: optimizeSpeed;
                    -webkit-font-smoothing: antialiased;
                }
            `;
            document.head.appendChild(style);
        },

        setupObserver() {
            this.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.remove('is-off-screen');
                    } else {
                        entry.target.classList.add('is-off-screen');
                    }
                });
            }, { threshold: 0.1 });

            // Watch existing and future elements
            const watch = () => {
                document.querySelectorAll(CONFIG.VISIBILITY_SELECTORS).forEach(el => {
                    this.observer.observe(el);
                });
            };

            watch();
            // Periodic re-scan for dynamic elements
            setInterval(watch, 5000);
        }
    };

    // ==========================================
    // 3. EXECUTION ENGINE (Throttling & Idle Tasks)
    // ==========================================
    const ExecutionEngine = {
        tasks: [],
        
        init() {
            this.patchEventListeners();
            this.setupIdleProcessor();
        },

        // Force passive listeners to unblock main thread
        patchEventListeners() {
            const originalAdd = EventTarget.prototype.addEventListener;
            EventTarget.prototype.addEventListener = function(type, listener, options) {
                if (['wheel', 'mousewheel', 'touchstart', 'touchmove'].includes(type)) {
                    if (this.id !== 'pongCanvas' && this.id !== 'sketchCanvas' && this.id !== 'cvs') {
                        if (typeof options === 'boolean') {
                            options = { capture: options, passive: true };
                        } else if (!options || (typeof options === 'object' && options.passive === undefined)) {
                            options = Object.assign({}, options || {}, { passive: true });
                        }
                    }
                }
                return originalAdd.call(this, type, listener, options);
            };
        },

        setupIdleProcessor() {
            const process = (deadline) => {
                const timeRemaining = () => deadline ? deadline.timeRemaining() : 8;
                while (timeRemaining() > 0 && this.tasks.length > 0) {
                    const task = this.tasks.shift();
                    task();
                }
                this.scheduleNext();
            };

            this.scheduleNext = () => {
                if ('requestIdleCallback' in window) {
                    requestIdleCallback(process);
                } else {
                    setTimeout(() => process(null), 50);
                }
            };

            this.scheduleNext();
        },

        enqueue(task) {
            this.tasks.push(task);
        }
    };

    // ==========================================
    // 4. CANVAS & MEDIA ENGINE
    // ==========================================
    const MediaEngine = {
        init() {
            this.patchCanvas();
            this.optimizeImages();
            this.setupResolutionMonitor();
        },

        patchCanvas() {
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
        },

        optimizeImages() {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach(mutation => {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeName === 'IMG' && !node.complete) {
                            node.decode().catch(() => {});
                        }
                    });
                });
            });
            observer.observe(document.documentElement, { childList: true, subtree: true });
        },

        setupResolutionMonitor() {
            // Unorthodox: Monitor canvas frame times and drop resolution if lagging
            let frameTimes = [];
            let lastTime = performance.now();

            const monitor = (time) => {
                const delta = time - lastTime;
                lastTime = time;
                
                if (frameTimes.push(delta) > 60) frameTimes.shift();
                
                const avg = frameTimes.reduce((a, b) => a + b, 0) / frameTimes.length;
                
                // If avg frame time > 20ms (sub 50fps), flag for optimization
                if (avg > 20 && frameTimes.length >= 60) {
                    document.documentElement.setAttribute('data-perf-mode', 'low');
                    frameTimes = []; // Reset
                }
                
                requestAnimationFrame(monitor);
            };
            requestAnimationFrame(monitor);
        }
    };


    // ==========================================
    // INITIALIZE ALL ENGINES
    // ==========================================
    VisibilityEngine.init();
    ExecutionEngine.init();
    MediaEngine.init();

    // Export for external use
    window.ComputeOptimizer = {
        Hardware: HardwareEngine,
        Execution: ExecutionEngine,
        enqueue: (task) => ExecutionEngine.enqueue(task)
    };

})();

