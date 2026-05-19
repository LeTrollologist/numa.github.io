/**
 * Sentinel Analytics Uplink
 * Tracks page views, advanced hardware telemetry, and session metrics.
 * Exposes a global window.Sentinel.track() SDK and dispatches periodic activity heartbeats.
 */
(function () {
    const SENTINEL_URL = 'https://analytics-server-bdrm.onrender.com';
    const host = window.location.hostname;

    if (
        host === 'localhost' ||
        host === '127.0.0.1' ||
        host === '::1' ||
        window.location.protocol === 'file:'
    ) {
        return;
    }
    
    // Session & Page View Management
    let sessionId = sessionStorage.getItem('_sid');
    if (!sessionId) {
        sessionId = Math.random().toString(36).slice(2) + Date.now().toString(36);
        sessionStorage.setItem('_sid', sessionId);
    }
    
    let sessViews = parseInt(sessionStorage.getItem('_sv') || '0') + 1;
    sessionStorage.setItem('_sv', sessViews);

    // Calculate Page Load Duration
    let loadTime = null;
    try {
        const perf = window.performance || window.webkitPerformance || window.msPerformance || window.mozPerformance;
        if (perf && perf.timing) {
            loadTime = perf.timing.domComplete - perf.timing.navigationStart;
            // If domComplete is not finished yet, register a load listener to capture it later
            if (loadTime <= 0) {
                window.addEventListener('load', function() {
                    setTimeout(function() {
                        const finalLoadTime = perf.timing.domComplete - perf.timing.navigationStart;
                        if (finalLoadTime > 0) {
                            sendPayload({ loadTime: finalLoadTime });
                        }
                    }, 0);
                });
            }
        }
    } catch (e) {}

    function sendPayload(extra = {}) {
        const payload = {
            ua: navigator.userAgent,
            page: window.location.pathname + window.location.search || '/',
            screen: window.screen.width + 'x' + window.screen.height,
            vp: window.innerWidth + 'x' + window.innerHeight,
            dpr: window.devicePixelRatio || 1,
            col: (window.screen.colorDepth || 24) + 'bit',
            referrer: document.referrer || '',
            sessionId: sessionId,
            sessViews: sessViews,
            lang: navigator.language || 'en',
            tz: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
            timestamp: new Date().toISOString(),
            ...extra
        };

        fetch(SENTINEL_URL + '/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            keepalive: true
        }).catch(() => {});
    }

    // Initial log dispatch
    sendPayload({ loadTime: loadTime > 0 ? loadTime : null });

    // Expose Custom Event tracking SDK globally
    window.Sentinel = {
        track: function (eventName, eventData) {
            if (!eventName) return;
            const eventPayload = {
                sessionId: sessionId,
                event: eventName.toString().slice(0, 50),
                data: eventData || {},
                page: window.location.pathname + window.location.search || '/',
                timestamp: new Date().toISOString()
            };
            fetch(SENTINEL_URL + '/log/event', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(eventPayload),
                keepalive: true
            }).catch(() => {});
        }
    };

    // ── Heartbeat Activity Engine ─────────────────────────────────────────────
    // Tracks active engagement on dedicated sectors with custom page-specific rates:
    // - Sketchbook (sketchin): 5 minutes
    // - Core SPA (index/gamein): 2 minutes
    // - Grove (grovein): 10 minutes
    // - Planner (planner): 2 minutes
    try {
        const path = window.location.pathname.toLowerCase();
        let intervalMs = 300000; // default 5 mins
        let sectorLabel = 'Core SPA';

        if (path.includes('sketchin')) {
            intervalMs = 300000; // 5 mins
            sectorLabel = 'Sketchbook';
        } else if (path.includes('grovein')) {
            intervalMs = 600000; // 10 mins
            sectorLabel = 'Grove';
        } else if (path.includes('planner')) {
            intervalMs = 120000; // 2 mins
            sectorLabel = 'Planner';
        } else if (path.includes('index') || path === '/' || path.includes('gamein')) {
            intervalMs = 120000; // 2 mins
            sectorLabel = 'Core SPA';
        }

        let activeMinutes = 0;
        setInterval(function () {
            activeMinutes += (intervalMs / 60000);
            fetch(SENTINEL_URL + '/log/heartbeat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sessionId: sessionId,
                    page: window.location.pathname + window.location.search || '/',
                    sector: sectorLabel,
                    duration: activeMinutes
                }),
                keepalive: true
            }).catch(() => {});
        }, intervalMs);
    } catch (err) {}
})();
