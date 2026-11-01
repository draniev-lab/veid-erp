# -*- coding: utf-8 -*-
{
    'name': 'VEID Secteur Agricole',
    'version': '19.0.1.0.0',
    'category': 'Vertical/Agriculture',
    'summary': 'Gestion des exploitations agricoles, parcelles et récoltes VEID',
    'description': """
VEID Agriculture Module
=========================
Extension sectorielle verticale pour le domaine agricole :
- Gestion des exploitations et cartographie des parcelles (Hectares)
- Suivi des cultures et des campagnes agricoles
- Traçabilité des semences, engrais et traitements
- Calcul des coûts et rendements par parcelle
    """,
    'author': 'VEID Enterprise',
    'website': 'https://veid.com',
    'license': 'LGPL-3',
    'depends': [
        'monerp_core',
        'monerp_stock',
        'monerp_analytic',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/farm_parcel_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
