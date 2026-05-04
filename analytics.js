/**
 * Sentinel Analytics Uplink
 * Tracks page views and session metadata.
 */
(function () {
    const SENTINEL_URL = 'https://analytics-server-bdrm.onrender.com/log';
    
    // Session Management
    let sessionId = sessionStorage.getItem('_sid');
    if (!sessionId) {
        sessionId = Math.random().toString(36).slice(2) + Date.now().toString(36);
        sessionStorage.setItem('_sid', sessionId);
    }

    // Tracking Payload
    const payload = {
        ua: navigator.userAgent,
        page: window.location.pathname + window.location.search || '/',
        screen: window.innerWidth + 'x' + window.innerHeight,
        referrer: document.referrer || '',
        sessionId: sessionId,
        timestamp: new Date().toISOString()
    };

    // Dispatch
    fetch(SENTINEL_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        keepalive: true
    }).catch(() => {
        // Fail silently to avoid interrupting user experience
    });
})();
