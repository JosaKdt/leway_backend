from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS notification (
            id_notification UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            destinataire_id UUID NOT NULL,
            destinataire_role VARCHAR(20) NOT NULL,
            type VARCHAR(50) NOT NULL,
            titre VARCHAR(200) NOT NULL,
            message TEXT NOT NULL,
            lu BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_notif_destinataire ON notification(destinataire_id, lu)"))
    conn.commit()
    print('Table notification créée')