"""
migration_complete.py
Migration complète : tous les champs Filiere v7 + table notification
Idempotent (ADD COLUMN IF NOT EXISTS)
"""
from app.core.database import engine
from sqlalchemy import text

SQL_FILIERE = """
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
    ADD COLUMN IF NOT EXISTS popularite          INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS statut              VARCHAR(20) DEFAULT 'active';
"""

SQL_NOTIF = """
CREATE TABLE IF NOT EXISTS notification (
    id_notification UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    destinataire_id UUID NOT NULL,
    destinataire_role VARCHAR(20) NOT NULL,
    type VARCHAR(50) NOT NULL,
    titre VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    lu BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_notif_destinataire ON notification(destinataire_id, lu);
"""

with engine.connect() as conn:
    print("Migration table filiere...")
    conn.execute(text(SQL_FILIERE))
    conn.commit()
    print("  ✅ Colonnes Filiere v7 ajoutées")

    print("Migration table notification...")
    conn.execute(text(SQL_NOTIF))
    conn.commit()
    print("  ✅ Table notification créée")

    # Vérification
    cols = conn.execute(text(
        "SELECT column_name FROM information_schema.columns WHERE table_name='filiere' ORDER BY ordinal_position"
    )).fetchall()
    print(f"\nTable filiere — {len(cols)} colonnes :")
    for c in cols:
        print(f"  {c[0]}")

print("\n✅ Migration complète OK")
