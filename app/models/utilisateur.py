from sqlmodel import SQLModel


class UtilisateurBase(SQLModel):
    """
    Classe de base partagée entre Bachelier et Administrateur.
    Représente les attributs communs décrits dans le diagramme de classes ORIAB.
    Non mappée en table — utilisée uniquement comme contrat de schéma.
    """
    email: str
    mot_de_passe_hash: str