# -*- coding: utf-8 -*-
{
    'name': 'VEID CRM & Relations Clients',
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Gestion des opportunités, pistes et relations clients VEID',
    'description': """
VEID CRM Module
=================
Extension commerciale VEID pour la gestion de la relation client :
- Qualification enrichie des prospects
- Indicateurs de maturité commerciale VEID
- Historique d'interactions et rappels d'activités
- Préparation à la conversion automatique Devis / Ventes
    """,
    'author': 'VEID Enterprise',
    'website': 'https://veid.com',
    'license': 'LGPL-3',
    'depends': [
        'monerp_core',
        'crm',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
