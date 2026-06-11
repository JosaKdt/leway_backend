# -*- coding: utf-8 -*-
"""
Vérifie les domaines en base : nombre de filières par domaine + leurs noms
Usage: python check_domaines.py
"""
from sqlmodel import Session, select
from app.core.database import engine
from app.models.filiere import Filiere
from collections import defaultdict

with Session(engine) as session:
    filieres = session.exec(select(Filiere).order_by(Filiere.domaine, Filiere.nom)).all()

by_domain = defaultdict(list)
for f in filieres:
    by_domain[f.domaine].append(f.nom)

total = 0
print(f"\n{'='*55}")
print(f"  FILIÈRES EN BASE — {len(filieres)} au total")
print(f"{'='*55}")

for domaine in sorted(by_domain):
    noms = by_domain[domaine]
    total += len(noms)
    print(f"\n▸ {domaine.upper()} ({len(noms)})")
    for nom in noms:
        print(f"    - {nom}")

print(f"\n{'='*55}")
print(f"  TOTAL : {total} filières dans {len(by_domain)} domaines")
print(f"{'='*55}\n")
