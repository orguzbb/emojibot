/**
 * ==========================================================================
 * COPYRIGHT NOTICE & LICENSE AGREEMENT (C) 2026 GN STUDIO
 * Project: GnEmoji Studio — Telegram Animated Emoji Mini App
 * All Rights Reserved.
 *
 * LEGAL WARNING:
 * This software, source code, visual styles, stylesheets, animations and all associated
 * intellectual properties are the exclusive property of GN Studio (c) 2026.
 * Unauthorized copying, distribution, decompilation, reverse engineering,
 * scraping, re-hosting, modification or commercial exploitation in any form is STRICTLY
 * PROHIBITED under international copyright laws and treaties.
 * ==========================================================================
 */

// ==================== SECURITY SHIELD & ANTI-DEVTOOLS SYSTEM ====================
(function initSecurityShield() {
    'use strict';

    // 1. Console Warning Banner
    try {
        const titleStyle = "color: #ef4444; font-size: 24px; font-weight: 900; -webkit-text-stroke: 1px black; padding: 4px;";
        const textStyle = "color: #f59e0b; font-size: 13px; font-weight: 600; line-height: 1.6;";
        const copyStyle = "color: #38bdf8; font-size: 12px; font-weight: 700; margin-top: 4px;";
        console.log("%c⛔ DIQQAT: XAVFSIZLIK TIZIMI FAOL!", titleStyle);
        console.log("%c© 2026 GN Studio. Ushbu ilova va uning barcha kodlari mualliflik huquqi bilan qat'iy himoyalangan.\nKodni ruxsatsiz nusxalash, o'g'irlash yoki o'zgartirish qat'iyan taqiqlanadi va jinoiy javobgarlikka sabab bo'ladi.", textStyle);
        console.log("%cAll Rights Reserved (c) 2026 GN Studio", copyStyle);
    } catch (e) {}

    // 2. Block Inspect, F12, View Source, Save, Print shortcuts
    window.addEventListener('keydown', function(e) {
        // F12 key
        if (e.key === 'F12' || e.keyCode === 123) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }

        const isCtrlOrMeta = e.ctrlKey || e.metaKey;

        // Ctrl+Shift+I / J / C / K (DevTools & Console)
        if (isCtrlOrMeta && e.shiftKey) {
            const k = (e.key || '').toUpperCase();
            if (k === 'I' || k === 'J' || k === 'C' || k === 'K') {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        }

        // Ctrl+U (View Source), Ctrl+S (Save Page), Ctrl+P (Print)
        if (isCtrlOrMeta) {
            const k = (e.key || '').toUpperCase();
            if (k === 'U' || k === 'S' || k === 'P') {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        }
    }, true);

    // 3. Block Context Menu (Right-Click)
    document.addEventListener('contextmenu', function(e) {
        const active = document.activeElement;
        if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA')) {
            return true;
        }
        e.preventDefault();
        e.stopPropagation();
        return false;
    }, true);

    // 4. Block Dragging
    document.addEventListener('dragstart', function(e) {
        if (e.target && (e.target.tagName === 'IMG' || e.target.tagName === 'A' || e.target.tagName === 'SVG')) {
            e.preventDefault();
            return false;
        }
    }, true);

    // 5. Anti-Debugging / DevTools Detection
    try {
        setInterval(function() {
            const startTime = performance.now();
            (function() { return false; })["constructor"]("debugger")();
            const endTime = performance.now();
            if (endTime - startTime > 100) {
                try {
                    console.clear();
                    console.log("%c⛔ DIQQAT: XAVFSIZLIK TIZIMI FAOL! (© 2026 GN Studio)", "color: #ef4444; font-size: 20px; font-weight: 800;");
                } catch (_) {}
            }
        }, 1200);
    } catch (e) {}
})();

// Telegram Environment Verification
function isTelegramEnvironment() {
    // 1. Localhost or 127.0.0.1 bypass for local testing
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.hostname === '') {
        return true;
    }
    
    // 2. Query param bypass for admin/dev testing
    const params = new URLSearchParams(window.location.search);
    if (params.get('dev') === '1' || params.get('allow_web') === '1') {
        return true;
    }

    // 3. Telegram WebApp object check
    const tg = window.Telegram?.WebApp;
    if (tg) {
        if (tg.initData && tg.initData.length > 0) return true;
        if (tg.initDataUnsafe && Object.keys(tg.initDataUnsafe).length > 0) return true;
        if (tg.platform && tg.platform !== 'unknown') return true;
    }

    // 4. Native Telegram Webview Proxy on Android & iOS
    if (window.TelegramWebviewProxy || window.TelegramGameProxy) {
        return true;
    }

    // 5. URL Hash / Query check (Telegram WebApp passes tgWebAppData)
    const href = window.location.href;
    if (href.includes('tgWebAppData') || href.includes('tgWebAppVersion') || href.includes('tgWebAppPlatform')) {
        return true;
    }

    // 6. UserAgent check
    const ua = navigator.userAgent || '';
    if (/Telegram|TDesktop/i.test(ua)) {
        return true;
    }

    return false;
}

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

// The 103 Logo Emojis (14.tgs to 117.tgs, excluding 81)
const LOGO_TEMPLATES = [];
for (let i = 14; i <= 117; i++) {
    if (i === 81) continue; // Template 81 removed
    LOGO_TEMPLATES.push({
        id: `${i}`,
        file: `${i}.tgs`,
        name: `Logo #${i}`,
        tag: "Logo & Badge"
    });
}

// The 65 Grey Metallic 3D Emojis (118.tgs to 182.tgs)
const GREY_TEMPLATES = [];
for (let i = 118; i <= 182; i++) {
    GREY_TEMPLATES.push({
        id: `${i}`,
        file: `${i}.tgs`,
        name: `Grey #${i - 117}`,
        tag: "Grey 3D Emoji"
    });
}

// App State (Nothing selected by default on load, empty text/svg for user input)
const state = {
    user: null,
    userBalance: 0,
    emojiPrice: 6,
    isAdmin: false,
    destinationMode: "new", // "new" or "existing"
    selectedExistingPack: "",
    inputType: "text", // "text" or "svg"
    text: "",
    svgData: "",
    svgFileName: "",
    svgPackName: "",
    badgeColor: "#FFFFFF",
    badgeBgColor: "#000000",
    textColor: "#FFFFFF",
    activeColorTarget: "outer",
    font: "stapel",
    scale: 1.0,
    activeTab: "name",
    selectedTemplate: "1.tgs", // for top live preview only
    selectedTickets: new Set(), // 0 selected on start
    selectedLogos: new Set(),   // 0 selected on start
    selectedGrey: new Set(),    // 0 selected on start
    userPacks: [],
    
    // Lottie player instances
    livePlayer: null,
    modalPlayer: null,
    ticketPlayers: {},
    logoPlayers: {},
    greyPlayers: {},
    
    // In-memory preview cache
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
    
    // Mode Switch Tabs
    modeTabText: document.getElementById('mode-tab-text'),
    modeTabSvg: document.getElementById('mode-tab-svg'),
    modeSectionText: document.getElementById('mode-section-text'),
    modeSectionSvg: document.getElementById('mode-section-svg'),
    
    // SVG Controls
    svgFileInput: document.getElementById('svg-file-input'),
    svgDropzone: document.getElementById('svg-dropzone'),
    svgActiveCard: document.getElementById('svg-active-card'),
    svgThumbPreview: document.getElementById('svg-thumb-preview'),
    svgFileName: document.getElementById('svg-file-name'),
    svgPackNameInput: document.getElementById('svg-pack-name-input'),
    btnChangeSvg: document.getElementById('btn-change-svg'),
    btnRemoveSvg: document.getElementById('btn-remove-svg'),
    
    // Inputs
    nameInput: document.getElementById('name-input'),
    charCount: document.getElementById('char-count'),
    btnRandomName: document.getElementById('btn-random-name'),
    btnClearName: document.getElementById('btn-clear-name'),
    fontPills: document.getElementById('font-pills'),
    sizeSlider: document.getElementById('size-slider'),
    // Color Customizer
    logoColorSection: document.getElementById('logo-color-section'),
    logoHexInput: document.getElementById('logo-hex-input'),
    logoColorPicker: document.getElementById('logo-color-picker'),
    pickerSwatchCircle: document.getElementById('picker-swatch-circle'),
    btnColorPickerTrigger: document.getElementById('btn-color-picker-trigger'),
    btnResetBadgeColor: document.getElementById('btn-reset-badge-color'),
    presetColorsBar: document.getElementById('preset-colors-bar'),
    targetPillOuter: document.getElementById('target-pill-outer'),
    targetPillInner: document.getElementById('target-pill-inner'),
    targetPillText: document.getElementById('target-pill-text'),
    targetDotOuter: document.getElementById('target-dot-outer'),
    targetDotInner: document.getElementById('target-dot-inner'),
    targetDotText: document.getElementById('target-dot-text'),
    dotSummaryOuter: document.getElementById('dot-summary-outer'),
    dotSummaryInner: document.getElementById('dot-summary-inner'),
    dotSummaryText: document.getElementById('dot-summary-text'),
    badgeSummaryText: document.getElementById('badge-summary-text'),
    
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
    tabBtnGrey: document.getElementById('tab-btn-grey'),
    tabContentName: document.getElementById('tab-content-name'),
    tabContentLogo: document.getElementById('tab-content-logo'),
    tabContentGrey: document.getElementById('tab-content-grey'),
    tabCounterGrey: document.getElementById('tab-counter-grey'),
    
    // Name Tab (13 Ticket Emojis)
    templatesGrid: document.getElementById('templates-grid'),
    templateSearch: document.getElementById('template-search'),
    btnSelectAllTickets: document.getElementById('btn-select-all-tickets'),
    txtSelectAllTickets: document.getElementById('txt-select-all-tickets'),
    ticketSelectionCount: document.getElementById('ticket-selection-count'),
    
    // Logo Tab (103 Logo Emojis)
    logosGrid: document.getElementById('logos-grid'),
    logoSearch: document.getElementById('logo-search'),
    btnSelectAllLogos: document.getElementById('btn-select-all-logos'),
    txtSelectAllLogos: document.getElementById('txt-select-all-logos'),
    logoSelectionCount: document.getElementById('logo-selection-count'),
    btnCreateFullpack: document.getElementById('btn-create-fullpack'),
    
    // Grey Tab (65 Metallic 3D Emojis)
    greyGrid: document.getElementById('grey-grid'),
    greySearch: document.getElementById('grey-search'),
    btnSelectAllGrey: document.getElementById('btn-select-all-grey'),
    txtSelectAllGrey: document.getElementById('txt-select-all-grey'),
    greySelectionCount: document.getElementById('grey-selection-count'),
    btnCreateGreyFullpack: document.getElementById('btn-create-grey-fullpack'),
    
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
    btnReferralInvite: document.getElementById('btn-referral-invite'),
    btnHeaderTopup: document.getElementById('btn-header-topup'),
    modalCurrBal: document.getElementById('modal-curr-bal'),
    modalNeededBal: document.getElementById('modal-needed-bal'),
    modalDiffBal: document.getElementById('modal-diff-bal'),
    
    // Payment Choice Modal
    modalPaymentChoice: document.getElementById('modal-payment-choice'),
    btnClosePaymentChoice: document.getElementById('btn-close-payment-choice'),
    btnCancelPayChoice: document.getElementById('btn-cancel-pay-choice'),
    payChoiceCount: document.getElementById('pay-choice-count'),
    payChoiceText: document.getElementById('pay-choice-text'),
    payChoiceCost: document.getElementById('pay-choice-cost'),
    payChoiceBalance: document.getElementById('pay-choice-balance'),
    btnPayStarsBot: document.getElementById('btn-pay-stars-bot'),
    btnPayWallet: document.getElementById('btn-pay-wallet'),
    
    // Invoice Sent Modal
    modalInvoiceSent: document.getElementById('modal-invoice-sent'),
    btnCloseInvoiceSent: document.getElementById('btn-close-invoice-sent'),
    btnGotoBot: document.getElementById('btn-goto-bot'),
    
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
    let str = msg;
    if (msg instanceof Error) {
        str = msg.message;
    } else if (typeof msg === 'object' && msg !== null) {
        if (msg.message) str = msg.message;
        else if (msg.detail) str = typeof msg.detail === 'string' ? msg.detail : JSON.stringify(msg.detail);
        else str = JSON.stringify(msg);
    }
    if (typeof str === 'string' && (str.includes('[object Object]') || str.trim() === '❌' || str.trim() === '⚠️')) {
        str = "Xatolik yuz berdi. Qaytadan urinib ko'ring.";
    }
    if (dom.toastMsg) dom.toastMsg.textContent = str || "Xabar";
    if (dom.toastIcon) dom.toastIcon.textContent = icon;
    if (dom.toast) dom.toast.classList.remove('hidden');
    
    toastTimeout = setTimeout(() => {
        dom.toast?.classList.add('hidden');
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

// Sanitizes Lottie animation JSON to guarantee 100% bodymovin / lottie-web specification compliance
function sanitizeLottieAnimationData(data) {
    if (!data || typeof data !== 'object') return data;
    try {
        const w = data.w || 512;
        const h = data.h || 512;
        function fixLayer(l) {
            if (!l || typeof l !== 'object') return;
            if (l.ty === 4) {
                if ('shes' in l) delete l.shes;
                if (!l.shapes || !Array.isArray(l.shapes)) l.shapes = [];
            } else if (l.ty === 0) {
                if (!l.w) l.w = w;
                if (!l.h) l.h = h;
            }
        }
        if (Array.isArray(data.layers)) data.layers.forEach(fixLayer);
        if (Array.isArray(data.assets)) {
            data.assets.forEach(a => {
                if (a && typeof a === 'object' && Array.isArray(a.layers)) {
                    if (!a.w) a.w = w;
                    if (!a.h) a.h = h;
                    a.layers.forEach(fixLayer);
                }
            });
        }
    } catch (_) {}
    return data;
}

function safeLoadLottieAnimation(params) {
    if (!params || !params.container || !params.animationData) return null;
    try {
        params.animationData = sanitizeLottieAnimationData(params.animationData);
        if (window.lottie && typeof window.lottie.loadAnimation === 'function') {
            return window.lottie.loadAnimation(params);
        } else if (window.bodymovin && typeof window.bodymovin.loadAnimation === 'function') {
            return window.bodymovin.loadAnimation(params);
        }
    } catch (err) {
        console.error("Lottie load animation error:", err);
    }
    return null;
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

// Client-side Lottie 3-way recolorer for 0ms latency real-time preview (Outer, Inner, Text)
function applyBadgeColorToLottieJSON(jsonObj, badgeColor, badgeBgColor, textColor) {
    if (!jsonObj) return jsonObj;
    try {
        function parseHex(hexStr) {
            if (!hexStr) return null;
            let cleanHex = String(hexStr).trim();
            if (!cleanHex.startsWith('#') && (cleanHex.length === 3 || cleanHex.length === 6 || cleanHex.length === 8)) {
                cleanHex = '#' + cleanHex;
            }
            if (!/^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$/.test(cleanHex)) return null;
            let h = cleanHex.slice(1);
            if (h.length === 3) h = h.split('').map(c => c + c).join('');
            return [
                parseInt(h.slice(0, 2), 16) / 255.0,
                parseInt(h.slice(2, 4), 16) / 255.0,
                parseInt(h.slice(4, 6), 16) / 255.0
            ];
        }

        const cPrimary = parseHex(badgeColor);
        const cSecondary = parseHex(badgeBgColor);
        const cText = parseHex(textColor);

        const cloned = JSON.parse(JSON.stringify(jsonObj));

        function walk(item, isInText = false) {
            if (!item || typeof item !== 'object') return;
            const nm = String(item.nm || '');
            if (nm === 'SVG_Symbol' || nm.includes('SVG Path') || nm.includes('Logo path')) {
                return;
            }
            const isTextNode = isInText || nm === 'TextGroup' || nm === 'EMOJI' || (nm.length === 1 && /^[A-Za-z0-9]$/.test(nm) && item.ty === 'gr');

            if ((item.ty === 'fl' || item.ty === 'st') && item.c && Array.isArray(item.c.k)) {
                const k = item.c.k;
                if (k.length >= 3 && typeof k[0] === 'number') {
                    const alpha = k[3] !== undefined ? k[3] : 1.0;
                    
                    if (!item._role) {
                        if (isTextNode) {
                            item._role = 'text';
                        } else if (item.ty === 'st' || (k[0] > 0.82 && k[1] > 0.82 && k[2] > 0.82)) {
                            item._role = 'outer';
                        } else if (item.ty === 'fl' && k[0] < 0.18 && k[1] < 0.18 && k[2] < 0.18) {
                            item._role = 'inner';
                        } else {
                            item._role = 'none';
                        }
                    }

                    if (item._role === 'outer' && cPrimary) {
                        item.c.k = [cPrimary[0], cPrimary[1], cPrimary[2], alpha];
                    } else if (item._role === 'inner' && cSecondary) {
                        item.c.k = [cSecondary[0], cSecondary[1], cSecondary[2], alpha];
                    } else if (item._role === 'text' && cText && item.ty === 'fl') {
                        item.c.k = [cText[0], cText[1], cText[2], alpha];
                    }
                }
            }
            if (Array.isArray(item.it)) {
                item.it.forEach(sub => walk(sub, isTextNode));
            }
            if (Array.isArray(item.shapes)) {
                item.shapes.forEach(sub => walk(sub, isTextNode));
            }
        }

        if (Array.isArray(cloned.layers)) {
            cloned.layers.forEach(l => walk(l, false));
        }
        if (Array.isArray(cloned.assets)) {
            cloned.assets.forEach(a => {
                if (Array.isArray(a.layers)) {
                    a.layers.forEach(l => walk(l, false));
                }
            });
        }
        return cloned;
    } catch (e) {
        console.warn("Client recolor error:", e);
        return jsonObj;
    }
}

function getActiveTargetColor() {
    if (state.activeColorTarget === 'inner') return state.badgeBgColor || "#000000";
    if (state.activeColorTarget === 'text') return state.textColor || "#FFFFFF";
    return state.badgeColor || "#FFFFFF";
}

function setActiveColorTarget(target) {
    state.activeColorTarget = target;
    dom.targetPillOuter?.classList.toggle('active', target === 'outer');
    dom.targetPillInner?.classList.toggle('active', target === 'inner');
    dom.targetPillText?.classList.toggle('active', target === 'text');
    syncColorControlsUI();
}

function syncColorControlsUI() {
    const isLogoTab = state.activeTab === 'logo' || state.inputType === 'svg';
    if (dom.logoColorSection) {
        if (isLogoTab) {
            dom.logoColorSection.classList.remove('hidden');
        } else {
            dom.logoColorSection.classList.add('hidden');
        }
    }

    const curColor = getActiveTargetColor();
    const hexClean = curColor.replace('#', '').toUpperCase();
    if (dom.logoHexInput && document.activeElement !== dom.logoHexInput) {
        dom.logoHexInput.value = hexClean;
    }
    if (dom.logoColorPicker) {
        dom.logoColorPicker.value = curColor.slice(0, 7);
    }
    if (dom.pickerSwatchCircle) {
        dom.pickerSwatchCircle.style.backgroundColor = curColor;
    }

    if (dom.presetColorsBar) {
        dom.presetColorsBar.querySelectorAll('.color-swatch-btn').forEach(btn => {
            if (btn.dataset.color && btn.dataset.color.toUpperCase() === curColor.toUpperCase()) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    if (dom.targetDotOuter) dom.targetDotOuter.style.backgroundColor = state.badgeColor || '#FFFFFF';
    if (dom.targetDotInner) dom.targetDotInner.style.backgroundColor = state.badgeBgColor || '#000000';
    if (dom.targetDotText) dom.targetDotText.style.backgroundColor = state.textColor || '#FFFFFF';
    if (dom.dotSummaryOuter) dom.dotSummaryOuter.style.backgroundColor = state.badgeColor || '#FFFFFF';
    if (dom.dotSummaryInner) dom.dotSummaryInner.style.backgroundColor = state.badgeBgColor || '#000000';
    if (dom.dotSummaryText) dom.dotSummaryText.style.backgroundColor = state.textColor || '#FFFFFF';

    const isSvg = state.inputType === 'svg';
    if (dom.targetPillText) dom.targetPillText.style.display = isSvg ? 'none' : '';
    if (dom.badgeSummaryText) dom.badgeSummaryText.style.display = isSvg ? 'none' : '';
}

function setTargetColor(rawHex, triggerUpdate = true) {
    if (!rawHex) {
        rawHex = state.activeColorTarget === 'inner' ? '#000000' : '#FFFFFF';
    }
    let clean = String(rawHex).trim();
    if (!clean.startsWith('#') && (clean.length === 3 || clean.length === 6 || clean.length === 8)) {
        clean = '#' + clean;
    }
    if (!/^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$/.test(clean)) {
        return;
    }
    let hexUpper = clean.toUpperCase();
    if (hexUpper.length === 4) {
        hexUpper = '#' + hexUpper[1] + hexUpper[1] + hexUpper[2] + hexUpper[2] + hexUpper[3] + hexUpper[3];
    }

    if (state.activeColorTarget === 'inner') {
        state.badgeBgColor = hexUpper;
    } else if (state.activeColorTarget === 'text') {
        state.textColor = hexUpper;
    } else {
        state.badgeColor = hexUpper;
    }

    syncColorControlsUI();

    if (triggerUpdate) {
        state.previewCache.clear();
        updateLivePreview();
        debouncedFullUpdate();
    }
}

function setBadgeColor(rawHex, triggerUpdate = true) {
    state.badgeColor = rawHex || '#FFFFFF';
    syncColorControlsUI();
    if (triggerUpdate) {
        state.previewCache.clear();
        updateLivePreview();
        debouncedFullUpdate();
    }
}

// ==================== INITIALIZATION ====================

async function initApp() {
    // 0. Strict Telegram Environment Verification
    if (window.IS_TG_BLOCKED || !isTelegramEnvironment()) {
        if (dom.loadingScreen) {
            dom.loadingScreen.style.display = 'none';
            dom.loadingScreen.classList.add('hidden');
        }
        dom.appContainer?.classList.add('hidden');
        const guard = document.getElementById('telegram-only-guard');
        if (guard) {
            guard.classList.remove('hidden');
            guard.style.display = 'flex';
        }
        return;
    }

    let currentP = 35;
    updateLoadingProgress(35, "Telegram muhiti tayyorlanmoqda...");

    const progressTimer = setInterval(() => {
        if (currentP < 95) {
            currentP += 20;
            updateLoadingProgress(currentP, currentP < 60 ? "Shablonlar yuklanmoqda..." : "Animatsiyalar tayyorlanmoqda...");
        }
    }, 200);

    const safetyTimeout = setTimeout(() => {
        clearInterval(progressTimer);
        updateLoadingProgress(100, "Tayyor!");
        dom.loadingScreen?.classList.add('fade-out');
        dom.appContainer?.classList.remove('hidden');
    }, 3800);

    try {
        if (tg) {
            tg.ready();
            tg.expand();
            // True fullscreen in modern Telegram (API 8.0+)
            if (typeof tg.requestFullscreen === 'function') {
                try { tg.requestFullscreen(); } catch (_) {}
            }
            // Disable vertical swipes to prevent accidental closing on scroll
            if (typeof tg.disableVerticalSwipes === 'function') {
                try { tg.disableVerticalSwipes(); } catch (_) {}
            }
            // Seamless deep dark header & background
            if (typeof tg.setHeaderColor === 'function') {
                try { tg.setHeaderColor('#060911'); } catch (_) {}
            }
            if (typeof tg.setBackgroundColor === 'function') {
                try { tg.setBackgroundColor('#060911'); } catch (_) {}
            }
            // Always keep full expanded state
            if (typeof tg.onEvent === 'function') {
                tg.onEvent('viewportChanged', () => {
                    if (!tg.isExpanded) tg.expand();
                });
            }
            document.body.classList.add('telegram-theme');
            
            const user = tg.initDataUnsafe?.user;
            if (user) {
                state.user = user;
                if (dom.userName) dom.userName.textContent = user.first_name || user.username || "Foydalanuvchi";
                if (dom.userAvatar) {
                    if (user.photo_url) {
                        dom.userAvatar.innerHTML = `<img src="${user.photo_url}" alt="Avatar">`;
                    } else {
                        const initials = (user.first_name ? user.first_name[0] : 'U').toUpperCase();
                        dom.userAvatar.textContent = initials;
                    }
                }
            }
        }
        
        updateLoadingProgress(70, "Shablonlar va emojilar yuklanmoqda...");
        
        // 0. Initialize Colors
        state.badgeColor = "#FFFFFF";
        state.badgeBgColor = "#000000";
        state.textColor = "#FFFFFF";
        state.activeColorTarget = "outer";
        syncColorControlsUI();

        // 1. Render initial Live Hero Preview & SVG Thumbnail
        updateSvgThumbnail();
        await updateLivePreview();
        
        // 2. Render the 13 Ticket Templates in Name Tab (none selected by default)
        renderTicketsGrid();
        
        // 3. Render the 103 Logo Templates in Logo Tab (none selected by default)
        renderLogosGrid();
        
        // 3.5. Render the 65 Grey Metallic 3D Templates in Grey Tab (none selected by default)
        renderGreyGrid();
        
        // 4. Update Selection Status
        updateSelectionStatus();
        
        // 5. Load user info, balance & existing packs
        const uid = state.user?.id || 1323217434;
        await loadUserInfo(uid);
        
        clearTimeout(safetyTimeout);
        clearInterval(progressTimer);
        updateLoadingProgress(100, "Tayyor!");
        
        setTimeout(() => {
            dom.loadingScreen?.classList.add('fade-out');
            dom.appContainer?.classList.remove('hidden');
        }, 150);
        
    } catch (err) {
        console.error("App init error:", err);
        clearTimeout(safetyTimeout);
        clearInterval(progressTimer);
        dom.loadingScreen?.classList.add('fade-out');
        dom.appContainer?.classList.remove('hidden');
    }
}

function updateLoadingProgress(percent, statusText) {
    if (dom.loaderBar) dom.loaderBar.style.width = `${percent}%`;
    if (dom.loaderStatus) dom.loaderStatus.textContent = statusText;
}

// ==================== ROBUST MULTI-FALLBACK API ====================

async function apiFetch(endpoint, options = {}) {
    let cleanEndpoint = endpoint;
    let queryPart = '';
    if (endpoint.includes('?')) {
        const parts = endpoint.split('?');
        cleanEndpoint = parts[0];
        queryPart = '?' + parts[1];
    }
    
    // Always use trailing slash on API endpoints so Nginx doesn't redirect POST requests
    const slashEndpoint = cleanEndpoint.endsWith('/') ? cleanEndpoint : `${cleanEndpoint}/`;
    
    const urls = [
        `/api/${slashEndpoint}${queryPart}`,
        `/api/${cleanEndpoint}${queryPart}`,
        `/api/index.php?endpoint=${cleanEndpoint}${queryPart ? '&' + queryPart.slice(1) : ''}`
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
                let detailMsg = errData.detail;
                if (Array.isArray(detailMsg)) {
                    detailMsg = detailMsg.map(d => (d && (d.msg || d.detail)) ? (d.msg || d.detail) : JSON.stringify(d)).join("; ");
                } else if (typeof detailMsg === 'object' && detailMsg !== null) {
                    detailMsg = detailMsg.msg || detailMsg.detail || JSON.stringify(detailMsg);
                }
                throw new Error(String(detailMsg));
            }
            lastError = new Error(`Server xatosi (${res.status})`);
        } catch (e) {
            let errorMsg = e.message || String(e);
            if (typeof e === 'object' && e !== null && !e.message) {
                errorMsg = JSON.stringify(e);
            }
            if (errorMsg && !errorMsg.startsWith("Server xatosi") && !errorMsg.startsWith("HTTP")) {
                throw new Error(errorMsg);
            }
            lastError = new Error(errorMsg);
        }
    }
    throw lastError || new Error("API ulanishida xatolik yuz berdi");
}

async function loadUserInfo(userId) {
    try {
        let startParam = '';
        if (window.Telegram?.WebApp?.initDataUnsafe?.start_param) {
            startParam = encodeURIComponent(window.Telegram.WebApp.initDataUnsafe.start_param);
        } else {
            const urlParams = new URLSearchParams(window.location.search);
            const refFromUrl = urlParams.get('tgWebAppStartParam') || urlParams.get('startapp') || urlParams.get('ref') || urlParams.get('start');
            if (refFromUrl) startParam = encodeURIComponent(refFromUrl);
        }

        const query = startParam ? `user_info?user_id=${userId}&ref=${startParam}` : `user_info?user_id=${userId}`;
        const res = await apiFetch(query);
        const data = await res.json();
        state.userBalance = data.balance ?? 0;
        state.emojiPrice = data.emoji_price ?? 6;
        state.userPacks = data.packs ?? [];
        state.referralStats = data.referral_stats ?? { count: 0, total_earned: 0 };
        state.referralBonus = data.referral_bonus ?? 10;
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

function escapeHtml(str) {
    if (!str) return "";
    return String(str).replace(/[&<>"']/g, m => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    })[m]);
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
    
    state.userPacks.forEach((pack) => {
        let pname = "";
        let ptitle = "";
        if (Array.isArray(pack)) {
            pname = pack[0] || "";
            ptitle = pack[1] || pack[0] || "";
        } else if (typeof pack === 'object' && pack !== null) {
            pname = pack.pack_name || pack.name || "";
            ptitle = pack.pack_title || pack.title || pname;
        } else if (typeof pack === 'string') {
            pname = pack;
            ptitle = pack;
        }
        if (pname) {
            const opt = document.createElement('option');
            opt.value = pname;
            opt.textContent = `📦 ${ptitle}`;
            dom.existingPackSelect.appendChild(opt);
        }
    });
}

function renderUserPacks() {
    if (!dom.userPacksList) return;
    dom.userPacksList.innerHTML = '';
    
    if (!state.userPacks || state.userPacks.length === 0) {
        dom.userPacksList.innerHTML = `
            <div class="packs-empty">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="32" height="32">
                    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                </svg>
                <span>Hali yaratilgan to'plamlar yo'q</span>
            </div>
        `;
        return;
    }
    
    state.userPacks.forEach(pack => {
        let pname = "";
        let ptitle = "";
        let pdate = "";
        if (Array.isArray(pack)) {
            pname = pack[0] || "";
            ptitle = pack[1] || pack[0] || "";
            pdate = pack[2] || "";
        } else if (typeof pack === 'object' && pack !== null) {
            pname = pack.pack_name || pack.name || "";
            ptitle = pack.pack_title || pack.title || pname;
            pdate = pack.created_at || "";
        } else if (typeof pack === 'string') {
            pname = pack;
            ptitle = pack;
        }
        
        if (!pname) return;
        
        const packLink = `https://t.me/addemoji/${pname}`;
        const item = document.createElement('a');
        item.href = packLink;
        item.target = '_blank';
        item.className = 'pack-item-card';
        item.onclick = (e) => {
            if (tg) {
                e.preventDefault();
                tg.openTelegramLink(packLink);
            }
        };
        
        item.innerHTML = `
            <div class="pack-info-left">
                <span class="pack-name-txt">${escapeHtml(ptitle)}</span>
                <span class="pack-date-txt">${pdate || pname}</span>
            </div>
            <span class="pack-btn-open">Ochish</span>
        `;
        dom.userPacksList.appendChild(item);
    });
}

function getPreviewCacheKey(file, scale) {
    const isLogo = parseInt(getTemplateNumber(file)) >= 14 || state.inputType === 'svg';
    if (state.inputType === 'svg') {
        const svgHash = (state.svgData || "").length + "_" + (state.svgData || "").slice(0, 30);
        const bColor = state.badgeColor || '#FFFFFF';
        const bgCol = state.badgeBgColor || '#000000';
        const tCol = state.textColor || '#FFFFFF';
        return `${file}_svg_${scale}_${svgHash}_${bColor}_${bgCol}_${tCol}`;
    }
    const cleanTxt = (state.text && state.text.trim()) ? state.text.trim().toUpperCase() : "ISMINGIZ";
    if (!isLogo) {
        return `${file}_${state.font}_${scale}_${cleanTxt}`;
    }
    const bColor = state.badgeColor || '#FFFFFF';
    const bgCol = state.badgeBgColor || '#000000';
    const tCol = state.textColor || '#FFFFFF';
    return `${file}_${state.font}_${scale}_${cleanTxt}_${bColor}_${bgCol}_${tCol}`;
}

async function fetchLottiePreview(templateFile, text, font, scale = 1.0) {
    const isSvg = state.inputType === 'svg';
    const isLogo = parseInt(getTemplateNumber(templateFile)) >= 14 || isSvg;
    const cleanTxt = (text && text.trim()) ? text.trim().toUpperCase() : (isSvg ? "SVG" : "ISMINGIZ");
    const cacheKey = getPreviewCacheKey(templateFile, scale);
    
    if (state.previewCache.has(cacheKey)) {
        return state.previewCache.get(cacheKey);
    }
    
    try {
        const res = await apiFetch('preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                template_id: templateFile,
                input_type: state.inputType,
                text: cleanTxt,
                font: font,
                scale: scale,
                svg_data: isSvg ? state.svgData : null,
                badge_color: isLogo ? (state.badgeColor || null) : null,
                badge_bg_color: isLogo ? (state.badgeBgColor || null) : null,
                text_color: isLogo ? (state.textColor || null) : null
            })
        });
        
        let animationData = await res.json();
        if (animationData && !animationData.detail) {
            state.previewCache.set(cacheKey, animationData);
            return animationData;
        }
        throw new Error(animationData.detail || "Xato");
    } catch (err) {
        console.warn("API preview fallback:", err);
        if (!isSvg) {
            let fallbackData = getPreRenderedTemplateData(templateFile, font, scale);
            if (fallbackData) {
                if (isLogo) {
                    fallbackData = applyBadgeColorToLottieJSON(fallbackData, state.badgeColor, state.badgeBgColor, state.textColor);
                }
                return fallbackData;
            }
        }
        return null;
    }
}

async function fetchBatchPreviews(templateFiles, text, font, scale = 1.0) {
    const isSvg = state.inputType === 'svg';
    const cleanTxt = (text && text.trim()) ? text.trim().toUpperCase() : (isSvg ? "SVG" : "ISMINGIZ");
    const needed = [];
    const results = {};
    const isDefaultColors = (!state.badgeColor || state.badgeColor === '#FFFFFF') && 
                            (!state.badgeBgColor || state.badgeBgColor === '#000000') &&
                            (!state.textColor || state.textColor === '#FFFFFF');
    
    templateFiles.forEach(file => {
        const isLogo = parseInt(getTemplateNumber(file)) >= 14 || isSvg;
        const cacheKey = getPreviewCacheKey(file, scale);
        if (state.previewCache.has(cacheKey)) {
            results[file] = state.previewCache.get(cacheKey);
        } else if (!isSvg && cleanTxt === "ISMINGIZ" && (isDefaultColors || !isLogo)) {
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
                input_type: state.inputType,
                text: cleanTxt,
                font: font,
                scale: scale,
                svg_data: isSvg ? state.svgData : null,
                badge_color: state.badgeColor || null,
                badge_bg_color: state.badgeBgColor || null,
                text_color: state.textColor || null
            })
        });
        
        const data = await res.json();
        if (data.previews) {
            Object.entries(data.previews).forEach(([fname, lottieData]) => {
                const cacheKey = getPreviewCacheKey(fname, scale);
                state.previewCache.set(cacheKey, lottieData);
                results[fname] = lottieData;
            });
        }
    } catch (e) {
        if (!isSvg) {
            needed.forEach(file => {
                let fallbackData = getPreRenderedTemplateData(file, font, scale);
                if (fallbackData) {
                    const isLogo = parseInt(getTemplateNumber(file)) >= 14;
                    if (isLogo) {
                        fallbackData = applyBadgeColorToLottieJSON(fallbackData, state.badgeColor, state.badgeBgColor, state.textColor);
                    }
                    results[file] = fallbackData;
                }
            });
        }
    }
    
    return results;
}

// ==================== TAB & MODE NAVIGATION ====================

function switchTab(tabKey) {
    state.activeTab = tabKey;
    dom.tabBtnName?.classList.toggle('active', tabKey === 'name');
    dom.tabBtnLogo?.classList.toggle('active', tabKey === 'logo');
    dom.tabBtnGrey?.classList.toggle('active', tabKey === 'grey');
    
    dom.tabContentName?.classList.toggle('active', tabKey === 'name');
    dom.tabContentLogo?.classList.toggle('active', tabKey === 'logo');
    dom.tabContentGrey?.classList.toggle('active', tabKey === 'grey');
    
    if (tabKey === 'name') {
        if (state.inputType !== 'svg') {
            state.selectedTemplate = Array.from(state.selectedTickets)[0] || "1.tgs";
        }
    } else if (tabKey === 'logo') {
        state.selectedTemplate = Array.from(state.selectedLogos)[0] || "14.tgs";
        if (Object.keys(state.logoPlayers).length === 0) {
            renderLogosGrid(dom.logoSearch?.value || '');
        }
    } else if (tabKey === 'grey') {
        state.selectedTemplate = Array.from(state.selectedGrey)[0] || "118.tgs";
        renderGreyGrid(dom.greySearch?.value || '');
    }
    syncColorControlsUI();
    updateLivePreview();
    updateSelectionStatus();
}

const debouncedFullUpdate = debounce(() => {
    if (state.activeTab === 'name') {
        renderTicketsGrid(dom.templateSearch?.value || '');
    } else if (state.activeTab === 'logo') {
        renderLogosGrid(dom.logoSearch?.value || '');
    } else {
        renderGreyGrid(dom.greySearch?.value || '');
    }
}, 300);

// ==================== SVG LOGIC & HANDLERS ====================

function setInputMode(mode) {
    state.inputType = mode;
    state.previewCache.clear();
    
    if (mode === 'svg') {
        dom.modeTabText?.classList.remove('active');
        dom.modeTabSvg?.classList.add('active');
        dom.modeSectionText?.classList.add('hidden');
        dom.modeSectionSvg?.classList.remove('hidden');
        if (state.activeColorTarget === 'text') {
            setActiveColorTarget('outer');
        }
        
        // Auto-switch to logo tab because SVG icons belong to 104 Logo icon templates (14-117)
        switchTab('logo');
        if (!state.selectedTemplate || state.selectedTemplate === '1.tgs' || parseInt(getTemplateNumber(state.selectedTemplate)) <= 13) {
            state.selectedTemplate = Array.from(state.selectedLogos)[0] || "14.tgs";
        }
        updateSvgThumbnail();
    } else {
        dom.modeTabSvg?.classList.remove('active');
        dom.modeTabText?.classList.add('active');
        dom.modeSectionSvg?.classList.add('hidden');
        dom.modeSectionText?.classList.remove('hidden');
    }
    syncColorControlsUI();
    haptic('light');
    updateLivePreview();
    debouncedFullUpdate();
}

function updateSvgThumbnail() {
    if (state.svgData && state.svgFileName) {
        dom.svgDropzone?.classList.add('hidden');
        dom.svgActiveCard?.classList.remove('hidden');
        if (dom.svgFileName) dom.svgFileName.textContent = state.svgFileName;
        if (dom.svgThumbPreview) dom.svgThumbPreview.innerHTML = state.svgData;
    } else {
        dom.svgDropzone?.classList.remove('hidden');
        dom.svgActiveCard?.classList.add('hidden');
        if (dom.svgThumbPreview) dom.svgThumbPreview.innerHTML = '';
    }
}

function loadSvgFile(file) {
    if (!file) return;
    const name = file.name || "vector.svg";
    const lower = name.toLowerCase();
    
    if (!lower.endsWith('.svg') && file.type !== 'image/svg+xml') {
        showToast("❌ Faqat .svg formatidagi vektor fayllar qabul qilinadi! (PNG, JPG qo'llab-quvvatlanmaydi)", "⚠️", 4500);
        haptic('error');
        if (dom.svgFileInput) dom.svgFileInput.value = '';
        return;
    }
    
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const content = e.target.result;
            if (!content || !content.toLowerCase().includes('<svg')) {
                showToast("❌ Yaroqsiz SVG fayl! <svg> tegi topilmadi.", "❌", 4000);
                haptic('error');
                return;
            }
            state.svgData = content;
            state.svgFileName = name;
            state.inputType = 'svg';

            if (!state.svgPackName && dom.svgPackNameInput) {
                const autoName = name.replace(/\.[^/.]+$/, "").replace(/[^a-zA-Z0-9а-яА-ЯёЁ_ \-]/g, '').toUpperCase().slice(0, 20);
                if (autoName) {
                    state.svgPackName = autoName;
                    dom.svgPackNameInput.value = autoName;
                }
            }

            dom.modeTabText?.classList.remove('active');
            dom.modeTabSvg?.classList.add('active');
            dom.modeSectionText?.classList.add('hidden');
            dom.modeSectionSvg?.classList.remove('hidden');
            state.previewCache.clear();
            switchTab('logo');
            if (!state.selectedTemplate || parseInt(getTemplateNumber(state.selectedTemplate)) <= 13) {
                state.selectedTemplate = Array.from(state.selectedLogos)[0] || "14.tgs";
            }
            updateSvgThumbnail();
            showToast(`✅ Vektor SVG yuklandi: ${name}`, "🎨", 2500);
            haptic('success');
            updateLivePreview();
            debouncedFullUpdate();
        } catch (err) {
            console.error("SVG parsing error:", err);
            showToast(`❌ Xatolik: ${err.message || err}`, "❌");
        }
    };
    reader.onerror = () => {
        showToast("❌ Faylni o'qishda xatolik yuz berdi", "❌");
    };
    reader.readAsText(file);
}

function removeSvg() {
    state.svgData = "";
    state.svgFileName = "";
    state.svgPackName = "";
    if (dom.svgFileInput) dom.svgFileInput.value = "";
    if (dom.svgPackNameInput) dom.svgPackNameInput.value = "";
    state.previewCache.clear();
    updateSvgThumbnail();
    showToast("SVG olib tashlandi", "🗑");
    haptic('light');
    updateLivePreview();
    debouncedFullUpdate();
}

// ==================== UI RENDERING ====================

async function updateLivePreview() {
    const num = parseInt(getTemplateNumber(state.selectedTemplate));
    let tag = `Logo #${num}`;
    if (num <= 13) {
        tag = `Ticket #${num}`;
    } else if (num >= 118) {
        tag = `Grey #${num - 117}`;
    }
    if (dom.currentTemplateTag) {
        dom.currentTemplateTag.textContent = tag;
    }
    
    if (state.inputType === 'svg') {
        if (!state.svgData) {
            if (dom.previewTextDisplay) dom.previewTextDisplay.textContent = "SVG tanlanmagan";
            if (dom.previewFontDisplay) dom.previewFontDisplay.textContent = "🎨 Vektor";
            if (state.livePlayer) {
                try { state.livePlayer.destroy(); } catch (e) {}
                state.livePlayer = null;
            }
            if (dom.liveLottiePlayer) {
                dom.liveLottiePlayer.innerHTML = `
                    <div class="empty-svg-preview">
                        <div class="empty-svg-icon">🎨</div>
                        <span>SVG faylingizni yuklang</span>
                        <div class="empty-svg-sub">Vektor avtomatik tanlangan logo shablonga joylashtiriladi</div>
                    </div>
                `;
            }
            return;
        }
        if (dom.previewTextDisplay) dom.previewTextDisplay.textContent = state.svgFileName || "SVG Vektor";
        if (dom.previewFontDisplay) dom.previewFontDisplay.textContent = `🎨 Vektor (${Math.round(state.scale * 100)}%)`;
    } else {
        if (dom.previewTextDisplay) dom.previewTextDisplay.textContent = state.text ? state.text.trim().toUpperCase() : "—";
        const fontNames = { stapel: 'Stapel', inter: 'Inter', grobold: 'Grobold' };
        if (dom.previewFontDisplay) dom.previewFontDisplay.textContent = `${fontNames[state.font] || 'Stapel'} (${Math.round(state.scale * 100)}%)`;
    }
    
    const cleanTxt = (state.text && state.text.trim()) ? state.text.trim().toUpperCase() : "ISMINGIZ";
    try {
        const lottieData = await fetchLottiePreview(state.selectedTemplate, cleanTxt, state.font, state.scale);
        
        if (lottieData && dom.liveLottiePlayer) {
            state.currentHeroTemplateData = lottieData;
            if (state.livePlayer) {
                try { state.livePlayer.destroy(); } catch (e) {}
                state.livePlayer = null;
            }
            dom.liveLottiePlayer.innerHTML = '';
            state.livePlayer = safeLoadLottieAnimation({
                container: dom.liveLottiePlayer,
                renderer: 'svg',
                loop: true,
                autoplay: true,
                animationData: lottieData
            });
        }
    } catch (err) {
        console.warn("Live preview failed:", err);
    }
}

// Update selection counters and bottom action button text
function updateSelectionStatus() {
    let activeSet = state.selectedTickets;
    if (state.activeTab === 'logo') activeSet = state.selectedLogos;
    else if (state.activeTab === 'grey') activeSet = state.selectedGrey;
    
    const totalSelected = state.selectedTickets.size + state.selectedLogos.size + state.selectedGrey.size;
    
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

    // Grey tab toolbar
    if (dom.greySelectionCount) {
        dom.greySelectionCount.textContent = `${state.selectedGrey.size} ta tanlandi`;
    }
    if (dom.txtSelectAllGrey) {
        if (state.selectedGrey.size === GREY_TEMPLATES.length && GREY_TEMPLATES.length > 0) {
            dom.txtSelectAllGrey.textContent = "Tanlovni bekor qilish";
            dom.btnSelectAllGrey?.classList.add('active-all');
        } else {
            dom.txtSelectAllGrey.textContent = "Hammasini belgilash";
            dom.btnSelectAllGrey?.classList.remove('active-all');
        }
    }
    
    // Price & Label Calculation — HAR DOIM STARS TO'LOV HISOB-KITOBLARI
    const count = totalSelected > 0 ? totalSelected : 1;
    const unitPrice = state.emojiPrice || 6;
    const totalCost = count * unitPrice;
    state.lastNeededBal = totalCost;
    const priceBadge = `<span class="btn-stars-badge">${totalCost} <img src="images/image.png" class="btn-star-icon" alt="Stars"></span>`;
    
    const isExisting = state.destinationMode === 'existing';
    const actionVerb = isExisting ? "Qo'shish" : "Yaratish";
    
    // Bottom Action Button Text
    if (totalSelected > 1) {
        dom.mainBtnText.innerHTML = `Tanlangan Emojilarni ${actionVerb} (${totalSelected} ta • ${priceBadge})`;
    } else if (totalSelected === 1) {
        const allSel = [...state.selectedTickets, ...state.selectedLogos, ...state.selectedGrey];
        const singleFile = allSel[0];
        const num = getTemplateNumber(singleFile);
        dom.mainBtnText.innerHTML = `Tanlangan #${num} Emojini ${actionVerb} (${priceBadge})`;
    } else {
        const num = getTemplateNumber(state.selectedTemplate);
        dom.mainBtnText.innerHTML = `Tanlangan #${num} Emojini ${actionVerb} (${priceBadge})`;
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
        const data = batchData[file] || (state.inputType === 'svg' ? null : getPreRenderedTemplateData(file, state.font, state.scale));
        
        if (container && data) {
            container.innerHTML = '';
            const player = safeLoadLottieAnimation({
                container: container,
                renderer: 'svg',
                loop: true,
                autoplay: true,
                animationData: data
            });
            if (player) state.ticketPlayers[file] = player;
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
        const lottieData = data || (state.inputType === 'svg' ? null : getPreRenderedTemplateData(file, state.font, state.scale));
        if (container && lottieData) {
            container.innerHTML = '';
            const player = safeLoadLottieAnimation({
                container: container,
                renderer: 'svg',
                loop: true,
                autoplay: true,
                animationData: lottieData
            });
            if (player) state.logoPlayers[file] = player;
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
                            const player = safeLoadLottieAnimation({
                                container: container,
                                renderer: 'svg',
                                loop: true,
                                autoplay: true,
                                animationData: data
                            });
                            if (player) state.logoPlayers[file] = player;
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

// Render the 65 Grey Metallic 3D Emojis in Grey Tab (118.tgs to 182.tgs)
async function renderGreyGrid(filterText = '') {
    Object.values(state.greyPlayers).forEach(p => {
        try { p.destroy(); } catch (e) {}
    });
    state.greyPlayers = {};
    if (!dom.greyGrid) return;
    dom.greyGrid.innerHTML = '';
    
    let filtered = GREY_TEMPLATES;
    if (filterText && filterText.trim()) {
        const query = filterText.trim().toLowerCase();
        filtered = GREY_TEMPLATES.filter(t => 
            t.name.toLowerCase().includes(query) || 
            t.file.toLowerCase().includes(query) ||
            t.id.includes(query) ||
            `grey #${parseInt(t.id) - 117}`.toLowerCase().includes(query) ||
            `${parseInt(t.id) - 117}` === query
        );
    }
    
    if (filtered.length === 0) {
        dom.greyGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-dim);">
                Grey emoji shabloni topilmadi 🔍
            </div>
        `;
        return;
    }
    
    filtered.forEach((tpl) => {
        const num = tpl.id;
        const displayIdx = parseInt(num) - 117;
        const isSelected = state.selectedGrey.has(tpl.file);
        const card = document.createElement('div');
        card.className = `tpl-card ${isSelected ? 'selected' : ''}`;
        card.dataset.file = tpl.file;
        
        card.innerHTML = `
            <span class="tpl-badge" style="background: rgba(100, 116, 139, 0.35); border-color: rgba(148, 163, 184, 0.4);">#${displayIdx}</span>
            <div class="tpl-check-badge">✓</div>
            <div class="tpl-lottie-thumb" id="thumb-grey-${num}">
                <div class="thumb-loader"></div>
            </div>
            <div class="tpl-meta">
                <div class="tpl-title">Grey #${displayIdx}</div>
                <div class="tpl-tag-label">${tpl.tag}</div>
            </div>
        `;
        
        card.addEventListener('click', () => {
            haptic('selection');
            toggleCardSelection(tpl.file, 'grey');
        });
        
        dom.greyGrid.appendChild(card);
    });
    
    // Load first 12 grey emojis immediately via batch preview (fast & light payload)
    const initialBatch = filtered.slice(0, 12).map(t => t.file);
    try {
        const batchData = await fetchBatchPreviews(initialBatch, state.text, state.font, state.scale);
        Object.entries(batchData).forEach(([file, data]) => {
            const num = getTemplateNumber(file);
            const container = document.getElementById(`thumb-grey-${num}`);
            if (container && data && !state.greyPlayers[file]) {
                container.innerHTML = '';
                const player = safeLoadLottieAnimation({
                    container: container,
                    renderer: 'svg',
                    loop: true,
                    autoplay: true,
                    animationData: data
                });
                if (player) state.greyPlayers[file] = player;
            }
        });
    } catch (e) {
        console.warn("Initial grey batch error:", e);
    }
    
    // Lazy load remaining grey emojis on scroll (and fallback for initial cards)
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(async entry => {
                if (entry.isIntersecting) {
                    const card = entry.target;
                    const file = card.dataset.file;
                    const num = getTemplateNumber(file);
                    const container = document.getElementById(`thumb-grey-${num}`);
                    
                    if (container && !state.greyPlayers[file]) {
                        try {
                            const data = await fetchLottiePreview(file, state.text, state.font, state.scale);
                            if (data && container && !state.greyPlayers[file]) {
                                container.innerHTML = '';
                                const player = safeLoadLottieAnimation({
                                    container: container,
                                    renderer: 'svg',
                                    loop: true,
                                    autoplay: true,
                                    animationData: data
                                });
                                if (player) state.greyPlayers[file] = player;
                            }
                        } catch (err) {
                            console.warn("Lazy load thumb error:", file, err);
                        }
                    }
                    observer.unobserve(card);
                }
            });
        }, { rootMargin: '250px' });
        
        dom.greyGrid.querySelectorAll('.tpl-card').forEach((card) => {
            const file = card.dataset.file;
            if (!state.greyPlayers[file]) {
                observer.observe(card);
            }
        });
    }
}

// Toggle selection on a card (multi-select supported)
function toggleCardSelection(filename, tabKey) {
    let targetSet = state.selectedTickets;
    let container = dom.templatesGrid;
    if (tabKey === 'logo') {
        targetSet = state.selectedLogos;
        container = dom.logosGrid;
    } else if (tabKey === 'grey') {
        targetSet = state.selectedGrey;
        container = dom.greyGrid;
    }
    
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
    let targetSet = state.selectedTickets;
    let allList = TICKET_TEMPLATES;
    let container = dom.templatesGrid;
    if (tabKey === 'logo') {
        targetSet = state.selectedLogos;
        allList = LOGO_TEMPLATES;
        container = dom.logosGrid;
    } else if (tabKey === 'grey') {
        targetSet = state.selectedGrey;
        allList = GREY_TEMPLATES;
        container = dom.greyGrid;
    }
    
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
        state.modalPlayer = safeLoadLottieAnimation({
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
    const isSvg = state.inputType === 'svg';
    const cleanText = (state.text && state.text.trim()) ? state.text.trim().toUpperCase() : (isSvg ? "SVG" : "");
    
    if (!isSvg && !cleanText) {
        showToast("⚠️ Iltimos, ism yoki so'z kiriting!", "⚠️");
        dom.nameInput?.focus();
        haptic('error');
        return;
    }
    if (isSvg && !state.svgData) {
        showToast("⚠️ Iltimos, .svg vektor faylini yuklang!", "⚠️");
        haptic('error');
        return;
    }
    
    const userId = state.user?.id || 1323217434;
    
    let targetMode = mode;
    let selectedFiles = [];
    
    if (mode === 'all') {
        selectedFiles = LOGO_TEMPLATES.map(t => t.file);
    } else if (mode === 'all_grey') {
        selectedFiles = GREY_TEMPLATES.map(t => t.file);
    } else {
        const allSelected = [...state.selectedTickets, ...state.selectedLogos, ...state.selectedGrey];
        if (allSelected.length === 0) {
            targetMode = "single";
            selectedFiles = [state.selectedTemplate];
        } else if (allSelected.length === 1) {
            targetMode = "single";
            selectedFiles = allSelected;
        } else {
            targetMode = "selected";
            selectedFiles = allSelected;
        }
    }
    
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
    
    const totalCount = selectedFiles.length > 0 ? selectedFiles.length : 1;
    const unitPrice = state.emojiPrice || 6;
    const totalCost = totalCount * unitPrice;
    state.lastNeededBal = totalCost;

    const effectiveText = isSvg 
        ? (state.svgPackName ? state.svgPackName.trim().toUpperCase() : (state.text ? state.text.trim().toUpperCase() : "SVG")) 
        : cleanText;

    currentPendingAction = {
        userId,
        cleanText: effectiveText,
        inputType: state.inputType,
        svgData: isSvg ? state.svgData : null,
        badgeColor: state.badgeColor || null,
        badgeBgColor: state.badgeBgColor || null,
        textColor: state.textColor || null,
        mode: targetMode,
        rawMode: mode,
        packName,
        selectedFiles,
        totalCount,
        totalCost
    };

    if (dom.payChoiceCount) dom.payChoiceCount.textContent = `${totalCount} ta`;
    if (dom.payChoiceText) dom.payChoiceText.textContent = `"${effectiveText}"`;
    if (dom.payChoiceCost) dom.payChoiceCost.innerHTML = `${totalCost} <img src="images/image.png" class="inline-star-icon" alt="Stars">`;
    if (dom.payChoiceBalance) dom.payChoiceBalance.innerHTML = `${state.userBalance || 0} <img src="images/image.png" class="inline-star-icon" alt="Stars">`;

    dom.modalPaymentChoice?.classList.remove('hidden');
    haptic('medium');
}

let currentPendingAction = null;

function closePaymentChoiceModal() {
    dom.modalPaymentChoice?.classList.add('hidden');
}

async function handlePayViaBotStars() {
    if (!currentPendingAction) return;
    const uid = state.user?.id || 1323217434;
    const { cleanText, inputType, svgData, mode, packName, selectedFiles, totalCount } = currentPendingAction;
    
    closePaymentChoiceModal();
    showToast("Botga hisob yuborilmoqda...", "⏳");

    try {
        const res = await apiFetch('send_invoice_to_chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: uid,
                count: totalCount,
                input_type: inputType || (state.inputType === 'svg' ? 'svg' : 'text'),
                svg_data: svgData || (state.inputType === 'svg' ? state.svgData : null),
                text: cleanText,
                font: state.font,
                scale: state.scale,
                badge_color: state.badgeColor || null,
                badge_bg_color: state.badgeBgColor || null,
                text_color: state.textColor || null,
                mode: mode,
                pack_name: packName,
                template_id: selectedFiles[0] || state.selectedTemplate,
                selected_templates: selectedFiles.length > 0 ? selectedFiles : undefined
            })
        });

        await res.json();
        haptic('success');
        dom.modalInvoiceSent?.classList.remove('hidden');
    } catch (err) {
        console.error('Send invoice error:', err);
        showToast(`❌ Xatolik: ${err.message}`, "❌", 4000);
        haptic('error');
    }
}

async function handlePayViaWallet() {
    if (!currentPendingAction) return;
    const { totalCost } = currentPendingAction;

    if ((state.userBalance || 0) < totalCost) {
        closePaymentChoiceModal();
        openBalanceModal(state.userBalance || 0, totalCost);
        haptic('error');
        return;
    }

    closePaymentChoiceModal();
    executeGeneration(currentPendingAction);
}

async function executeGeneration(pendingAction) {
    const { userId, cleanText, inputType, svgData, mode, rawMode, packName, selectedFiles, totalCount, totalCost } = pendingAction;
    
    haptic('medium');
    
    if (mode === 'add_to_pack') {
        showProgressModal("Mavjud to'plamga qo'shilmoqda...", `\"${packName}\" to'plamiga ${totalCount} ta emoji qo'shilmoqda...`, 15);
    } else if (rawMode === 'all') {
        showProgressModal("Mega Logo Pack Tayyorlanmoqda...", "Barcha 103 ta logo shablon qayta ishlanmoqda...", 10);
    } else if (rawMode === 'all_grey') {
        showProgressModal("Grey 3D Pack Tayyorlanmoqda...", "Barcha 65 ta grey shablon qayta ishlanmoqda...", 10);
    } else if (mode === "single") {
        const num = parseInt(getTemplateNumber(selectedFiles[0]));
        const tag = num <= 13 ? `Ticket #${num}` : (num >= 118 ? `Grey #${num - 117}` : `Logo #${num}`);
        showProgressModal(`${tag} Tayyorlanmoqda...`, "Animatsiya qayta ishlanmoqda...", 20);
    } else {
        showProgressModal(`Maxsus Emoji Pack (${selectedFiles.length} ta)...`, "Tanlangan emojilar paketga jamlanmoqda...", 15);
    }
    
    try {
        let progress = 12;
        updateProgressStep(12, "Shablonlar tekshirilmoqda...");
        
        const progressInterval = setInterval(() => {
            if (progress < 80) {
                progress += mode === 'single' ? 12 : 5;
                let desc = "Shablonlar tayyorlanmoqda...";
                if (progress > 25 && progress <= 50) desc = "Animatsiyalar render qilinmoqda...";
                if (progress > 50) desc = "Telegram API to'plami yaratilmoqda...";
                updateProgressStep(progress, desc);
            }
        }, 220);
        
        const payload = {
            user_id: userId,
            input_type: inputType || state.inputType,
            svg_data: svgData || (state.inputType === 'svg' ? state.svgData : null),
            text: cleanText,
            font: state.font,
            scale: state.scale,
            badge_color: state.badgeColor || null,
            badge_bg_color: state.badgeBgColor || null,
            text_color: state.textColor || null,
            mode: mode,
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
        updateProgressStep(100, "Muvaffaqiyatli tayyorlandi!");
        
        if (result.remaining_balance !== undefined) {
            state.userBalance = result.remaining_balance;
            if (dom.userBalanceVal) dom.userBalanceVal.textContent = state.userBalance;
            updateSelectionStatus();
        }
        
        // Refresh user info and packs list immediately
        await loadUserInfo(userId);
        
        setTimeout(() => {
            showSuccessModal(result.pack_name, result.pack_link, rawMode === 'all');
        }, 350);
        
    } catch (err) {
        console.error('Generation failed:', err);
        hideProgressModal();
        if ((state.userBalance || 0) < totalCost) {
            openBalanceModal(state.userBalance || 0, totalCost);
        } else {
            showToast(`❌ ${err.message || "Generatsiyada xatolik yuz berdi"}`, "❌", 5000);
        }
        haptic('error');
    }
}

function openBalanceModal(currBal, neededBal) {
    const diff = Math.max(1, neededBal - currBal);
    if (dom.modalCurrBal) dom.modalCurrBal.innerHTML = `${currBal} <img src="images/image.png" class="inline-star-icon" alt="Stars">`;
    if (dom.modalNeededBal) dom.modalNeededBal.innerHTML = `${neededBal} <img src="images/image.png" class="inline-star-icon" alt="Stars">`;
    if (dom.modalDiffBal) dom.modalDiffBal.innerHTML = `${diff} <img src="images/image.png" class="inline-star-icon" alt="Stars">`;
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
    const isSvg = state.inputType === 'svg';
    const cleanText = (state.text && state.text.trim()) ? state.text.trim().toUpperCase() : (isSvg ? "SVG" : "EMOJI");
    
    showProgressModal("Paketga qo'shilmoqda...", `\"${firstPack[1]}\" to'plamiga emoji qo'shilmoqda...`, 40);
    
    try {
        const payload = {
            user_id: state.user?.id || 1323217434,
            input_type: state.inputType,
            svg_data: isSvg ? state.svgData : null,
            pack_name: packName,
            text: cleanText,
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
    
    // Mode Switch Tabs (Matn vs SVG)
    dom.modeTabText?.addEventListener('click', () => setInputMode('text'));
    dom.modeTabSvg?.addEventListener('click', () => setInputMode('svg'));
    
    // SVG File Input & Dropzone triggers
    dom.btnChangeSvg?.addEventListener('click', () => dom.svgFileInput?.click());
    dom.svgDropzone?.addEventListener('click', () => dom.svgFileInput?.click());
    
    dom.svgFileInput?.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            loadSvgFile(e.target.files[0]);
        }
    });
    
    // SVG Drag & Drop
    dom.svgDropzone?.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dom.svgDropzone.classList.add('dragover');
    });
    
    dom.svgDropzone?.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dom.svgDropzone.classList.remove('dragover');
    });
    
    dom.svgDropzone?.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dom.svgDropzone.classList.remove('dragover');
        if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            loadSvgFile(e.dataTransfer.files[0]);
        }
    });
    
    // SVG Remove Button
    dom.btnRemoveSvg?.addEventListener('click', () => {
        removeSvg();
    });

    // SVG Custom Pack Name Input
    dom.svgPackNameInput?.addEventListener('input', (e) => {
        let val = e.target.value.replace(/[^a-zA-Z0-9а-яА-ЯёЁ_ \-]/g, '').toUpperCase();
        state.svgPackName = val;
        e.target.value = val;
    });

    function updateCharCount() {
        const len = dom.nameInput.value.length;
        dom.charCount.textContent = `${len}/16`;
    }
    
    // Fast real-time live preview update
    const debouncedLiveTextUpdate = debounce(() => {
        updateLivePreview();
        if (typeof debouncedFullUpdate === 'function') {
            debouncedFullUpdate();
        }
    }, 100);
    
    dom.nameInput.addEventListener('input', () => {
        let val = dom.nameInput.value.replace(/[^a-zA-Z0-9а-яА-ЯёЁ_ \-]/g, '').toUpperCase();
        state.text = val;
        if (dom.previewTextDisplay) {
            dom.previewTextDisplay.textContent = val || "—";
        }
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

    // Color Customizer Target Selector Pills
    dom.targetPillOuter?.addEventListener('click', () => {
        haptic('selection');
        setActiveColorTarget('outer');
    });
    dom.targetPillInner?.addEventListener('click', () => {
        haptic('selection');
        setActiveColorTarget('inner');
    });
    dom.targetPillText?.addEventListener('click', () => {
        haptic('selection');
        setActiveColorTarget('text');
    });

    // Real-time live color preview on HEX input
    dom.logoHexInput?.addEventListener('input', (e) => {
        let val = e.target.value.replace(/[^0-9A-Fa-f]/g, '').slice(0, 6);
        e.target.value = val;
        if (val.length === 3 || val.length === 6) {
            setTargetColor('#' + val, false);
            const isLogo = parseInt(getTemplateNumber(state.selectedTemplate)) >= 14 || state.inputType === 'svg';
            if (isLogo && state.livePlayer && dom.liveLottiePlayer) {
                const currentData = state.currentHeroTemplateData || getPreRenderedTemplateData(state.selectedTemplate, state.font, state.scale);
                if (currentData) {
                    const recolored = applyBadgeColorToLottieJSON(currentData, state.badgeColor, state.badgeBgColor, state.textColor);
                    try {
                        state.livePlayer.destroy();
                        state.livePlayer = safeLoadLottieAnimation({
                            container: dom.liveLottiePlayer,
                            renderer: 'svg',
                            loop: true,
                            autoplay: true,
                            animationData: recolored
                        });
                    } catch (err) {}
                }
            }
            debouncedFullUpdate();
        }
    });

    dom.logoHexInput?.addEventListener('change', (e) => {
        let val = e.target.value.replace(/[^0-9A-Fa-f]/g, '').slice(0, 6);
        if (val.length === 3 || val.length === 6) {
            setTargetColor('#' + val, true);
        } else {
            syncColorControlsUI();
        }
    });

    // Real-time live color preview on native color picker input
    dom.logoColorPicker?.addEventListener('input', (e) => {
        const val = e.target.value;
        setTargetColor(val, false);
        const isLogo = parseInt(getTemplateNumber(state.selectedTemplate)) >= 14 || state.inputType === 'svg';
        if (isLogo && state.livePlayer && dom.liveLottiePlayer) {
            const currentData = state.currentHeroTemplateData || getPreRenderedTemplateData(state.selectedTemplate, state.font, state.scale);
            if (currentData) {
                const recolored = applyBadgeColorToLottieJSON(currentData, state.badgeColor, state.badgeBgColor, state.textColor);
                try {
                    state.livePlayer.destroy();
                    state.livePlayer = safeLoadLottieAnimation({
                        container: dom.liveLottiePlayer,
                        renderer: 'svg',
                        loop: true,
                        autoplay: true,
                        animationData: recolored
                    });
                } catch (err) {}
            }
        }
        debouncedFullUpdate();
    });

    dom.logoColorPicker?.addEventListener('change', (e) => {
        setTargetColor(e.target.value, true);
    });

    dom.btnColorPickerTrigger?.addEventListener('click', () => {
        dom.logoColorPicker?.click();
    });

    dom.btnResetBadgeColor?.addEventListener('click', () => {
        haptic('light');
        if (state.activeColorTarget === 'inner') {
            state.badgeBgColor = "#000000";
        } else if (state.activeColorTarget === 'text') {
            state.textColor = "#FFFFFF";
        } else {
            state.badgeColor = "#FFFFFF";
        }
        syncColorControlsUI();
        state.previewCache.clear();
        updateLivePreview();
        debouncedFullUpdate();
        showToast("Tanlangan qism rangi standart holatga qaytarildi", "↺");
    });

    dom.presetColorsBar?.querySelectorAll('.color-swatch-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            haptic('selection');
            const col = btn.dataset.color;
            if (col) {
                setTargetColor(col, true);
            }
        });
    });
    
    // Clear Name Button
    dom.btnClearName?.addEventListener('click', () => {
        haptic('light');
        state.text = "";
        if (dom.nameInput) dom.nameInput.value = "";
        updateCharCount();
        dom.nameInput?.focus();
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
            renderGreyGrid(dom.greySearch?.value || '');
        });
    });
    
    // Tab switching (Name vs Logo vs Grey)
    dom.tabBtnName?.addEventListener('click', () => {
        haptic('selection');
        switchTab('name');
    });
    
    dom.tabBtnLogo?.addEventListener('click', () => {
        haptic('selection');
        switchTab('logo');
    });

    dom.tabBtnGrey?.addEventListener('click', () => {
        haptic('selection');
        switchTab('grey');
    });
    
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

    dom.btnHeaderTopup?.addEventListener('click', (e) => {
        e.stopPropagation();
        haptic('medium');
        openBalanceModal(state.userBalance || 0, (state.lastNeededBal || state.emojiPrice || 6));
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

    dom.btnReferralInvite?.addEventListener('click', () => {
        haptic('medium');
        const uid = state.user?.id || 1323217434;
        const refLink = `https://t.me/${BOT_USERNAME}?start=ref_${uid}`;
        const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(refLink)}&text=${encodeURIComponent('✨ O`z ismingiz yoki SVG logongiz bilan Telegram Premium Animatsiyali Emoji to`plamini yarating!')}`;
        closeBalanceModal();
        if (tg?.openTelegramLink) {
            tg.openTelegramLink(shareUrl);
        } else {
            window.open(shareUrl, '_blank');
        }
    });
    
    dom.btnCloseBalanceModal?.addEventListener('click', closeBalanceModal);
    dom.btnCancelBalance?.addEventListener('click', closeBalanceModal);
    
    // Payment Choice Modal Listeners
    dom.btnPayStarsBot?.addEventListener('click', handlePayViaBotStars);
    dom.btnPayWallet?.addEventListener('click', handlePayViaWallet);
    dom.btnClosePaymentChoice?.addEventListener('click', closePaymentChoiceModal);
    dom.btnCancelPayChoice?.addEventListener('click', closePaymentChoiceModal);
    dom.btnCloseInvoiceSent?.addEventListener('click', () => {
        dom.modalInvoiceSent?.classList.add('hidden');
    });
    
    // Select All Buttons
    dom.btnSelectAllTickets?.addEventListener('click', () => toggleSelectAll('name'));
    dom.btnSelectAllLogos?.addEventListener('click', () => toggleSelectAll('logo'));
    dom.btnSelectAllGrey?.addEventListener('click', () => toggleSelectAll('grey'));
    
    // Search ticket templates (1-13)
    dom.templateSearch?.addEventListener('input', (e) => {
        renderTicketsGrid(e.target.value);
    });
    
    // Search logo templates (14-117)
    dom.logoSearch?.addEventListener('input', (e) => {
        renderLogosGrid(e.target.value);
    });

    // Search grey templates (118-182)
    dom.greySearch?.addEventListener('input', (e) => {
        renderGreyGrid(e.target.value);
    });
    
    // Bottom Action Button
    dom.btnMainAction.addEventListener('click', () => {
        startGeneration('selected');
    });
    
    // Logo Tab Full Pack Button (all 103)
    dom.btnCreateFullpack?.addEventListener('click', () => {
        startGeneration('all');
    });

    // Grey Tab Full Pack Button (all 65)
    dom.btnCreateGreyFullpack?.addEventListener('click', () => {
        startGeneration('all_grey');
    });
    
    // Refresh user packs
    dom.btnRefreshPacks?.addEventListener('click', () => {
        haptic('light');
        const uid = state.user?.id || 1323217434;
        loadUserInfo(uid);
        showToast("To'plamlar yangilandi", "🔄");
    });
    
    // Modal buttons
    dom.btnCloseModal?.addEventListener('click', closeTemplateModal);
    dom.btnGenerateSingle?.addEventListener('click', () => startGeneration('single'));
    dom.btnAddToPackModal?.addEventListener('click', addToExistingPack);
    dom.btnCloseSuccess?.addEventListener('click', () => {
        dom.modalSuccess?.classList.add('hidden');
    });
}

// Run when DOM is ready
function runInit() {
    if (window.IS_TG_BLOCKED) {
        return;
    }
    try {
        setupEventListeners();
    } catch (e) {
        console.warn("setupEventListeners warning:", e);
    }
    initApp();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runInit);
} else {
    runInit();
}
