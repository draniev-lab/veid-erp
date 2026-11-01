# -*- coding: utf-8 -*-
{
    'name': 'VEID Comptabilité & Finance',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Gestion comptable, financière et suivi de trésorerie VEID',
    'description': """
VEID Accounting Module
========================
Extension de la chaîne comptable et de facturation :
- Mentions légales et statut d'approbation des factures
- Suivi du recouvrement et échéances de paiement
- Intégration comptable multi-sociétés
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
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
