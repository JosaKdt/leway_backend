"""
Migration manuelle : ajout des nouveaux champs à la table filiere
Usage: python add_filiere_fields.py
"""
from app.core.database import engine
from sqlalchemy import text

SQL = """
ALTER TABLE filiere
    ADD COLUMN IF NOT EXISTS description         TEXT,
    ADD COLUMN IF NOT EXISTS debouches           JSONB,
    ADD COLUMN IF NOT EXISTS niveau_admission    VARCHAR(20),
    ADD COLUMN IF NOT EXISTS accreditation_mesrs BOOLEAN,
    ADD COLUMN IF NOT EXISTS accreditation_cames BOOLEAN,
    ADD COLUMN IF NOT EXISTS cout_annuel_min     INTEGER,
    ADD COLUMN IF NOT EXISTS cout_annuel_max     INTEGER,
    ADD COLUMN IF NOT EXISTS langue_enseignement VARCHAR(20),
    ADD COLUMN IF NOT EXISTS taux_reussite       FLOAT,
    ADD COLUMN IF NOT EXISTS popularite          INTEGER NOT NULL DEFAULT 0;
"""

with engine.connect() as conn:
    conn.execute(text(SQL))
    conn.commit()
    print("✅ Colonnes ajoutées à la table filiere")

    # Vérification
    result = conn.execute(text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'filiere'
        ORDER BY ordinal_position;
    """))
    print("\nColonnes de la table filiere :")
    for row in result:
        print(f"  {row[0]:35s} {row[1]}")
