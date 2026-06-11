from sqlmodel import Session, select
from app.core.database import engine
from app.models.formation import Formation
from app.models.filiere import Filiere
from app.models.score_compatibilite import ScoreCompatibilite
from app.models.recommandation import Recommandation
from app.models.favoris import Favoris

def reset():
    with Session(engine) as session:
        for sc in session.exec(select(ScoreCompatibilite)).all(): session.delete(sc)
        for r in session.exec(select(Recommandation)).all(): session.delete(r)
        for fv in session.exec(select(Favoris)).all(): session.delete(fv)
        for fo in session.exec(select(Formation)).all(): session.delete(fo)
        for f in session.exec(select(Filiere)).all(): session.delete(f)
        session.commit()
        print("Tables vidées.")

if __name__ == "__main__":
    reset()