# -*- coding: utf-8 -*-
{
    'name': 'VEID Localisation OHADA / Franc CFA',
    'version': '19.0.1.0.0',
    'category': 'Localization',
    'summary': 'Plan comptable OHADA, devises FCFA et fiscalité UEMOA/CEMAC',
    'description': """
VEID Localization & Fiscal Core Module
==========================================
Extension d'internationalisation et conformité fiscale :
- Numéro d'identification fiscale (NIF/STAT/RC) & validation TVA
- Retenue à la source (Withholding Tax) et précompte
- Buffers de taux de change multi-devises
    """,
    'author': 'VEID Enterprise',
    'website': 'https://veid.com',
    'license': 'LGPL-3',
    'depends': [
        'monerp_core',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_l10n_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
