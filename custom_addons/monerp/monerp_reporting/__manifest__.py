# -*- coding: utf-8 -*-
{
    'name': 'VEID Tableaux de Bord & Reporting',
    'version': '19.0.1.0.0',
    'category': 'Reporting',
    'summary': 'Rapports décisionnels et indicateurs clés de performance VEID',
    'description': """
VEID Reporting Module
=======================
Centre de pilotage stratégique VEID :
- Synthese du Chiffre d'Affaires, Marges, Achats et Stocks
- Indicateurs de performance commerciale et opérationnelle
- Vues consolidées pour la direction
    """,
    'author': 'VEID Enterprise',
    'website': 'https://veid.com',
    'license': 'LGPL-3',
    'depends': [
        'monerp_core',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/monerp_dashboard_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
