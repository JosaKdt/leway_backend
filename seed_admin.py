"""
seed_admin.py — Créer le compte administrateur ORIAB par défaut
Usage : venv/bin/python3 seed_admin.py
"""
import sys
sys.path.insert(0, ".")

from sqlmodel import Session, select
from app.core.database import engine, create_db_and_tables
from app.models.administrateur import Administrateur
from app.core.security import hash_password

EMAIL    = "admin@oriab.bj"
PASSWORD = "Admin2025!"

def seed_admin():
    create_db_and_tables()
    with Session(engine) as s:
        existing = s.exec(
            select(Administrateur).where(Administrateur.email == EMAIL)
        ).first()
        if existing:
            print(f"✅ Admin déjà existant : {EMAIL}")
            return
        admin = Administrateur(
            nom="ORIAB",
            prenom="Administrateur",
            email=EMAIL,
            mot_de_passe_hash=hash_password(PASSWORD),
        )
        s.add(admin)
        s.commit()
        s.refresh(admin)
        print(f"✅ Admin créé")
        print(f"   Email    : {EMAIL}")
        print(f"   Password : {PASSWORD}")
        print(f"   ID       : {admin.id_administrateur}")

if __name__ == "__main__":
    seed_admin()
