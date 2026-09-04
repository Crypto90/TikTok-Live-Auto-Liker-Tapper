"""Built-in Web Interface and REST API Server for Headless Server Mode.

Serves a modern, responsive single-page web dashboard for remote control,
stream monitoring, favorites management, and sync operations.
Zero external dependencies (uses standard library http.server).
"""

import os
import sys
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, Optional, List, Callable

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok Live Auto-Liker — Server Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #0c0e12;
            --bg-surface: #14171f;
            --bg-elevated: #1b202a;
            --bg-card: rgba(23, 27, 36, 0.7);
            --border-subtle: #242a38;
            --border-glow: rgba(254, 44, 85, 0.25);
            --primary: #FE2C55;
            --primary-glow: rgba(254, 44, 85, 0.4);
            --secondary: #25F4EE;
            --secondary-glow: rgba(37, 244, 238, 0.35);
            --text-main: #f0f2f5;
            --text-muted: #8c96a8;
            --text-dim: #545e70;
            --green: #00e676;
            --green-glow: rgba(0, 230, 118, 0.25);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg-base);
            color: var(--text-main);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }

        /* Top Navigation */
        header {
            background: rgba(20, 23, 31, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border-subtle);
            padding: 0.85rem 1.75rem;
            position: sticky;
            top: 0;
            z-index: 100;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .brand-container {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .logo-badge {
            width: 38px;
            height: 38px;
            border-radius: 10px;
            background: linear-gradient(135deg, var(--primary) 0%, #d4173d 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 15px var(--primary-glow);
            font-size: 20px;
        }

        .brand-title {
            font-size: 1.15rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: #fff;
        }

        .brand-subtitle {
            font-size: 0.75rem;
            color: var(--secondary);
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .sync-pill {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            border-radius: 20px;
            background: var(--bg-elevated);
            border: 1px solid var(--border-subtle);
            font-size: 0.8rem;
            color: var(--text-muted);
            cursor: pointer;
            transition: var(--transition);
        }

        .sync-pill:hover {
            border-color: var(--secondary);
            color: #fff;
        }

        .sync-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--green);
            box-shadow: 0 0 8px var(--green);
        }

        .btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-family: inherit;
            font-size: 0.85rem;
            font-weight: 600;
            padding: 8px 16px;
            border-radius: var(--radius-sm);
            border: none;
            cursor: pointer;
            transition: var(--transition);
            user-select: none;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--primary) 0%, #e01740 100%);
            color: white;
            box-shadow: 0 4px 12px var(--primary-glow);
        }

        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 16px var(--primary-glow);
        }

        .btn-secondary {
            background: var(--bg-elevated);
            color: var(--text-main);
            border: 1px solid var(--border-subtle);
        }

        .btn-secondary:hover {
            background: #252c3a;
            border-color: #3b4457;
        }

        /* Main Content Layout */
        main {
            flex: 1;
            max-width: 1280px;
            margin: 0 auto;
            padding: 2rem 1.5rem;
            width: 100%;
        }

        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 6px;
            position: relative;
            overflow: hidden;
            transition: var(--transition);
        }

        .stat-card:hover {
            border-color: #3b4457;
            transform: translateY(-2px);
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        }

        .stat-label {
            font-size: 0.8rem;
            font-weight: 500;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .stat-value {
            font-size: 1.8rem;
            font-weight: 800;
            color: #fff;
            letter-spacing: -0.02em;
        }

        .stat-accent-red { color: var(--primary); }
        .stat-accent-cyan { color: var(--secondary); }
        .stat-accent-green { color: var(--green); }

        /* Tabs Bar */
        .tabs-header {
            display: flex;
            gap: 8px;
            border-bottom: 1px solid var(--border-subtle);
            margin-bottom: 1.75rem;
        }

        .tab-btn {
            padding: 10px 18px;
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--text-muted);
            background: transparent;
            border: none;
            border-bottom: 2px solid transparent;
            cursor: pointer;
            transition: var(--transition);
        }

        .tab-btn:hover {
            color: #fff;
        }

        .tab-btn.active {
            color: #fff;
            border-bottom-color: var(--primary);
        }

        .tab-pane {
            display: none;
        }

        .tab-pane.active {
            display: block;
            animation: fadeIn 0.25s ease forwards;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(4px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Section Cards */
        .card {
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }

        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.25rem;
        }

        .card-title {
            font-size: 1.1rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Streams Grid */
        .streams-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 1.25rem;
        }

        .stream-card {
            background: var(--bg-elevated);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            position: relative;
            transition: var(--transition);
        }

        .stream-card:hover {
            border-color: var(--primary);
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }

        .stream-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .stream-user {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .stream-avatar {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: #252a36;
            object-fit: cover;
            border: 2px solid var(--primary);
        }

        .stream-info h4 {
            font-size: 1rem;
            font-weight: 700;
            color: #fff;
        }

        .stream-info p {
            font-size: 0.8rem;
            color: var(--text-muted);
        }

        .live-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            background: rgba(254, 44, 85, 0.15);
            border: 1px solid var(--primary);
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--primary);
        }

        .live-pulse {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--primary);
            box-shadow: 0 0 8px var(--primary);
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.9); opacity: 0.8; }
            50% { transform: scale(1.4); opacity: 1; }
            100% { transform: scale(0.9); opacity: 0.8; }
        }

        .stream-controls {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(0, 0, 0, 0.2);
            padding: 8px 12px;
            border-radius: var(--radius-sm);
        }

        .icon-toggle {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1.25rem;
            padding: 4px 8px;
            border-radius: 6px;
            transition: var(--transition);
        }

        .icon-toggle:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        /* Favorites List */
        .favorites-controls {
            display: flex;
            gap: 10px;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }

        .search-input, .add-input {
            flex: 1;
            min-width: 200px;
            background: var(--bg-elevated);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-sm);
            padding: 10px 14px;
            color: #fff;
            font-family: inherit;
            font-size: 0.9rem;
            outline: none;
            transition: var(--transition);
        }

        .search-input:focus, .add-input:focus {
            border-color: var(--secondary);
            box-shadow: 0 0 10px var(--secondary-glow);
        }

        .fav-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .fav-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 14px;
            background: var(--bg-elevated);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-sm);
            transition: var(--transition);
        }

        .fav-row:hover {
            border-color: #3b4457;
            background: #1f2533;
        }

        .fav-user-info {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .fav-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: #252a36;
            object-fit: cover;
        }

        .fav-username {
            font-weight: 600;
            font-size: 0.95rem;
        }

        .fav-status {
            font-size: 0.8rem;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 12px;
        }

        .fav-status.live {
            background: rgba(254, 44, 85, 0.2);
            color: var(--primary);
        }

        .fav-status.offline {
            color: var(--text-dim);
        }

        .fav-actions {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* Settings Form */
        .settings-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.5rem;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 1.25rem;
        }

        .form-label {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-main);
            display: flex;
            justify-content: space-between;
        }

        .form-range {
            accent-color: var(--primary);
            cursor: pointer;
            width: 100%;
        }

        .form-select {
            background: var(--bg-elevated);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-sm);
            padding: 10px 14px;
            color: #fff;
            font-family: inherit;
            font-size: 0.9rem;
            outline: none;
        }

        /* Logs Console */
        .logs-box {
            background: #090a0d;
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 1rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: #c9d1d9;
            height: 360px;
            overflow-y: auto;
            line-height: 1.6;
        }

        .log-entry {
            margin-bottom: 4px;
            word-break: break-all;
        }

        .log-time { color: var(--text-dim); }
        .log-info { color: var(--secondary); }
        .log-live { color: var(--primary); font-weight: bold; }
        .log-success { color: var(--green); }

        /* Toast notification */
        #toast {
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: var(--bg-elevated);
            border: 1px solid var(--border-subtle);
            color: #fff;
            padding: 12px 20px;
            border-radius: var(--radius-md);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            font-size: 0.9rem;
            font-weight: 600;
            opacity: 0;
            transform: translateY(10px);
            transition: var(--transition);
            pointer-events: none;
            z-index: 1000;
        }

        #toast.show {
            opacity: 1;
            transform: translateY(0);
        }

        @media (max-width: 768px) {
            header { padding: 0.75rem 1rem; }
            main { padding: 1rem; }
            .stats-grid { grid-template-columns: 1fr 1fr; }
        }
    </style>
</head>
<body>
    <header>
        <div class="brand-container">
            <div class="logo-badge">⚡</div>
            <div>
                <div class="brand-title">TikTok Live Auto-Liker</div>
                <div class="brand-subtitle">Headless Server Edition</div>
            </div>
        </div>
        <div class="header-actions">
            <div class="sync-pill" id="syncStatusBtn" onclick="triggerSync()" title="Click to sync now">
                <div class="sync-dot"></div>
                <span id="syncText">Sync: Idle</span>
            </div>
        </div>
    </header>

    <main>
        <!-- Top Stats Metrics -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Monitored Creators</div>
                <div class="stat-value" id="statMonitored">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Currently Live</div>
                <div class="stat-value stat-accent-red" id="statLive">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Active Tappers</div>
                <div class="stat-value stat-accent-cyan" id="statTapping">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Server Uptime</div>
                <div class="stat-value stat-accent-green" id="statUptime">0s</div>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="tabs-header">
            <button class="tab-btn active" id="tabStreamsBtn" onclick="switchTab('streams')">📡 Active Streams</button>
            <button class="tab-btn" id="tabFavsBtn" onclick="switchTab('favorites')">⭐ Favorites Manager</button>
            <button class="tab-btn" id="tabSettingsBtn" onclick="switchTab('settings')">⚙️ Settings & Sync</button>
            <button class="tab-btn" id="tabLogsBtn" onclick="switchTab('logs')">📜 Activity Logs</button>
        </div>

        <!-- Tab 1: Active Streams -->
        <div class="tab-pane active" id="pane-streams">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">Live Tapping Sessions</div>
                </div>
                <div id="streamsList" class="streams-grid">
                    <div style="color: var(--text-muted); font-size: 0.9rem; grid-column: 1 / -1; padding: 2rem 0; text-align: center;">
                        No active live streams currently. The server is quietly monitoring your favorites.
                    </div>
                </div>
            </div>
        </div>

        <!-- Tab 2: Favorites Manager -->
        <div class="tab-pane" id="pane-favorites">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">Manage Favorite Creators</div>
                </div>
                <div class="favorites-controls">
                    <input type="text" id="newUsername" class="add-input" placeholder="Add TikTok username (e.g. @username)">
                    <button class="btn btn-primary" id="addCreatorBtn" onclick="addFavorite()">+ Add Creator</button>
                    <input type="text" id="favSearch" class="search-input" placeholder="Search creators..." oninput="renderFavorites()">
                </div>
                <div id="favsListContainer" class="fav-list">
                    <!-- Populated dynamically -->
                </div>
            </div>
        </div>

        <!-- Tab 3: Settings & Sync -->
        <div class="tab-pane" id="pane-settings">
            <div class="settings-grid">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">⚡ Auto-Tapper Rates</div>
                    </div>
                    <div class="form-group">
                        <div class="form-label">
                            <span>Base Delay</span>
                            <span id="delayValLbl" style="color: var(--primary);">100 ms</span>
                        </div>
                        <input type="range" class="form-range" id="delaySlider" min="50" max="500" value="100" oninput="onSpeedChange()">
                    </div>
                    <div class="form-group">
                        <div class="form-label">
                            <span>Randomization Jitter</span>
                            <span id="randValLbl" style="color: var(--secondary);">50 ms</span>
                        </div>
                        <input type="range" class="form-range" id="randSlider" min="0" max="100" value="50" oninput="onSpeedChange()">
                    </div>
                    <button class="btn btn-primary" id="saveSpeedBtn" onclick="saveSettings()">Save Rates</button>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">☁️ Multi-Device Sync</div>
                    </div>
                    <div class="form-group">
                        <div class="form-label">Sync Status</div>
                        <div id="syncDetailText" style="font-size: 0.85rem; color: var(--text-muted);">
                            Checking sync status...
                        </div>
                    </div>
                    <div style="display: flex; gap: 10px; margin-top: 1rem;">
                        <button class="btn btn-primary" id="manualSyncBtn" onclick="triggerSync()">Sync Now</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tab 4: Logs -->
        <div class="tab-pane" id="pane-logs">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">Server Event Log</div>
                    <button class="btn btn-secondary" onclick="fetchLogs()">Refresh Logs</button>
                </div>
                <div id="logsConsole" class="logs-box">
                    <!-- Populated dynamically -->
                </div>
            </div>
        </div>
    </main>

    <div id="toast">Notification</div>

    <script>
        let allFavorites = [];
        let activeStreams = [];

        function showToast(msg) {
            const toast = document.getElementById('toast');
            toast.textContent = msg;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2800);
        }

        function switchTab(tabId) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            document.getElementById('tab' + tabId.charAt(0).toUpperCase() + tabId.slice(1) + 'Btn').classList.add('active');
            document.getElementById('pane-' + tabId).classList.add('active');
            if (tabId === 'logs') fetchLogs();
        }

        function formatUptime(seconds) {
            const h = Math.floor(seconds / 3600);
            const m = Math.floor((seconds % 3600) / 60);
            const s = Math.floor(seconds % 60);
            if (h > 0) return `${h}h ${m}m ${s}s`;
            if (m > 0) return `${m}m ${s}s`;
            return `${s}s`;
        }

        async function fetchStatus() {
            try {
                const res = await fetch('/api/status');
                if (!res.ok) return;
                const data = await res.json();
                document.getElementById('statMonitored').textContent = data.monitored_count || 0;
                document.getElementById('statLive').textContent = data.live_count || 0;
                document.getElementById('statTapping').textContent = data.tapping_count || 0;
                document.getElementById('statUptime').textContent = formatUptime(data.uptime || 0);

                if (data.sync_status) {
                    document.getElementById('syncText').textContent = data.sync_status;
                    document.getElementById('syncDetailText').textContent = data.sync_status;
                }

                activeStreams = data.active_streams || [];
                renderActiveStreams();
            } catch (e) {}
        }

        function renderActiveStreams() {
            const container = document.getElementById('streamsList');
            if (!activeStreams.length) {
                container.innerHTML = `
                    <div style="color: var(--text-muted); font-size: 0.9rem; grid-column: 1 / -1; padding: 2rem 0; text-align: center;">
                        No active live streams currently. The server is quietly monitoring your favorites.
                    </div>
                `;
                return;
            }

            container.innerHTML = activeStreams.map(s => `
                <div class="stream-card">
                    <div class="stream-header">
                        <div class="stream-user">
                            <img class="stream-avatar" src="${s.avatar_url || 'data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'40\\' height=\\'40\\' fill=\\'%23555\\'><circle cx=\\'20\\' cy=\\'20\\' r=\\'20\\'/></svg>'}" alt="${s.username}">
                            <div class="stream-info">
                                <h4>@${s.username}</h4>
                                <p>Rate: ~${s.base_delay_ms || 100}ms</p>
                            </div>
                        </div>
                        <div class="live-badge">
                            <div class="live-pulse"></div>
                            LIVE
                        </div>
                    </div>
                    <div class="stream-controls">
                        <span style="font-size: 0.85rem; color: var(--text-muted);">Auto-Tapper:</span>
                        <div>
                            <button class="icon-toggle" onclick="toggleCreator('${s.username}', 'tapper')" title="Toggle Tapping">
                                ${s.tapper_enabled ? '❤️' : '🤍'}
                            </button>
                            <button class="icon-toggle" onclick="toggleCreator('${s.username}', 'mute')" title="Toggle Audio Mute">
                                ${s.is_muted ? '🔇' : '🔊'}
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        async function fetchFavorites() {
            try {
                const res = await fetch('/api/favorites');
                if (!res.ok) return;
                allFavorites = await res.json();
                renderFavorites();
            } catch (e) {}
        }

        function renderFavorites() {
            const query = (document.getElementById('favSearch').value || '').toLowerCase();
            const container = document.getElementById('favsListContainer');
            const filtered = allFavorites.filter(f => f.username.toLowerCase().includes(query));

            if (!filtered.length) {
                container.innerHTML = '<div style="color: var(--text-muted); padding: 1rem; text-align: center;">No creators found.</div>';
                return;
            }

            container.innerHTML = filtered.map(f => `
                <div class="fav-row">
                    <div class="fav-user-info">
                        <img class="fav-avatar" src="${f.avatar_url || 'data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'32\\' height=\\'32\\' fill=\\'%23555\\'><circle cx=\\'16\\' cy=\\'16\\' r=\\'16\\'/></svg>'}" alt="${f.username}">
                        <span class="fav-username">@${f.username}</span>
                        <span class="fav-status ${f.is_live ? 'live' : 'offline'}">${f.is_live ? '● LIVE' : 'Offline'}</span>
                    </div>
                    <div class="fav-actions">
                        <button class="icon-toggle" onclick="toggleCreator('${f.username}', 'tapper')" title="Toggle Auto-Tapper">
                            ${f.tapper_enabled ? '❤️' : '🤍'}
                        </button>
                        <button class="icon-toggle" onclick="toggleCreator('${f.username}', 'mute')" title="Toggle Mute">
                            ${f.is_muted ? '🔇' : '🔊'}
                        </button>
                        <button class="icon-toggle" onclick="removeFavorite('${f.username}')" title="Remove Creator" style="color: #ff5252;">
                            ✕
                        </button>
                    </div>
                </div>
            `).join('');
        }

        async function addFavorite() {
            const input = document.getElementById('newUsername');
            let un = input.value.trim().replace(/^@/, '');
            if (!un) return;
            try {
                const res = await fetch('/api/favorites/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: un })
                });
                if (res.ok) {
                    input.value = '';
                    showToast(`Added @${un} to favorites!`);
                    await fetchFavorites();
                    await fetchStatus();
                }
            } catch (e) {}
        }

        async function removeFavorite(username) {
            if (!confirm(`Remove @${username} from favorites?`)) return;
            try {
                const res = await fetch('/api/favorites/remove', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username })
                });
                if (res.ok) {
                    showToast(`Removed @${username}`);
                    await fetchFavorites();
                    await fetchStatus();
                }
            } catch (e) {}
        }

        async function toggleCreator(username, field) {
            try {
                const res = await fetch('/api/favorites/toggle', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, field })
                });
                if (res.ok) {
                    await fetchFavorites();
                    await fetchStatus();
                }
            } catch (e) {}
        }

        function onSpeedChange() {
            document.getElementById('delayValLbl').textContent = document.getElementById('delaySlider').value + ' ms';
            document.getElementById('randValLbl').textContent = document.getElementById('randSlider').value + ' ms';
        }

        async function fetchSettings() {
            try {
                const res = await fetch('/api/settings');
                if (!res.ok) return;
                const data = await res.json();
                if (data.like_delay_ms) document.getElementById('delaySlider').value = data.like_delay_ms;
                if (data.randomization_ms !== undefined) document.getElementById('randSlider').value = data.randomization_ms;
                onSpeedChange();
            } catch (e) {}
        }

        async function saveSettings() {
            const like_delay_ms = parseInt(document.getElementById('delaySlider').value);
            const randomization_ms = parseInt(document.getElementById('randSlider').value);
            try {
                const res = await fetch('/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ like_delay_ms, randomization_ms })
                });
                if (res.ok) {
                    showToast('Tapping rates saved!');
                }
            } catch (e) {}
        }

        async function triggerSync() {
            showToast('Triggering synchronization...');
            try {
                const res = await fetch('/api/sync', { method: 'POST' });
                const data = await res.json();
                showToast(data.message || 'Sync completed!');
                await fetchStatus();
                await fetchFavorites();
            } catch (e) {
                showToast('Sync request failed');
            }
        }

        async function fetchLogs() {
            try {
                const res = await fetch('/api/logs');
                if (!res.ok) return;
                const logs = await res.json();
                const box = document.getElementById('logsConsole');
                box.innerHTML = logs.map(l => {
                    let cls = 'log-entry';
                    if (l.includes('LIVE')) cls += ' log-live';
                    else if (l.includes('Synced')) cls += ' log-success';
                    return `<div class="${cls}"><span class="log-time">[${l.time}]</span> ${l.message}</div>`;
                }).join('');
                box.scrollTop = box.scrollHeight;
            } catch (e) {}
        }

        // Initialize dashboard
        fetchStatus();
        fetchFavorites();
        fetchSettings();

        // Real-time polling
        setInterval(fetchStatus, 3000);
        setInterval(fetchFavorites, 6000);
    </script>
</body>
</html>
"""


class DashboardHTTPRequestHandler(BaseHTTPRequestHandler):
    server_version = "TikTokLiveHeadlessWeb/1.0"
    runner_ref = None  # Injected by WebServer

    def _send_json(self, status_code: int, data: Any):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        runner = self.runner_ref
        path = self.path.split("?")[0].rstrip("/")

        if path in ("", "/index.html", "/dashboard"):
            payload = DASHBOARD_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if path == "/api/status":
            if not runner:
                self._send_json(200, {})
                return
            status_data = runner.get_status_summary()
            self._send_json(200, status_data)
            return

        if path == "/api/favorites":
            if not runner:
                self._send_json(200, [])
                return
            favs = runner.get_favorites_list()
            self._send_json(200, favs)
            return

        if path == "/api/settings":
            if not runner:
                self._send_json(200, {})
                return
            self._send_json(200, runner.get_settings())
            return

        if path == "/api/logs":
            if not runner:
                self._send_json(200, [])
                return
            self._send_json(200, runner.get_recent_logs())
            return

        self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        runner = self.runner_ref
        path = self.path.split("?")[0].rstrip("/")

        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        if path == "/api/favorites/add":
            username = str(payload.get("username", "")).strip().lower().replace("@", "")
            if not username:
                self._send_json(400, {"error": "Username required"})
                return
            if runner:
                runner.add_favorite(username)
            self._send_json(200, {"status": "ok", "username": username})
            return

        if path == "/api/favorites/remove":
            username = str(payload.get("username", "")).strip().lower().replace("@", "")
            if not username:
                self._send_json(400, {"error": "Username required"})
                return
            if runner:
                runner.remove_favorite(username)
            self._send_json(200, {"status": "ok", "username": username})
            return

        if path == "/api/favorites/toggle":
            username = str(payload.get("username", "")).strip().lower().replace("@", "")
            field = str(payload.get("field", "tapper"))
            if not username:
                self._send_json(400, {"error": "Username required"})
                return
            if runner:
                runner.toggle_favorite_field(username, field)
            self._send_json(200, {"status": "ok", "username": username, "field": field})
            return

        if path == "/api/settings":
            if runner:
                runner.update_settings(payload)
            self._send_json(200, {"status": "ok"})
            return

        if path == "/api/sync":
            if runner:
                msg = runner.trigger_sync()
            else:
                msg = "No runner connected"
            self._send_json(200, {"status": "ok", "message": msg})
            return

        self._send_json(404, {"error": "Not found"})

    def log_message(self, format, *args):
        # Silence per-request console spam in headless mode
        pass


class HeadlessWebServer:
    """Manages the background HTTP server serving the Web Dashboard."""
    def __init__(self, host: str = "0.0.0.0", port: int = 8080, runner_ref=None):
        self.host = host
        self.port = port
        self.runner_ref = runner_ref
        self.httpd: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    def start(self):
        DashboardHTTPRequestHandler.runner_ref = self.runner_ref
        server_address = (self.host, self.port)
        self.httpd = HTTPServer(server_address, DashboardHTTPRequestHandler)
        self._thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self._thread.start()
        print(f"[Web Dashboard] Server running at: http://{self.host}:{self.port}")

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.httpd = None
