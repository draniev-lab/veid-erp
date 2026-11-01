# -*- coding: utf-8 -*-
{
    'name': 'VEID Stocks & Logistique',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Gestion des inventaires, traçabilité et alertes de réapprovisionnement VEID',
    'description': """
VEID Stock Module
===================
Gestion logistique et valorisation des stocks VEID :
- Contrôle qualité des réceptions et livraisons
- Statuts d'inspection et traçabilité
- Intégration avancée avec les entrepôts et réapprovisionnements
    """,
    'author': 'VEID Enterprise',
    'website': 'https://veid.com',
    'license': 'LGPL-3',
    'depends': [
        'monerp_core',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
