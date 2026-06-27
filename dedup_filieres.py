"""
dedup_filieres.py — Supprimer les filières dupliquées (même domaine IA/Data Science)
Les doublons viennent de la coexistence de seed.py (ancien) et seed_v7.py (Boladé)
"""
import sys
sys.path.insert(0, ".")
from sqlmodel import Session, select, text
from app.core.database import engine
from app.models.filiere import Filiere

# Paires de doublons à fusionner — garder la version la plus détaillée (seed_v7)
DOUBLONS = [
    # (à_supprimer, à_garder)
    ("Intelligence Artificielle et Data Science", "Data Science & Intelligence Artificielle"),
    ("Data Science et Intelligence Artificielle",  "Data Science & Intelligence Artificielle"),
    ("Génie Informatique et Logiciels",            "Génie Informatique"),
    ("Génie Logiciel",                             "Réseaux et Génie Logiciel"),
]

with Session(engine) as s:
    print("=== Déduplication des filières ===\n")
    supprimées = 0
    for nom_del, nom_keep in DOUBLONS:
        # Vérifier si le doublon existe
        f_del = s.exec(select(Filiere).where(Filiere.nom == nom_del)).first()
        f_keep = s.exec(select(Filiere).where(Filiere.nom == nom_keep)).first()
        if f_del and f_keep:
            # Mettre à jour les score_compatibilite qui référencent f_del → f_keep
            s.exec(text(
                "UPDATE score_compatibilite SET id_filiere = :keep WHERE id_filiere = :del"
            ).bindparams(keep=f_keep.id_filiere, id_del=f_del.id_filiere))
            # Supprimer les formations liées à f_del
            s.exec(text("DELETE FROM formation WHERE id_filiere = :del").bindparams(id_del=f_del.id_filiere))
            # Supprimer la filière doublon
            s.delete(f_del)
            s.commit()
            print(f"✅ Supprimé '{nom_del}' → gardé '{nom_keep}'")
            supprimées += 1
        elif f_del and not f_keep:
            print(f"⏭️  '{nom_del}' trouvé mais '{nom_keep}' absent — pas de fusion")
        else:
            print(f"⏭️  '{nom_del}' absent en DB — pas de doublon")

    print(f"\n✅ {supprimées} doublon(s) supprimé(s)")

    # Vérification finale
    total = s.exec(text("SELECT COUNT(*) FROM filiere")).one()[0]
    print(f"\nTotal filières en base : {total}")
