from sqlmodel import Session, select
from app.core.database import engine
from app.models.bachelier import Bachelier
from app.models.profil_psychometrique import ProfilPsychometrique
from app.models.recommandation import Recommandation
from app.models.score_compatibilite import ScoreCompatibilite
from app.models.favoris import Favoris

EMAIL = "dayan2620060@gmail.com"

with Session(engine) as session:
    bachelier = session.exec(
        select(Bachelier).where(Bachelier.email == EMAIL)
    ).first()

    if not bachelier:
        print(f"Aucun compte trouvé pour {EMAIL}")
    else:
        id_bachelier = bachelier.id_bachelier

        # Supprimer les recommandations + scores liés
        recos = session.exec(
            select(Recommandation).where(Recommandation.id_bachelier == id_bachelier)
        ).all()
        for r in recos:
            scores = session.exec(
                select(ScoreCompatibilite).where(ScoreCompatibilite.id_recommandation == r.id_recommandation)
            ).all()
            for s in scores:
                session.delete(s)
            session.delete(r)

        # Supprimer le profil psychométrique
        profil = session.exec(
            select(ProfilPsychometrique).where(ProfilPsychometrique.id_bachelier == id_bachelier)
        ).first()
        if profil:
            session.delete(profil)

        # Supprimer les favoris
        favs = session.exec(
            select(Favoris).where(Favoris.id_bachelier == id_bachelier)
        ).all()
        for f in favs:
            session.delete(f)

        # Supprimer le bachelier
        session.delete(bachelier)
        session.commit()
        print(f"✅ Compte {EMAIL} et toutes ses données supprimés.")