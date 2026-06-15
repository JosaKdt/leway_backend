"""
fix_series_ea.py — Corriger les séries bac des filières Agriculture
La série EA (Enseignement Agricole) doit être acceptée dans les filières
agricoles. seed_v7 les avait oubliées, laissant les bacheliers EA sans
filières accessibles.
Source : Guide MESRS 2024-2025 / UNA Kétou
"""
import sys
sys.path.insert(0, ".")

from sqlmodel import Session, select
from app.core.database import engine
from app.models.filiere import Filiere

# Filières qui doivent accepter EA en plus de C et D
FILIÈRES_AGRO = [
    "Agronomie Générale",
    "Production Végétale et Semencière",
    "Production et Santé Animales",
    "Nutrition Humaine et Agroalimentaire",
    "Conseil Agricole et Gestion des Exploitations",
    "Agroéconomie et Développement Rural",
    "Génie Rural et Eaux-Forêts",
    "Machinisme Agricole et Mécanique",
    "Pêche et Aquaculture",
    "Sciences et Techniques des Eaux",
    "Contrôle Qualité et Génie Agroalimentaire",
    # Notre ancien seed
    "Agronomie",
    "Production Végétale & Phytotechnie",
    "Production Animale & Zootechnie",
    "Agroalimentaire & Nutrition",
    "Aménagement & Gestion des Ressources Naturelles",
    "Économie & Sociologie Rurale",
    "Génie Rural & Maîtrise de l'Eau",
    "Foresterie & Gestion des Forêts",
    "Aquaculture & Pêche",
]

def fix_series_ea():
    with Session(engine) as s:
        filieres = s.exec(select(Filiere)).all()
        updated = 0
        for f in filieres:
            if f.nom in FILIÈRES_AGRO:
                vf = dict(f.veto_factors or {})
                series = list(vf.get("serie_bac_requise", []))
                if "EA" not in series:
                    series.append("EA")
                    vf["serie_bac_requise"] = series
                    f.veto_factors = vf
                    s.add(f)
                    updated += 1
                    print(f"  ✅ {f.nom[:50]} → séries: {series}")
                else:
                    print(f"  ⏭️  {f.nom[:50]} — EA déjà présent")
        s.commit()
        print(f"\n✅ {updated} filière(s) mise(s) à jour")

if __name__ == "__main__":
    fix_series_ea()
