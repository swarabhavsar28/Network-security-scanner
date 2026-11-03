// ===========================
// Global State
// ===========================
let pieChartInstance = null;
let barChartInstance = null;
let liveInterval = null;
let allEvents = [];
let rawFilter = '';

Chart.defaults.color = '#71717a';
Chart.defaults.font.family = "'Inter', sans-serif";

// ===========================
// SPA Navigation
// ===========================
function navigate(viewName) {
    document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
    document.getElementById('view-' + viewName).classList.remove('hidden');
    document.querySelectorAll('.nav-link').forEach(l => {
        l.classList.remove('active');
        if (l.dataset.view === viewName) l.classList.add('active');
    });
}

document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        navigate(link.dataset.view);
    });
});

// ===========================
// Global Search
// ===========================
document.getElementById('globalSearch').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        const q = e.target.value.trim();
        if (q) {
            rawFilter = q.toLowerCase();
            navigate('rawlogs');
            renderRawLogs();
        }
    }
});

// ===========================
// File Input Label Update
// ===========================
document.getElementById('csvFile').addEventListener('change', function(e) {
    const fileName = e.target.files[0]?.name || 'Select File';
    document.getElementById('fileName').textContent = fileName;
});

// ===========================
// Live Mode
// ===========================
const liveModeBtn = document.getElementById('liveModeBtn');
const liveIndicator = document.getElementById('liveIndicator');

liveModeBtn.addEventListener('click', async () => {
    if (liveInterval) {
        clearInterval(liveInterval);
        liveInterval = null;
        liveIndicator.className = 'mr-2 w-1.5 h-1.5 rounded-full bg-slate-600 transition-all';
        liveModeBtn.classList.remove('text-emerald-400');
    } else {
        await fetch('/api/live-data', { method: 'DELETE' });
        liveIndicator.className = 'mr-2 w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse';
        liveModeBtn.classList.add('text-emerald-400');
        document.getElementById('dashboardContent').classList.remove('hidden');
        fetchLiveData();
        liveInterval = setInterval(fetchLiveData, 2000);
    }
});

async function fetchLiveData() {
    try {
        const response = await fetch('/api/live-data');
        const data = await response.json();
        if (response.ok && data.status === 'success') {
            updateDashboard(data.data);
        }
    } catch (err) {
        console.error("Live fetch error:", err);
    }
}

// ===========================
// CSV Upload
// ===========================
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('csvFile');
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    const loading = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const originalBtnContent = analyzeBtn.innerHTML;

    loading.classList.remove('hidden');
    errorDiv.classList.add('hidden');
    document.getElementById('dashboardContent').classList.add('hidden');
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-1.5 text-xs"></i> Ingesting...';

    try {
        const response = await fetch('/upload', { method: 'POST', body: formData });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Failed to analyze');
        updateDashboard(data.data);
        document.getElementById('dashboardContent').classList.remove('hidden');
    } catch (err) {
        document.getElementById('errorText').textContent = err.message;
        errorDiv.classList.remove('hidden');
    } finally {
        loading.classList.add('hidden');
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = originalBtnContent;
    }
});

// ===========================
// Update all views with data
// ===========================
function updateDashboard(data) {
    const stats = data.stats;
    const events = data.events;
    allEvents = events;

    // Stats
    document.getElementById('statTotalLogs').textContent = stats.total_logs.toLocaleString();
    document.getElementById('statTotalAnomalies').textContent = stats.total_anomalies.toLocaleString();
    document.getElementById('logTypeHeader').textContent = stats.log_type || '—';

    const threatEl = document.getElementById('statThreatLevel');
    const ratio = stats.total_anomalies / (stats.total_logs || 1);
    if (stats.total_anomalies === 0) {
        threatEl.textContent = 'Clear'; threatEl.className = 'text-3xl font-semibold text-emerald-400 tracking-tight';
    } else if (ratio < 0.05) {
        threatEl.textContent = 'Elevated'; threatEl.className = 'text-3xl font-semibold text-amber-400 tracking-tight';
    } else if (ratio < 0.15) {
        threatEl.textContent = 'High'; threatEl.className = 'text-3xl font-semibold text-orange-400 tracking-tight';
    } else {
        threatEl.textContent = 'Critical'; threatEl.className = 'text-3xl font-semibold text-rose-500 tracking-tight';
    }

    // Notification dot & badge
    if (events.length > 0) {
        document.getElementById('notifDot').classList.remove('hidden');
        const badge = document.getElementById('incidentBadge');
        badge.textContent = events.length;
        badge.classList.remove('hidden');
    }

    renderCharts(stats);
    renderRecentEvents(events.slice(-5).reverse());
    renderIncidents(events);
    renderRawLogs();
}

// ===========================
// Charts
// ===========================
function renderCharts(stats) {
    renderPieChart(stats.anomaly_breakdown);
    renderBarChart(stats.top_active_ips);
}

function renderPieChart(breakdown) {
    const ctx = document.getElementById('anomalyPieChart').getContext('2d');
    if (pieChartInstance) pieChartInstance.destroy();
    const labels = Object.keys(breakdown);
    const data = Object.values(breakdown);
    if (labels.length === 0) { labels.push("No Anomalies"); data.push(1); }
    pieChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels, datasets: [{
                data,
                backgroundColor: ['#f43f5e','#6366f1','#0ea5e9','#f59e0b','#10b981'],
                borderWidth: 0, hoverOffset: 4
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom', labels: { usePointStyle: true, padding: 16, font: { size: 11 } } } },
            cutout: '72%'
        }
    });
}

function renderBarChart(topIps) {
    const ctx = document.getElementById('topIpsBarChart').getContext('2d');
    if (barChartInstance) barChartInstance.destroy();
    barChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(topIps),
            datasets: [{
                label: 'Events', data: Object.values(topIps),
                backgroundColor: 'rgba(99,102,241,0.15)',
                borderColor: '#6366f1', borderWidth: 1,
                hoverBackgroundColor: 'rgba(99,102,241,0.35)',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.04)' }, border: { display: false } },
                x: { grid: { display: false }, border: { display: false } }
            },
            plugins: { legend: { display: false } }
        }
    });
}

// ===========================
// Recent Events (Dashboard)
// ===========================
function renderRecentEvents(events) {
    const tbody = document.getElementById('recentEventsBody');
    tbody.innerHTML = '';
    if (events.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="px-5 py-8 text-center text-slate-600 text-xs">No anomalies detected</td></tr>`;
        return;
    }
    events.forEach(event => {
        const badge = getBadge(event.reason);
        let timeStr = event.timestamp.includes('T') ? event.timestamp.split('T')[1].split('.')[0] : event.timestamp;
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-white/[0.015] transition-colors text-xs';
        tr.innerHTML = `
            <td class="px-5 py-3 font-mono text-slate-500">${timeStr}</td>
            <td class="px-5 py-3 font-mono text-slate-300">${event.source_ip}</td>
            <td class="px-5 py-3"><span class="${badge.cls} px-2 py-0.5 rounded text-[10px] font-medium">${event.reason}</span></td>
            <td class="px-5 py-3 text-slate-500 truncate max-w-xs">${event.details}</td>
        `;
        tbody.appendChild(tr);
    });
}

// ===========================
// Incidents View
// ===========================
let currentFilter = 'all';

function renderIncidents(events) {
    const empty = document.getElementById('incidentsEmpty');
    const table = document.getElementById('incidentsTable');
    document.getElementById('incidentCount').textContent = events.length;

    if (events.length === 0) {
        empty.classList.remove('hidden');
        table.classList.add('hidden');
        return;
    }
    empty.classList.add('hidden');
    table.classList.remove('hidden');
    renderIncidentRows(events, currentFilter);
}

function filterIncidents(filter) {
    currentFilter = filter;
    document.querySelectorAll('.filter-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.filter === filter);
    });
    renderIncidentRows(allEvents, filter);
}

function renderIncidentRows(events, filter) {
    const tbody = document.getElementById('incidentsBody');
    tbody.innerHTML = '';
    const filtered = events.filter(e => {
        if (filter === 'all') return true;
        const sev = getSeverity(e.reason);
        return sev === filter;
    });
    filtered.forEach(event => {
        const badge = getBadge(event.reason);
        const sev = getSeverity(event.reason);
        let timeStr = event.timestamp.includes('T') ? event.timestamp.split('T')[1].split('.')[0] : event.timestamp;
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-white/[0.015] transition-colors text-xs';
        tr.innerHTML = `
            <td class="px-5 py-3"><span class="${badge.cls} px-2 py-0.5 rounded text-[10px] font-semibold uppercase">${sev}</span></td>
            <td class="px-5 py-3 font-mono text-slate-500">${timeStr}</td>
            <td class="px-5 py-3 font-mono text-slate-200">${event.source_ip}</td>
            <td class="px-5 py-3 font-mono text-slate-500">${event.destination_ip}</td>
            <td class="px-5 py-3 text-slate-500">${event.destination_port}</td>
            <td class="px-5 py-3"><span class="${badge.cls} px-2 py-0.5 rounded text-[10px] font-medium">${event.reason}</span></td>
            <td class="px-5 py-3 text-slate-500 max-w-xs truncate" title="${event.details}">${event.details}</td>
        `;
        tbody.appendChild(tr);
    });
}

// ===========================
// Raw Logs View
// ===========================
document.getElementById('rawSearch').addEventListener('input', (e) => {
    rawFilter = e.target.value.toLowerCase();
    renderRawLogs();
});

function renderRawLogs() {
    const empty = document.getElementById('rawEmpty');
    const table = document.getElementById('rawTable');
    if (allEvents.length === 0) {
        empty.classList.remove('hidden');
        table.classList.add('hidden');
        return;
    }
    empty.classList.add('hidden');
    table.classList.remove('hidden');

    const filtered = allEvents.filter(e => {
        if (!rawFilter) return true;
        return JSON.stringify(e).toLowerCase().includes(rawFilter);
    });
    document.getElementById('rawCount').textContent = `${filtered.length} events`;

    const tbody = document.getElementById('rawBody');
    tbody.innerHTML = '';
    filtered.forEach(event => {
        const badge = getBadge(event.reason);
        let timeStr = event.timestamp.includes('T') ? event.timestamp.split('T')[1].split('.')[0] : event.timestamp;
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-white/[0.015] transition-colors';
        tr.innerHTML = `
            <td class="px-5 py-2.5 text-slate-500">${timeStr}</td>
            <td class="px-5 py-2.5 text-slate-300">${event.source_ip}</td>
            <td class="px-5 py-2.5 text-slate-500">${event.destination_ip}</td>
            <td class="px-5 py-2.5 text-slate-500">${event.destination_port}</td>
            <td class="px-5 py-2.5"><span class="${badge.cls} px-2 py-0.5 rounded text-[10px] font-medium">${event.reason}</span></td>
            <td class="px-5 py-2.5 text-slate-500 max-w-xs truncate" title="${event.details}">${event.details}</td>
        `;
        tbody.appendChild(tr);
    });
}

// ===========================
// Helpers
// ===========================
function getBadge(reason) {
    const r = reason.toLowerCase();
    if (r.includes('sql') || r.includes('xss') || r.includes('blacklisted'))
        return { cls: 'bg-rose-500/10 text-rose-400 border border-rose-500/20' };
    if (r.includes('spike') || r.includes('brute force') || r.includes('dir'))
        return { cls: 'bg-amber-500/10 text-amber-400 border border-amber-500/20' };
    if (r.includes('unusual') || r.includes('admin'))
        return { cls: 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20' };
    return { cls: 'bg-white/5 text-slate-400 border border-white/10' };
}

function getSeverity(reason) {
    const r = reason.toLowerCase();
    if (r.includes('sql') || r.includes('xss') || r.includes('blacklisted')) return 'critical';
    if (r.includes('spike') || r.includes('brute force') || r.includes('dir')) return 'warning';
    return 'info';
}
