# -*- coding: utf-8 -*-
"""
migrate_v7.py — Migration domaines anciens → nouveaux + suppression doublons
Usage: python migrate_v7.py
"""
from sqlmodel import Session, select
from app.core.database import engine
from app.models.filiere import Filiere
from app.models.formation import Formation

# ── 1. Renommage des domaines anciens → nouveaux ──────────────────────────────
DOMAINE_MAP = {
    'Administration':   'Administration Publique',
    'Agriculture':      'Agriculture',          # même nom, juste nettoyer doublons
    'Arts':             'Arts et Culture',
    'Commerce':         'Commerce et Marketing',
    'Communication':    'Communication et Médias',
    'Droit':            'Droit',                # même nom
    'Environnement':    'Environnement',        # même nom
    'Finance':          'Finance et Comptabilité',
    'Gestion':          'Gestion et Management',
    'Informatique':     'Informatique et Numérique',
    'Ingénierie':       'Ingénierie et Technologie',
    'Lettres':          'Langues et Lettres',
    'Santé':            'Santé',                # même nom
    'Sciences':         'Sciences Fondamentales',
    'Sciences Sociales':'Sciences Sociales et Humaines',
    'Sport':            'Sport et Éducation Physique',
    'Tourisme':         'Commerce et Marketing', # Tourisme absorbé dans Commerce
    'Transport':        'Transport et Logistique',
    'Économie':         'Économie',             # même nom
    'Éducation':        'Éducation et Pédagogie',
}

# ── 2. Doublons à fusionner (ancien → canonique du seed_v7) ───────────────────
# Format : ('nom doublon', 'nom canonique à garder')
FUSIONS = [
    # Agriculture
    ('Agronomie',                               'Agronomie Générale'),
    ('Agroéconomie',                            'Agroéconomie et Développement Rural'),
    ('Sciences et Techniques de Production Végétale', 'Production Végétale et Semencière'),
    ('Sciences et Techniques de Production Animale',  'Production et Santé Animales'),
    ('Nutrition Humaine et Sciences Agroalimentaires','Nutrition Humaine et Agroalimentaire'),
    ('Économie Rurale et Sociologie Agricole',  'Agroéconomie et Développement Rural'),

    # Arts
    # Arts et Management Culturel → Arts et Culture (juste renommage domaine)

    # Commerce
    ('Management Communication et Commerce',    'Marketing et Action Commerciale'),
    ('Hôtellerie et Tourisme',                  'Hôtellerie Restauration et Tourisme'),

    # Communication
    ('Communication et Relations Internationales', 'Communication et Relations Publiques'),

    # Droit
    ('Droit',                                   'Sciences Juridiques'),
    ('Sciences Politiques et Juridiques',       'Science Politique et Relations Internationales'),

    # Environnement
    ('Aménagement et Gestion des Ressources Naturelles', 'Gestion de l\'Environnement et Aménagement'),

    # Finance
    ('Administration des Finances',             'Gestion Financière et Comptable'),
    ('Finance Comptabilité et Audit',           'Finance et Contrôle de Gestion'),
    ('Audit et Contrôle de Gestion',            'Finance et Contrôle de Gestion'),

    # Gestion
    ('Gestion',                                 'Sciences de Gestion'),
    ('Administration des Affaires',             'Administration et Gestion des Entreprises'),
    ('Économie et Gestion',                     'Sciences de Gestion'),

    # Informatique
    ('Informatique',                            'Génie Informatique et Télécommunications'),
    ('Informatique (IFRI)',                     'Intelligence Artificielle et Data Science'),
    ('Informatique Réseaux et Télécommunication','Informatique Réseaux et Télécommunications'),
    ('Système Informatique et Logiciel',        'Réseaux et Génie Logiciel'),
    ('Génie Informatique',                      'Génie Informatique et Télécommunications'),

    # Ingénierie
    ('Bâtiment et Travaux Publics',             'Génie Civil et BTP'),
    ('Génie Civil',                             'Génie Civil et BTP'),
    ('Froid Industriel',                        'Génie Frigorifique et Climatisation'),
    ('Génie Frigorifique Climatisation et Énergies Renouvelables', 'Génie Frigorifique et Climatisation'),
    ('Génie des Énergies Renouvelables',        'Génie Énergétique et Énergies Renouvelables'),
    ('Génie Énergétique et Développement Durable','Génie Énergétique et Énergies Renouvelables'),
    ('Génie Électrique',                        'Génie Électrique et Automatisme'),
    ('Électronique',                            'Génie Électronique et Télécommunications'),
    ('Génie de l\'Eau',                         'Génie de l\'Eau et Hydraulique'),
    ('Génie des Procédés de Fabrication et Maintenance Industrielle', 'Génie des Procédés Industriels'),
    ('Génie des Procédés de Productions Industrielles', 'Génie des Procédés Industriels'),
    ('Génie de Biologie Appliquée',             'Contrôle Qualité et Génie Agroalimentaire'),
    ('Système Industriel',                      'Système Industriel et Automatisation'),

    # Lettres
    ('Sociologie-Anthropologie',                'Sociologie et Anthropologie'),

    # Santé
    ('Génie Biomédical',                        'Génie Biomédical'),  # reste, juste changer domaine

    # Sciences
    ('Sciences et Techniques des Eaux',         'Sciences et Techniques des Eaux'),  # reste

    # Sciences Sociales
    ('Psychologie et Sciences de l\'Éducation', 'Psychologie et Sciences de l\'Éducation'),  # reste

    # Sport
    # inchangé

    # Transport
    # inchangé

    # Éducation
    ('Sciences de l\'Éducation',                'Éducation et Pédagogie'),
]

# Filières à juste renommer (pas de fusion, juste correction nom)
RENAMES = [
    ('Informatique Réseaux et Télécommunication', 'Informatique Réseaux et Télécommunications'),
]

def migrate():
    with Session(engine) as session:
        all_filieres = session.exec(select(Filiere)).all()
        filieres_by_nom = {f.nom: f for f in all_filieres}
        formations = session.exec(select(Formation)).all()
        forms_by_filiere = {}
        for f in formations:
            forms_by_filiere.setdefault(str(f.id_filiere), []).append(f)

        nb_domaines = 0
        nb_fusions = 0
        nb_renames = 0
        errors = []

        print("\n" + "="*60)
        print("  MIGRATION V7")
        print("="*60)

        # ── Étape 1 : Renommer les domaines ──────────────────────────
        print("\n── Étape 1 : Renommage des domaines ──")
        for f in all_filieres:
            if f.domaine in DOMAINE_MAP:
                nouveau = DOMAINE_MAP[f.domaine]
                if f.domaine != nouveau:
                    f.domaine = nouveau
                    session.add(f)
                    nb_domaines += 1
        session.flush()
        print(f"  {nb_domaines} filières mises à jour")

        # ── Étape 2 : Renommages simples ─────────────────────────────
        print("\n── Étape 2 : Renommages ──")
        for old_nom, new_nom in RENAMES:
            f = filieres_by_nom.get(old_nom)
            if not f:
                continue
            f.nom = new_nom
            session.add(f)
            filieres_by_nom[new_nom] = f
            nb_renames += 1
            print(f"  ✏️  '{old_nom}' → '{new_nom}'")
        session.flush()

        # ── Étape 3 : Fusions ────────────────────────────────────────
        print("\n── Étape 3 : Fusions ──")
        # Recharger après flush
        all_filieres2 = session.exec(select(Filiere)).all()
        filieres_by_nom2 = {f.nom: f for f in all_filieres2}

        for doublon_nom, canon_nom in FUSIONS:
            if doublon_nom == canon_nom:
                continue
            doublon = filieres_by_nom2.get(doublon_nom)
            canon   = filieres_by_nom2.get(canon_nom)
            if not doublon:
                continue
            if not canon:
                errors.append(f"Canonique introuvable : '{canon_nom}'")
                continue

            # Migrer les formations
            canon_univs = {
                str(f.id_universite)
                for f in forms_by_filiere.get(str(canon.id_filiere), [])
            }
            migrated = 0
            deleted  = 0
            for f in forms_by_filiere.get(str(doublon.id_filiere), []):
                uid = str(f.id_universite)
                if uid not in canon_univs:
                    f.id_filiere = canon.id_filiere
                    session.add(f)
                    canon_univs.add(uid)
                    migrated += 1
                else:
                    session.delete(f)
                    deleted += 1
            session.flush()
            session.delete(doublon)
            session.flush()
            nb_fusions += 1
            print(f"  ✅ '{doublon_nom}' → '{canon_nom}' ({migrated} migrées, {deleted} supprimées)")

        session.commit()

        # ── Résumé final ─────────────────────────────────────────────
        from collections import Counter
        remaining = session.exec(select(Filiere)).all()
        domaines = Counter(f.domaine for f in remaining)

        print(f"\n{'='*60}")
        print(f"  {nb_domaines} domaines renommés")
        print(f"  {nb_fusions} fusions effectuées")
        print(f"  {nb_renames} renommages")
        if errors:
            print(f"\n  ⚠️  {len(errors)} avertissement(s) :")
            for e in errors: print(f"    - {e}")
        print(f"\n  Total filières : {len(remaining)}")
        print(f"  Domaines ({len(domaines)}) :")
        for dom, count in sorted(domaines.items()):
            print(f"    {dom:45s} {count:3d}")
        print("="*60)

if __name__ == '__main__':
    migrate()
