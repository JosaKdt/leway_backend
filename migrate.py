from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE filiere ADD COLUMN IF NOT EXISTS statut VARCHAR(20) DEFAULT 'active' NOT NULL"))
    conn.commit()
    print('Colonne statut ajoutee')