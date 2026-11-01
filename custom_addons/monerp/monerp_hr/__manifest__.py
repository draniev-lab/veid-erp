# -*- coding: utf-8 -*-
{
    'name': 'VEID Ressources Humaines',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Employees',
    'summary': 'Gestion des collaborateurs, présences et congés VEID',
    'description': """
VEID HR Module
================
Gestion unifiée du capital humain pour VEID :
- Profils employés enrichis et matricule RH VEID
- Habilitations de validation des dépenses
- Suivi du département et responsable analytique
    """,
    'author': 'VEID Enterprise',
    'website': 'https://veid.com',
    'license': 'LGPL-3',
    'depends': [
        'monerp_core',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_certification_views.xml',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
