# -*- coding: utf-8 -*-
{
    'name': 'VEID Achats & Fournisseurs',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'Gestion des commandes fournisseurs, réceptions et factures achats',
    'description': """
VEID Purchase Module
======================
Extension du cycle des achats pour VEID :
- Demandes de prix et comparatifs fournisseurs
- Suivi de la chaîne d'approvisionnement et réceptions
- Évaluation de la performance fournisseur
    """,
    'author': 'VEID Enterprise',
    'website': 'https://veid.com',
    'license': 'LGPL-3',
    'depends': [
        'monerp_core',
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
