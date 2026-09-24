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
    // 1. Explicit developer query parameter bypass (?dev=1 or ?allow_web=1)
    const params = new URLSearchParams(window.location.search);
    if (params.get('dev') === '1' || params.get('allow_web') === '1') {
        return true;
    }

    // 2. Telegram WebApp URL hash & query check (Telegram always passes tgWebAppData in hash)
    const href = window.location.href || '';
    const hash = window.location.hash || '';
    if (hash.includes('tgWebAppData=') || href.includes('tgWebAppData=')) {
        return true;
    }
    if (href.includes('tgWebAppVersion=') && href.includes('tgWebAppPlatform=')) {
        return true;
    }

    // 3. Telegram WebApp SDK verification (real initData string from Telegram)
    const tg = window.Telegram?.WebApp;
    if (tg) {
        if (tg.initData && typeof tg.initData === 'string' && tg.initData.trim().length > 15) {
            return true;
        }
        if (tg.initDataUnsafe && tg.initDataUnsafe.user && tg.initDataUnsafe.user.id) {
            return true;
        }
        if (tg.initDataUnsafe && tg.initDataUnsafe.query_id) {
            return true;
        }
    }

    // 4. Native Android Telegram JavascriptInterface with valid Telegram UA
    if (window.TelegramWebviewProxy && typeof window.TelegramWebviewProxy.postEvent === 'function') {
        if (/Telegram/i.test(navigator.userAgent || '')) {
            return true;
        }
    }

    // 5. Telegram in-app User-Agent
    const ua = navigator.userAgent || '';
    if (/Telegram|TDesktop/i.test(ua)) {
        return true;
    }

    // Outside Telegram: BLOCK!
    return false;
}

// Random name suggestions
const RANDOM_NAMES = [
    "ABDURAHIM", "ASILBEK", "BEKZOD", "SHAXRIYOR", "DILSHOD", 
    "SARDOR", "JASUR", "NODIR", "UMID", "AZIZ", 
    "TEMUR", "MALIKA", "SEVARA", "MADINA", "ZILOLA", 
    "RAYHONA", "IBROHIM", "JAVOHIR", "SHERZOD", "BOBUR"
];

// The 24 Ism Emojis (1.tgs to 13.tgs Ticket + 263.tgs to 274.tgs, excluding 266)
const TICKET_TEMPLATES = [];
for (let i = 1; i <= 13; i++) {
    TICKET_TEMPLATES.push({
        id: `${i}`,
        file: `${i}.tgs`,
        displayNum: i,
        name: `Ticket #${i}`,
        tag: "Ism Emoji"
    });
}
let ticketCounter = 14;
for (let i = 263; i <= 274; i++) {
    if (i === 266) continue; // Abu #4 (266) removed as requested
    const dNum = ticketCounter++;
    TICKET_TEMPLATES.push({
        id: `${i}`,
        file: `${i}.tgs`,
        displayNum: dNum,
        name: `Ticket #${dNum}`,
        tag: "Ism Emoji"
    });
}

// The 100 Logo Emojis (14.tgs to 117.tgs, excluding 81, 84, 91, 103)
const LOGO_TEMPLATES = [];
for (let i = 14; i <= 117; i++) {
    if (i === 81 || i === 84 || i === 91 || i === 103) continue; // Templates removed
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

// The 80 High Quality 3D Emojis (183.tgs to 262.tgs)
const HQ_TEMPLATES = [];
for (let i = 183; i <= 262; i++) {
    HQ_TEMPLATES.push({
        id: `${i}`,
        file: `${i}.tgs`,
        name: `High Quality #${i - 182}`,
        tag: "High Quality"
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
    selectedHQ: new Set(),      // 0 selected on start
    userPacks: [],
    
    // Lottie player instances
    livePlayer: null,
    modalPlayer: null,
    ticketPlayers: {},
    logoPlayers: {},
    greyPlayers: {},
    hqPlayers: {},
    
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
    
    // Main App Views & Bottom Navigation
    viewStudio: document.getElementById('view-studio'),
    viewRating: document.getElementById('view-rating'),
    viewProfile: document.getElementById('view-profile'),
    bottomNav: document.getElementById('bottom-nav'),
    navBtnStudio: document.getElementById('nav-btn-studio'),
    navBtnRating: document.getElementById('nav-btn-rating'),
    navBtnProfile: document.getElementById('nav-btn-profile'),

    // Reyting / Leaderboard
    tabRatingReferral: document.getElementById('tab-rating-referral'),
    tabRatingCreator: document.getElementById('tab-rating-creator'),
    myRankCard: document.getElementById('my-rank-card'),
    myRankNum: document.getElementById('my-rank-num'),
    myRankVal: document.getElementById('my-rank-val'),
    myRankBadge: document.getElementById('my-rank-badge'),
    podiumContainer: document.getElementById('podium-container'),
    leaderboardList: document.getElementById('leaderboard-list'),

    // Daily Bonus
    dailyBonusCard: document.getElementById('daily-bonus-card'),
    btnClaimDailyBonus: document.getElementById('btn-claim-daily-bonus'),
    claimBtnText: document.getElementById('claim-btn-text'),
    bonusDescText: document.getElementById('bonus-desc-text'),
    
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
    colorPickerLabelText: document.getElementById('color-picker-label-text'),
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
    badgeSummaryOuter: document.getElementById('badge-summary-outer'),
    badgeSummaryInner: document.getElementById('badge-summary-inner'),
    badgeSummaryText: document.getElementById('badge-summary-text'),
    dotSummaryOuter: document.getElementById('dot-summary-outer'),
    dotSummaryInner: document.getElementById('dot-summary-inner'),
    dotSummaryText: document.getElementById('dot-summary-text'),
    
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
    tabBtnHQ: document.getElementById('tab-btn-hq'),
    tabContentName: document.getElementById('tab-content-name'),
    tabContentLogo: document.getElementById('tab-content-logo'),
    tabContentGrey: document.getElementById('tab-content-grey'),
    tabContentHQ: document.getElementById('tab-content-hq'),
    tabCounterGrey: document.getElementById('tab-counter-grey'),
    tabCounterHQ: document.getElementById('tab-counter-hq'),
    
    // Name Tab (25 100x100 Emojis)
    templatesGrid: document.getElementById('templates-grid'),
    templateSearch: document.getElementById('template-search'),
    btnSelectAllTickets: document.getElementById('btn-select-all-tickets'),
    txtSelectAllTickets: document.getElementById('txt-select-all-tickets'),
    ticketSelectionCount: document.getElementById('ticket-selection-count'),
    
    // Logo Tab (100 Logo Emojis)
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
    
    // High Quality Tab (80 3D Emojis)
    hqGrid: document.getElementById('hq-grid'),
    hqSearch: document.getElementById('hq-search'),
    btnSelectAllHQ: document.getElementById('btn-select-all-hq'),
    txtSelectAllHQ: document.getElementById('txt-select-all-hq'),
    hqSelectionCount: document.getElementById('hq-selection-count'),
    btnCreateHQFullpack: document.getElementById('btn-create-hq-fullpack'),
    
    userPacksList: document.getElementById('user-packs-list'),
    btnRefreshPacks: document.getElementById('btn-refresh-packs'),
    
    // Bottom Action
    bottomActionBar: document.getElementById('bottom-action-bar'),
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
    toastIcon: document.getElementById('toast-icon'),
    
    // Profile Page Elements
    profileAvatar: document.getElementById('profile-avatar'),
    profileInitials: document.getElementById('profile-initials'),
    profileFullName: document.getElementById('profile-full-name'),
    profileUsername: document.getElementById('profile-username'),
    profileIdBadge: document.getElementById('profile-id-badge'),
    profileStarsCount: document.getElementById('profile-stars-count'),
    btnProfileTopup: document.getElementById('btn-profile-topup'),
    profileRefLinkInput: document.getElementById('profile-ref-link-input'),
    btnCopyRef: document.getElementById('btn-copy-ref'),
    copyBtnText: document.getElementById('copy-btn-text'),
    copyIconSvg: document.getElementById('copy-icon-svg'),
    btnShareTelegramRef: document.getElementById('btn-share-telegram-ref'),
    refStatCount: document.getElementById('ref-stat-count'),
    refStatEarned: document.getElementById('ref-stat-earned'),
    profilePriceDisplay: document.getElementById('profile-price-display'),
    profileRefDesc: document.getElementById('profile-ref-desc'),
    profileRefBonusText: document.getElementById('profile-ref-bonus-text'),
    profileRefBadge: document.getElementById('profile-ref-badge'),
    profilePacksCount: document.getElementById('profile-packs-count'),
    profilePacksList: document.getElementById('profile-packs-list'),
    btnGotoStudio: document.getElementById('btn-goto-studio'),
    btnProfileChannel: document.getElementById('btn-profile-channel'),
    btnProfileHelp: document.getElementById('btn-profile-help'),

    // Views & Main Navigation
    viewStudio: document.getElementById('view-studio'),
    viewRating: document.getElementById('view-rating'),
    viewProfile: document.getElementById('view-profile'),
    navBtnStudio: document.getElementById('nav-btn-studio'),
    navBtnRating: document.getElementById('nav-btn-rating'),
    navBtnProfile: document.getElementById('nav-btn-profile'),

    // Rating (Leaderboard) Elements
    tabRatingReferral: document.getElementById('tab-rating-referral'),
    tabRatingCreator: document.getElementById('tab-rating-creator'),
    myRankNum: document.getElementById('my-rank-num'),
    myRankVal: document.getElementById('my-rank-val'),
    myRankBadge: document.getElementById('my-rank-badge'),
    leaderboardList: document.getElementById('leaderboard-list'),

    // Daily Bonus Elements
    dailyBonusCard: document.getElementById('daily-bonus-card'),
    btnClaimDailyBonus: document.getElementById('btn-claim-daily-bonus'),
    claimBtnText: document.getElementById('claim-btn-text'),
    bonusDescText: document.getElementById('bonus-desc-text')
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

const toastSvgMap = {
    info: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#38bdf8" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`,
    success: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#22c55e" stroke-width="2.2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`,
    warning: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#f59e0b" stroke-width="2.2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`,
    error: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#ef4444" stroke-width="2.2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`,
    gift: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#c084fc" stroke-width="2"><polyline points="20 12 20 22 4 22 4 12"></polyline><rect x="2" y="7" width="20" height="5"></rect><line x1="12" y1="22" x2="12" y2="7"></line><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"></path><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"></path></svg>`,
    copy: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#38bdf8" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`,
    refresh: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#38bdf8" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>`,
    palette: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#a855f7" stroke-width="2"><circle cx="13.5" cy="6.5" r=".5" fill="currentColor"></circle><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"></circle><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"></circle><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"></circle><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.563-2.512 5.563-5.563C22 6.5 17.5 2 12 2z"></path></svg>`
};

let toastTimeout = null;
function showToast(msg, iconType = 'info', duration = 3000) {
    if (toastTimeout) clearTimeout(toastTimeout);
    let str = msg;
    if (msg instanceof Error) {
        str = msg.message;
    } else if (typeof msg === 'object' && msg !== null) {
        if (msg.message) str = msg.message;
        else if (msg.detail) str = typeof msg.detail === 'string' ? msg.detail : JSON.stringify(msg.detail);
        else str = JSON.stringify(msg);
    }
    if (typeof str === 'string') {
        // Strip any leading emojis so toast is always crisp SVG only
        str = str.replace(/^[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}⚠️❌✅⭐️🎁🔗🔄↺⏳🎨ℹ️🗑\s]+/u, '').trim();
        if (str.includes('[object Object]') || !str) {
            const dict = (typeof i18n !== 'undefined' && i18n[state.lang]) ? i18n[state.lang] : {};
            str = dict.toast_error || "Xatolik yuz berdi. Qaytadan urinib ko'ring.";
        }
    }
    
    // Map emoji or type string to vector SVG icon
    let typeKey = 'info';
    if (iconType === 'success' || iconType === '✅') typeKey = 'success';
    else if (iconType === 'error' || iconType === '❌') typeKey = 'error';
    else if (iconType === 'warning' || iconType === '⚠️') typeKey = 'warning';
    else if (iconType === 'gift' || iconType === '🎁') typeKey = 'gift';
    else if (iconType === 'copy' || iconType === '🔗') typeKey = 'copy';
    else if (iconType === 'refresh' || iconType === '🔄' || iconType === '↺' || iconType === '🗑') typeKey = 'refresh';
    else if (iconType === 'palette' || iconType === '🎨') typeKey = 'palette';
    else if (toastSvgMap[iconType]) typeKey = iconType;

    if (dom.toastMsg) dom.toastMsg.textContent = str || "Xabar";
    if (dom.toastIcon) dom.toastIcon.innerHTML = toastSvgMap[typeKey] || toastSvgMap.info;
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
    // Fallback: check Abu templates cache for 263-274
    if (window.ABU_TEMPLATE_DATA && window.ABU_TEMPLATE_DATA[font]) {
        const raw = window.ABU_TEMPLATE_DATA[font][filename];
        if (raw) {
            return scale === 1.0 ? raw : applyScaleToLottieJSON(raw, scale);
        }
    }
    return null;
}

// Client-side Lottie 3-way recolorer for 0ms latency real-time preview (Outer, Inner, Text)
function applyBadgeColorToLottieJSON(jsonObj, badgeColor, badgeBgColor, textColor, isGrey = false) {
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

        const cPrimary = isGrey ? null : parseHex(badgeColor);
        const cSecondary = isGrey ? null : parseHex(badgeBgColor);
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
    const isHQTab = state.activeTab === 'hq';
    const isGreyTab = state.activeTab === 'grey';
    const isLogoTab = state.activeTab === 'logo' || state.inputType === 'svg';
    const showColorSection = isLogoTab || isGreyTab || isHQTab;

    if (dom.logoColorSection) {
        if (showColorSection) {
            dom.logoColorSection.classList.remove('hidden');
        } else {
            dom.logoColorSection.classList.add('hidden');
        }
    }

    const isSingleTextMode = isGreyTab || isHQTab;
    if (isSingleTextMode) {
        state.activeColorTarget = 'text';
    }

    if (dom.colorPickerLabelText) {
        dom.colorPickerLabelText.textContent = isHQTab ? "High Quality Matn Rangi" : (isGreyTab ? "Grey Emoji Matn Rangi" : "Ranglarni sozlash");
    }

    if (dom.targetPillOuter) dom.targetPillOuter.style.display = isSingleTextMode ? 'none' : '';
    if (dom.targetPillInner) dom.targetPillInner.style.display = isSingleTextMode ? 'none' : '';
    if (dom.badgeSummaryOuter) dom.badgeSummaryOuter.style.display = isSingleTextMode ? 'none' : '';
    if (dom.badgeSummaryInner) dom.badgeSummaryInner.style.display = isSingleTextMode ? 'none' : '';

    const isSvg = state.inputType === 'svg';
    if (dom.targetPillText) dom.targetPillText.style.display = isSvg ? 'none' : '';
    if (dom.badgeSummaryText) dom.badgeSummaryText.style.display = isSvg ? 'none' : '';

    if (isSingleTextMode) {
        dom.targetPillText?.classList.add('active');
        dom.targetPillOuter?.classList.remove('active');
        dom.targetPillInner?.classList.remove('active');
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
            // Enable Telegram closing confirmation dialog ("Changes that you made may not be saved")
            if (typeof tg.enableClosingConfirmation === 'function') {
                try { tg.enableClosingConfirmation(); } catch (_) {}
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
        
        // 3.6. Render the 80 High Quality Templates in HQ Tab (none selected by default)
        renderHQGrid();
        
        // 4. Update Selection Status
        updateSelectionStatus();
        
        // 5. Load user info, balance & existing packs
        const uid = state.user?.id || 1323217434;
        await loadUserInfo(uid);

        // 6. Initialize Language & Daily Bonus
        const savedLang = localStorage.getItem('gn_lang') || (state.user?.language_code === 'ru' ? 'ru' : state.user?.language_code === 'en' ? 'en' : 'uz');
        applyLanguage(savedLang);
        checkDailyBonusStatus();
        
        clearTimeout(safetyTimeout);
        clearInterval(progressTimer);
        updateLoadingProgress(100, "Tayyor!");
        
        setTimeout(() => {
            dom.loadingScreen?.classList.add('fade-out');
            dom.appContainer?.classList.remove('hidden');
            if (window.lucide && window.lucide.createIcons) {
                window.lucide.createIcons();
            }
            if (window.__pendingTab) {
                const pTab = window.__pendingTab;
                delete window.__pendingTab;
                switchTab(pTab);
            }
        }, 150);
        
    } catch (err) {
        console.error("App init error:", err);
        clearTimeout(safetyTimeout);
        clearInterval(progressTimer);
        dom.loadingScreen?.classList.add('fade-out');
        dom.appContainer?.classList.remove('hidden');
        if (window.__pendingTab) {
            const pTab = window.__pendingTab;
            delete window.__pendingTab;
            switchTab(pTab);
        }
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
        updateProfileUI();
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
            opt.textContent = `${ptitle}`;
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
                <span class="pack-date-txt">${escapeHtml(pdate || pname)}</span>
            </div>
            <span class="pack-btn-open">Ochish</span>
        `;
        dom.userPacksList.appendChild(item);
    });
}

function renderProfilePacks() {
    if (!dom.profilePacksList) return;
    const packs = state.userPacks || [];

    if (dom.profilePacksCount) {
        dom.profilePacksCount.textContent = `${packs.length} ta`;
    }

    if (packs.length === 0) {
        const curLang = state.lang || 'uz';
        const dict = (typeof i18n !== 'undefined' && i18n[curLang]) ? i18n[curLang] : {};
        dom.profilePacksList.innerHTML = `
            <div class="packs-empty-state">
                <div class="empty-icon-wrap">
                    <svg viewBox="0 0 24 24" width="36" height="36" fill="none" stroke="#38bdf8" stroke-width="1.8">
                        <line x1="16.5" y1="9.4" x2="7.5" y2="4.21"></line>
                        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                        <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                        <line x1="12" y1="22.08" x2="12" y2="12"></line>
                    </svg>
                </div>
                <p class="empty-title">${dict.packs_empty_title || "Hali to'plamlar yo'q"}</p>
                <p class="empty-sub">${dict.packs_empty_desc || "Studiyaga o'ting va birinchi eksklyuziv emoji to'plamingizni yarating!"}</p>
                <button type="button" class="btn-goto-studio" id="btn-goto-studio-inline">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="13.5" cy="6.5" r=".5" fill="currentColor"></circle>
                        <circle cx="17.5" cy="10.5" r=".5" fill="currentColor"></circle>
                        <circle cx="8.5" cy="7.5" r=".5" fill="currentColor"></circle>
                        <circle cx="6.5" cy="12.5" r=".5" fill="currentColor"></circle>
                        <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.563-2.512 5.563-5.563C22 6.5 17.5 2 12 2z"></path>
                    </svg>
                    <span>${dict.btn_goto_studio || "Studiyaga o'tish"}</span>
                </button>
            </div>
        `;
        document.getElementById('btn-goto-studio-inline')?.addEventListener('click', () => {
            haptic('selection');
            switchMainView('studio');
        });
        return;
    }

    dom.profilePacksList.innerHTML = '';
    packs.forEach(pack => {
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
            haptic('light');
            if (tg) {
                e.preventDefault();
                tg.openTelegramLink(packLink);
            }
        };

        item.innerHTML = `
            <div class="pack-info-left">
                <span class="pack-name-txt">${escapeHtml(ptitle)}</span>
                <span class="pack-date-txt">${escapeHtml(pdate || pname)}</span>
            </div>
            <span class="pack-btn-open">${(typeof i18n !== "undefined" && i18n[state.lang]?.btn_open_pack) ? i18n[state.lang].btn_open_pack.replace("Telegramga ", "") : "Ochish"} ↗</span>
        `;
        dom.profilePacksList.appendChild(item);
    });
}

function updateProfileUI() {
    const user = state.user || window.Telegram?.WebApp?.initDataUnsafe?.user;
    const userId = user?.id || 1323217434;

    // 1. Full name & initials from Telegram
    let fullName = "Abdurahim Abdurahmonov";
    if (user?.first_name || user?.last_name) {
        fullName = [user.first_name, user.last_name].filter(Boolean).join(' ').trim();
    } else if (user?.username) {
        fullName = user.username;
    }

    let initials = "AA";
    if (user?.first_name && user?.last_name) {
        initials = (user.first_name[0] + user.last_name[0]).toUpperCase();
    } else if (user?.first_name) {
        initials = user.first_name.slice(0, 2).toUpperCase();
    }

    if (dom.profileFullName) dom.profileFullName.textContent = fullName;
    if (dom.profileUsername) dom.profileUsername.textContent = user?.username ? `@${user.username}` : "—";
    if (dom.profileIdBadge) dom.profileIdBadge.textContent = `ID: ${userId}`;

    if (dom.profileAvatar) {
        if (user?.photo_url) {
            dom.profileAvatar.innerHTML = `<img src="${user.photo_url}" alt="${escapeHtml(fullName)}">`;
        } else {
            dom.profileAvatar.innerHTML = `<span id="profile-initials">${escapeHtml(initials)}</span>`;
        }
    }

    // 2. Stars Balance & Dynamic Emoji Price
    const balance = state.userBalance ?? 0;
    if (dom.profileStarsCount) dom.profileStarsCount.textContent = balance;
    
    const emojiPrice = state.emojiPrice || 1;
    if (dom.profilePriceDisplay) dom.profilePriceDisplay.textContent = `${emojiPrice} ⭐ Stars`;

    // 3. Referral Link, Bonus & Stats
    const refLink = `https://t.me/${BOT_USERNAME}?start=ref_${userId}`;
    if (dom.profileRefLinkInput) dom.profileRefLinkInput.value = refLink;

    const refBonus = state.referralBonus || 1;
    if (dom.profileRefBonusText) dom.profileRefBonusText.textContent = `+${refBonus} ⭐ Stars`;
    if (dom.profileRefBadge) dom.profileRefBadge.textContent = `+${refBonus} ⭐ BONUS`;
    if (dom.profileRefDesc) dom.profileRefDesc.innerHTML = `Har bir yangi do'st uchun bepul <b id="profile-ref-bonus-text">+${refBonus} ⭐ Stars</b> oling!`;

    const refStats = state.referralStats || { count: 0, total_earned: 0 };
    if (dom.refStatCount) dom.refStatCount.textContent = `${refStats.count || 0} ta`;
    if (dom.refStatEarned) dom.refStatEarned.textContent = `+${refStats.total_earned || 0} ⭐`;

    // 4. Packs History
    renderProfilePacks();

    // 5. Render Lucide Icons
    if (window.lucide && window.lucide.createIcons) {
        window.lucide.createIcons();
    }
}

// ==================== MULTI-LANGUAGE (i18n) SYSTEM ====================
state.lang = localStorage.getItem('gn_lang') || 'uz';

const i18n = {
    "uz": {
        "guard_badge": "FAQAT TELEGRAM ILOVASI UCHUN",
        "guard_title": "Faqat Telegram orqali ochiladi",
        "guard_desc": "GnEmoji Studio mini ilovasi faqat rasmiy Telegram orqali xavfsiz foydalanish va maxsus emoji to'plamlarini avtomatik chiqarish uchun himoyalangan.",
        "guard_feat_1": "180+ Telegram Animatsiyali Emojilar",
        "guard_feat_2": "Matnli, Logo va 3D Metallik Uslublar",
        "guard_feat_3": "Rasmiy Telegram Stars & API orqali himoyalangan",
        "guard_btn_open": "Telegram Botda Ochish",
        "guard_copy": "© 2026 GN Studio • Barcha huquqlar himoyalangan",
        "loader_status": "Shablonlar yuklanmoqda...",
        "nav_studio": "Studiya",
        "nav_rating": "Reyting",
        "nav_profile": "Profil",
        "mode_text": "Matn",
        "mode_svg": "SVG Vektor",
        "label_name_input": "Ism yoki Matn kiriting",
        "ph_name_input": "Masalan: AZIZBEK",
        "font_selector_label": "Shrift turi:",
        "font_stapel_sub": "Geometrik",
        "font_inter_sub": "Klassik",
        "font_grobold_sub": "Zamonaviy",
        "font_montserrat_sub": "Hashamatli",
        "font_bebas_sub": "Tik & Kuchli",
        "font_rubik_sub": "Yumshoq",
        "font_poppins_sub": "Silliq",
        "font_impact_sub": "Katta & Qalin",
        "label_svg_file": "SVG Vektor Fayl (.svg)",
        "dropzone_main": "SVG faylni tanlang",
        "dropzone_sub": "Faqat .svg vektor fayli (PNG/JPG qabul qilinmaydi)",
        "svg_active_status": "✓ SVG faol va tayyor",
        "btn_change_svg": "Almashtirish",
        "label_svg_pack": "To'plam nomi (Link uchun nom)",
        "ph_svg_pack": "Masalan: my_cool_pack",
        "size_label": "O'lcham (Masshtab)",
        "color_customizer_title": "Ranglarni sozlash",
        "badge_outer": "Tashqi",
        "badge_inner": "Ichki",
        "badge_text": "Matn",
        "target_outer": "Tashqi chegara",
        "target_inner": "Ichki qism",
        "target_text": "Matn rangi",
        "btn_choose_color": "Tanlash",
        "btn_reset_color": "Qaytarish",
        "dest_label": "To'plam turi:",
        "dest_new": "Yangi to'plam",
        "dest_existing": "Mavjud to'plamga",
        "ph_select_existing": "Yuklanmoqda...",
        "live_preview_badge": "Jonli Prevyu",
        "preview_info_text": "Matn:",
        "preview_info_font": "Shrift:",
        "tab_name": "Ism",
        "tab_logo": "Logo",
        "tab_grey": "Grey",
        "tab_hq": "HQ",
        "tab_name_badge": "24 ta Ism Emoji",
        "tab_name_title": "Ism Emojilar",
        "tab_name_desc": "1-24 gacha maxsus animatsiyalardan birini yoki bir nechtasini tanlang",
        "ph_search_tickets": "Ism emoji qidirish (1-24)...",
        "btn_select_all": "Hammasini belgilash",
        "btn_deselect_all": "Tanlovni bekor qilish",
        "tab_logo_badge": "PREMIUM LOGO PACK",
        "tab_logo_title": "100 ta Logo Shablonlar To'plami",
        "tab_logo_desc": "Ismingiz uchun 14.tgs dan 117.tgs gacha barcha turli uslubdagi doiraviy va logo emojilarni 1 bosishda to'liq to'plam sifatida yarating!",
        "btn_create_fullpack_logo": "To'liq 100 ta Logoni Yaratish",
        "all_logos_title": "Barcha Logo Shablonlar",
        "all_logos_desc": "Kerakli logoni tanlang yoki bir nechtasini belgilab maxsus to'plam yarating",
        "ph_search_logos": "Logolardan qidirish...",
        "tab_grey_badge": "PREMIUM GREY PACK",
        "tab_grey_title": "65 ta Grey 3D Emoji Shablonlar",
        "tab_grey_desc": "Kumushrang, metallik va nozik 3D uslubdagi yangi shablonlar to'plami. Tanlangan yoki to'liq 65 ta emojini 1 bosishda yarating!",
        "btn_create_fullpack_grey": "To'liq 65 ta Grey Emojini Yaratish",
        "all_grey_title": "Barcha Grey Shablonlar",
        "all_grey_desc": "Kerakli shablonni tanlang yoki bir nechtasini belgilab maxsus to'plam yarating",
        "ph_search_grey": "Grey shablonlardan qidirish...",
        "tab_hq_badge": "HIGH QUALITY PACK",
        "tab_hq_title": "80 ta High Quality 3D Emoji Shablonlar",
        "tab_hq_desc": "Premium darajadagi eng so'nggi 3D harakatlanuvchi zamonaviy shablonlar to'plami. Barcha 80 ta emojini 1 bosishda to'liq yarating!",
        "btn_create_fullpack_hq": "To'liq 80 ta High Quality Emojini Yaratish",
        "all_hq_title": "Barcha High Quality Shablonlar",
        "all_hq_desc": "Kerakli shablonni tanlang yoki bir nechtasini belgilab maxsus to'plam yarating",
        "ph_search_hq": "HQ shablonlardan qidirish...",
        "btn_main_action": "Tanlangan Emojini Yaratish",
        "selected_count": "ta tanlandi",
        "btn_action_create": "Yaratish",
        "btn_action_add": "Qo'shish",
        "action_btn_multiple": "Tanlangan Emojilarni {action} ({count} ta • {price})",
        "action_btn_single": "Tanlangan #{num} Emojini {action} ({price})",
        "rating_badge": "PESHQADAMLAR",
        "rating_title": "Foydalanuvchilar Reytingi",
        "rating_subtitle": "Eng faol do'st taklif qilganlar va eng ko'p emoji yaratuvchilar",
        "rating_tab_ref": "Do'stlar taklifi",
        "rating_tab_creator": "Emoji ustalari",
        "my_rank_label": "Sizning o'rningiz:",
        "rank_badge_active": "Faol",
        "rank_place_1": "1-O'rin",
        "rank_place_2": "2-O'rin",
        "rank_place_3": "3-O'rin",
        "top_list_title": "Yetakchilar ro'yxati (4 - 20)",
        "no_other_users": "Hozircha boshqa ishtirokchilar yo'q",
        "unit_packs": "ta to'plam",
        "unit_refs": "ta do'st",
        "user_default_name": "Foydalanuvchi",
        "bonus_card_title": "Kunlik Bonus: +3 ⭐ Stars",
        "bonus_card_desc": "Har 24 soatda bepul Stars sovg'asini oling!",
        "btn_claim_now": "Olish (3 ⭐)",
        "bonus_ready": "Bonus tayyor! 3 Stars sovg'angizni oling!",
        "bonus_next_wait": "Keyingi bonusgacha:",
        "bonus_claimed": "+3 ⭐ Stars hisobingizga qo'shildi!",
        "balance_sub": "Joriy Stars Balansingiz",
        "btn_profile_topup": "To'ldirish",
        "price_note": "1 ta emoji yaratish narxi:",
        "ref_title": "Do'stlarni Taklif Qilish",
        "ref_desc_prefix": "Har bir yangi do'st uchun bepul",
        "btn_copy": "Nusxalash",
        "btn_share_ref": "Do'stlarga Ulashish",
        "stat_invited": "Taklif qilingan do'stlar",
        "stat_earned": "Jami ishlangan Stars",
        "history_title": "Yaratilgan To'plamlar Tarixi",
        "your_packs_title": "Sizning To'plamlaringiz",
        "packs_empty_title": "Hali yaratilgan to'plamlar yo'q",
        "packs_empty_desc": "Studiyaga o'ting va birinchi eksklyuziv emoji to'plamingizni yarating!",
        "btn_goto_studio": "Studiyaga o'tish",
        "official_channel": "➤ Rasmiy Kanalimiz",
        "channel_desc": "Yangiliklar, tanlovlar va promokodlar",
        "help_pricing": "Yordam & Narxlar",
        "help_desc": "Qanday ishlatish va barcha qoidalar",
        "lang_settings_title": "Muloqot tili (Language)",
        "modal_tpl_title": "Emoji Tafsiloti",
        "modal_text_label": "Matn:",
        "modal_font_label": "Shrift:",
        "modal_format_label": "Format:",
        "btn_generate_single": "Shu Emojini Yaratish",
        "btn_add_to_pack_modal": "Mavjud To'plamga Qo'shish",
        "progress_title": "Emoji Tayyorlanmoqda...",
        "progress_desc": "Iltimos, kuting, animatsiya render qilinmoqda",
        "success_title": "Muvaffaqiyatli Tayyorlandi!",
        "success_desc": "Sizning Premium animatsiyali emoji to'plamingiz Telegramda yaratildi.",
        "pack_link_label": "Emoji Pack Havolasi:",
        "btn_open_pack": "Telegramga Qo'shish",
        "btn_share_pack": "Do'stlarga Ulashish",
        "balance_modal_title": "Balansingiz yetarli emas!",
        "balance_modal_desc": "Tanlangan emojilarni yaratish uchun balansingizda yetarli Stars mavjud emas.",
        "calc_curr_bal": "Sizning balansingiz:",
        "calc_needed_bal": "Kerakli miqdor:",
        "calc_diff_bal": "Yetishmayotgan:",
        "btn_topup_wallet": "Stars Sotib Olish",
        "btn_referral_invite": "Do'stlarni taklif qilish (Bepul +1 ⭐)",
        "btn_back": "Orqaga",
        "pay_choice_title": "To'lov Usulini Tanlang",
        "pay_choice_desc": "Tanlangan emojilar uchun to'lovni tasdiqlang.",
        "pay_choice_total": "Jami narx:",
        "pay_choice_wallet_bal": "Hamyon balansingiz:",
        "pay_choice_stars_title": "Telegram Stars orqali to'lash",
        "pay_choice_stars_sub": "Botga to'g'ridan-to'g'ri XTR hisob yuborish",
        "pay_choice_wallet_title": "Hamyondan to'lash",
        "pay_choice_wallet_sub": "Mavjud Stars balansidan yechish",
        "btn_cancel": "Bekor qilish",
        "invoice_sent_title": "Hisob Botga Yuborildi!",
        "invoice_sent_desc": "Telegram chatiga @GnEmojiBot botiga to'lov hisob-fakturasi yuborildi. Chatga o'tib to'lovni tasdiqlang. To'lov qilingach, bot to'plamingizni avtomatik yaratib beradi!",
        "btn_goto_bot": "Telegram Botga O'tish",
        "footer_copyright": "Mualliflik Huquqi Himoyalangan",
        "footer_all_rights": "© 2026 GN Studio. Barcha huquqlar himoyalangan.",
        "footer_desc": "Maxsus Telegram Mini App litsenziyasi ostida taqdim etiladi. Sayt va kodlardan ruxsatsiz nusxa ko'chirish qat'iyan man etiladi.",
        "toast_enter_name": "Iltimos, ism yoki so'z kiriting!",
        "toast_upload_svg": "Iltimos, .svg vektor faylini yuklang!",
        "toast_choose_existing": "Iltimos, qo'shish uchun mavjud to'plamni tanlang!",
        "toast_sending_invoice": "Botga hisob yuborilmoqda...",
        "toast_no_packs_yet": "Sizda hali paketlar yo'q. Avval to'liq to'plam yarating!",
        "toast_copied_ref": "Taklif havolangiz nusxalandi! Do'stlaringizga yuboring",
        "toast_color_reset": "Tanlangan qism rangi standart holatga qaytarildi",
        "toast_stars_success": "Stars to'lovi qabul qilindi!",
        "toast_packs_refreshed": "To'plamlar yangilandi",
        "toast_svg_only": "Faqat .svg formatidagi vektor fayllar qabul qilinadi! (PNG, JPG qo'llab-quvvatlanmaydi)",
        "toast_svg_invalid": "Yaroqsiz SVG fayl! <svg> tegi topilmadi.",
        "toast_svg_loaded": "Vektor SVG muvaffaqiyatli yuklandi",
        "toast_svg_removed": "SVG olib tashlandi",
        "toast_error": "Xatolik yuz berdi. Qaytadan urinib ko'ring."
    },
    "ru": {
        "guard_badge": "ТОЛЬКО ДЛЯ ПРИЛОЖЕНИЯ TELEGRAM",
        "guard_title": "Открывается только через Telegram",
        "guard_desc": "Мини-приложение GnEmoji Studio защищено для безопасного использования и автоматического создания эмодзи-паков только через официальный Telegram.",
        "guard_feat_1": "180+ Анимированных эмодзи Telegram",
        "guard_feat_2": "Текстовые, логотипные и 3D стили",
        "guard_feat_3": "Защищено официальным Telegram Stars и API",
        "guard_btn_open": "Открыть в Telegram боте",
        "guard_copy": "© 2026 GN Studio • Все права защищены",
        "loader_status": "Загрузка шаблонов...",
        "nav_studio": "Студия",
        "nav_rating": "Рейтинг",
        "nav_profile": "Профиль",
        "mode_text": "Текст",
        "mode_svg": "Вектор SVG",
        "label_name_input": "Введите имя или текст",
        "ph_name_input": "Например: AZIZBEK",
        "font_selector_label": "Шрифт:",
        "font_stapel_sub": "Геометрический",
        "font_inter_sub": "Классический",
        "font_grobold_sub": "Современный",
        "font_montserrat_sub": "Премиальный",
        "font_bebas_sub": "Высокий & Дерзкий",
        "font_rubik_sub": "Мягкий & Округлый",
        "font_poppins_sub": "Гладкий",
        "font_impact_sub": "Массивный & Жирный",
        "label_svg_file": "SVG Векторный файл (.svg)",
        "dropzone_main": "Выберите SVG файл",
        "dropzone_sub": "Только векторные .svg файлы (PNG/JPG не принимаются)",
        "svg_active_status": "✓ SVG активен и готов",
        "btn_change_svg": "Заменить",
        "label_svg_pack": "Название пака (для ссылки)",
        "ph_svg_pack": "Например: my_cool_pack",
        "size_label": "Размер (Масштаб)",
        "color_customizer_title": "Настройка цветов",
        "badge_outer": "Внешний",
        "badge_inner": "Внутренний",
        "badge_text": "Текст",
        "target_outer": "Внешняя граница",
        "target_inner": "Внутренняя часть",
        "target_text": "Цвет текста",
        "btn_choose_color": "Выбрать",
        "btn_reset_color": "Сбросить",
        "dest_label": "Тип пака:",
        "dest_new": "Новый пак",
        "dest_existing": "В существующий",
        "ph_select_existing": "Загрузка...",
        "live_preview_badge": "Живое превью",
        "preview_info_text": "Текст:",
        "preview_info_font": "Шрифт:",
        "tab_name": "Имя",
        "tab_logo": "Logo",
        "tab_grey": "Grey",
        "tab_hq": "HQ",
        "tab_name_badge": "24 Именных эмодзи",
        "tab_name_title": "Именные эмодзи",
        "tab_name_desc": "Выберите из 1-24 именных анимаций",
        "ph_search_tickets": "Поиск именных эмодзи (1-24)...",
        "btn_select_all": "Выбрать все",
        "btn_deselect_all": "Снять выбор",
        "tab_logo_badge": "ПРЕМИУМ ЛОГО ПАК",
        "tab_logo_title": "Коллекция из 100 шаблонов логотипов",
        "tab_logo_desc": "Создайте полный пак из всех стилей от 14.tgs до 117.tgs в 1 клик для вашего имени!",
        "btn_create_fullpack_logo": "Создать полный пак (100 лого)",
        "all_logos_title": "Все шаблоны логотипов",
        "all_logos_desc": "Выберите нужные логотипы или отметьте несколько для своего пака",
        "ph_search_logos": "Поиск логотипов...",
        "tab_grey_badge": "ПРЕМИУМ СЕРЫЙ ПАК",
        "tab_grey_title": "65 Серых 3D шаблонов эмодзи",
        "tab_grey_desc": "Стильные серебристые, металлические и 3D эмодзи. Создайте пак из 65 эмодзи в 1 клик!",
        "btn_create_fullpack_grey": "Создать полный пак (65 Grey)",
        "all_grey_title": "Все серые шаблоны",
        "all_grey_desc": "Выберите нужные шаблоны или отметьте несколько для своего пака",
        "ph_search_grey": "Поиск шаблонов Grey...",
        "tab_hq_badge": "HIGH QUALITY ПАК",
        "tab_hq_title": "80 High Quality 3D шаблонов",
        "tab_hq_desc": "Коллекция новейших 3D анимированных эмодзи высшего качества. Создайте 80 эмодзи в 1 клик!",
        "btn_create_fullpack_hq": "Создать полный пак (80 HQ)",
        "all_hq_title": "Все шаблоны High Quality",
        "all_hq_desc": "Выберите шаблоны или отметьте несколько для своего пака",
        "ph_search_hq": "Поиск шаблонов HQ...",
        "btn_main_action": "Создать выбранные эмодзи",
        "selected_count": "выбрано",
        "btn_action_create": "Создать",
        "btn_action_add": "Добавить",
        "action_btn_multiple": "Выбранные эмодзи: {action} ({count} шт. • {price})",
        "action_btn_single": "Выбранный #{num} эмодзи: {action} ({price})",
        "rating_badge": "ЛИДЕРЫ",
        "rating_title": "Рейтинг пользователей",
        "rating_subtitle": "Самые активные по приглашениям друзей и созданию эмодзи",
        "rating_tab_ref": "Приглашения",
        "rating_tab_creator": "Мастера эмодзи",
        "my_rank_label": "Ваше место:",
        "rank_badge_active": "Активен",
        "rank_place_1": "1-е Место",
        "rank_place_2": "2-е Место",
        "rank_place_3": "3-е Место",
        "top_list_title": "Список лидеров (4 - 20)",
        "no_other_users": "Пока нет других участников",
        "unit_packs": "паков",
        "unit_refs": "чел",
        "user_default_name": "Пользователь",
        "bonus_card_title": "Ежедневный бонус: +3 ⭐ Stars",
        "bonus_card_desc": "Получайте бесплатные Stars каждые 24 часа!",
        "btn_claim_now": "Забрать (3 ⭐)",
        "bonus_ready": "Бонус готов! Заберите свои 3 Stars!",
        "bonus_next_wait": "До следующего бонуса:",
        "bonus_claimed": "+3 ⭐ Stars начислено на ваш баланс!",
        "balance_sub": "Текущий баланс Stars",
        "btn_profile_topup": "Пополнить",
        "price_note": "Стоимость создания 1 эмодзи:",
        "ref_title": "Пригласить друзей",
        "ref_desc_prefix": "За каждого нового друга бесплатно",
        "btn_copy": "Копировать",
        "btn_share_ref": "Поделиться",
        "stat_invited": "Приглашено друзей",
        "stat_earned": "Всего заработано Stars",
        "history_title": "История созданных паков",
        "your_packs_title": "Ваши паки",
        "packs_empty_title": "Пока нет созданных паков",
        "packs_empty_desc": "Перейдите в студию и создайте свой первый эксклюзивный пак эмодзи!",
        "btn_goto_studio": "В студию",
        "official_channel": "➤ Наш официальный канал",
        "channel_desc": "Новости, розыгрыши и промокоды",
        "help_pricing": "Помощь и цены",
        "help_desc": "Как использовать и все правила",
        "lang_settings_title": "Язык интерфейса (Language)",
        "modal_tpl_title": "Детали эмодзи",
        "modal_text_label": "Текст:",
        "modal_font_label": "Шрифт:",
        "modal_format_label": "Формат:",
        "btn_generate_single": "Создать этот эмодзи",
        "btn_add_to_pack_modal": "Добавить в существующий пак",
        "progress_title": "Создание эмодзи...",
        "progress_desc": "Пожалуйста, подождите, идет рендеринг анимации",
        "success_title": "Успешно создано!",
        "success_desc": "Ваш премиальный анимированный пак эмодзи создан в Telegram.",
        "pack_link_label": "Ссылка на пак эмодзи:",
        "btn_open_pack": "Добавить в Telegram",
        "btn_share_pack": "Поделиться паком",
        "balance_modal_title": "Недостаточно баланса!",
        "balance_modal_desc": "Для создания выбранных эмодзи на вашем балансе недостаточно Stars.",
        "calc_curr_bal": "Ваш баланс:",
        "calc_needed_bal": "Требуется:",
        "calc_diff_bal": "Не хватает:",
        "btn_topup_wallet": "Купить Stars",
        "btn_referral_invite": "Пригласить друзей (Бесплатно +1 ⭐)",
        "btn_back": "Назад",
        "pay_choice_title": "Выберите способ оплаты",
        "pay_choice_desc": "Подтвердите оплату выбранных эмодзи.",
        "pay_choice_total": "Итого:",
        "pay_choice_wallet_bal": "Баланс кошелька:",
        "pay_choice_stars_title": "Оплата через Telegram Stars",
        "pay_choice_stars_sub": "Отправить инвойс XTR напрямую в бота",
        "pay_choice_wallet_title": "Оплата с баланса",
        "pay_choice_wallet_sub": "Списать со счета в приложении",
        "btn_cancel": "Отмена",
        "invoice_sent_title": "Счет отправлен боту!",
        "invoice_sent_desc": "В чат с ботом @GnEmojiBot выставлен счет. Перейдите в чат и оплатите его. После оплаты пак будет создан автоматически!",
        "btn_goto_bot": "Перейти к боту",
        "footer_copyright": "Авторские права защищены",
        "footer_all_rights": "© 2026 GN Studio. Все права защищены.",
        "footer_desc": "Предоставляется по эксклюзивной лицензии Telegram Mini App. Несанкционированное копирование строго запрещено.",
        "toast_enter_name": "Пожалуйста, введите имя или текст!",
        "toast_upload_svg": "Пожалуйста, загрузите векторный .svg файл!",
        "toast_choose_existing": "Пожалуйста, выберите пак для добавления!",
        "toast_sending_invoice": "Отправка счета боту...",
        "toast_no_packs_yet": "У вас пока нет паков. Сначала создайте пак!",
        "toast_copied_ref": "Реферальная ссылка скопирована! Отправьте друзьям",
        "toast_color_reset": "Цвет сброшен на исходный",
        "toast_stars_success": "Оплата Stars принята!",
        "toast_packs_refreshed": "Паки обновлены",
        "toast_svg_only": "Принимаются только векторные файлы формата .svg! (PNG, JPG не поддерживаются)",
        "toast_svg_invalid": "Некорректный SVG! Тег <svg> не найден.",
        "toast_svg_loaded": "Векторный SVG успешно загружен",
        "toast_svg_removed": "SVG удален",
        "toast_error": "Произошла ошибка. Попробуйте снова."
    },
    "en": {
        "guard_badge": "TELEGRAM EXCLUSIVE APP",
        "guard_title": "Opens only via Telegram",
        "guard_desc": "GnEmoji Studio mini app is protected for secure usage and automatic custom emoji pack generation only through official Telegram.",
        "guard_feat_1": "180+ Telegram Animated Emojis",
        "guard_feat_2": "Text, Logo & 3D Metallic Styles",
        "guard_feat_3": "Protected via official Telegram Stars & API",
        "guard_btn_open": "Open in Telegram Bot",
        "guard_copy": "© 2026 GN Studio • All rights reserved",
        "loader_status": "Loading templates...",
        "nav_studio": "Studio",
        "nav_rating": "Rating",
        "nav_profile": "Profile",
        "mode_text": "Text",
        "mode_svg": "SVG Vector",
        "label_name_input": "Enter Name or Text",
        "ph_name_input": "Example: AZIZBEK",
        "font_selector_label": "Font style:",
        "font_stapel_sub": "Geometric",
        "font_inter_sub": "Classic",
        "font_grobold_sub": "Modern",
        "font_montserrat_sub": "Luxury",
        "font_bebas_sub": "Tall & Bold",
        "font_rubik_sub": "Soft & Rounded",
        "font_poppins_sub": "Smooth",
        "font_impact_sub": "Bold & Heavy",
        "label_svg_file": "SVG Vector File (.svg)",
        "dropzone_main": "Select SVG file",
        "dropzone_sub": "Only .svg vector files (PNG/JPG not accepted)",
        "svg_active_status": "✓ SVG active & ready",
        "btn_change_svg": "Replace",
        "label_svg_pack": "Pack name (for link)",
        "ph_svg_pack": "Example: my_cool_pack",
        "size_label": "Size (Scale)",
        "color_customizer_title": "Color Customizer",
        "badge_outer": "Outer",
        "badge_inner": "Inner",
        "badge_text": "Text",
        "target_outer": "Outer border",
        "target_inner": "Inner layer",
        "target_text": "Text color",
        "btn_choose_color": "Choose",
        "btn_reset_color": "Reset",
        "dest_label": "Destination:",
        "dest_new": "New pack",
        "dest_existing": "Add to existing",
        "ph_select_existing": "Loading...",
        "live_preview_badge": "Live Preview",
        "preview_info_text": "Text:",
        "preview_info_font": "Font:",
        "tab_name": "Name",
        "tab_logo": "Logo",
        "tab_grey": "Grey",
        "tab_hq": "HQ",
        "tab_name_badge": "24 Name Emojis",
        "tab_name_title": "Name Emojis",
        "tab_name_desc": "Choose from 1-24 special name animations",
        "ph_search_tickets": "Search name emojis (1-24)...",
        "btn_select_all": "Select all",
        "btn_deselect_all": "Deselect all",
        "tab_logo_badge": "PREMIUM LOGO PACK",
        "tab_logo_title": "100 Logo Templates Collection",
        "tab_logo_desc": "Generate all circular and logo styles from 14.tgs to 117.tgs in 1 click for your name!",
        "btn_create_fullpack_logo": "Create Full Pack (100 Logos)",
        "all_logos_title": "All Logo Templates",
        "all_logos_desc": "Select your desired logos or choose several to build a custom pack",
        "ph_search_logos": "Search logos...",
        "tab_grey_badge": "PREMIUM GREY PACK",
        "tab_grey_title": "65 Grey 3D Emoji Templates",
        "tab_grey_desc": "Sleek silver, metallic, and 3D styles. Generate all 65 emojis in 1 click!",
        "btn_create_fullpack_grey": "Create Full Pack (65 Grey)",
        "all_grey_title": "All Grey Templates",
        "all_grey_desc": "Select templates or choose multiple to create a custom pack",
        "ph_search_grey": "Search Grey templates...",
        "tab_hq_badge": "HIGH QUALITY PACK",
        "tab_hq_title": "80 High Quality 3D Templates",
        "tab_hq_desc": "Top-tier collection of animated 3D emojis. Generate all 80 emojis in 1 click!",
        "btn_create_fullpack_hq": "Create Full Pack (80 HQ)",
        "all_hq_title": "All High Quality Templates",
        "all_hq_desc": "Select templates or choose multiple to build a custom pack",
        "ph_search_hq": "Search HQ templates...",
        "btn_main_action": "Create Selected Emojis",
        "selected_count": "selected",
        "btn_action_create": "Create",
        "btn_action_add": "Add",
        "action_btn_multiple": "Selected Emojis: {action} ({count} • {price})",
        "action_btn_single": "Selected #{num} Emoji: {action} ({price})",
        "rating_badge": "LEADERBOARD",
        "rating_title": "User Leaderboard",
        "rating_subtitle": "Top referrers and most active emoji creators",
        "rating_tab_ref": "Referrals",
        "rating_tab_creator": "Emoji Creators",
        "my_rank_label": "Your Rank:",
        "rank_badge_active": "Active",
        "rank_place_1": "1st Place",
        "rank_place_2": "2nd Place",
        "rank_place_3": "3rd Place",
        "top_list_title": "Top Leaders (4 - 20)",
        "no_other_users": "No other participants yet",
        "unit_packs": "packs",
        "unit_refs": "friends",
        "user_default_name": "User",
        "bonus_card_title": "Daily Bonus: +3 ⭐ Stars",
        "bonus_card_desc": "Claim free Stars every 24 hours!",
        "btn_claim_now": "Claim (3 ⭐)",
        "bonus_ready": "Bonus ready! Claim your 3 Stars gift!",
        "bonus_next_wait": "Next bonus in:",
        "bonus_claimed": "+3 ⭐ Stars added to your balance!",
        "balance_sub": "Current Stars Balance",
        "btn_profile_topup": "Top Up",
        "price_note": "Cost to create 1 emoji:",
        "ref_title": "Invite Friends",
        "ref_desc_prefix": "Free for each invited friend",
        "btn_copy": "Copy",
        "btn_share_ref": "Share",
        "stat_invited": "Friends Invited",
        "stat_earned": "Total Stars Earned",
        "history_title": "Created Packs History",
        "your_packs_title": "Your Packs",
        "packs_empty_title": "No packs created yet",
        "packs_empty_desc": "Go to Studio and create your first exclusive emoji pack!",
        "btn_goto_studio": "Go to Studio",
        "official_channel": "➤ Official Channel",
        "channel_desc": "News, giveaways and promo codes",
        "help_pricing": "Help & Pricing",
        "help_desc": "How to use and all rules",
        "lang_settings_title": "Interface Language",
        "modal_tpl_title": "Emoji Details",
        "modal_text_label": "Text:",
        "modal_font_label": "Font:",
        "modal_format_label": "Format:",
        "btn_generate_single": "Create This Emoji",
        "btn_add_to_pack_modal": "Add to Existing Pack",
        "progress_title": "Preparing Emojis...",
        "progress_desc": "Please wait, animation is being rendered",
        "success_title": "Successfully Created!",
        "success_desc": "Your premium animated emoji pack has been created in Telegram.",
        "pack_link_label": "Emoji Pack Link:",
        "btn_open_pack": "Add to Telegram",
        "btn_share_pack": "Share Pack",
        "balance_modal_title": "Insufficient Balance!",
        "balance_modal_desc": "You don't have enough Stars to create the selected emojis.",
        "calc_curr_bal": "Your balance:",
        "calc_needed_bal": "Required:",
        "calc_diff_bal": "Missing:",
        "btn_topup_wallet": "Buy Stars",
        "btn_referral_invite": "Invite Friends (Free +1 ⭐)",
        "btn_back": "Back",
        "pay_choice_title": "Choose Payment Method",
        "pay_choice_desc": "Confirm payment for selected emojis.",
        "pay_choice_total": "Total price:",
        "pay_choice_wallet_bal": "Wallet balance:",
        "pay_choice_stars_title": "Pay with Telegram Stars",
        "pay_choice_stars_sub": "Send direct XTR invoice to bot",
        "pay_choice_wallet_title": "Pay from Wallet Balance",
        "pay_choice_wallet_sub": "Deduct from in-app Stars balance",
        "btn_cancel": "Cancel",
        "invoice_sent_title": "Invoice Sent to Bot!",
        "invoice_sent_desc": "An invoice was sent to @GnEmojiBot in Telegram. Open the chat and confirm payment. Your pack will be generated automatically upon payment!",
        "btn_goto_bot": "Go to Telegram Bot",
        "footer_copyright": "Copyright Protected",
        "footer_all_rights": "© 2026 GN Studio. All rights reserved.",
        "footer_desc": "Provided under exclusive Telegram Mini App license. Unauthorized copying is strictly prohibited.",
        "toast_enter_name": "Please enter a name or text!",
        "toast_upload_svg": "Please upload an .svg vector file!",
        "toast_choose_existing": "Please select an existing pack to add to!",
        "toast_sending_invoice": "Sending invoice to bot...",
        "toast_no_packs_yet": "You don't have any packs yet. Create a full pack first!",
        "toast_copied_ref": "Referral link copied! Share with friends",
        "toast_color_reset": "Color reset to default",
        "toast_stars_success": "Stars payment received!",
        "toast_packs_refreshed": "Packs refreshed",
        "toast_svg_only": "Only .svg vector files are accepted! (PNG, JPG not supported)",
        "toast_svg_invalid": "Invalid SVG! Tag <svg> not found.",
        "toast_svg_loaded": "Vector SVG successfully loaded",
        "toast_svg_removed": "SVG removed",
        "toast_error": "An error occurred. Please try again."
    }
};

function applyLanguage(lang) {
    if (!i18n[lang]) lang = 'uz';
    state.lang = lang;
    try { localStorage.setItem('gn_lang', lang); } catch (_) {}
    document.documentElement.lang = lang;

    // 1. Text elements with data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (i18n[lang] && i18n[lang][key]) {
            el.textContent = i18n[lang][key];
        }
    });

    // 2. Input and search placeholder elements with data-i18n-ph
    document.querySelectorAll('[data-i18n-ph]').forEach(el => {
        const key = el.getAttribute('data-i18n-ph');
        if (i18n[lang] && i18n[lang][key]) {
            el.setAttribute('placeholder', i18n[lang][key]);
        }
    });

    // 3. Language switcher buttons active state
    document.querySelectorAll('.lang-switch-btn').forEach(b => {
        if (b.dataset.lang === lang) {
            b.classList.add('active');
        } else {
            b.classList.remove('active');
        }
    });

    // 4. Update dynamic selection toolbar and action button immediately
    if (typeof updateSelectionStatus === 'function') {
        updateSelectionStatus();
    }

    // 5. Update Existing packs dropdown
    if (typeof renderExistingPacksDropdown === 'function') {
        renderExistingPacksDropdown();
    }

    // 6. Update Leaderboard if loaded
    if (state.lastLeaderboardData && typeof renderLeaderboardUI === 'function') {
        renderLeaderboardUI(state.lastLeaderboardData, state.ratingTab || 'ref');
    }

    // 7. Sync to backend database
    const uid = state.user?.id || 1323217434;
    apiFetch('set_language', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: uid, language: lang })
    }).catch(() => {});
}

// ==================== VIEW SWITCHER (3 TABS) ====================
function switchMainView(viewName) {
    haptic('selection');
    const vStudio = dom.viewStudio || document.getElementById('view-studio');
    const vRating = dom.viewRating || document.getElementById('view-rating');
    const vProfile = dom.viewProfile || document.getElementById('view-profile');
    const btnStudio = dom.navBtnStudio || document.getElementById('nav-btn-studio');
    const btnRating = dom.navBtnRating || document.getElementById('nav-btn-rating');
    const btnProfile = dom.navBtnProfile || document.getElementById('nav-btn-profile');

    if (viewName === 'rating') {
        vStudio?.classList.add('hidden');
        vProfile?.classList.add('hidden');
        vRating?.classList.remove('hidden');

        btnStudio?.classList.remove('active');
        btnProfile?.classList.remove('active');
        btnRating?.classList.add('active');

        dom.bottomActionBar?.classList.remove('visible');
        loadLeaderboard(state.ratingTab || 'referral');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (viewName === 'profile') {
        vStudio?.classList.add('hidden');
        vRating?.classList.add('hidden');
        vProfile?.classList.remove('hidden');

        btnStudio?.classList.remove('active');
        btnRating?.classList.remove('active');
        btnProfile?.classList.add('active');

        dom.bottomActionBar?.classList.remove('visible');
        updateProfileUI();
        checkDailyBonusStatus();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
        vRating?.classList.add('hidden');
        vProfile?.classList.add('hidden');
        vStudio?.classList.remove('hidden');

        btnRating?.classList.remove('active');
        btnProfile?.classList.remove('active');
        btnStudio?.classList.add('active');

        updateSelectionStatus();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    if (window.lucide && window.lucide.createIcons) {
        window.lucide.createIcons();
    }
}
window.switchMainView = switchMainView;

function switchRatingTab(tabType) {
    haptic('selection');
    state.ratingTab = tabType;
    const tabRef = dom.tabRatingReferral || document.getElementById('tab-rating-referral');
    const tabCreator = dom.tabRatingCreator || document.getElementById('tab-rating-creator');
    if (tabType === 'creator') {
        tabCreator?.classList.add('active');
        tabRef?.classList.remove('active');
    } else {
        tabRef?.classList.add('active');
        tabCreator?.classList.remove('active');
    }
    loadLeaderboard(tabType);
}
window.switchRatingTab = switchRatingTab;
window.applyLanguage = applyLanguage;

// ==================== LEADERBOARD (REYTING) ====================
state.ratingTab = 'referral';

async function loadLeaderboard(tabType = 'referral') {
    state.ratingTab = tabType;
    const uid = state.user?.id || 1323217434;
    try {
        const res = await apiFetch(`leaderboard?user_id=${uid}`);
        if (!res.ok) throw new Error("Leaderboard fetch error");
        const data = await res.json();
        renderLeaderboardUI(data, tabType);
    } catch (e) {
        console.warn("Leaderboard error:", e);
    }
}

function renderLeaderboardUI(data, tabType) {
    state.lastLeaderboardData = data;
    const curLang = state.lang || 'uz';
    const dict = (typeof i18n !== 'undefined' && i18n[curLang]) ? i18n[curLang] : {};

    const list = tabType === 'creator' ? (data.creators || []) : (data.referrals || []);
    const rankInfo = data.user_rank || {};
    const myRank = tabType === 'creator' ? rankInfo.creator_rank : rankInfo.referral_rank;
    const myScore = tabType === 'creator' ? rankInfo.total_packs : rankInfo.referral_count;
    const unit = tabType === 'creator' ? (dict.unit_packs || "ta to'plam") : (dict.unit_refs || "ta do'st");

    // My rank
    if (dom.myRankNum) dom.myRankNum.textContent = myRank > 0 ? `#${myRank}` : '#--';
    if (dom.myRankVal) dom.myRankVal.textContent = `${myScore || 0} ${unit}`;
    if (dom.myRankBadge) {
        if (myRank === 1) dom.myRankBadge.textContent = dict.rank_place_1 || "1-O'rin";
        else if (myRank === 2) dom.myRankBadge.textContent = dict.rank_place_2 || "2-O'rin";
        else if (myRank === 3) dom.myRankBadge.textContent = dict.rank_place_3 || "3-O'rin";
        else if (myRank > 0 && myRank <= 10) dom.myRankBadge.textContent = "TOP 10";
        else dom.myRankBadge.textContent = dict.rank_badge_active || "Faol";
    }

    // Top 3 Podium
    const p1 = list[0];
    const p2 = list[1];
    const p3 = list[2];

    const fillPodiumItem = (pNum, item) => {
        const nameEl = document.getElementById(`podium-name-${pNum}`);
        const scoreEl = document.getElementById(`podium-score-${pNum}`);
        const avatarEl = document.getElementById(`podium-avatar-${pNum}`);
        if (item) {
            const displayName = item.first_name || (item.username ? `@${item.username}` : `User ${item.user_id}`);
            if (nameEl) nameEl.textContent = displayName;
            const scoreVal = tabType === 'creator' ? item.total_packs : item.referral_count;
            if (scoreEl) scoreEl.textContent = `${scoreVal} ${unit}`;
            if (avatarEl) {
                const initials = (displayName[0] || `${pNum}`).toUpperCase();
                avatarEl.textContent = initials;
            }
        } else {
            if (nameEl) nameEl.textContent = "—";
            if (scoreEl) scoreEl.textContent = `0 ${unit}`;
            if (avatarEl) avatarEl.textContent = `${pNum}`;
        }
    };

    fillPodiumItem(1, p1);
    fillPodiumItem(2, p2);
    fillPodiumItem(3, p3);

    // 4 to 20 list
    if (dom.leaderboardList) {
        dom.leaderboardList.innerHTML = '';
        const rest = list.slice(3, 20);
        if (rest.length === 0) {
            dom.leaderboardList.innerHTML = `<div style="text-align:center;color:#64748b;font-size:13px;padding:16px;">${dict.no_other_users || "Hozircha boshqa ishtirokchilar yo'q"}</div>`;
        } else {
            rest.forEach((u, idx) => {
                const rankNum = idx + 4;
                const displayName = u.first_name || (u.username ? `@${u.username}` : `User ${u.user_id}`);
                const scoreVal = tabType === 'creator' ? u.total_packs : u.referral_count;
                const initials = (displayName[0] || `${rankNum}`).toUpperCase();

                const row = document.createElement('div');
                row.className = 'lb-row';
                row.innerHTML = `
                    <div class="lb-row-left">
                        <span class="lb-rank">#${rankNum}</span>
                        <div class="lb-avatar">${initials}</div>
                        <span class="lb-name">${displayName}</span>
                    </div>
                    <span class="lb-score">${scoreVal} ${unit}</span>
                `;
                dom.leaderboardList.appendChild(row);
            });
        }
    }
}

// ==================== DAILY BONUS (KUNLIK BONUS: +3 STARS) ====================
let bonusCooldownTimer = null;

async function checkDailyBonusStatus() {
    const uid = state.user?.id || 1323217434;
    try {
        const res = await apiFetch(`daily_bonus/status?user_id=${uid}`);
        if (!res.ok) return;
        const data = await res.json();
        updateDailyBonusUI(data);
    } catch (e) {
        console.warn("Daily bonus status error:", e);
    }
}

function updateDailyBonusUI(data) {
    if (bonusCooldownTimer) {
        clearInterval(bonusCooldownTimer);
        bonusCooldownTimer = null;
    }
    const btn = dom.btnClaimDailyBonus || document.getElementById('btn-claim-daily-bonus');
    const btnTxt = dom.claimBtnText || document.getElementById('claim-btn-text');
    const descTxt = dom.bonusDescText || document.getElementById('bonus-desc-text');
    if (!btn || !btnTxt) return;

    if (data.can_claim) {
        btn.disabled = false;
        btnTxt.textContent = i18n[state.lang]?.btn_claim_now || "Olish (3 ⭐)";
        if (descTxt) descTxt.textContent = i18n[state.lang]?.bonus_ready || "Bonus tayyor! 3 Stars sovg'angizni oling!";
    } else {
        btn.disabled = true;
        let remainingSec = data.remaining_seconds || 0;
        const updateTimer = () => {
            if (remainingSec <= 0) {
                checkDailyBonusStatus();
                return;
            }
            const hours = Math.floor(remainingSec / 3600);
            const mins = Math.floor((remainingSec % 3600) / 60);
            const secs = remainingSec % 60;
            btnTxt.textContent = `${hours}s ${mins}m ${secs}s`;
            if (descTxt) descTxt.textContent = `${i18n[state.lang]?.bonus_next_wait || "Keyingi bonusgacha:"} ${hours}s ${mins}m`;
            remainingSec--;
        };
        updateTimer();
        bonusCooldownTimer = setInterval(updateTimer, 1000);
    }
}

async function claimDailyBonus() {
    const uid = state.user?.id || 1323217434;
    const btn = dom.btnClaimDailyBonus || document.getElementById('btn-claim-daily-bonus');
    if (!btn || btn.disabled) return;
    btn.disabled = true;
    haptic('medium');

    try {
        const res = await apiFetch('daily_bonus/claim', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: uid })
        });
        const data = await res.json();
        if (data.success) {
            haptic('success');
            if (window.confetti) {
                window.confetti({ particleCount: 70, spread: 60, origin: { y: 0.7 } });
            }
            state.userBalance = data.new_balance;
            if (dom.userBalanceVal) dom.userBalanceVal.textContent = state.userBalance;
            const profBal = document.getElementById('profile-stars-count');
            if (profBal) profBal.textContent = state.userBalance;

            showToast(i18n[state.lang]?.bonus_claimed || "+3 ⭐ Stars hisobingizga qo'shildi!", "🎁");
            checkDailyBonusStatus();
        } else {
            showToast(data.message || "Xatolik yuz berdi", "⚠️");
            checkDailyBonusStatus();
        }
    } catch (e) {
        showToast("Internet aloqasi xatosi", "⚠️");
        btn.disabled = false;
    }
}
window.claimDailyBonus = claimDailyBonus;


function getPreviewCacheKey(file, scale, text = null) {
    const tplNum = parseInt(getTemplateNumber(file));
    const isHQ = tplNum >= 183 && tplNum <= 262;
    const isGrey = tplNum >= 118 && tplNum <= 182;
    const isLogo = (tplNum >= 14 && tplNum <= 117) || state.inputType === 'svg';
    if (state.inputType === 'svg') {
        const svgHash = (state.svgData || "").length + "_" + (state.svgData || "").slice(0, 30);
        const bColor = state.badgeColor || '#FFFFFF';
        const bgCol = state.badgeBgColor || '#000000';
        const tCol = state.textColor || '#FFFFFF';
        return `${file}_svg_${scale}_${svgHash}_${bColor}_${bgCol}_${tCol}`;
    }
    const txtToUse = text !== null ? text : state.text;
    const cleanTxt = (txtToUse && txtToUse.trim() && txtToUse.trim().toUpperCase() !== "SVG") ? txtToUse.trim().toUpperCase() : "ISMINGIZ";
    if (isGrey || isHQ) {
        const tCol = state.textColor || '#FFFFFF';
        return `${file}_${state.font}_${scale}_${cleanTxt}_${tCol}`;
    }
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
    const tplNum = parseInt(getTemplateNumber(templateFile));
    const isHQ = tplNum >= 183 && tplNum <= 262;
    const isGrey = tplNum >= 118 && tplNum <= 182;
    const isLogo = (tplNum >= 14 && tplNum <= 117) || isSvg;
    const cleanTxt = isSvg ? "" : ((text && text.trim() && text.trim().toUpperCase() !== "SVG") ? text.trim().toUpperCase() : "ISMINGIZ");
    const cacheKey = getPreviewCacheKey(templateFile, scale, text);
    
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
                badge_color: (isGrey || isHQ) ? null : (isLogo ? (state.badgeColor || null) : null),
                badge_bg_color: (isGrey || isHQ) ? null : (isLogo ? (state.badgeBgColor || null) : null),
                text_color: (isLogo || isGrey || isHQ) ? (state.textColor || null) : null
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
                if (isGrey || isHQ) {
                    fallbackData = applyBadgeColorToLottieJSON(fallbackData, null, null, state.textColor, true);
                } else if (isLogo) {
                    fallbackData = applyBadgeColorToLottieJSON(fallbackData, state.badgeColor, state.badgeBgColor, state.textColor, false);
                }
                return fallbackData;
            }
        }
        return null;
    }
}

async function fetchBatchPreviews(templateFiles, text, font, scale = 1.0) {
    const isSvg = state.inputType === 'svg';
    const cleanTxt = isSvg ? "" : ((text && text.trim() && text.trim().toUpperCase() !== "SVG") ? text.trim().toUpperCase() : "ISMINGIZ");
    const needed = [];
    const results = {};
    const isDefaultColors = (!state.badgeColor || state.badgeColor === '#FFFFFF') && 
                            (!state.badgeBgColor || state.badgeBgColor === '#000000') &&
                            (!state.textColor || state.textColor === '#FFFFFF');
    
    templateFiles.forEach(file => {
        const isLogo = parseInt(getTemplateNumber(file)) >= 14 || isSvg;
        const cacheKey = getPreviewCacheKey(file, scale, text);
        if (state.previewCache.has(cacheKey)) {
            results[file] = state.previewCache.get(cacheKey);
        } else if (isSvg && !state.svgData) {
            let preData = getPreRenderedTemplateData(file, font, scale);
            if (preData) {
                if (!isDefaultColors && isLogo) {
                    preData = applyBadgeColorToLottieJSON(preData, state.badgeColor, state.badgeBgColor, state.textColor, false);
                }
                state.previewCache.set(cacheKey, preData);
                results[file] = preData;
            } else {
                needed.push(file);
            }
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
                const cacheKey = getPreviewCacheKey(fname, scale, text);
                state.previewCache.set(cacheKey, lottieData);
                results[fname] = lottieData;
            });
        }
    } catch (e) {
        if (!isSvg) {
            needed.forEach(file => {
                let fallbackData = getPreRenderedTemplateData(file, font, scale);
                if (fallbackData) {
                    const isGrey = tplNum >= 118;
                    const isLogo = (tplNum >= 14 && !isGrey) || isSvg;
                    if (isGrey) {
                        fallbackData = applyBadgeColorToLottieJSON(fallbackData, null, null, state.textColor, true);
                    } else if (isLogo) {
                        fallbackData = applyBadgeColorToLottieJSON(fallbackData, state.badgeColor, state.badgeBgColor, state.textColor, false);
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
    try {
        dom.tabBtnName?.classList.toggle('active', tabKey === 'name');
        dom.tabBtnLogo?.classList.toggle('active', tabKey === 'logo');
        dom.tabBtnGrey?.classList.toggle('active', tabKey === 'grey');
        dom.tabBtnHQ?.classList.toggle('active', tabKey === 'hq');
        
        dom.tabContentName?.classList.toggle('active', tabKey === 'name');
        dom.tabContentLogo?.classList.toggle('active', tabKey === 'logo');
        dom.tabContentGrey?.classList.toggle('active', tabKey === 'grey');
        dom.tabContentHQ?.classList.toggle('active', tabKey === 'hq');
    } catch (err) {
        console.warn("switchTab class toggle error:", err);
    }
    
    try {
        if (tabKey === 'name') {
            if (state.inputType !== 'svg') {
                state.selectedTemplate = Array.from(state.selectedTickets)[0] || "1.tgs";
            }
            renderTicketsGrid(dom.templateSearch?.value || '');
        } else if (tabKey === 'logo') {
            state.selectedTemplate = Array.from(state.selectedLogos)[0] || "14.tgs";
            renderLogosGrid(dom.logoSearch?.value || '');
        } else if (tabKey === 'grey') {
            state.selectedTemplate = Array.from(state.selectedGrey)[0] || "118.tgs";
            state.activeColorTarget = 'text';
            renderGreyGrid(dom.greySearch?.value || '');
        } else if (tabKey === 'hq') {
            state.selectedTemplate = Array.from(state.selectedHQ)[0] || "183.tgs";
            state.activeColorTarget = 'text';
            renderHQGrid(dom.hqSearch?.value || '');
        }
    } catch (err) {
        console.warn("switchTab grid render error:", err);
    }

    try {
        syncColorControlsUI();
        updateLivePreview();
        updateSelectionStatus();
    } catch (err) {
        console.warn("switchTab UI update error:", err);
    }
}
window.switchTab = switchTab;
window.__realSwitchTab = switchTab;

const debouncedFullUpdate = debounce(() => {
    if (state.activeTab === 'name') {
        renderTicketsGrid(dom.templateSearch?.value || '');
    } else if (state.activeTab === 'logo') {
        renderLogosGrid(dom.logoSearch?.value || '');
    } else if (state.activeTab === 'grey') {
        renderGreyGrid(dom.greySearch?.value || '');
    } else if (state.activeTab === 'hq') {
        renderHQGrid(dom.hqSearch?.value || '');
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
            Object.values(state.logoPlayers).forEach(p => {
                try { p.destroy(); } catch (e) {}
            });
            if (state.activeTab === 'name') {
                switchTab('logo');
                if (!state.selectedTemplate || parseInt(getTemplateNumber(state.selectedTemplate)) <= 13) {
                    state.selectedTemplate = Array.from(state.selectedLogos)[0] || "14.tgs";
                }
            } else if (state.activeTab === 'hq') {
                if (!state.selectedTemplate || parseInt(getTemplateNumber(state.selectedTemplate)) < 183) {
                    state.selectedTemplate = Array.from(state.selectedHQ)[0] || "183.tgs";
                }
            }
            updateSvgThumbnail();
            showToast(`✅ Vektor SVG yuklandi: ${name}`, "🎨", 2500);
            haptic('success');
            updateLivePreview();
            renderLogosGrid(dom.logoSearch?.value || '');
            renderGreyGrid(dom.greySearch?.value || '');
            renderHQGrid(dom.hqSearch?.value || '');
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
    } else if (num >= 263 && num <= 274) {
        const found = TICKET_TEMPLATES.find(t => parseInt(t.id) === num);
        const dNum = found ? found.displayNum : (num < 266 ? num - 263 + 14 : num - 264 + 14);
        tag = `Ticket #${dNum}`;
    } else if (num >= 183 && num <= 262) {
        tag = `High Quality #${num - 182}`;
    } else if (num >= 118 && num <= 182) {
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
        const fontNames = { 
            stapel: 'Stapel', 
            inter: 'Inter', 
            grobold: 'Grobold',
            montserrat: 'Montserrat',
            bebas: 'Bebas',
            rubik: 'Rubik',
            poppins: 'Poppins',
            impact: 'Impact'
        };
        if (dom.previewFontDisplay) dom.previewFontDisplay.textContent = `${fontNames[state.font] || 'Stapel'} (${Math.round(state.scale * 100)}%)`;
    }
    
    const cleanTxt = (state.inputType === 'svg') ? "" : ((state.text && state.text.trim()) ? state.text.trim().toUpperCase() : "ISMINGIZ");
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
    else if (state.activeTab === 'hq') activeSet = state.selectedHQ;
    
    const totalSelected = state.selectedTickets.size + state.selectedLogos.size + state.selectedGrey.size + state.selectedHQ.size;
    const curLang = state.lang || 'uz';
    const dict = (typeof i18n !== 'undefined' && i18n[curLang]) ? i18n[curLang] : {};

    // Ticket tab toolbar
    if (dom.ticketSelectionCount) {
        dom.ticketSelectionCount.textContent = `${state.selectedTickets.size} ${dict.selected_count || "ta tanlandi"}`;
    }
    if (dom.txtSelectAllTickets) {
        if (state.selectedTickets.size === TICKET_TEMPLATES.length && TICKET_TEMPLATES.length > 0) {
            dom.txtSelectAllTickets.textContent = dict.btn_deselect_all || "Tanlovni bekor qilish";
            dom.btnSelectAllTickets?.classList.add('active-all');
        } else {
            dom.txtSelectAllTickets.textContent = dict.btn_select_all || "Hammasini belgilash";
            dom.btnSelectAllTickets?.classList.remove('active-all');
        }
    }
    
    // Logo tab toolbar
    if (dom.logoSelectionCount) {
        dom.logoSelectionCount.textContent = `${state.selectedLogos.size} ${dict.selected_count || "ta tanlandi"}`;
    }
    if (dom.txtSelectAllLogos) {
        if (state.selectedLogos.size === LOGO_TEMPLATES.length && LOGO_TEMPLATES.length > 0) {
            dom.txtSelectAllLogos.textContent = dict.btn_deselect_all || "Tanlovni bekor qilish";
            dom.btnSelectAllLogos?.classList.add('active-all');
        } else {
            dom.txtSelectAllLogos.textContent = dict.btn_select_all || "Hammasini belgilash";
            dom.btnSelectAllLogos?.classList.remove('active-all');
        }
    }

    // Grey tab toolbar
    if (dom.greySelectionCount) {
        dom.greySelectionCount.textContent = `${state.selectedGrey.size} ${dict.selected_count || "ta tanlandi"}`;
    }
    if (dom.txtSelectAllGrey) {
        if (state.selectedGrey.size === GREY_TEMPLATES.length && GREY_TEMPLATES.length > 0) {
            dom.txtSelectAllGrey.textContent = dict.btn_deselect_all || "Tanlovni bekor qilish";
            dom.btnSelectAllGrey?.classList.add('active-all');
        } else {
            dom.txtSelectAllGrey.textContent = dict.btn_select_all || "Hammasini belgilash";
            dom.btnSelectAllGrey?.classList.remove('active-all');
        }
    }

    // High Quality tab toolbar
    if (dom.hqSelectionCount) {
        dom.hqSelectionCount.textContent = `${state.selectedHQ.size} ${dict.selected_count || "ta tanlandi"}`;
    }
    if (dom.txtSelectAllHQ) {
        if (state.selectedHQ.size === HQ_TEMPLATES.length && HQ_TEMPLATES.length > 0) {
            dom.txtSelectAllHQ.textContent = dict.btn_deselect_all || "Tanlovni bekor qilish";
            dom.btnSelectAllHQ?.classList.add('active-all');
        } else {
            dom.txtSelectAllHQ.textContent = dict.btn_select_all || "Hammasini belgilash";
            dom.btnSelectAllHQ?.classList.remove('active-all');
        }
    }
    
    // Price & Label Calculation
    const count = totalSelected > 0 ? totalSelected : 1;
    const unitPrice = state.emojiPrice || 6;
    const totalCost = count * unitPrice;
    state.lastNeededBal = totalCost;
    const priceBadge = `<span class="btn-stars-badge">${totalCost} <img src="images/image.png" class="btn-star-icon" alt="Stars"></span>`;
    
    const isExisting = state.destinationMode === 'existing';
    const actionVerb = isExisting ? (dict.btn_action_add || "Qo'shish") : (dict.btn_action_create || "Yaratish");
    
    // Bottom Action Button Text
    if (dom.mainBtnText) {
        if (totalSelected > 1) {
            const tmpl = dict.action_btn_multiple || "Tanlangan Emojilarni {action} ({count} ta • {price})";
            dom.mainBtnText.innerHTML = tmpl.replace('{action}', actionVerb).replace('{count}', totalSelected).replace('{price}', priceBadge);
        } else if (totalSelected === 1) {
            const allSel = [...state.selectedTickets, ...state.selectedLogos, ...state.selectedGrey, ...state.selectedHQ];
            const singleFile = allSel[0];
            const num = getTemplateNumber(singleFile);
            const tmpl = dict.action_btn_single || "Tanlangan #{num} Emojini {action} ({price})";
            dom.mainBtnText.innerHTML = tmpl.replace('{num}', num).replace('{action}', actionVerb).replace('{price}', priceBadge);
        } else {
            const num = getTemplateNumber(state.selectedTemplate);
            const tmpl = dict.action_btn_single || "Tanlangan #{num} Emojini {action} ({price})";
            dom.mainBtnText.innerHTML = tmpl.replace('{num}', num).replace('{action}', actionVerb).replace('{price}', priceBadge);
        }
    }

    // Floating action bar visibility
    const bar = dom.bottomActionBar || document.getElementById('bottom-action-bar');
    if (bar) {
        if (totalSelected > 0 && dom.viewStudio && !dom.viewStudio.classList.contains('hidden')) {
            bar.classList.add('visible');
        } else {
            bar.classList.remove('visible');
        }
    }
}

// Dynamically update or revert a single card's preview
async function updateCardPreview(file, tabKey, isSelected) {
    if (!file) return;
    const num = getTemplateNumber(file);
    let container = null;
    let playersMap = null;
    if (tabKey === 'name') {
        container = document.getElementById(`thumb-ticket-${num}`);
        playersMap = state.ticketPlayers;
    } else if (tabKey === 'logo') {
        container = document.getElementById(`thumb-logo-${num}`);
        playersMap = state.logoPlayers;
    } else if (tabKey === 'grey') {
        container = document.getElementById(`thumb-grey-${num}`);
        playersMap = state.greyPlayers;
    } else if (tabKey === 'hq') {
        container = document.getElementById(`thumb-hq-${num}`);
        playersMap = state.hqPlayers;
    }
    if (!container) return;

    // Selected cards get user text/svg; unselected cards revert to clean template sample!
    const txt = isSelected ? (state.inputType === 'svg' ? "" : state.text) : "";
    let data = null;
    if (!isSelected && state.inputType !== 'svg') {
        data = getPreRenderedTemplateData(file, state.font, state.scale);
    }
    if (!data) {
        data = await fetchLottiePreview(file, txt, state.font, state.scale);
    }
    if (data && container) {
        if (playersMap && playersMap[file]) {
            try { playersMap[file].destroy(); } catch (e) {}
            delete playersMap[file];
        }
        container.innerHTML = '';
        const player = safeLoadLottieAnimation({
            container: container,
            renderer: 'svg',
            loop: true,
            autoplay: true,
            animationData: data
        });
        if (player && playersMap) {
            playersMap[file] = player;
        }
    }
}

// Update all currently selected cards in active tab
function updateSelectedCardsPreview() {
    let activeSet = state.selectedTickets;
    let tabKey = 'name';
    if (state.activeTab === 'logo') {
        activeSet = state.selectedLogos;
        tabKey = 'logo';
    } else if (state.activeTab === 'grey') {
        activeSet = state.selectedGrey;
        tabKey = 'grey';
    } else if (state.activeTab === 'hq') {
        activeSet = state.selectedHQ;
        tabKey = 'hq';
    }
    
    if (!activeSet || activeSet.size === 0) return;
    activeSet.forEach(file => {
        updateCardPreview(file, tabKey, true);
    });
}

// Render the 24 Ism Emojis in Name Tab
async function renderTicketsGrid(filterText = '') {
    Object.values(state.ticketPlayers).forEach(p => {
        try { p.destroy(); } catch (e) {}
    });
    state.ticketPlayers = {};
    if (!dom.templatesGrid) return;
    dom.templatesGrid.innerHTML = '';
    
    let filtered = TICKET_TEMPLATES;
    if (filterText && filterText.trim()) {
        const query = filterText.trim().toLowerCase();
        filtered = TICKET_TEMPLATES.filter(t => 
            t.name.toLowerCase().includes(query) || 
            t.file.toLowerCase().includes(query) ||
            t.id.includes(query) ||
            `${t.displayNum}` === query ||
            `#${t.displayNum}` === query ||
            `ticket #${t.displayNum}`.toLowerCase().includes(query) ||
            `ism #${t.displayNum}`.toLowerCase().includes(query)
        );
    }
    
    if (filtered.length === 0) {
        dom.templatesGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-dim);">
                Ism shabloni topilmadi 🔍
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
            <span class="tpl-badge">#${tpl.displayNum}</span>
            <div class="tpl-check-badge">✓</div>
            <div class="tpl-lottie-thumb" id="thumb-ticket-${num}">
                <div class="thumb-loader"></div>
            </div>
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
    
    const selectedFiles = filtered.filter(t => state.selectedTickets.has(t.file)).map(t => t.file);
    const unselectedFiles = filtered.filter(t => !state.selectedTickets.has(t.file)).map(t => t.file);
    
    let batchDataSelected = {};
    if (selectedFiles.length > 0 && state.text) {
        batchDataSelected = await fetchBatchPreviews(selectedFiles, state.text, state.font, state.scale);
    }
    const batchDataUnselected = await fetchBatchPreviews(unselectedFiles, "", state.font, state.scale);
    
    filtered.forEach(tpl => {
        const file = tpl.file;
        const num = tpl.id;
        const container = document.getElementById(`thumb-ticket-${num}`);
        const isSel = state.selectedTickets.has(file);
        const data = isSel 
            ? (batchDataSelected[file] || (state.inputType === 'svg' ? null : getPreRenderedTemplateData(file, state.font, state.scale)))
            : (batchDataUnselected[file] || (state.inputType === 'svg' ? null : getPreRenderedTemplateData(file, state.font, state.scale)));
        
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

window.__onTemplatesReady = function() {
    if (state.activeTab === 'name') {
        renderTicketsGrid(dom.templateSearch?.value || '');
    } else if (state.activeTab === 'logo') {
        renderLogosGrid(dom.logoSearch?.value || '');
    } else if (state.activeTab === 'grey') {
        renderGreyGrid(dom.greySearch?.value || '');
    } else if (state.activeTab === 'hq') {
        renderHQGrid(dom.hqSearch?.value || '');
    }
    updateLivePreview();
};

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
            <div class="tpl-lottie-thumb" id="thumb-logo-${num}">
                <div class="thumb-loader"></div>
            </div>
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
    const selBatch = initialBatch.filter(f => state.selectedLogos.has(f));
    const unselBatch = initialBatch.filter(f => !state.selectedLogos.has(f));
    
    let batchSel = {};
    if (selBatch.length > 0 && (state.text || state.svgData)) {
        batchSel = await fetchBatchPreviews(selBatch, (state.inputType === 'svg' ? "" : state.text), state.font, state.scale);
    }
    const batchUnsel = await fetchBatchPreviews(unselBatch, "", state.font, state.scale);
    
    initialBatch.forEach(file => {
        const num = getTemplateNumber(file);
        const container = document.getElementById(`thumb-logo-${num}`);
        const isSel = state.selectedLogos.has(file);
        const lottieData = isSel ? (batchSel[file] || getPreRenderedTemplateData(file, state.font, state.scale))
                                 : (batchUnsel[file] || getPreRenderedTemplateData(file, state.font, state.scale));
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
                        const isSel = state.selectedLogos.has(file);
                        const txtToUse = isSel ? (state.inputType === 'svg' ? "" : state.text) : "";
                        const data = await fetchLottiePreview(file, txtToUse, state.font, state.scale);
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
    const selBatch = initialBatch.filter(f => state.selectedGrey.has(f));
    const unselBatch = initialBatch.filter(f => !state.selectedGrey.has(f));

    let batchSel = {};
    if (selBatch.length > 0 && state.text) {
        batchSel = await fetchBatchPreviews(selBatch, state.text, state.font, state.scale);
    }
    const batchUnsel = await fetchBatchPreviews(unselBatch, "", state.font, state.scale);

    try {
        initialBatch.forEach(file => {
            const num = getTemplateNumber(file);
            const container = document.getElementById(`thumb-grey-${num}`);
            const isSel = state.selectedGrey.has(file);
            const data = isSel ? batchSel[file] : batchUnsel[file];
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
                            const isSel = state.selectedGrey.has(file);
                            const data = await fetchLottiePreview(file, isSel ? state.text : "", state.font, state.scale);
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

// Render the 80 High Quality 3D Emojis in HQ Tab (183.tgs to 262.tgs)
async function renderHQGrid(filterText = '') {
    Object.values(state.hqPlayers).forEach(p => {
        try { p.destroy(); } catch (e) {}
    });
    state.hqPlayers = {};
    if (!dom.hqGrid) return;
    dom.hqGrid.innerHTML = '';
    
    let filtered = HQ_TEMPLATES;
    if (filterText && filterText.trim()) {
        const query = filterText.trim().toLowerCase();
        filtered = HQ_TEMPLATES.filter(t => 
            t.name.toLowerCase().includes(query) || 
            t.file.toLowerCase().includes(query) ||
            t.id.includes(query) ||
            `hq #${parseInt(t.id) - 182}`.toLowerCase().includes(query) ||
            `high quality #${parseInt(t.id) - 182}`.toLowerCase().includes(query) ||
            `${parseInt(t.id) - 182}` === query
        );
    }
    
    if (filtered.length === 0) {
        dom.hqGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-dim);">
                High Quality emoji shabloni topilmadi 🔍
            </div>
        `;
        return;
    }
    
    filtered.forEach((tpl) => {
        const num = tpl.id;
        const displayIdx = parseInt(num) - 182;
        const isSelected = state.selectedHQ.has(tpl.file);
        const card = document.createElement('div');
        card.className = `tpl-card ${isSelected ? 'selected' : ''}`;
        card.dataset.file = tpl.file;
        
        card.innerHTML = `
            <span class="tpl-badge" style="background: rgba(44, 219, 158, 0.18); border-color: rgba(44, 219, 158, 0.4); color: #2cdb9e;">#${displayIdx}</span>
            <div class="tpl-check-badge">✓</div>
            <div class="tpl-lottie-thumb" id="thumb-hq-${num}">
                <div class="thumb-loader"></div>
            </div>
            <div class="tpl-meta">
                <div class="tpl-title">High Quality #${displayIdx}</div>
                <div class="tpl-tag-label">${tpl.tag}</div>
            </div>
        `;
        
        card.addEventListener('click', () => {
            haptic('selection');
            toggleCardSelection(tpl.file, 'hq');
        });
        
        dom.hqGrid.appendChild(card);
    });
    
    // Load first 12 HQ emojis immediately via batch preview
    const initialBatch = filtered.slice(0, 12).map(t => t.file);
    const selBatch = initialBatch.filter(f => state.selectedHQ.has(f));
    const unselBatch = initialBatch.filter(f => !state.selectedHQ.has(f));

    let batchSel = {};
    if (selBatch.length > 0 && state.text) {
        batchSel = await fetchBatchPreviews(selBatch, state.text, state.font, state.scale);
    }
    const batchUnsel = await fetchBatchPreviews(unselBatch, "", state.font, state.scale);

    try {
        initialBatch.forEach(file => {
            const num = getTemplateNumber(file);
            const container = document.getElementById(`thumb-hq-${num}`);
            const isSel = state.selectedHQ.has(file);
            const data = isSel ? batchSel[file] : batchUnsel[file];
            if (container && data && !state.hqPlayers[file]) {
                container.innerHTML = '';
                const player = safeLoadLottieAnimation({
                    container: container,
                    renderer: 'svg',
                    loop: true,
                    autoplay: true,
                    animationData: data
                });
                if (player) state.hqPlayers[file] = player;
            }
        });
    } catch (e) {
        console.warn("Initial HQ batch error:", e);
    }
    
    // Lazy load remaining HQ emojis on scroll
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(async entry => {
                if (entry.isIntersecting) {
                    const card = entry.target;
                    const file = card.dataset.file;
                    const num = getTemplateNumber(file);
                    const container = document.getElementById(`thumb-hq-${num}`);
                    
                    if (container && !state.hqPlayers[file]) {
                        try {
                            const isSel = state.selectedHQ.has(file);
                            const data = await fetchLottiePreview(file, isSel ? state.text : "", state.font, state.scale);
                            if (data && container && !state.hqPlayers[file]) {
                                container.innerHTML = '';
                                const player = safeLoadLottieAnimation({
                                    container: container,
                                    renderer: 'svg',
                                    loop: true,
                                    autoplay: true,
                                    animationData: data
                                });
                                if (player) state.hqPlayers[file] = player;
                            }
                        } catch (err) {
                            console.warn("Lazy load thumb error:", file, err);
                        }
                    }
                    observer.unobserve(card);
                }
            });
        }, { rootMargin: '250px' });
        
        dom.hqGrid.querySelectorAll('.tpl-card').forEach((card) => {
            const file = card.dataset.file;
            if (!state.hqPlayers[file]) {
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
    } else if (tabKey === 'hq') {
        targetSet = state.selectedHQ;
        container = dom.hqGrid;
    }
    
    const isNowSelected = !targetSet.has(filename);
    if (isNowSelected) {
        targetSet.add(filename);
    } else {
        targetSet.delete(filename);
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
    
    // Update preview for this specific card
    updateCardPreview(filename, tabKey, isNowSelected);
    
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
    } else if (tabKey === 'hq') {
        targetSet = state.selectedHQ;
        allList = HQ_TEMPLATES;
        container = dom.hqGrid;
    }
    
    const selectAll = targetSet.size !== allList.length;
    if (!selectAll) {
        // Deselect all
        targetSet.clear();
        container?.querySelectorAll('.tpl-card').forEach(card => {
            card.classList.remove('selected');
            updateCardPreview(card.dataset.file, tabKey, false);
        });
    } else {
        // Select all
        allList.forEach(t => targetSet.add(t.file));
        state.selectedTemplate = allList[0].file;
        updateLivePreview();
        container?.querySelectorAll('.tpl-card').forEach(card => {
            card.classList.add('selected');
            updateCardPreview(card.dataset.file, tabKey, true);
        });
    }
    
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
    
    const fontNames = { 
        stapel: 'Stapel', 
        inter: 'Inter', 
        grobold: 'Grobold',
        montserrat: 'Montserrat',
        bebas: 'Bebas',
        rubik: 'Rubik',
        poppins: 'Poppins',
        impact: 'Impact'
    };
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
    } else if (mode === 'all_hq') {
        selectedFiles = HQ_TEMPLATES.map(t => t.file);
    } else {
        const allSelected = [...state.selectedTickets, ...state.selectedLogos, ...state.selectedGrey, ...state.selectedHQ];
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
        showProgressModal("Mega Logo Pack Tayyorlanmoqda...", "Barcha 100 ta logo shablon qayta ishlanmoqda...", 10);
    } else if (rawMode === 'all_grey') {
        showProgressModal("Grey 3D Pack Tayyorlanmoqda...", "Barcha 65 ta grey shablon qayta ishlanmoqda...", 10);
    } else if (rawMode === 'all_hq') {
        showProgressModal("High Quality Pack Tayyorlanmoqda...", "Barcha 80 ta High Quality shablon qayta ishlanmoqda...", 10);
    } else if (mode === "single") {
        const num = parseInt(getTemplateNumber(selectedFiles[0]));
        let tag = `Logo #${num}`;
        if (num <= 13) {
            tag = `Ticket #${num}`;
        } else if (num >= 263 && num <= 274) {
            const found = TICKET_TEMPLATES.find(t => parseInt(t.id) === num);
            const dNum = found ? found.displayNum : (num < 266 ? num - 263 + 14 : num - 264 + 14);
            tag = `Ticket #${dNum}`;
        } else if (num >= 183 && num <= 262) {
            tag = `High Quality #${num - 182}`;
        } else if (num >= 118 && num <= 182) {
            tag = `Grey #${num - 117}`;
        }
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
            badge_color: state.badgeColor || null,
            badge_bg_color: state.badgeBgColor || null,
            text_color: state.textColor || null,
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
    
    // Fast real-time live preview update (Hero preview + selected cards only)
    const debouncedLiveTextUpdate = debounce(() => {
        updateLivePreview();
        updateSelectedCardsPreview();
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

    // Quick tap on size percentage badge to reset back to 100%
    dom.sizeValDisplay?.addEventListener('click', () => {
        if (dom.sizeSlider) {
            dom.sizeSlider.value = "1.0";
            state.scale = 1.0;
            dom.sizeValDisplay.textContent = "100%";
            state.previewCache.clear();
            haptic('light');
            updateLivePreview();
            debouncedFullUpdate();
        }
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
            const tplNum = parseInt(getTemplateNumber(state.selectedTemplate));
            const isGrey = tplNum >= 118 && tplNum < 183;
            const isHQ = tplNum >= 183;
            const isLogo = (tplNum >= 14 && tplNum < 118) || state.inputType === 'svg';
            if ((isLogo || isGrey || isHQ) && state.livePlayer && dom.liveLottiePlayer) {
                const currentData = state.currentHeroTemplateData || getPreRenderedTemplateData(state.selectedTemplate, state.font, state.scale);
                if (currentData) {
                    const recolored = applyBadgeColorToLottieJSON(currentData, (isGrey || isHQ) ? null : state.badgeColor, (isGrey || isHQ) ? null : state.badgeBgColor, state.textColor, isGrey);
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
        const tplNum = parseInt(getTemplateNumber(state.selectedTemplate));
        const isGrey = tplNum >= 118 && tplNum < 183;
        const isHQ = tplNum >= 183;
        const isLogo = (tplNum >= 14 && tplNum < 118) || state.inputType === 'svg';
        if ((isLogo || isGrey || isHQ) && state.livePlayer && dom.liveLottiePlayer) {
            const currentData = state.currentHeroTemplateData || getPreRenderedTemplateData(state.selectedTemplate, state.font, state.scale);
            if (currentData) {
                const recolored = applyBadgeColorToLottieJSON(currentData, (isGrey || isHQ) ? null : state.badgeColor, (isGrey || isHQ) ? null : state.badgeBgColor, state.textColor, isGrey);
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
        updateSelectedCardsPreview();
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
            renderHQGrid(dom.hqSearch?.value || '');
        });
    });
    
    // Tab switching (Name vs Logo vs Grey vs HQ)
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

    dom.tabBtnHQ?.addEventListener('click', () => {
        haptic('selection');
        switchTab('hq');
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
    dom.btnSelectAllHQ?.addEventListener('click', () => toggleSelectAll('hq'));
    
    // Search ticket templates (1-13 & 263-274)
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

    // Search HQ templates (183-262)
    dom.hqSearch?.addEventListener('input', (e) => {
        renderHQGrid(e.target.value);
    });
    
    // Bottom Action Button
    dom.btnMainAction.addEventListener('click', () => {
        startGeneration('selected');
    });
    
    // Logo Tab Full Pack Button (all 100)
    dom.btnCreateFullpack?.addEventListener('click', () => {
        startGeneration('all');
    });

    // Grey Tab Full Pack Button (all 65)
    dom.btnCreateGreyFullpack?.addEventListener('click', () => {
        startGeneration('all_grey');
    });

    // High Quality Tab Full Pack Button (all 80)
    dom.btnCreateHQFullpack?.addEventListener('click', () => {
        startGeneration('all_hq');
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

    // ==================== BOTTOM NAVIGATION & PROFILE LISTENERS ====================
    dom.navBtnStudio?.addEventListener('click', () => {
        haptic('selection');
        switchMainView('studio');
    });

    dom.navBtnRating?.addEventListener('click', () => {
        haptic('selection');
        switchMainView('rating');
    });

    dom.navBtnProfile?.addEventListener('click', () => {
        haptic('selection');
        switchMainView('profile');
    });

    dom.btnGotoStudio?.addEventListener('click', () => {
        haptic('selection');
        switchMainView('studio');
    });

    // Rating View Tabs (Referral vs Creator)
    dom.tabRatingReferral?.addEventListener('click', () => {
        haptic('selection');
        dom.tabRatingReferral.classList.add('active');
        dom.tabRatingCreator?.classList.remove('active');
        loadLeaderboard('referral');
    });

    dom.tabRatingCreator?.addEventListener('click', () => {
        haptic('selection');
        dom.tabRatingCreator.classList.add('active');
        dom.tabRatingReferral?.classList.remove('active');
        loadLeaderboard('creator');
    });

    // Daily Bonus Claim Button
    dom.btnClaimDailyBonus?.addEventListener('click', claimDailyBonus);

    // Language Selector Buttons
    document.querySelectorAll('.lang-switch-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            haptic('light');
            applyLanguage(btn.dataset.lang);
        });
    });

    // 1-Click Copy Referral Link
    dom.btnCopyRef?.addEventListener('click', () => {
        haptic('success');
        const refInput = dom.profileRefLinkInput;
        const uid = state.user?.id || 1323217434;
        const refUrl = refInput?.value || `https://t.me/${BOT_USERNAME}?start=ref_${uid}`;

        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(refUrl).catch(() => {
                refInput?.select();
                document.execCommand('copy');
            });
        } else {
            refInput?.select();
            document.execCommand('copy');
        }

        if (dom.copyBtnText) dom.copyBtnText.textContent = "Nusxalandi! ✨";
        dom.btnCopyRef?.classList.add('copied');
        showToast("Taklif havolangiz nusxalandi! Do'stlaringizga yuboring ✨", "🔗", 3000);

        setTimeout(() => {
            if (dom.copyBtnText) dom.copyBtnText.textContent = "Nusxalash";
            dom.btnCopyRef?.classList.remove('copied');
        }, 2500);
    });

    // Share to Telegram button
    dom.btnShareTelegramRef?.addEventListener('click', () => {
        haptic('medium');
        const uid = state.user?.id || 1323217434;
        const refLink = `https://t.me/${BOT_USERNAME}?start=ref_${uid}`;
        const shareText = "✨ Ismingiz bilan eksklyuziv animatsiyali Telegram emoji to'plamini yarating!";
        const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(refLink)}&text=${encodeURIComponent(shareText)}`;
        if (tg?.openTelegramLink) {
            tg.openTelegramLink(shareUrl);
        } else {
            window.open(shareUrl, '_blank');
        }
    });

    // Profile Topup button
    dom.btnProfileTopup?.addEventListener('click', () => {
        haptic('medium');
        openBalanceModal(state.userBalance || 0, (state.lastNeededBal || state.emojiPrice || 6));
    });

    // Profile Channel link
    dom.btnProfileChannel?.addEventListener('click', (e) => {
        haptic('light');
        const channelUrl = "https://t.me/c/3900982155/1";
        if (tg?.openTelegramLink) {
            e.preventDefault();
            tg.openTelegramLink(channelUrl);
        }
    });

    // Profile Help button
    dom.btnProfileHelp?.addEventListener('click', () => {
        haptic('light');
        if (tg?.openTelegramLink) {
            tg.openTelegramLink(`https://t.me/${BOT_USERNAME}?start=help`);
        } else {
            showToast("Botda /help yoki 🗪 Yordam bo'limiga o'ting", "ℹ️");
        }
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
