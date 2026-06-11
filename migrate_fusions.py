# -*- coding: utf-8 -*-
"""
Migration v2 : fusionne les filières doublonnées en base
- Supprime les formations orphelines des doublons (déjà couvertes par le canonique)
- Supprime les filières doublonnées
- Corrige les fautes de frappe
Usage: python migrate_fusions.py
"""
from sqlmodel import Session, select
from app.core.database import engine
from app.models.filiere import Filiere
from app.models.formation import Formation

FUSIONS = [
    ("Communication et Relation Publique",           "Communication et Relations Publiques"),
    ("Journalisme",                                  "Journalisme et Communication"),
    ("Science Juridique",                            "Sciences Juridiques"),
    ("Audit et Finance des Entreprises",             "Audit et Contrôle de Gestion"),
    ("Comptabilité et Finance d'Entreprise",         "Comptabilité Contrôle et Audit"),
    ("Comptabilité et Gestion",                      "Comptabilité Contrôle et Audit"),
    ("Comptabilité Gestion",                         "Comptabilité Contrôle et Audit"),
    ("Administration des Entreprises (MBA)",         "Administration et Gestion des Entreprises"),
    ("Gestion et Administration des Entreprises",    "Administration et Gestion des Entreprises"),
    ("Entrepreneuriat et Gestion de Projets",        "Entrepreneuriat et Gestion des PME"),
    ("Marketing et Communication",                   "Marketing et Action Commerciale"),
    ("Gestion des Transports",                       "Gestion des Transports et Logistique"),
    ("Transport et Logistique",                      "Gestion des Transports et Logistique"),
    ("STAPS",                                        "Sciences et Techniques des Activités Physiques et Sportives"),
    ("Science Politique",                            "Science Politique et Relations Internationales"),
    ("Relations Internationales",                    "Science Politique et Relations Internationales"),
]

RENAMES = [
    ("Sciences de Gestions", "Sciences de Gestion"),
]

def migrate():
    with Session(engine) as session:
        filieres    = {f.nom: f for f in session.exec(select(Filiere)).all()}
        formations  = session.exec(select(Formation)).all()

        # Index formations par id_filiere
        from collections import defaultdict
        forms_by_filiere = defaultdict(list)
        for f in formations:
            forms_by_filiere[f.id_filiere].append(f)

        nb_fusions = 0
        nb_formations_migrees = 0
        nb_formations_supprimees = 0
        nb_renames = 0
        errors = []

        print("\n" + "="*60)
        print("  MIGRATION v2 — FUSIONS DE FILIÈRES")
        print("="*60)

        for doublon_nom, canon_nom in FUSIONS:
            doublon = filieres.get(doublon_nom)
            canon   = filieres.get(canon_nom)

            if not doublon:
                errors.append(f"Doublon introuvable : '{doublon_nom}'")
                continue
            if not canon:
                errors.append(f"Canonique introuvable : '{canon_nom}'")
                continue

            # Universités déjà couvertes par le canonique
            canon_univs = {
                f.id_universite
                for f in forms_by_filiere[canon.id_filiere]
            }

            migrated = 0
            deleted  = 0
            for f in forms_by_filiere[doublon.id_filiere]:
                if f.id_universite not in canon_univs:
                    # L'université n'est pas encore liée au canonique → on migre
                    f.id_filiere = canon.id_filiere
                    session.add(f)
                    canon_univs.add(f.id_universite)
                    migrated += 1
                else:
                    # Déjà couverte → on supprime la formation en double
                    session.delete(f)
                    deleted += 1

            nb_formations_migrees    += migrated
            nb_formations_supprimees += deleted

            # Flush pour que les DELETE/UPDATE formation soient envoyés
            # avant le DELETE filiere
            session.flush()

            session.delete(doublon)
            session.flush()

            nb_fusions += 1
            print(f"  ✅ '{doublon_nom}' → '{canon_nom}'")
            print(f"     {migrated} formations migrées, {deleted} supprimées")

        # Renommages
        print()
        for old_nom, new_nom in RENAMES:
            f = filieres.get(old_nom)
            if not f:
                errors.append(f"Filière introuvable pour renommage : '{old_nom}'")
                continue
            f.nom = new_nom
            session.add(f)
            nb_renames += 1
            print(f"  ✏️  '{old_nom}' → '{new_nom}'")

        session.commit()

        print("\n" + "="*60)
        print(f"  ✅ {nb_fusions} fusions effectuées")
        print(f"  ✅ {nb_formations_migrees} formations migrées")
        print(f"  ✅ {nb_formations_supprimees} formations en double supprimées")
        print(f"  ✅ {nb_renames} renommages")
        if errors:
            print(f"\n  ⚠️  {len(errors)} avertissement(s) :")
            for e in errors:
                print(f"    - {e}")

        remaining = session.exec(select(Filiere)).all()
        print(f"\n  Filières restantes : {len(remaining)}")
        print("  (relance check_domaines.py pour le détail)")
        print("="*60 + "\n")


if __name__ == "__main__":
    migrate()
