/**
 * VEID Enterprise - Modern Rail & Sidebar Navigation
 * Transforms the application shell into a state-of-the-art enterprise workspace.
 */

(function () {
    'use strict';

    const NAV_ITEMS = [
        {
            group: 'ESPACES MÉTIERS',
            items: [
                { id: 'nav-dashboard', label: 'Pilotage & Cockpit', icon: 'fa-tachometer', url: '/odoo' },
                { id: 'nav-invoicing', label: 'Finances & SYSCOHADA', icon: 'fa-balance-scale', url: '/odoo/action-270' },
                { id: 'nav-momo', label: 'Hub Mobile Money', icon: 'fa-mobile-phone', url: '/odoo/action-270', toggleKey: 'enable_space_momo' },
                { id: 'nav-btp', label: 'Chantiers & BTP', icon: 'fa-building', url: '/odoo', toggleKey: 'enable_space_btp' },
                { id: 'nav-agri', label: 'Agro-Industrie', icon: 'fa-leaf', url: '/odoo', toggleKey: 'enable_space_agri' },
                { id: 'nav-transport', label: 'Flotte & Convois', icon: 'fa-truck', url: '/odoo', toggleKey: 'enable_space_transport' },
            ]
        },
        {
            group: 'GOUVERNANCE & TERRAIN',
            items: [
                { id: 'nav-audit', label: 'Audit Ledger SHA-256', icon: 'fa-shield', url: '/odoo/action-270', toggleKey: 'enable_space_audit' },
                { id: 'nav-pwa', label: 'Field PWA (Déconnecté)', icon: 'fa-wifi', url: '/field', external: true },
            ]
        },
        {
            group: 'ADMINISTRATION & MODULES',
            items: [
                { id: 'nav-spaces', label: 'Gestion Espaces Métiers', icon: 'fa-th-list', url: '/odoo/action-92' },
                { id: 'nav-apps', label: 'Modules & Applications', icon: 'fa-cubes', url: '/odoo/action-39' },
                { id: 'nav-settings', label: 'Paramètres Système', icon: 'fa-cogs', url: '/odoo/action-92' },
                { id: 'nav-all-apps', label: 'Toutes les Applications', icon: 'fa-th-large', action: 'toggle_drawer', url: '#' },
            ]
        }
    ];

    function getActiveSpaces() {
        try {
            const raw = localStorage.getItem('veid_company_spaces');
            return raw ? JSON.parse(raw) : null;
        } catch (_) {
            return null;
        }
    }

    function isItemVisible(item) {
        if (!item.toggleKey) return true;
        const spaces = getActiveSpaces();
        if (!spaces) return true; // Default to all visible if not yet fetched
        return spaces[item.toggleKey] !== false;
    }

    function isCollapsed() {
        return localStorage.getItem('veid_sidebar_collapsed') === 'true';
    }

    function setCollapsed(collapsed) {
        localStorage.setItem('veid_sidebar_collapsed', collapsed ? 'true' : 'false');
        const sidebar = document.getElementById('veid-enterprise-sidebar');
        const webClient = document.querySelector('.o_web_client');
        if (sidebar && webClient) {
            if (collapsed) {
                sidebar.classList.add('collapsed');
                webClient.classList.add('veid-sidebar-collapsed');
                webClient.classList.remove('veid-sidebar-expanded');
            } else {
                sidebar.classList.remove('collapsed');
                webClient.classList.add('veid-sidebar-expanded');
                webClient.classList.remove('veid-sidebar-collapsed');
            }
        }
    }

    function initSidebar() {
        if (document.getElementById('veid-enterprise-sidebar')) {
            return;
        }

        const webClient = document.querySelector('.o_web_client') || document.body;
        if (!webClient) return;

        const sidebar = document.createElement('aside');
        sidebar.id = 'veid-enterprise-sidebar';
        sidebar.className = 'veid-app-sidebar' + (isCollapsed() ? ' collapsed' : '');
        
        let groupsHtml = '';
        NAV_ITEMS.forEach(grp => {
            let itemsHtml = '';
            grp.items.forEach(item => {
                if (!isItemVisible(item)) {
                    return; // Skip disabled spaces
                }
                const isCurrent = window.location.pathname === item.url || 
                    (item.url === '/odoo/action-270' && window.location.href.includes('action-270')) ||
                    (item.url === '/odoo/action-39' && window.location.href.includes('action-39'));
                const actionAttr = item.action ? `data-action="${item.action}"` : '';
                itemsHtml += `
                    <a href="${item.url}" class="veid-nav-link ${isCurrent ? 'active' : ''}" data-nav-id="${item.id}" ${actionAttr} title="${item.label}">
                        <div class="veid-nav-icon"><i class="fa ${item.icon}"></i></div>
                        <span class="veid-nav-text">${item.label}</span>
                    </a>
                `;
            });

            if (itemsHtml) {
                groupsHtml += `
                    <div class="veid-nav-group">
                        <div class="veid-nav-group-header">${grp.group}</div>
                        <div class="veid-nav-group-items">${itemsHtml}</div>
                    </div>
                `;
            }
        });

        sidebar.innerHTML = `
            <div class="veid-sidebar-brand">
                <a href="/odoo" class="veid-brand-link">
                    <img src="/monerp_core/static/src/img/veid_logo_dark.svg" alt="VEID Logo" class="veid-brand-icon" />
                    <span class="veid-brand-name">VEID</span>
                </a>
                <button type="button" id="veid-sidebar-toggle" class="veid-sidebar-toggle-btn" title="Réduire/Agrandir le menu">
                    <i class="fa fa-angle-double-left"></i>
                </button>
            </div>
            
            <div class="veid-sidebar-content">
                ${groupsHtml}
            </div>

            <div class="veid-sidebar-footer">
                <button type="button" class="veid-quick-cmd-btn" onclick="window.veidOpenCommandPalette &amp;&amp; window.veidOpenCommandPalette()">
                    <i class="fa fa-search"></i>
                    <span class="veid-nav-text">Command Palette</span>
                    <span class="veid-kbd-hint">⌘K</span>
                </button>
                <div class="veid-tenant-card">
                    <div class="veid-tenant-indicator"></div>
                    <div class="veid-tenant-info">
                        <div class="veid-tenant-name">VEID Enterprise</div>
                        <div class="veid-tenant-status">Production • SYSCOHADA</div>
                    </div>
                </div>
            </div>
        `;

        // Prepend sidebar into .o_web_client
        webClient.prepend(sidebar);
        if (isCollapsed()) {
            webClient.classList.add('veid-sidebar-collapsed');
        } else {
            webClient.classList.add('veid-sidebar-expanded');
        }

        // Toggle event
        const toggleBtn = document.getElementById('veid-sidebar-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', (e) => {
                e.preventDefault();
                setCollapsed(!isCollapsed());
            });
        }

        // Action events (e.g. toggle drawer)
        sidebar.querySelectorAll('a[data-action="toggle_drawer"]').forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                const drawerBtn = document.querySelector('.o_grid_apps_menu__button, .o_navbar_apps_menu button');
                if (drawerBtn) {
                    drawerBtn.click();
                } else {
                    window.location.href = '/odoo';
                }
            });
        });
    }

    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        setTimeout(initSidebar, 100);
    } else {
        document.addEventListener('DOMContentLoaded', initSidebar);
    }
    setInterval(initSidebar, 1500);
})();
