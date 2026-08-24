/**
 * GnEmoji Studio — Telegram Mini App Application Logic
 */

// Random name suggestions
const RANDOM_NAMES = [
    "ABDURAHIM", "ASILBEK", "BEKZOD", "SHAXRIYOR", "DILSHOD", 
    "SARDOR", "JASUR", "NODIR", "UMID", "AZIZ", 
    "TEMUR", "MALIKA", "SEVARA", "MADINA", "ZILOLA", 
    "RAYHONA", "IBROHIM", "JAVOHIR", "SHERZOD", "BOBUR"
];

// The 13 Ticket Emojis (1.tgs to 13.tgs)
const TICKET_TEMPLATES = [];
for (let i = 1; i <= 13; i++) {
    TICKET_TEMPLATES.push({
        id: `${i}`,
        file: `${i}.tgs`,
        name: `Ticket #${i}`,
        tag: "100x100 Ticket"
    });
}

// The 104 Logo Emojis (14.tgs to 117.tgs)
const LOGO_TEMPLATES = [];
for (let i = 14; i <= 117; i++) {
    LOGO_TEMPLATES.push({
        id: `${i}`,
        file: `${i}.tgs`,
        name: `Logo #${i}`,
        tag: "Logo & Badge"
    });
}

// App State (Nothing selected by default on load, empty text for user input)
const state = {
    user: null,
    userBalance: 0,
    emojiPrice: 6,
    isAdmin: false,
    destinationMode: "new", // "new" or "existing"
    selectedExistingPack: "",
    text: "",
    font: "stapel",
    scale: 1.0,
    activeTab: "name",
    selectedTemplate: "1.tgs", // for top live preview only
    selectedTickets: new Set(), // 0 selected on start
    selectedLogos: new Set(),   // 0 selected on start
    userPacks: [],
    
    // Lottie player instances
    livePlayer: null,
    modalPlayer: null,
    ticketPlayers: {},
    logoPlayers: {},
    
    // In-memory preview cache: key = `${filename}_${font}_${scale}_${text}`
    previewCache: new Map()
};

// Telegram WebApp Object
const tg = window.Telegram?.WebApp;
const BOT_USERNAME = "GnEmojiBot";

// DOM Elements
const dom = {
    loadingScreen: document.getElementById('loading-screen'),
    loaderBar: document.getElementById('loader-bar'),
    loaderStatus: document.getElementById('loader-status'),
    appContainer: document.getElementById('app-container'),
    
    // Header
    userAvatar: document.getElementById('user-avatar'),
    userName: document.getElementById('user-name'),
    userBalancePill: document.getElementById('user-balance-pill'),
    userBalanceVal: document.getElementById('user-balance-val'),
    
    // Inputs
    nameInput: document.getElementById('name-input'),
    charCount: document.getElementById('char-count'),
    btnRandomName: document.getElementById('btn-random-name'),
    btnClearName: document.getElementById('btn-clear-name'),
    fontPills: document.getElementById('font-pills'),
    sizeSlider: document.getElementById('size-slider'),
    sizeValDisplay: document.getElementById('size-val-display'),
    
    // Destination Selector (New vs Existing)
    destPillNew: document.getElementById('dest-pill-new'),
    destPillExisting: document.getElementById('dest-pill-existing'),
    existingPackSelectWrapper: document.getElementById('existing-pack-select-wrapper'),
    existingPackSelect: document.getElementById('existing-pack-select'),
    
    // Live Preview
    liveLottiePlayer: document.getElementById('live-lottie-player'),
    currentTemplateTag: document.getElementById('current-template-tag'),
    previewTextDisplay: document.getElementById('preview-text-display'),
    previewFontDisplay: document.getElementById('preview-font-display'),
    
    // Tabs
    tabBtnName: document.getElementById('tab-btn-name'),
    tabBtnLogo: document.getElementById('tab-btn-logo'),
    tabContentName: document.getElementById('tab-content-name'),
    tabContentLogo: document.getElementById('tab-content-logo'),
    
    // Name Tab (13 Ticket Emojis)
    templatesGrid: document.getElementById('templates-grid'),
    templateSearch: document.getElementById('template-search'),
    btnSelectAllTickets: document.getElementById('btn-select-all-tickets'),
    txtSelectAllTickets: document.getElementById('txt-select-all-tickets'),
    ticketSelectionCount: document.getElementById('ticket-selection-count'),
    
    // Logo Tab (104 Logo Emojis)
    logosGrid: document.getElementById('logos-grid'),
    logoSearch: document.getElementById('logo-search'),
    btnSelectAllLogos: document.getElementById('btn-select-all-logos'),
    txtSelectAllLogos: document.getElementById('txt-select-all-logos'),
    logoSelectionCount: document.getElementById('logo-selection-count'),
    btnCreateFullpack: document.getElementById('btn-create-fullpack'),
    userPacksList: document.getElementById('user-packs-list'),
    btnRefreshPacks: document.getElementById('btn-refresh-packs'),
    
    // Bottom Action
    btnMainAction: document.getElementById('btn-main-action'),
    mainBtnText: document.getElementById('main-btn-text'),
    
    // Modals
    modalTemplate: document.getElementById('modal-template'),
    btnCloseModal: document.getElementById('btn-close-modal'),
    modalTplTag: document.getElementById('modal-tpl-tag'),
    modalTplTitle: document.getElementById('modal-tpl-title'),
    modalLottiePlayer: document.getElementById('modal-lottie-player'),
    modalTextVal: document.getElementById('modal-text-val'),
    modalFontVal: document.getElementById('modal-font-val'),
    btnGenerateSingle: document.getElementById('btn-generate-single'),
    btnAddToPackModal: document.getElementById('btn-add-to-pack-modal'),
    
    modalProgress: document.getElementById('modal-progress'),
    progressTitle: document.getElementById('progress-title'),
    progressDesc: document.getElementById('progress-desc'),
    genProgressBar: document.getElementById('gen-progress-bar'),
    genProgressPercent: document.getElementById('gen-progress-percent'),
    
    modalSuccess: document.getElementById('modal-success'),
    btnCloseSuccess: document.getElementById('btn-close-success'),
    successDesc: document.getElementById('success-desc'),
    packLinkText: document.getElementById('pack-link-text'),
    btnOpenPack: document.getElementById('btn-open-pack'),
    btnSharePack: document.getElementById('btn-share-pack'),
    
    // Balance Modal
    modalBalance: document.getElementById('modal-balance'),
    btnCloseBalanceModal: document.getElementById('btn-close-balance-modal'),
    btnCancelBalance: document.getElementById('btn-cancel-balance'),
    btnTopupWallet: document.getElementById('btn-topup-wallet'),
    modalCurrBal: document.getElementById('modal-curr-bal'),
    modalNeededBal: document.getElementById('modal-needed-bal'),
    modalDiffBal: document.getElementById('modal-diff-bal'),
    
    // Toast
    toast: document.getElementById('toast'),
    toastMsg: document.getElementById('toast-msg'),
    toastIcon: document.getElementById('toast-icon')
};

// ==================== HELPER FUNCTIONS ====================

function haptic(style = 'light') {
    if (!tg?.HapticFeedback) return;
    try {
        if (style === 'light' || style === 'medium' || style === 'heavy') {
            tg.HapticFeedback.impactOccurred(style);
        } else if (style === 'success' || style === 'error' || style === 'warning') {
            tg.HapticFeedback.notificationOccurred(style);
        } else if (style === 'selection') {
            tg.HapticFeedback.selectionChanged();
        }
    } catch (e) {
        console.warn('Haptic error:', e);
    }
}

let toastTimeout = null;
function showToast(msg, icon = 'ℹ️', duration = 3000) {
    if (toastTimeout) clearTimeout(toastTimeout);
    dom.toastMsg.textContent = msg;
    dom.toastIcon.textContent = icon;
    dom.toast.classList.remove('hidden');
    
    toastTimeout = setTimeout(() => {
        dom.toast.classList.add('hidden');
    }, duration);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function getTemplateNumber(filename) {
    return String(filename).replace('.tgs', '').replace('emoji_', '');
}

// Client-side Lottie text scale modifier (scales letter bezier vectors around their center)
function applyScaleToLottieJSON(jsonObj, scaleFactor) {
    if (!jsonObj || scaleFactor === 1.0) return jsonObj;
    try {
        const cloned = JSON.parse(JSON.stringify(jsonObj));
        
        // 1. Collect all vertex points across all letter shapes
        const allXs = [];
        const allYs = [];
        
        function findPts(obj) {
            if (!obj) return;
            if (typeof obj === 'object') {
                if (obj.ty === 'sh' && obj.nm && obj.nm.length === 1 && obj.ks && obj.ks.k && Array.isArray(obj.ks.k.v)) {
                    const v = obj.ks.k.v;
                    for (let i = 0; i < v.length; i++) {
                        allXs.push(v[i][0]);
                        allYs.push(v[i][1]);
                    }
                }
                for (const k in obj) {
                    findPts(obj[k]);
                }
            } else if (Array.isArray(obj)) {
                for (let i = 0; i < obj.length; i++) {
                    findPts(obj[i]);
                }
            }
        }
        
        findPts(cloned);
        if (allXs.length === 0) return cloned;
        
        const minX = Math.min(...allXs);
        const maxX = Math.max(...allXs);
        const minY = Math.min(...allYs);
        const maxY = Math.max(...allYs);
        
        const cx = (minX + maxX) / 2.0;
        const cy = (minY + maxY) / 2.0;
        
        // 2. Scale all vertex coordinates around (cx, cy)
        function scalePts(obj) {
            if (!obj) return;
            if (typeof obj === 'object') {
                if (obj.ty === 'sh' && obj.nm && obj.nm.length === 1 && obj.ks && obj.ks.k && Array.isArray(obj.ks.k.v)) {
                    const ks = obj.ks.k;
                    const v = ks.v || [];
                    const inT = ks.i || [];
                    const outT = ks.o || [];
                    for (let i = 0; i < v.length; i++) {
                        v[i][0] = cx + (v[i][0] - cx) * scaleFactor;
                        v[i][1] = cy + (v[i][1] - cy) * scaleFactor;
                    }
                    for (let i = 0; i < inT.length; i++) {
                        inT[i][0] = inT[i][0] * scaleFactor;
                        inT[i][1] = inT[i][1] * scaleFactor;
                    }
                    for (let i = 0; i < outT.length; i++) {
                        outT[i][0] = outT[i][0] * scaleFactor;
                        outT[i][1] = outT[i][1] * scaleFactor;
                    }
                }
                for (const k in obj) {
                    scalePts(obj[k]);
                }
            } else if (Array.isArray(obj)) {
                for (let i = 0; i < obj.length; i++) {
                    scalePts(obj[i]);
                }
            }
        }
        
        scalePts(cloned);
        return cloned;
    } catch (e) {
        console.error("Scale error:", e);
        return jsonObj;
    }
}

function getPreRenderedTemplateData(filename, font, scale = 1.0) {
    if (window.DEFAULT_TEMPLATE_DATA && window.DEFAULT_TEMPLATE_DATA[font]) {
        const raw = window.DEFAULT_TEMPLATE_DATA[font][filename];
        if (raw) {
            return scale === 1.0 ? raw : applyScaleToLottieJSON(raw, scale);
        }
    }
    return null;
}

// ==================== INITIALIZATION ====================

async function initApp() {
    try {
        updateLoadingProgress(20, "Telegram muhiti aniqlanmoqda...");
        
        if (tg) {
            tg.ready();
            tg.expand();
            document.body.classList.add('telegram-theme');
            
            const user = tg.initDataUnsafe?.user;
            if (user) {
                state.user = user;
                dom.userName.textContent = user.first_name || user.username || "Foydalanuvchi";
                if (user.photo_url) {
                    dom.userAvatar.innerHTML = `<img src="${user.photo_url}" alt="Avatar">`;
                } else {
                    const initials = (user.first_name ? user.first_name[0] : 'U').toUpperCase();
                    dom.userAvatar.textContent = initials;
                }
            }
        }
        
        updateLoadingProgress(45, "13 ta Ticket va 104 ta Logo stikerlar yuklanmoqda...");
        
        // 1. Render initial Live Hero Preview
        await updateLivePreview();
        
        // 2. Render the 13 Ticket Templates in Name Tab (none selected by default)
        renderTicketsGrid();
        
        // 3. Render the 104 Logo Templates in Logo Tab (none selected by default)
        renderLogosGrid();
        
        // 4. Update Selection Status
        updateSelectionStatus();
        
        // 5. Load user info, balance & existing packs
        const uid = state.user?.id || 1323217434;
        await loadUserInfo(uid);
        
        updateLoadingProgress(100, "Tayyor!");
        
        setTimeout(() => {
            dom.loadingScreen.classList.add('fade-out');
            dom.appContainer.classList.remove('hidden');
        }, 200);
        
    } catch (err) {
        console.error("App init error:", err);
        dom.loadingScreen.classList.add('fade-out');
        dom.appContainer.classList.remove('hidden');
    }
}

function updateLoadingProgress(percent, statusText) {
    if (dom.loaderBar) dom.loaderBar.style.width = `${percent}%`;
    if (dom.loaderStatus) dom.loaderStatus.textContent = statusText;
}

// ==================== ROBUST MULTI-FALLBACK API ====================

async function apiFetch(endpoint, options = {}) {
    const urls = [
        `/api/${endpoint}`,
        `/api/${endpoint}/index.php`,
        `/api/index.php?endpoint=${endpoint}`
    ];
    
    let lastError = null;
    for (const url of urls) {
        try {
            const res = await fetch(url, options);
            if (res.ok) {
                return res;
            }
            const errData = await res.json().catch(() => null);
            if (errData && errData.detail) {
                lastError = new Error(errData.detail);
            } else {
                lastError = new Error(`HTTP ${res.status}`);
            }
        } catch (e) {
            lastError = e;
        }
    }
    throw lastError || new Error("API ulanishida xatolik");
}

async function loadUserInfo(userId) {
    try {
        const res = await apiFetch(`user_info?user_id=${userId}`);
        const data = await res.json();
        state.userBalance = data.balance ?? 0;
        state.emojiPrice = data.emoji_price ?? 6;
        state.userPacks = data.packs ?? [];
        state.isAdmin = !!data.is_admin;
        
        if (dom.userBalanceVal) {
            dom.userBalanceVal.textContent = state.userBalance;
        }
        
        renderExistingPacksDropdown();
        renderUserPacks();
        updateSelectionStatus();
    } catch (e) {
        console.warn('User info fetch error:', e);
    }
}

async function loadUserPacks(userId) {
    return loadUserInfo(userId);
}

function renderExistingPacksDropdown() {
    if (!dom.existingPackSelect) return;
    dom.existingPackSelect.innerHTML = '';
    
    if (!state.userPacks || state.userPacks.length === 0) {
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = "Sizda hali yaratilgan to'plamlar yo'q";
        dom.existingPackSelect.appendChild(opt);
        return;
    }
    
    const defaultOpt = document.createElement('option');
    defaultOpt.value = '';
    defaultOpt.textContent = "To'plamni tanlang...";
    dom.existingPackSelect.appendChild(defaultOpt);
    
    state.userPacks.forEach(([pname, ptitle]) => {
        const opt = document.createElement('option');
        opt.value = pname;
        opt.textContent = `📦 ${ptitle || pname}`;
        dom.existingPackSelect.appendChild(opt);
    });
}

async function fetchLottiePreview(templateFile, text, font, scale = 1.0) {
    const cleanTxt = (text && text.trim()) ? text.trim().toUpperCase() : "ISMINGIZ";
    const cacheKey = `${templateFile}_${font}_${scale}_${cleanTxt}`;
    
    if (state.previewCache.has(cacheKey)) {
        return state.previewCache.get(cacheKey);
    }
    
    try {
        const res = await apiFetch('preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                template_id: templateFile,
                text: cleanTxt,
                font: font,
                scale: scale
            })
        });
        
        const animationData = await res.json();
        if (animationData && !animationData.detail) {
            state.previewCache.set(cacheKey, animationData);
            return animationData;
        }
        throw new Error(animationData.detail || "Xato");
    } catch (err) {
        console.warn("API preview fallback:", err);
        const fallbackData = getPreRenderedTemplateData(templateFile, font, scale);
        if (fallbackData) return fallbackData;
        return null;
    }
}

async function fetchBatchPreviews(templateFiles, text, font, scale = 1.0) {
    const cleanTxt = (text || "ABDURAHIM").trim().toUpperCase();
    const needed = [];
    const results = {};
    
    templateFiles.forEach(file => {
        const cacheKey = `${file}_${font}_${scale}_${cleanTxt}`;
        if (state.previewCache.has(cacheKey)) {
            results[file] = state.previewCache.get(cacheKey);
        } else if (cleanTxt === "ABDURAHIM") {
            const preData = getPreRenderedTemplateData(file, font, scale);
            if (preData) {
                state.previewCache.set(cacheKey, preData);
                results[file] = preData;
            } else {
                needed.push(file);
            }
        } else {
            needed.push(file);
        }
    });
    
    if (needed.length === 0) {
        return results;
    }
    
    try {
        const res = await apiFetch('batch_preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                template_ids: needed,
                text: cleanTxt,
                font: font,
                scale: scale
            })
        });
        
        const data = await res.json();
        if (data.previews) {
            Object.entries(data.previews).forEach(([fname, lottieData]) => {
                const cacheKey = `${fname}_${font}_${scale}_${cleanTxt}`;
                state.previewCache.set(cacheKey, lottieData);
                results[fname] = lottieData;
            });
        }
    } catch (e) {
        needed.forEach(file => {
            const fallbackData = getPreRenderedTemplateData(file, font, scale);
            if (fallbackData) results[file] = fallbackData;
        });
    }
    
    return results;
}

// ==================== UI RENDERING ====================

async function updateLivePreview() {
    const num = getTemplateNumber(state.selectedTemplate);
    const isTicket = parseInt(num) <= 13;
    dom.currentTemplateTag.textContent = `${isTicket ? 'Ticket' : 'Logo'} #${num}`;
    const cleanTxt = (state.text && state.text.trim()) ? state.text.trim().toUpperCase() : "ISMINGIZ";
    dom.previewTextDisplay.textContent = state.text ? state.text.trim().toUpperCase() : "—";
    
    const fontNames = { stapel: 'Stapel', inter: 'Inter', grobold: 'Grobold' };
    dom.previewFontDisplay.textContent = `${fontNames[state.font] || 'Stapel'} (${Math.round(state.scale * 100)}%)`;
    
    const lottieData = await fetchLottiePreview(state.selectedTemplate, cleanTxt, state.font, state.scale);
    
    if (lottieData) {
        if (state.livePlayer) {
            state.livePlayer.destroy();
        }
        dom.liveLottiePlayer.innerHTML = '';
        state.livePlayer = lottie.loadAnimation({
            container: dom.liveLottiePlayer,
            renderer: 'svg',
            loop: true,
            autoplay: true,
            animationData: lottieData
        });
    }
}

// Update selection counters and bottom action button text
function updateSelectionStatus() {
    const activeSet = state.activeTab === 'name' ? state.selectedTickets : state.selectedLogos;
    const selectedCount = activeSet.size;
    
    // Ticket tab toolbar
    if (dom.ticketSelectionCount) {
        dom.ticketSelectionCount.textContent = `${state.selectedTickets.size} ta tanlandi`;
    }
    if (dom.txtSelectAllTickets) {
        if (state.selectedTickets.size === TICKET_TEMPLATES.length && TICKET_TEMPLATES.length > 0) {
            dom.txtSelectAllTickets.textContent = "Tanlovni bekor qilish";
            dom.btnSelectAllTickets?.classList.add('active-all');
        } else {
            dom.txtSelectAllTickets.textContent = "Hammasini belgilash";
            dom.btnSelectAllTickets?.classList.remove('active-all');
        }
    }
    
    // Logo tab toolbar
    if (dom.logoSelectionCount) {
        dom.logoSelectionCount.textContent = `${state.selectedLogos.size} ta tanlandi`;
    }
    if (dom.txtSelectAllLogos) {
        if (state.selectedLogos.size === LOGO_TEMPLATES.length && LOGO_TEMPLATES.length > 0) {
            dom.txtSelectAllLogos.textContent = "Tanlovni bekor qilish";
            dom.btnSelectAllLogos?.classList.add('active-all');
        } else {
            dom.txtSelectAllLogos.textContent = "Hammasini belgilash";
            dom.btnSelectAllLogos?.classList.remove('active-all');
        }
    }
    
    // Price & Label Calculation — HAR DOIM STARS TO'LOV HISOB-KITOBLARI
    const count = selectedCount > 0 ? selectedCount : 1;
    const unitPrice = state.emojiPrice || 6;
    const totalCost = count * unitPrice;
    state.lastNeededBal = totalCost;
    const priceBadge = `${totalCost} ⭐`;
    
    const isExisting = state.destinationMode === 'existing';
    const actionVerb = isExisting ? "Qo'shish" : "Yaratish";
    
    // Bottom Action Button Text
    if (selectedCount > 1) {
        dom.mainBtnText.textContent = `Tanlangan Emojilarni ${actionVerb} (${selectedCount} ta • ${priceBadge})`;
    } else if (selectedCount === 1) {
        const singleFile = Array.from(activeSet)[0];
        const num = getTemplateNumber(singleFile);
        dom.mainBtnText.textContent = `Tanlangan #${num} Emojini ${actionVerb} (${priceBadge})`;
    } else {
        const num = getTemplateNumber(state.selectedTemplate);
        dom.mainBtnText.textContent = `Tanlangan #${num} Emojini ${actionVerb} (${priceBadge})`;
    }
}

// Render the 13 Ticket Emojis in Name Tab (1.tgs to 13.tgs)
async function renderTicketsGrid(filterText = '') {
    Object.values(state.ticketPlayers).forEach(p => {
        try { p.destroy(); } catch (e) {}
    });
    state.ticketPlayers = {};
    dom.templatesGrid.innerHTML = '';
    
    let filtered = TICKET_TEMPLATES;
    if (filterText && filterText.trim()) {
        const query = filterText.trim().toLowerCase();
        filtered = TICKET_TEMPLATES.filter(t => 
            t.name.toLowerCase().includes(query) || 
            t.file.toLowerCase().includes(query) ||
            t.id.includes(query)
        );
    }
    
    if (filtered.length === 0) {
        dom.templatesGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-dim);">
                Ticket shabloni topilmadi 🔍
            </div>
        `;
        return;
    }
    
    filtered.forEach((tpl) => {
        const num = tpl.id;
        const isSelected = state.selectedTickets.has(tpl.file);
        const card = document.createElement('div');
        card.className = `tpl-card ${isSelected ? 'selected' : ''}`;
        card.dataset.file = tpl.file;
        
        card.innerHTML = `
            <span class="tpl-badge">#${num}</span>
            <div class="tpl-check-badge">✓</div>
            <div class="tpl-lottie-thumb" id="thumb-ticket-${num}"></div>
            <div class="tpl-meta">
                <div class="tpl-title">${tpl.name}</div>
                <div class="tpl-tag-label">${tpl.tag}</div>
            </div>
        `;
        
        card.addEventListener('click', () => {
            haptic('selection');
            toggleCardSelection(tpl.file, 'name');
        });
        
        dom.templatesGrid.appendChild(card);
    });
    
    const batchFiles = filtered.map(t => t.file);
    const batchData = await fetchBatchPreviews(batchFiles, state.text, state.font, state.scale);
    
    filtered.forEach(tpl => {
        const file = tpl.file;
        const num = tpl.id;
        const container = document.getElementById(`thumb-ticket-${num}`);
        const data = batchData[file] || getPreRenderedTemplateData(file, state.font, state.scale);
        
        if (container && data) {
            container.innerHTML = '';
            const player = lottie.loadAnimation({
                container: container,
                renderer: 'svg',
                loop: true,
                autoplay: true,
                animationData: data
            });
            state.ticketPlayers[file] = player;
        }
    });
}

// Render the 104 Logo Emojis in Logo Tab (14.tgs to 117.tgs)
async function renderLogosGrid(filterText = '') {
    Object.values(state.logoPlayers).forEach(p => {
        try { p.destroy(); } catch (e) {}
    });
    state.logoPlayers = {};
    if (!dom.logosGrid) return;
    dom.logosGrid.innerHTML = '';
    
    let filtered = LOGO_TEMPLATES;
    if (filterText && filterText.trim()) {
        const query = filterText.trim().toLowerCase();
        filtered = LOGO_TEMPLATES.filter(t => 
            t.name.toLowerCase().includes(query) || 
            t.file.toLowerCase().includes(query) ||
            t.id.includes(query)
        );
    }
    
    if (filtered.length === 0) {
        dom.logosGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-dim);">
                Logo shabloni topilmadi 🔍
            </div>
        `;
        return;
    }
    
    filtered.forEach((tpl) => {
        const num = tpl.id;
        const isSelected = state.selectedLogos.has(tpl.file);
        const card = document.createElement('div');
        card.className = `tpl-card ${isSelected ? 'selected' : ''}`;
        card.dataset.file = tpl.file;
        
        card.innerHTML = `
            <span class="tpl-badge">#${num}</span>
            <div class="tpl-check-badge">✓</div>
            <div class="tpl-lottie-thumb" id="thumb-logo-${num}"></div>
            <div class="tpl-meta">
                <div class="tpl-title">${tpl.name}</div>
                <div class="tpl-tag-label">${tpl.tag}</div>
            </div>
        `;
        
        card.addEventListener('click', () => {
            haptic('selection');
            toggleCardSelection(tpl.file, 'logo');
        });
        
        dom.logosGrid.appendChild(card);
    });
    
    // Load first 24 logos immediately
    const initialBatch = filtered.slice(0, 24).map(t => t.file);
    const batchData = await fetchBatchPreviews(initialBatch, state.text, state.font, state.scale);
    
    Object.entries(batchData).forEach(([file, data]) => {
        const num = getTemplateNumber(file);
        const container = document.getElementById(`thumb-logo-${num}`);
        const lottieData = data || getPreRenderedTemplateData(file, state.font, state.scale);
        if (container && lottieData) {
            container.innerHTML = '';
            const player = lottie.loadAnimation({
                container: container,
                renderer: 'svg',
                loop: true,
                autoplay: true,
                animationData: lottieData
            });
            state.logoPlayers[file] = player;
        }
    });
    
    // Lazy load remaining logos on scroll
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(async entry => {
                if (entry.isIntersecting) {
                    const card = entry.target;
                    const file = card.dataset.file;
                    const num = getTemplateNumber(file);
                    const container = document.getElementById(`thumb-logo-${num}`);
                    
                    if (container && !state.logoPlayers[file]) {
                        const data = await fetchLottiePreview(file, state.text, state.font, state.scale);
                        if (data && container) {
                            container.innerHTML = '';
                            const player = lottie.loadAnimation({
                                container: container,
                                renderer: 'svg',
                                loop: true,
                                autoplay: true,
                                animationData: data
                            });
                            state.logoPlayers[file] = player;
                        }
                    }
                    observer.unobserve(card);
                }
            });
        }, { rootMargin: '150px' });
        
        dom.logosGrid.querySelectorAll('.tpl-card').forEach((card, idx) => {
            if (idx >= 24) observer.observe(card);
        });
    }
}

// Toggle selection on a card (multi-select supported)
function toggleCardSelection(filename, tabKey) {
    const targetSet = tabKey === 'name' ? state.selectedTickets : state.selectedLogos;
    const container = tabKey === 'name' ? dom.templatesGrid : dom.logosGrid;
    
    if (targetSet.has(filename)) {
        targetSet.delete(filename);
    } else {
        targetSet.add(filename);
    }
    
    // Update live hero preview to clicked item
    state.selectedTemplate = filename;
    updateLivePreview();
    
    // Update UI card classes
    container?.querySelectorAll('.tpl-card').forEach(card => {
        if (targetSet.has(card.dataset.file)) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }
    });
    
    updateSelectionStatus();
}

// Select All / Deselect All
function toggleSelectAll(tabKey) {
    haptic('medium');
    const targetSet = tabKey === 'name' ? state.selectedTickets : state.selectedLogos;
    const allList = tabKey === 'name' ? TICKET_TEMPLATES : LOGO_TEMPLATES;
    const container = tabKey === 'name' ? dom.templatesGrid : dom.logosGrid;
    
    if (targetSet.size === allList.length) {
        // Deselect all
        targetSet.clear();
    } else {
        // Select all
        allList.forEach(t => targetSet.add(t.file));
        state.selectedTemplate = allList[0].file;
        updateLivePreview();
    }
    
    container?.querySelectorAll('.tpl-card').forEach(card => {
        if (targetSet.has(card.dataset.file)) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }
    });
    
    updateSelectionStatus();
}

function renderUserPacks() {
    if (!state.userPacks || state.userPacks.length === 0) {
        dom.userPacksList.innerHTML = `
            <div class="packs-empty">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="28" height="28">
                    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                </svg>
                <span>Hali yaratilgan to'plamlar yo'q</span>
            </div>
        `;
        return;
    }
    
    dom.userPacksList.innerHTML = '';
    state.userPacks.forEach(([pname, ptitle, pdate]) => {
        const link = `https://t.me/addemoji/${pname}`;
        const item = document.createElement('a');
        item.className = 'pack-item-card';
        item.href = link;
        item.target = '_blank';
        
        item.innerHTML = `
            <div class="pack-info-left">
                <span class="pack-name-txt">${ptitle}</span>
                <span class="pack-date-txt">${pdate || 'Saqlangan to\'plam'}</span>
            </div>
            <div class="pack-btn-open">Ochish ↗</div>
        `;
        
        item.addEventListener('click', (e) => {
            haptic('light');
            if (tg) {
                e.preventDefault();
                tg.openTelegramLink(link);
            }
        });
        
        dom.userPacksList.appendChild(item);
    });
}

// ==================== MODALS & GENERATION ====================

async function openTemplateModal(filename, typeLabel = 'Emoji') {
    const num = getTemplateNumber(filename);
    dom.modalTplTag.textContent = `Shablon #${num}`;
    dom.modalTplTitle.textContent = `${typeLabel} #${num}`;
    dom.modalTextVal.textContent = state.text;
    
    const fontNames = { stapel: 'Stapel', inter: 'Inter', grobold: 'Grobold' };
    dom.modalFontVal.textContent = `${fontNames[state.font] || 'Stapel'} (${Math.round(state.scale * 100)}%)`;
    
    dom.modalLottiePlayer.innerHTML = '';
    dom.modalTemplate.classList.remove('hidden');
    
    const data = await fetchLottiePreview(filename, state.text, state.font, state.scale);
    if (data) {
        if (state.modalPlayer) {
            state.modalPlayer.destroy();
        }
        dom.modalLottiePlayer.innerHTML = '';
        state.modalPlayer = lottie.loadAnimation({
            container: dom.modalLottiePlayer,
            renderer: 'svg',
            loop: true,
            autoplay: true,
            animationData: data
        });
    }
}

function closeTemplateModal() {
    dom.modalTemplate.classList.add('hidden');
    if (state.modalPlayer) {
        state.modalPlayer.destroy();
        state.modalPlayer = null;
    }
}

function showProgressModal(title, desc, percent) {
    dom.progressTitle.textContent = title;
    dom.progressDesc.textContent = desc;
    dom.genProgressBar.style.width = `${percent}%`;
    dom.genProgressPercent.textContent = `${percent}%`;
    dom.modalProgress.classList.remove('hidden');
}

function updateProgressStep(percent, desc) {
    dom.genProgressBar.style.width = `${percent}%`;
    dom.genProgressPercent.textContent = `${percent}%`;
    if (desc) dom.progressDesc.textContent = desc;
}

function hideProgressModal() {
    dom.modalProgress.classList.add('hidden');
}

function triggerConfetti() {
    if (typeof confetti === 'function') {
        confetti({
            particleCount: 90,
            spread: 75,
            origin: { y: 0.6 }
        });
    }
}

function showSuccessModal(packName, packLink, isFullPack = false) {
    hideProgressModal();
    closeTemplateModal();
    
    dom.packLinkText.textContent = packLink;
    dom.btnOpenPack.href = packLink;
    
    dom.btnOpenPack.onclick = (e) => {
        haptic('medium');
        if (tg) {
            e.preventDefault();
            tg.openTelegramLink(packLink);
        }
    };
    
    dom.btnSharePack.onclick = () => {
        haptic('light');
        const shareText = `🌟 Men o'z ismim bilan Telegram Premium Animatsiyali Emoji Pack yaratdim!\n\nHavola: ${packLink}`;
        const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(packLink)}&text=${encodeURIComponent(shareText)}`;
        if (tg) {
            tg.openTelegramLink(shareUrl);
        } else {
            window.open(shareUrl, '_blank');
        }
    };
    
    dom.modalSuccess.classList.remove('hidden');
    triggerConfetti();
    haptic('success');
    
    if (state.user?.id) {
        loadUserPacks(state.user.id);
    }
}

async function startGeneration(mode = 'selected') {
    const cleanText = state.text.trim().toUpperCase();
    if (!cleanText) {
        showToast("⚠️ Iltimos, ism yoki so'z kiriting!", "⚠️");
        dom.nameInput.focus();
        haptic('error');
        return;
    }
    
    const userId = state.user?.id || 1323217434;
    
    const activeSet = state.activeTab === 'name' ? state.selectedTickets : state.selectedLogos;
    const selectedArray = Array.from(activeSet);
    
    let targetMode = mode;
    let selectedFiles = [];
    
    if (mode === 'all') {
        selectedFiles = LOGO_TEMPLATES.map(t => t.file);
    } else if (selectedArray.length === 0) {
        targetMode = "single";
        selectedFiles = [state.selectedTemplate];
    } else if (selectedArray.length === 1) {
        targetMode = "single";
        selectedFiles = selectedArray;
    } else {
        targetMode = "selected";
        selectedFiles = selectedArray;
    }
    
    // Check destination (Yangi to'plam vs Mavjud to'plam)
    let packName = undefined;
    if (state.destinationMode === 'existing') {
        targetMode = 'add_to_pack';
        packName = dom.existingPackSelect?.value;
        if (!packName) {
            showToast("⚠️ Iltimos, qo'shish uchun mavjud to'plamni tanlang!", "⚠️");
            haptic('error');
            return;
        }
    }
    
    // Check balance — HAR DOIM STARS TALAB QILINADI
    const totalCount = selectedFiles.length;
    const unitPrice = state.emojiPrice || 6;
    const totalCost = totalCount * unitPrice;
    state.lastNeededBal = totalCost;
    
    if (totalCost > 0 && (state.userBalance || 0) < totalCost) {
        openBalanceModal(state.userBalance || 0, totalCost);
        haptic('error');
        return;
    }
    
    haptic('medium');
    
    if (targetMode === 'add_to_pack') {
        showProgressModal("Mavjud to'plamga qo'shilmoqda...", `\"${packName}\" to'plamiga ${totalCount} ta stiker qo'shilmoqda...`, 30);
    } else if (mode === 'all') {
        showProgressModal("Mega Logo Pack Tayyorlanmoqda...", "Barcha 104 ta logo shablon render qilinmoqda...", 15);
    } else if (targetMode === "single") {
        const num = getTemplateNumber(selectedFiles[0]);
        showProgressModal(`${parseInt(num) <= 13 ? 'Ticket' : 'Logo'} #${num} Tayyorlanmoqda...`, "Animatsiya qayta ishlanmoqda...", 25);
    } else {
        showProgressModal(`Maxsus Emoji Pack (${selectedFiles.length} ta)...`, "Tanlangan stikerlar paketga jamlanmoqda...", 20);
    }
    
    try {
        let progress = targetMode === 'single' ? 35 : 20;
        const progressInterval = setInterval(() => {
            if (progress < 85) {
                progress += targetMode === 'single' ? 15 : 6;
                updateProgressStep(progress, targetMode === 'single' ? "Telegram API-ga yuborilmoqda..." : "Stikerlar paketga qo'shilmoqda...");
            }
        }, 600);
        
        const payload = {
            user_id: userId,
            text: cleanText,
            font: state.font,
            scale: state.scale,
            mode: targetMode,
            pack_name: packName,
            template_id: selectedFiles[0] || state.selectedTemplate,
            selected_templates: selectedFiles.length > 0 ? selectedFiles : undefined,
            init_data: tg?.initData || ""
        };
        
        const res = await apiFetch('generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        clearInterval(progressInterval);
        
        const result = await res.json();
        updateProgressStep(100, "Tayyor bo'ldi!");
        
        if (result.remaining_balance !== undefined) {
            state.userBalance = result.remaining_balance;
            if (dom.userBalanceVal) dom.userBalanceVal.textContent = state.userBalance;
            updateSelectionStatus();
        }
        
        setTimeout(() => {
            showSuccessModal(result.pack_name, result.pack_link, mode === 'all');
        }, 400);
        
    } catch (err) {
        console.error('Generation failed:', err);
        hideProgressModal();
        if (err.message && err.message.includes("Balansingiz yetarli emas")) {
            openBalanceModal(state.userBalance, totalCost);
        } else {
            showToast(`❌ Xatolik: ${err.message}`, "❌", 4000);
        }
        haptic('error');
    }
}

function openBalanceModal(currBal, neededBal) {
    if (dom.modalCurrBal) dom.modalCurrBal.textContent = `${currBal} ⭐`;
    if (dom.modalNeededBal) dom.modalNeededBal.textContent = `${neededBal} ⭐`;
    if (dom.modalDiffBal) dom.modalDiffBal.textContent = `${Math.max(0, neededBal - currBal)} ⭐`;
    dom.modalBalance?.classList.remove('hidden');
}

function closeBalanceModal() {
    dom.modalBalance?.classList.add('hidden');
}

async function addToExistingPack() {
    if (!state.userPacks || state.userPacks.length === 0) {
        showToast("Sizda hali paketlar yo'q. Avval to'liq to'plam yarating!", "ℹ️");
        return;
    }
    
    const firstPack = state.userPacks[0];
    const packName = firstPack[0];
    
    showProgressModal("Paketga qo'shilmoqda...", `\"${firstPack[1]}\" to'plamiga stiker qo'shilmoqda...`, 40);
    
    try {
        const payload = {
            user_id: state.user?.id || 1323217434,
            pack_name: packName,
            text: state.text.trim().toUpperCase(),
            font: state.font,
            scale: state.scale,
            template_id: state.selectedTemplate
        };
        
        const res = await apiFetch('add_to_pack', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const result = await res.json();
        updateProgressStep(100, "Muvaffaqiyatli qo'shildi!");
        
        setTimeout(() => {
            showSuccessModal(result.pack_name, result.pack_link);
        }, 400);
        
    } catch (err) {
        hideProgressModal();
        showToast(`❌ Xatolik: ${err.message}`, "❌");
    }
}

// ==================== EVENT LISTENERS ====================

function setupEventListeners() {
    
    function updateCharCount() {
        const len = dom.nameInput.value.length;
        dom.charCount.textContent = `${len}/16`;
    }
    
    // Debounced text update: only updates the live hero preview, leaving grid cards lightning fast!
    const debouncedLiveTextUpdate = debounce(() => {
        let val = dom.nameInput.value.replace(/[^a-zA-Z0-9а-яА-ЯёЁ_ \-]/g, '').toUpperCase();
        state.text = val;
        dom.nameInput.value = val;
        updateCharCount();
        updateLivePreview();
    }, 180);
    
    dom.nameInput.addEventListener('input', () => {
        updateCharCount();
        debouncedLiveTextUpdate();
    });
    
    // Size Slider (O'lcham) — Real-time live interactive update
    dom.sizeSlider?.addEventListener('input', (e) => {
        state.scale = parseFloat(e.target.value);
        if (dom.sizeValDisplay) {
            dom.sizeValDisplay.textContent = `${Math.round(state.scale * 100)}%`;
        }
        
        // Clear preview cache so new vector scale takes immediate effect
        state.previewCache.clear();
        
        // Fast real-time live preview update
        updateLivePreview();
        
        // Debounce grid update so dragging remains 60fps smooth
        debouncedFullUpdate();
    });
    
    // Random Name Button
    dom.btnRandomName.addEventListener('click', () => {
        haptic('light');
        const rand = RANDOM_NAMES[Math.floor(Math.random() * RANDOM_NAMES.length)];
        state.text = rand;
        dom.nameInput.value = rand;
        updateCharCount();
        updateLivePreview();
        renderTicketsGrid(dom.templateSearch?.value || '');
        renderLogosGrid(dom.logoSearch?.value || '');
    });
    
    // Clear Name Button
    dom.btnClearName.addEventListener('click', () => {
        haptic('light');
        state.text = "";
        dom.nameInput.value = "";
        updateCharCount();
        dom.nameInput.focus();
        updateLivePreview();
    });
    
    // Font Selection Pills
    dom.fontPills.querySelectorAll('.font-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            haptic('selection');
            dom.fontPills.querySelectorAll('.font-pill').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            state.font = pill.dataset.font;
            updateLivePreview();
            renderTicketsGrid(dom.templateSearch?.value || '');
            renderLogosGrid(dom.logoSearch?.value || '');
        });
    });
    
    // Tab switching (Name vs Logo)
    dom.tabBtnName.addEventListener('click', () => {
        haptic('selection');
        switchTab('name');
    });
    
    dom.tabBtnLogo.addEventListener('click', () => {
        haptic('selection');
        switchTab('logo');
    });
    
    function switchTab(tabKey) {
        state.activeTab = tabKey;
        if (tabKey === 'name') {
            dom.tabBtnName.classList.add('active');
            dom.tabBtnLogo.classList.remove('active');
            dom.tabContentName.classList.add('active');
            dom.tabContentLogo.classList.remove('active');
            state.selectedTemplate = Array.from(state.selectedTickets)[0] || "1.tgs";
        } else {
            dom.tabBtnLogo.classList.add('active');
            dom.tabBtnName.classList.remove('active');
            dom.tabContentLogo.classList.add('active');
            dom.tabContentName.classList.remove('active');
            state.selectedTemplate = Array.from(state.selectedLogos)[0] || "14.tgs";
        }
        updateLivePreview();
        updateSelectionStatus();
    }
    
    // Destination selector (New Pack vs Existing Pack)
    dom.destPillNew?.addEventListener('click', () => {
        haptic('selection');
        state.destinationMode = 'new';
        dom.destPillNew.classList.add('active');
        dom.destPillExisting.classList.remove('active');
        dom.existingPackSelectWrapper?.classList.add('hidden');
        updateSelectionStatus();
    });
    
    dom.destPillExisting?.addEventListener('click', () => {
        haptic('selection');
        state.destinationMode = 'existing';
        dom.destPillExisting.classList.add('active');
        dom.destPillNew.classList.remove('active');
        dom.existingPackSelectWrapper?.classList.remove('hidden');
        if (!state.selectedExistingPack && dom.existingPackSelect?.value) {
            state.selectedExistingPack = dom.existingPackSelect.value;
        }
        updateSelectionStatus();
    });
    
    dom.existingPackSelect?.addEventListener('change', (e) => {
        state.selectedExistingPack = e.target.value;
    });
    
    // Balance top-up / modal listeners
    dom.userBalancePill?.addEventListener('click', () => {
        haptic('light');
        if (tg) {
            tg.openTelegramLink(`https://t.me/${BOT_USERNAME}?start=wallet`);
        } else {
            window.open(`https://t.me/${BOT_USERNAME}?start=wallet`, '_blank');
        }
    });
    
    dom.btnTopupWallet?.addEventListener('click', async () => {
        haptic('medium');
        const uid = state.user?.id || 1323217434;
        const diff = Math.max(1, (state.lastNeededBal || state.emojiPrice || 6) - (state.userBalance || 0));
        
        try {
            const count = Math.max(1, Math.ceil(diff / (state.emojiPrice || 6)));
            const res = await apiFetch('create_invoice', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: uid, count: count, text: state.text })
            });
            const data = await res.json();
            
            if (data.invoice_link && tg?.openInvoice) {
                closeBalanceModal();
                tg.openInvoice(data.invoice_link, async (status) => {
                    if (status === 'paid') {
                        showToast("⭐️ Stars to'lovi qabul qilindi!", "✅");
                        await loadUserInfo(uid);
                    }
                });
                return;
            }
        } catch (e) {
            console.warn('Invoice creation error:', e);
        }
        
        closeBalanceModal();
        if (tg) {
            tg.openTelegramLink(`https://t.me/${BOT_USERNAME}?start=wallet`);
        } else {
            window.open(`https://t.me/${BOT_USERNAME}?start=wallet`, '_blank');
        }
    });
    
    dom.btnCloseBalanceModal?.addEventListener('click', closeBalanceModal);
    dom.btnCancelBalance?.addEventListener('click', closeBalanceModal);
    
    // Select All Buttons
    dom.btnSelectAllTickets?.addEventListener('click', () => toggleSelectAll('name'));
    dom.btnSelectAllLogos?.addEventListener('click', () => toggleSelectAll('logo'));
    
    // Search ticket templates (1-13)
    dom.templateSearch?.addEventListener('input', (e) => {
        renderTicketsGrid(e.target.value);
    });
    
    // Search logo templates (14-117)
    dom.logoSearch?.addEventListener('input', (e) => {
        renderLogosGrid(e.target.value);
    });
    
    // Bottom Action Button
    dom.btnMainAction.addEventListener('click', () => {
        startGeneration('selected');
    });
    
    // Logo Tab Full Pack Button (all 104)
    dom.btnCreateFullpack?.addEventListener('click', () => {
        startGeneration('all');
    });
    
    // Refresh user packs
    dom.btnRefreshPacks?.addEventListener('click', () => {
        haptic('light');
        const uid = state.user?.id || 1323217434;
        loadUserInfo(uid);
        showToast("To'plamlar yangilandi", "🔄");
    });
    
    // Modal buttons
    dom.btnCloseModal.addEventListener('click', closeTemplateModal);
    dom.btnGenerateSingle.addEventListener('click', () => startGeneration('single'));
    dom.btnAddToPackModal.addEventListener('click', addToExistingPack);
    dom.btnCloseSuccess.addEventListener('click', () => {
        dom.modalSuccess.classList.add('hidden');
    });
}

// Run when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    initApp();
});
