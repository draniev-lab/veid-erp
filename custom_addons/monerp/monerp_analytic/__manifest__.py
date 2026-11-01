# -*- coding: utf-8 -*-
{
    'name': 'VEID Comptabilité Analytique',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Analytic',
    'summary': 'Comptabilité analytique, centres de coûts et rentabilité VEID',
    'description': """
VEID Analytic Module
======================
Extension de la comptabilité analytique pour VEID :
- Multi-axes analytiques (Projets, Chantiers, Activités, Centres de coûts)
- Suivi de rentabilité et d'imputation budgétaire
- Base analytique pour les extensions sectorielles (BTP, Agriculture, Transport)
    """,
    'author': 'VEID Enterprise',
    'website': 'https://veid.com',
    'license': 'LGPL-3',
    'depends': [
        'monerp_core',
        'analytic',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_analytic_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
