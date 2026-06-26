from app.core.database import engine
from sqlmodel import Session, text

with Session(engine) as s:
    result = s.exec(text("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """))
    for row in result:
        print(row)