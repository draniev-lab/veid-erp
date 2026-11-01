import os
import re

manifest_names = {
    'monerp_core': ('VEID Core', 'Socle applicatif, identité visuelle et configuration de VEID Enterprise'),
    'monerp_account': ('VEID Comptabilité & Finance', 'Gestion comptable, financière et suivi de trésorerie VEID'),
    'monerp_analytic': ('VEID Comptabilité Analytique', 'Comptabilité analytique, centres de coûts et rentabilité VEID'),
    'monerp_crm': ('VEID CRM & Relations Clients', 'Gestion des opportunités, pistes et relations clients VEID'),
    'monerp_hr': ('VEID Ressources Humaines', 'Gestion des collaborateurs, présences et congés VEID'),
    'monerp_l10n': ('VEID Localisation OHADA / Franc CFA', 'Plan comptable OHADA, devises FCFA et fiscalité UEMOA/CEMAC'),
    'monerp_purchase': ('VEID Achats & Fournisseurs', 'Gestion des commandes fournisseurs, réceptions et factures achats'),
    'monerp_reporting': ('VEID Tableaux de Bord & Reporting', 'Rapports décisionnels et indicateurs clés de performance VEID'),
    'monerp_sale': ('VEID Ventes & Devis', 'Gestion commerciale, devis, commandes clients et facturation VEID'),
    'monerp_stock': ('VEID Stocks & Logistique', 'Gestion des inventaires, traçabilité et alertes de réapprovisionnement VEID'),
    'monerp_agriculture': ('VEID Secteur Agricole', 'Gestion des exploitations agricoles, parcelles et récoltes VEID'),
    'monerp_construction': ('VEID Secteur BTP & Chantiers', 'Gestion des chantiers, engins et travaux BTP VEID'),
    'monerp_transport': ('VEID Secteur Transport & Flotte', 'Gestion du transport de fret, missions et suivi de flotte VEID'),
}

root = 'custom_addons/monerp'
for dirpath, dirnames, filenames in os.walk(root):
    if '__manifest__.py' in filenames:
        m_path = os.path.join(dirpath, '__manifest__.py')
        folder_name = os.path.basename(dirpath)
        with open(m_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace Author & Website
        content = re.sub(r"'author':\s*['\"][^'\"]+['\"]", "'author': 'VEID Enterprise'", content)
        content = re.sub(r"'website':\s*['\"][^'\"]+['\"]", "'website': 'https://veid.com'", content)
        
        # Replace Name & Summary if known
        if folder_name in manifest_names:
            v_name, v_summary = manifest_names[folder_name]
            content = re.sub(r"'name':\s*['\"][^'\"]+['\"]", f"'name': '{v_name}'", content)
            content = re.sub(r"'summary':\s*['\"][^'\"]+['\"]", f"'summary': '{v_summary}'", content)
        
        # Replace descriptions referring to MonErp
        content = content.replace('MonErp', 'VEID')
        
        with open(m_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {m_path} -> VEID branding")

print("All manifests successfully updated to VEID!")
