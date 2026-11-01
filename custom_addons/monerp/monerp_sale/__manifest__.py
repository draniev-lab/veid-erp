# -*- coding: utf-8 -*-
{
    'name': 'VEID Ventes & Devis',
    'version': '19.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Gestion commerciale, devis, commandes clients et facturation VEID',
    'description': """
VEID Sales Module
===================
Gestion commerciale avancée VEID :
- Devis et propositions commerciales enrichies
- Gestion des conditions de paiement et remises autorisées
- Traçabilité du parcours CRM -> Devis -> Commande -> Livraison -> Facturation
    """,
    'author': 'VEID Enterprise',
    'website': 'https://veid.com',
    'license': 'LGPL-3',
    'depends': [
        'monerp_core',
        'sale_management',
        'monerp_crm',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
