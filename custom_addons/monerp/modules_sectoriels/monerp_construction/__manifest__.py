# -*- coding: utf-8 -*-
{
    'name': 'VEID Secteur BTP & Chantiers',
    'version': '19.0.1.0.0',
    'category': 'Vertical/Construction',
    'summary': 'Gestion des chantiers, engins et travaux BTP VEID',
    'description': """
VEID Construction Module (BTP)
================================
Module sectoriel vertical dédié aux entreprises de construction et du BTP :
- Suivi complet des chantiers et des maîtres d'ouvrage
- Situations de travaux et avancement en pourcentage
- Gestion des matériaux, de la main-d'œuvre et des sous-traitants
- Suivi des marges et rentabilité analytique par chantier
    """,
    'author': 'VEID Enterprise',
    'website': 'https://veid.com',
    'license': 'LGPL-3',
    'depends': [
        'monerp_core',
        'monerp_analytic',
        'monerp_sale',
        'monerp_purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/construction_site_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
