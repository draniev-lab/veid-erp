/**
 * VEID Enterprise - Command Palette (Ctrl+K) & Universal Navigation
 * Provides instant keyboard-driven navigation across all VEID modules and actions.
 */

(function () {
    'use strict';

    const COMMAND_ITEMS = [
        { id: 'cockpit', title: 'Tableau de Bord & Pilotage Exécutif', category: 'Pilotage', icon: 'fa-tachometer', url: '/odoo' },
        { id: 'invoices', title: 'Factures Clients & SYSCOHADA', category: 'Finances', icon: 'fa-file-text-o', url: '/odoo/action-270' },
        { id: 'momo', title: 'Paiements Mobile Money (T-Money, Flooz, Wave, Orange, MTN)', category: 'Finances', icon: 'fa-money', url: '/odoo/action-270' },
        { id: 'ai_treasury', title: 'Trésorerie Prédictive IA (Projections 30/60/90j)', category: 'Intelligence Artificielle', icon: 'fa-line-chart', action: 'show_treasury' },
        { id: 'audit_ledger', title: 'Gouvernance & Journal Cryptographique SHA-256', category: 'Conformité & Sécurité', icon: 'fa-shield', url: '/odoo/action-270' },
        { id: 'btp', title: 'Chantiers BTP & Suivi de Travaux', category: 'Opérations Sectorielles', icon: 'fa-building', url: '/odoo' },
        { id: 'agri', title: 'Agro-Industrie & Campagnes Agricoles', category: 'Opérations Sectorielles', icon: 'fa-leaf', url: '/odoo' },
        { id: 'transport', title: 'Flotte & Convois Logistiques', category: 'Opérations Sectorielles', icon: 'fa-truck', url: '/odoo' },
        { id: 'pwa', title: 'Application Terrain Déconnectée (Field PWA)', category: 'Mobilité Terrain', icon: 'fa-mobile', url: '/field', external: true },
        { id: 'modules_apps', title: 'Gestionnaire de Modules & Applications (Activer / Désactiver)', category: 'Administration & Système', icon: 'fa-cubes', url: '/odoo/action-39' },
        { id: 'all_apps', title: 'Toutes les Applications & Grille Bento', category: 'Navigation', icon: 'fa-th-large', url: '/odoo' },
        { id: 'settings', title: 'Configuration & Paramètres Société', category: 'Administration & Système', icon: 'fa-cogs', url: '/odoo/action-92' }
    ];

    let paletteOpen = false;
    let selectedIndex = 0;
    let filteredItems = [...COMMAND_ITEMS];

    function createPaletteModal() {
        if (document.getElementById('veid-palette-overlay')) {
            return;
        }

        const overlay = document.createElement('div');
        overlay.id = 'veid-palette-overlay';
        overlay.className = 'veid-palette-overlay d-none';
        overlay.innerHTML = `
            <div class="veid-palette-card" role="dialog" aria-modal="true" aria-label="Palette de commandes VEID">
                <div class="veid-palette-header">
                    <i class="fa fa-search veid-palette-search-icon"></i>
                    <input type="text" id="veid-palette-input" class="veid-palette-input" placeholder="Rechercher une application, une facture, un chantier ou une action... (Echap pour fermer)" autocomplete="off" spellcheck="false" />
                    <span class="veid-palette-shortcut-badge">ESC</span>
                </div>
                <div class="veid-palette-results" id="veid-palette-results"></div>
                <div class="veid-palette-footer">
                    <div class="veid-palette-keys">
                        <span><kbd>↑</kbd><kbd>↓</kbd> Naviguer</span>
                        <span><kbd>↵</kbd> Ouvrir</span>
                        <span><kbd>ESC</kbd> Fermer</span>
                    </div>
                    <div class="veid-palette-branding">
                        <span class="veid-badge-tier">VEID Enterprise</span>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(overlay);

        // Click outside closes
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                closePalette();
            }
        });

        // Search filtering
        const input = document.getElementById('veid-palette-input');
        if (input) {
            input.addEventListener('input', (e) => {
                const q = e.target.value.toLowerCase().trim();
                if (!q) {
                    filteredItems = [...COMMAND_ITEMS];
                } else {
                    filteredItems = COMMAND_ITEMS.filter(it => 
                        it.title.toLowerCase().includes(q) || 
                        it.category.toLowerCase().includes(q)
                    );
                }
                selectedIndex = 0;
                renderResults();
            });

            input.addEventListener('keydown', handleKeyNavigation);
        }
    }

    function renderResults() {
        const container = document.getElementById('veid-palette-results');
        if (!container) return;

        if (filteredItems.length === 0) {
            container.innerHTML = `
                <div class="veid-palette-empty">
                    <i class="fa fa-info-circle mb-2"></i>
                    <div>Aucun résultat trouvé dans VEID Enterprise.</div>
                </div>
            `;
            return;
        }

        let html = '';
        let currentCat = '';
        filteredItems.forEach((item, idx) => {
            if (item.category !== currentCat) {
                currentCat = item.category;
                html += `<div class="veid-palette-group-title">${currentCat}</div>`;
            }
            const isSelected = idx === selectedIndex;
            html += `
                <div class="veid-palette-item ${isSelected ? 'selected' : ''}" data-idx="${idx}">
                    <div class="veid-palette-item-icon">
                        <i class="fa ${item.icon}"></i>
                    </div>
                    <div class="veid-palette-item-content">
                        <div class="veid-palette-item-title">${item.title}</div>
                        <div class="veid-palette-item-cat">${item.category}</div>
                    </div>
                    <div class="veid-palette-item-action">
                        <i class="fa fa-arrow-right"></i>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;

        // Add click events on items
        container.querySelectorAll('.veid-palette-item').forEach(el => {
            el.addEventListener('click', () => {
                const idx = parseInt(el.getAttribute('data-idx') || '0', 10);
                executeItem(filteredItems[idx]);
            });
            el.addEventListener('mouseenter', () => {
                selectedIndex = parseInt(el.getAttribute('data-idx') || '0', 10);
                highlightSelected();
            });
        });
    }

    function highlightSelected() {
        const container = document.getElementById('veid-palette-results');
        if (!container) return;
        const items = container.querySelectorAll('.veid-palette-item');
        items.forEach((el, idx) => {
            if (idx === selectedIndex) {
                el.classList.add('selected');
                el.scrollIntoView({ block: 'nearest' });
            } else {
                el.classList.remove('selected');
            }
        });
    }

    function handleKeyNavigation(e) {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIndex = (selectedIndex + 1) % Math.max(1, filteredItems.length);
            highlightSelected();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = (selectedIndex - 1 + filteredItems.length) % Math.max(1, filteredItems.length);
            highlightSelected();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (filteredItems[selectedIndex]) {
                executeItem(filteredItems[selectedIndex]);
            }
        } else if (e.key === 'Escape') {
            e.preventDefault();
            closePalette();
        }
    }

    function executeItem(item) {
        if (!item) return;
        closePalette();

        if (item.action === 'show_treasury') {
            window.open('/api/v1/veid/ai/treasury-forecast', '_blank');
        } else if (item.external) {
            window.location.href = item.url;
        } else if (item.url) {
            window.location.href = item.url;
        }
    }

    function openPalette() {
        createPaletteModal();
        const overlay = document.getElementById('veid-palette-overlay');
        const input = document.getElementById('veid-palette-input');
        if (overlay && input) {
            overlay.classList.remove('d-none');
            input.value = '';
            filteredItems = [...COMMAND_ITEMS];
            selectedIndex = 0;
            renderResults();
            input.focus();
            paletteOpen = true;
        }
    }

    function closePalette() {
        const overlay = document.getElementById('veid-palette-overlay');
        if (overlay) {
            overlay.classList.add('d-none');
            paletteOpen = false;
        }
    }

    // Global keyboard listener for Ctrl+K / Cmd+K
    window.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
            e.preventDefault();
            if (paletteOpen) {
                closePalette();
            } else {
                openPalette();
            }
        }
    });

    // Injects trigger button into header or control panel
    function injectPaletteTrigger() {
        if (document.getElementById('veid-header-palette-btn')) return;

        const navbar = document.querySelector('.o_main_navbar');
        if (!navbar) return;

        const trigger = document.createElement('button');
        trigger.id = 'veid-header-palette-btn';
        trigger.type = 'button';
        trigger.className = 'veid-command-trigger-btn';
        trigger.title = 'Rechercher ou exécuter (Ctrl+K)';
        trigger.innerHTML = `
            <i class="fa fa-search me-2 text-primary"></i>
            <span class="veid-trigger-label">Rechercher...</span>
            <span class="veid-trigger-kbd">Ctrl K</span>
        `;

        trigger.addEventListener('click', openPalette);

        // Insert after brand logo or at beginning of navbar sections
        const brand = navbar.querySelector('.o_menu_brand');
        if (brand && brand.nextSibling) {
            navbar.insertBefore(trigger, brand.nextSibling);
        } else {
            navbar.prepend(trigger);
        }
    }

    // Injects prominent Apps button directly into the top navbar
    function injectAppsButton() {
        if (document.getElementById('veid-header-apps-btn')) return;

        const navbar = document.querySelector('.o_main_navbar');
        if (!navbar) return;

        const appsBtn = document.createElement('a');
        appsBtn.id = 'veid-header-apps-btn';
        appsBtn.href = '/odoo/action-39';
        appsBtn.className = 'veid-header-apps-btn';
        appsBtn.title = 'Gérer, activer et désactiver les Applications & Modules';
        appsBtn.innerHTML = `
            <i class="fa fa-th-large me-2"></i>
            <span class="veid-apps-label">Apps</span>
        `;

        appsBtn.addEventListener('click', (e) => {
            const drawerBtn = document.querySelector('.o_grid_apps_menu__button');
            if (drawerBtn && window.location.pathname === '/odoo') {
                e.preventDefault();
                drawerBtn.click();
            }
        });

        const brand = navbar.querySelector('.o_menu_brand');
        if (brand) {
            navbar.insertBefore(appsBtn, brand);
        } else {
            navbar.prepend(appsBtn);
        }
    }

    function initPalette() {
        createPaletteModal();
        injectPaletteTrigger();
        injectAppsButton();
    }

    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        setTimeout(initPalette, 100);
    } else {
        document.addEventListener('DOMContentLoaded', initPalette);
    }
    setInterval(() => {
        injectPaletteTrigger();
        injectAppsButton();
    }, 1500);

    // Export to window for external button clicks
    window.veidOpenCommandPalette = openPalette;
})();
