<!DOCTYPE html>
<html lang="am">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Admin Dashboard</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
* { margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',system-ui,sans-serif; }
body { background:#0b1219; color:#fff; padding:20px; }
.dash-container { max-width:600px; margin:0 auto; }
h1 { font-size:24px; margin-bottom:20px; color:#4a9eff; }
.section { background:rgba(255,255,255,0.04); border-radius:12px; padding:16px; margin-bottom:16px; border:1px solid rgba(255,255,255,0.06); }
.section h3 { color:#b8a84a; font-size:16px; margin-bottom:10px; }
.section label { color:#c0d8e8; font-size:13px; display:block; margin:8px 0 4px; }
.section input, .section textarea, .section select { width:100%; padding:8px 12px; border-radius:8px; border:1px solid #2b3a4a; background:#232e3c; color:#fff; font-size:14px; outline:none; margin-bottom:8px; }
.section textarea { resize:vertical; min-height:60px; }
.save-btn { background:#4a9eff; color:#fff; border:none; padding:10px 20px; border-radius:30px; font-size:14px; font-weight:600; cursor:pointer; width:100%; transition:all 0.2s; }
.save-btn:active { transform:scale(0.97); }
.del-btn { background:#ff6b6b; color:#fff; border:none; padding:4px 10px; border-radius:16px; font-size:11px; cursor:pointer; margin-left:8px; }
.list-item { background:rgba(255,255,255,0.03); border-radius:8px; padding:8px 12px; margin-bottom:6px; display:flex; justify-content:space-between; align-items:center; font-size:13px; }
.list-item .del { color:#ff6b6b; cursor:pointer; }
.drag-item { background:rgba(255,255,255,0.05); border-radius:8px; padding:8px 12px; margin-bottom:4px; display:flex; justify-content:space-between; align-items:center; cursor:grab; border:1px solid rgba(255,255,255,0.05); }
.drag-item:active { cursor:grabbing; }
.stats-grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:12px; }
.stat-box { background:rgba(255,255,255,0.04); border-radius:8px; padding:10px; text-align:center; }
.stat-num { font-size:20px; font-weight:700; }
.stat-label { font-size:10px; color:#8aa3b5; }
.status-msg { color:#4aff8a; text-align:center; margin-top:8px; font-size:13px; }
.empty-msg { text-align:center; color:#6a8a9e; padding:20px 0; }
</style>
</head>
<body>
<div class="dash-container">
    <h1>⚙️ Admin Dashboard</h1>
    <div id="statusMsg" class="status-msg"></div>

    <!-- Stats -->
    <div class="section">
        <h3>📊 ስታት</h3>
        <div class="stats-grid" id="statsGrid">
            <div class="stat-box"><div class="stat-num" id="statCustomers">0</div><div class="stat-label">👥 ደንበኞች</div></div>
            <div class="stat-box"><div class="stat-num" id="statMessages">0</div><div class="stat-label">💬 መልእክቶች</div></div>
            <div class="stat-box"><div class="stat-num" id="statInquiries">0</div><div class="stat-label">💰 የዋጋ ጥያቄ</div></div>
            <div class="stat-box"><div class="stat-num" id="statProducts">0</div><div class="stat-label">🛍️ ምርቶች</div></div>
            <div class="stat-box"><div class="stat-num" id="statPromos">0</div><div class="stat-label">📢 ማስታወቂያ</div></div>
            <div class="stat-box"><div class="stat-num" id="statApps">0</div><div class="stat-label">📱 አፕሊኬሽን</div></div>
        </div>
    </div>

    <!-- Page Order (Drag & Drop) -->
    <div class="section">
        <h3>📌 የገጽ ቅደም ተከተል (Drag & Drop)</h3>
        <div id="pageOrderList"></div>
        <button class="save-btn" onclick="savePageOrder()">💾 ቅደም ተከተል አስቀምጥ</button>
    </div>

    <!-- Create New Page -->
    <div class="section">
        <h3>➕ አዲስ ገጽ ፍጠር</h3>
        <input type="text" id="newPageTitle" placeholder="የገጹ ርዕስ">
        <input type="text" id="newPageIcon" placeholder="አዶ (ለምሳሌ 📄)">
        <textarea id="newPageContent" placeholder="የገጹ ይዘት"></textarea>
        <button class="save-btn" onclick="createPage()">📄 ገጽ ፍጠር</button>
        <div id="pagesList"></div>
    </div>

    <!-- Theme Customizer -->
    <div class="section">
        <h3>🎨 ጭብጥ ማስተካከያ</h3>
        <label>ዋና ቀለም</label>
        <input type="color" id="themePrimary" value="#4a9eff">
        <label>የካርድ ቀለም</label>
        <input type="color" id="themeCard" value="#17212b">
        <label>የፊደል አይነት</label>
        <select id="themeFont">
            <option value="Segoe UI">Segoe UI</option>
            <option value="Arial">Arial</option>
            <option value="Times New Roman">Times New Roman</option>
        </select>
        <button class="save-btn" onclick="saveTheme()">💾 ጭብጥ አስቀምጥ</button>
    </div>

    <!-- System Settings -->
    <div class="section">
        <h3>⚙️ የስርዓት ምርጫዎች</h3>
        <label>የቦት ስም</label>
        <input type="text" id="settingsBotName" value="MarshalomSupportBot">
        <label>የእንኳን ደህና መጡ መልእክት</label>
        <input type="text" id="settingsWelcome" value="✨ እንኳን ደህና መጡ!">
        <label>የስራ ሰዓት</label>
        <input type="text" id="settingsHours" value="8:00 - 22:00">
        <button class="save-btn" onclick="saveSettings()">💾 ምርጫዎች አስቀምጥ</button>
    </div>

    <!-- Add New Feature -->
    <div class="section">
        <h3>🧩 አዲስ ባህሪ ጨምር</h3>
        <input type="text" id="newFeatureName" placeholder="የባህሪው ስም">
        <input type="text" id="newFeatureIcon" placeholder="አዶ (ለምሳሌ ⭐)">
        <button class="save-btn" onclick="addFeature()">➕ ባህሪ ጨምር</button>
        <div id="featuresList"></div>
    </div>
</div>

<script>
const tg = window.Telegram.WebApp;
tg.ready(); tg.expand();
const initData = tg.initData;

let currentPageOrder = [];
let currentPages = [];
let currentFeatures = [];

async function loadStats() {
    const res = await fetch('/api/admin/stats', {headers:{'X-Init-Data':initData}});
    const s = await res.json();
    if (s.customers !== undefined) {
        document.getElementById('statCustomers').textContent = s.customers;
        document.getElementById('statMessages').textContent = s.messages;
        document.getElementById('statInquiries').textContent = s.price_inquiries;
        document.getElementById('statProducts').textContent = s.products;
        document.getElementById('statPromos').textContent = s.promos;
    }
    const appRes = await fetch('/api/applications');
    const apps = await appRes.json();
    document.getElementById('statApps').textContent = apps.length || 0;
}

async function loadPageOrder() {
    const res = await fetch('/api/admin/page_order', {headers:{'X-Init-Data':initData}});
    currentPageOrder = await res.json();
    renderPageOrder();
}

function renderPageOrder() {
    const el = document.getElementById('pageOrderList');
    const defaultPages = ['page-home','page-products','page-call','page-social','page-share','page-news','page-applications','page-jobs','page-discount','page-ai','page-support','page-promo','page-tips','page-banks','page-feedback','page-admin','page-teamleader','page-employee'];
    const order = currentPageOrder.length ? currentPageOrder : defaultPages;
    el.innerHTML = order.map((p, i) => `
        <div class="drag-item" draggable="true" data-index="${i}" data-id="${p}">
            <span>${i+1}. ${p}</span>
            <span style="color:#6a8a9e; font-size:11px;">↕</span>
        </div>
    `).join('');
    // Drag & Drop
    let dragStart = null;
    el.querySelectorAll('.drag-item').forEach(item => {
        item.addEventListener('dragstart', (e) => {
            dragStart = parseInt(item.dataset.index);
            item.style.opacity = '0.5';
        });
        item.addEventListener('dragend', () => { item.style.opacity = '1'; });
        item.addEventListener('dragover', (e) => { e.preventDefault(); });
        item.addEventListener('drop', (e) => {
            e.preventDefault();
            const dragEnd = parseInt(item.dataset.index);
            if (dragStart !== null && dragStart !== dragEnd) {
                const items = order;
                const [removed] = items.splice(dragStart, 1);
                items.splice(dragEnd, 0, removed);
                currentPageOrder = items;
                renderPageOrder();
            }
        });
    });
}

async function savePageOrder() {
    await fetch('/api/admin/page_order', {
        method:'POST', headers:{'Content-Type':'application/json','X-Init-Data':initData},
        body:JSON.stringify({order:currentPageOrder})
    });
    showStatus('✅ ቅደም ተከተል ተቀምጧል!');
}

async function createPage() {
    const title = document.getElementById('newPageTitle').value.trim();
    const icon = document.getElementById('newPageIcon').value.trim() || '📄';
    const content = document.getElementById('newPageContent').value.trim();
    if (!title) { alert('ርዕስ ያስፈልጋል'); return; }
    await fetch('/api/admin/custom_pages', {
        method:'POST', headers:{'Content-Type':'application/json','X-Init-Data':initData},
        body:JSON.stringify({title, icon, content})
    });
    document.getElementById('newPageTitle').value = '';
    document.getElementById('newPageIcon').value = '';
    document.getElementById('newPageContent').value = '';
    showStatus('✅ ገጽ ተፈጥሯል!');
    loadPages();
}

async function loadPages() {
    const res = await fetch('/api/custom_pages');
    currentPages = await res.json();
    const el = document.getElementById('pagesList');
    if (!currentPages.length) { el.innerHTML = '<p class="empty-msg">ምንም ብጁ ገጽ የለም</p>'; return; }
    el.innerHTML = currentPages.map(p => `
        <div class="list-item">
            <span>${p.icon || '📄'} ${p.title}</span>
            <span class="del" onclick="deletePage(${p.id})">🗑️</span>
        </div>
    `).join('');
}

async function deletePage(id) {
    if (!confirm('እርግጠኛ ነህ?')) return;
    await fetch(`/api/admin/custom_pages/${id}`, {method:'DELETE', headers:{'X-Init-Data':initData}});
    showStatus('🗑️ ገጽ ተሰርዟል');
    loadPages();
}

async function saveTheme() {
    const theme = {
        primary_color: document.getElementById('themePrimary').value,
        card_color: document.getElementById('themeCard').value,
        font_family: document.getElementById('themeFont').value
    };
    await fetch('/api/admin/theme', {
        method:'POST', headers:{'Content-Type':'application/json','X-Init-Data':initData},
        body:JSON.stringify(theme)
    });
    showStatus('✅ ጭብጥ ተቀምጧል!');
}

async function saveSettings() {
    const settings = {
        bot_name: document.getElementById('settingsBotName').value,
        welcome_message: document.getElementById('settingsWelcome').value,
        working_hours: document.getElementById('settingsHours').value
    };
    await fetch('/api/admin/settings', {
        method:'POST', headers:{'Content-Type':'application/json','X-Init-Data':initData},
        body:JSON.stringify(settings)
    });
    showStatus('✅ ምርጫዎች ተቀምጠዋል!');
}

async function addFeature() {
    const name = document.getElementById('newFeatureName').value.trim();
    const icon = document.getElementById('newFeatureIcon').value.trim() || '🧩';
    if (!name) { alert('ስም ያስፈልጋል'); return; }
    // Save to custom_pages as a feature
    await fetch('/api/admin/custom_pages', {
        method:'POST', headers:{'Content-Type':'application/json','X-Init-Data':initData},
        body:JSON.stringify({title:name, icon:icon, content:'# ባህሪ\nአዲስ ባህሪ እዚህ ይጨመራል'})
    });
    document.getElementById('newFeatureName').value = '';
    document.getElementById('newFeatureIcon').value = '';
    showStatus('✅ ባህሪ ተጨምሯል!');
    loadFeatures();
}

async function loadFeatures() {
    const res = await fetch('/api/custom_pages');
    const pages = await res.json();
    const el = document.getElementById('featuresList');
    const features = pages.filter(p => p.title.includes('🧩') || p.content.includes('ባህሪ'));
    if (!features.length) { el.innerHTML = '<p class="empty-msg">ምንም ተጨማሪ ባህሪ የለም</p>'; return; }
    el.innerHTML = features.map(f => `
        <div class="list-item">
            <span>${f.icon || '🧩'} ${f.title}</span>
            <span class="del" onclick="deletePage(${f.id})">🗑️</span>
        </div>
    `).join('');
}

function showStatus(msg) {
    const el = document.getElementById('statusMsg');
    el.textContent = msg;
    setTimeout(() => { el.textContent = ''; }, 3000);
}

// ===== INIT =====
loadStats();
loadPageOrder();
loadPages();
loadFeatures();

// Check admin access
(async () => {
    const res = await fetch('/api/admin/verify', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({initData})
    });
    const data = await res.json();
    if (!data.ok) {
        document.querySelector('.dash-container').innerHTML = '<h1>🚫 ተደራሽነት የለዎትም</h1>';
    }
})();
</script>
</body>
</html>
