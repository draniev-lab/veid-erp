import json
import psycopg2

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

conn = psycopg2.connect('postgresql://odoo:odoo@db:5432/monerp')
cur = conn.cursor()

for mod, (v_name, v_sum) in manifest_names.items():
    json_name = json.dumps({"en_US": v_name, "fr_FR": v_name})
    json_sum = json.dumps({"en_US": v_sum, "fr_FR": v_sum})
    cur.execute("""
        UPDATE ir_module_module 
        SET shortdesc = %s::jsonb, summary = %s::jsonb, author = 'VEID Enterprise', website = 'https://veid.com'
        WHERE name = %s
    """, (json_name, json_sum, mod))
    print(f"Updated in DB: {mod} -> {v_name}")

conn.commit()
cur.close()
conn.close()
print("All module records in database updated to VEID successfully!")
