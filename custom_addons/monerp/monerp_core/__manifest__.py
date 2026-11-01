# -*- coding: utf-8 -*-
{
    'name': 'VEID Core',
    'version': '19.0.1.0.0',
    'category': 'Core',
    'summary': 'Socle applicatif, identité visuelle et système de design VEID Enterprise',
    'description': """
VEID Core Module
==================
Ce module constitue le socle fondamental de l'ERP VEID.
- Identité visuelle et système de design VEID
- Base responsive et lanceur Bento Grid (web_responsive)
- Menus racines et organisation de la navigation
- Paramètres système globaux VEID
- Sécurité et gestion des groupes VEID
- Multi-sociétés et helpers de localisation
    """,
    'author': 'VEID Enterprise',
    'website': 'https://veid.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'web_responsive',
    ],
    'data': [
        'security/monerp_security.xml',
        'security/ir.model.access.csv',
        'views/web_layout_templates.xml',
        'views/monerp_menus.xml',
        'views/res_config_settings_views.xml',
        'views/res_company_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'monerp_core/static/src/scss/monerp_style.scss',
            'monerp_core/static/src/scss/veid_ai_assistant.scss',
            'monerp_core/static/src/js/monerp_title.js',
            'monerp_core/static/src/js/veid_sidebar.js',
            'monerp_core/static/src/js/veid_command_palette.js',
            'monerp_core/static/src/js/veid_ai_assistant.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
