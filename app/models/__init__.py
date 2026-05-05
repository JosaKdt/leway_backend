# Import de tous les modèles pour que SQLModel.metadata.create_all() les découvre
from app.models.bachelier import Bachelier, BachelierCreate, BachelierRead
from app.models.administrateur import Administrateur, AdministrateurCreate, AdministrateurRead
from app.models.profil_psychometrique import ProfilPsychometrique, ProfilPsychometriqueRead
from app.models.filiere import Filiere, FiliereCreate, FiliereRead
from app.models.universite import Universite, UniversiteCreate, UniversiteRead
from app.models.formation import Formation, FormationCreate, FormationRead
from app.models.recommandation import Recommandation, RecommandationRead
from app.models.score_compatibilite import ScoreCompatibilite, ScoreCompatibiliteRead
from app.models.favoris import Favoris, FavorisCreate, FavorisRead

__all__ = [
    # Tables
    "Bachelier", "Administrateur", "ProfilPsychometrique",
    "Filiere", "Universite", "Formation",
    "Recommandation", "ScoreCompatibilite", "Favoris",
    # Schémas Create
    "BachelierCreate", "AdministrateurCreate",
    "FiliereCreate", "UniversiteCreate", "FormationCreate",
    "FavorisCreate",
    # Schémas Read
    "BachelierRead", "AdministrateurRead", "ProfilPsychometriqueRead",
    "FiliereRead", "UniversiteRead", "FormationRead",
    "RecommandationRead", "ScoreCompatibiliteRead", "FavorisRead",
]
