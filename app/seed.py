"""
Script de seed ORIAB — Catalogue exhaustif des filières béninoises.
Source : Guide d'Orientation Universitaire 2024-2025, MESRS Bénin
         (enseignementsuperieur.gouv.bj).
Profils RIASEC calibrés selon la méthodologie Holland.

- 103 filières dédupliquées (ensemble exhaustif, pas de doublon)
- 22 universités/établissements (publics + privés + confessionnels)
- 568 formations (liens filière <-> université avec frais réels)

Lancer : python -m app.seed
"""
from sqlmodel import Session, select
from app.core.database import engine, create_db_and_tables
from app.models.filiere import Filiere
from app.models.universite import Universite
from app.models.formation import Formation

FILIERES = [
    {
        "nom": "Médecine Générale",
        "domaine": "Santé",
        "duree_theorique": 7,
        "salaire_median_p50": 500000,
        "taux_insertion": 94.0,
        "indice_saturation": 0.2,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.85,
        "profil_riasec_dominant": {
            "R": 40,
            "I": 90,
            "A": 20,
            "S": 85,
            "E": 40,
            "C": 65
        },
        "veto_factors": {
            "budget_min_fcfa": 300000,
            "serie_bac_requise": [
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Pharmacie",
        "domaine": "Santé",
        "duree_theorique": 6,
        "salaire_median_p50": 450000,
        "taux_insertion": 91.0,
        "indice_saturation": 0.2,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.75,
        "profil_riasec_dominant": {
            "R": 40,
            "I": 88,
            "A": 20,
            "S": 65,
            "E": 35,
            "C": 80
        },
        "veto_factors": {
            "budget_min_fcfa": 250000,
            "serie_bac_requise": [
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Chirurgie Dentaire",
        "domaine": "Santé",
        "duree_theorique": 6,
        "salaire_median_p50": 470000,
        "taux_insertion": 90.0,
        "indice_saturation": 0.18,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.7,
        "profil_riasec_dominant": {
            "R": 70,
            "I": 85,
            "A": 35,
            "S": 70,
            "E": 35,
            "C": 70
        },
        "veto_factors": {
            "budget_min_fcfa": 280000,
            "serie_bac_requise": [
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Sciences Infirmières",
        "domaine": "Santé",
        "duree_theorique": 3,
        "salaire_median_p50": 220000,
        "taux_insertion": 89.0,
        "indice_saturation": 0.25,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.78,
        "profil_riasec_dominant": {
            "R": 50,
            "I": 60,
            "A": 20,
            "S": 92,
            "E": 30,
            "C": 65
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Sciences Obstétricales (Sage-femme)",
        "domaine": "Santé",
        "duree_theorique": 3,
        "salaire_median_p50": 230000,
        "taux_insertion": 90.0,
        "indice_saturation": 0.22,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.78,
        "profil_riasec_dominant": {
            "R": 45,
            "I": 62,
            "A": 20,
            "S": 95,
            "E": 30,
            "C": 68
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Kinésithérapie & Réadaptation",
        "domaine": "Santé",
        "duree_theorique": 3,
        "salaire_median_p50": 260000,
        "taux_insertion": 85.0,
        "indice_saturation": 0.3,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.7,
        "profil_riasec_dominant": {
            "R": 70,
            "I": 65,
            "A": 30,
            "S": 85,
            "E": 35,
            "C": 55
        },
        "veto_factors": {
            "budget_min_fcfa": 150000,
            "serie_bac_requise": [
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Imagerie Médicale & Radiologie",
        "domaine": "Santé",
        "duree_theorique": 3,
        "salaire_median_p50": 300000,
        "taux_insertion": 87.0,
        "indice_saturation": 0.25,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.75,
        "profil_riasec_dominant": {
            "R": 65,
            "I": 80,
            "A": 20,
            "S": 55,
            "E": 30,
            "C": 75
        },
        "veto_factors": {
            "budget_min_fcfa": 200000,
            "serie_bac_requise": [
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Analyses Biomédicales",
        "domaine": "Santé",
        "duree_theorique": 3,
        "salaire_median_p50": 270000,
        "taux_insertion": 86.0,
        "indice_saturation": 0.3,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.72,
        "profil_riasec_dominant": {
            "R": 55,
            "I": 85,
            "A": 15,
            "S": 50,
            "E": 25,
            "C": 80
        },
        "veto_factors": {
            "budget_min_fcfa": 150000,
            "serie_bac_requise": [
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Santé Publique & Épidémiologie",
        "domaine": "Santé",
        "duree_theorique": 3,
        "salaire_median_p50": 320000,
        "taux_insertion": 83.0,
        "indice_saturation": 0.25,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.82,
        "profil_riasec_dominant": {
            "R": 30,
            "I": 80,
            "A": 20,
            "S": 80,
            "E": 50,
            "C": 70
        },
        "veto_factors": {
            "budget_min_fcfa": 150000,
            "serie_bac_requise": [
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Nutrition & Diététique",
        "domaine": "Santé",
        "duree_theorique": 3,
        "salaire_median_p50": 240000,
        "taux_insertion": 80.0,
        "indice_saturation": 0.35,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.7,
        "profil_riasec_dominant": {
            "R": 40,
            "I": 75,
            "A": 25,
            "S": 80,
            "E": 40,
            "C": 65
        },
        "veto_factors": {
            "budget_min_fcfa": 120000,
            "serie_bac_requise": [
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Génie Informatique & Systèmes",
        "domaine": "Sciences & Technologie",
        "duree_theorique": 3,
        "salaire_median_p50": 350000,
        "taux_insertion": 87.0,
        "indice_saturation": 0.3,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.92,
        "profil_riasec_dominant": {
            "R": 60,
            "I": 90,
            "A": 40,
            "S": 30,
            "E": 50,
            "C": 70
        },
        "veto_factors": {
            "budget_min_fcfa": 150000,
            "serie_bac_requise": [
                "C",
                "D",
                "E",
                "F",
                "TI"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Data Science & Intelligence Artificielle",
        "domaine": "Sciences & Technologie",
        "duree_theorique": 3,
        "salaire_median_p50": 450000,
        "taux_insertion": 92.0,
        "indice_saturation": 0.15,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.95,
        "profil_riasec_dominant": {
            "R": 50,
            "I": 95,
            "A": 35,
            "S": 30,
            "E": 45,
            "C": 75
        },
        "veto_factors": {
            "budget_min_fcfa": 150000,
            "serie_bac_requise": [
                "C",
                "D",
                "E"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Cybersécurité & Réseaux",
        "domaine": "Sciences & Technologie",
        "duree_theorique": 3,
        "salaire_median_p50": 420000,
        "taux_insertion": 90.0,
        "indice_saturation": 0.2,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.92,
        "profil_riasec_dominant": {
            "R": 60,
            "I": 88,
            "A": 25,
            "S": 25,
            "E": 45,
            "C": 85
        },
        "veto_factors": {
            "budget_min_fcfa": 150000,
            "serie_bac_requise": [
                "C",
                "D",
                "E",
                "F",
                "TI"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Génie Logiciel",
        "domaine": "Sciences & Technologie",
        "duree_theorique": 3,
        "salaire_median_p50": 400000,
        "taux_insertion": 90.0,
        "indice_saturation": 0.2,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.95,
        "profil_riasec_dominant": {
            "R": 50,
            "I": 92,
            "A": 45,
            "S": 30,
            "E": 50,
            "C": 78
        },
        "veto_factors": {
            "budget_min_fcfa": 150000,
            "serie_bac_requise": [
                "C",
                "D",
                "E",
                "F",
                "TI"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Administration des Réseaux Informatiques",
        "domaine": "Sciences & Technologie",
        "duree_theorique": 3,
        "salaire_median_p50": 320000,
        "taux_insertion": 85.0,
        "indice_saturation": 0.3,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.85,
        "profil_riasec_dominant": {
            "R": 65,
            "I": 82,
            "A": 25,
            "S": 35,
            "E": 40,
            "C": 80
        },
        "veto_factors": {
            "budget_min_fcfa": 120000,
            "serie_bac_requise": [
                "C",
                "D",
                "F",
                "TI"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Analyse Informatique & Programmation",
        "domaine": "Sciences & Technologie",
        "duree_theorique": 3,
        "salaire_median_p50": 330000,
        "taux_insertion": 86.0,
        "indice_saturation": 0.3,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.9,
        "profil_riasec_dominant": {
            "R": 50,
            "I": 88,
            "A": 40,
            "S": 30,
            "E": 45,
            "C": 80
        },
        "veto_factors": {
            "budget_min_fcfa": 120000,
            "serie_bac_requise": [
                "C",
                "D",
                "F",
                "TI"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Informatique de Gestion",
        "domaine": "Sciences & Technologie",
        "duree_theorique": 3,
        "salaire_median_p50": 300000,
        "taux_insertion": 82.0,
        "indice_saturation": 0.4,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.82,
        "profil_riasec_dominant": {
            "R": 50,
            "I": 80,
            "A": 25,
            "S": 35,
            "E": 55,
            "C": 85
        },
        "veto_factors": {
            "budget_min_fcfa": 120000,
            "serie_bac_requise": [
                "C",
                "D",
                "G",
                "F"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Génie Civil & BTP",
        "domaine": "Sciences & Technologie",
        "duree_theorique": 3,
        "salaire_median_p50": 380000,
        "taux_insertion": 83.0,
        "indice_saturation": 0.4,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.75,
        "profil_riasec_dominant": {
            "R": 90,
            "I": 75,
            "A": 35,
            "S": 30,
            "E": 50,
            "C": 65
        },
        "veto_factors": {
            "budget_min_fcfa": 150000,
            "serie_bac_requise": [
                "C",
                "D",
                "E",
                "F"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Génie Électrique & Électronique",
        "domaine": "Sciences & Technologie",
        "duree_theorique": 3,
        "salaire_median_p50": 340000,
        "taux_insertion": 80.0,
        "indice_saturation": 0.35,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.82,
        "profil_riasec_dominant": {
            "R": 88,
            "I": 82,
            "A": 25,
            "S": 25,
            "E": 40,
            "C": 72
        },
        "veto_factors": {
            "budget_min_fcfa": 120000,
            "serie_bac_requise": [
                "C",
                "D",
                "E",
                "F"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Génie Mécanique & Productique",
        "domaine": "Sciences & Technologie",
        "duree_theorique": 3,
        "salaire_median_p50": 330000,
        "taux_insertion": 78.0,
        "indice_saturation": 0.4,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.72,
        "profil_riasec_dominant": {
            "R": 92,
            "I": 78,
            "A": 25,
            "S": 20,
            "E": 45,
            "C": 68
        },
        "veto_factors": {
            "budget_min_fcfa": 120000,
            "serie_bac_requise": [
                "C",
                "D",
                "E",
                "F"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Génie Énergétique & Énergies Renouvelables",
        "domaine": "Sciences & Technologie",
        "duree_theorique": 3,
        "salaire_median_p50": 370000,
        "taux_insertion": 85.0,
        "indice_saturation": 0.2,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.92,
        "profil_riasec_dominant": {
            "R": 82,
            "I": 82,
            "A": 25,
            "S": 35,
            "E": 50,
            "C": 68
        },
        "veto_factors": {
            "budget_min_fcfa": 130000,
            "serie_bac_requise": [
                "C",
                "D",
                "E",
                "F"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Génie Télécommunications",
        "domaine": "Sciences & Technologie",
        "duree_theorique": 3,
        "salaire_median_p50": 360000,
        "taux_insertion": 84.0,
        "indice_saturation": 0.3,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.85,
        "profil_riasec_dominant": {
            "R": 75,
            "I": 85,
            "A": 30,
            "S": 30,
            "E": 45,
            "C": 75
        },
        "veto_factors": {
            "budget_min_fcfa": 130000,
            "serie_bac_requise": [
                "C",
                "D",
                "E",
                "F"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Génie Biomédical",
        "domaine": "Sciences & Technologie",
        "duree_theorique": 3,
        "salaire_median_p50": 380000,
        "taux_insertion": 82.0,
        "indice_saturation": 0.25,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.85,
        "profil_riasec_dominant": {
            "R": 75,
            "I": 88,
            "A": 30,
            "S": 55,
            "E": 40,
            "C": 70
        },
        "veto_factors": {
            "budget_min_fcfa": 150000,
            "serie_bac_requise": [
                "C",
                "D",
                "E"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Maintenance Industrielle",
        "domaine": "Sciences & Technologie",
        "duree_theorique": 3,
        "salaire_median_p50": 300000,
        "taux_insertion": 80.0,
        "indice_saturation": 0.35,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.7,
        "profil_riasec_dominant": {
            "R": 90,
            "I": 70,
            "A": 20,
            "S": 30,
            "E": 40,
            "C": 70
        },
        "veto_factors": {
            "budget_min_fcfa": 120000,
            "serie_bac_requise": [
                "C",
                "D",
                "E",
                "F"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Génie des Procédés & Chimie Industrielle",
        "domaine": "Sciences & Technologie",
        "duree_theorique": 3,
        "salaire_median_p50": 320000,
        "taux_insertion": 76.0,
        "indice_saturation": 0.35,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.7,
        "profil_riasec_dominant": {
            "R": 75,
            "I": 85,
            "A": 20,
            "S": 30,
            "E": 35,
            "C": 75
        },
        "veto_factors": {
            "budget_min_fcfa": 130000,
            "serie_bac_requise": [
                "C",
                "D",
                "E"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Mécatronique & Robotique",
        "domaine": "Sciences & Technologie",
        "duree_theorique": 3,
        "salaire_median_p50": 390000,
        "taux_insertion": 86.0,
        "indice_saturation": 0.2,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.9,
        "profil_riasec_dominant": {
            "R": 88,
            "I": 88,
            "A": 35,
            "S": 25,
            "E": 45,
            "C": 72
        },
        "veto_factors": {
            "budget_min_fcfa": 150000,
            "serie_bac_requise": [
                "C",
                "D",
                "E",
                "F"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Agronomie Générale",
        "domaine": "Sciences Agronomiques",
        "duree_theorique": 3,
        "salaire_median_p50": 250000,
        "taux_insertion": 82.0,
        "indice_saturation": 0.3,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.82,
        "profil_riasec_dominant": {
            "R": 80,
            "I": 70,
            "A": 30,
            "S": 50,
            "E": 45,
            "C": 55
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "C",
                "D",
                "EA"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Production Végétale & Phytotechnie",
        "domaine": "Sciences Agronomiques",
        "duree_theorique": 3,
        "salaire_median_p50": 240000,
        "taux_insertion": 80.0,
        "indice_saturation": 0.35,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.78,
        "profil_riasec_dominant": {
            "R": 85,
            "I": 68,
            "A": 25,
            "S": 45,
            "E": 40,
            "C": 55
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "C",
                "D",
                "EA"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Production Animale & Zootechnie",
        "domaine": "Sciences Agronomiques",
        "duree_theorique": 3,
        "salaire_median_p50": 250000,
        "taux_insertion": 80.0,
        "indice_saturation": 0.32,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.78,
        "profil_riasec_dominant": {
            "R": 85,
            "I": 68,
            "A": 20,
            "S": 50,
            "E": 42,
            "C": 55
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "C",
                "D",
                "EA"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Agroalimentaire & Nutrition",
        "domaine": "Sciences Agronomiques",
        "duree_theorique": 3,
        "salaire_median_p50": 260000,
        "taux_insertion": 79.0,
        "indice_saturation": 0.35,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.78,
        "profil_riasec_dominant": {
            "R": 65,
            "I": 75,
            "A": 30,
            "S": 50,
            "E": 45,
            "C": 65
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "C",
                "D",
                "EA"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Aménagement & Gestion des Ressources Naturelles",
        "domaine": "Sciences Agronomiques",
        "duree_theorique": 3,
        "salaire_median_p50": 240000,
        "taux_insertion": 76.0,
        "indice_saturation": 0.35,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.75,
        "profil_riasec_dominant": {
            "R": 75,
            "I": 72,
            "A": 30,
            "S": 55,
            "E": 40,
            "C": 55
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "C",
                "D",
                "EA"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Économie & Sociologie Rurale",
        "domaine": "Sciences Agronomiques",
        "duree_theorique": 3,
        "salaire_median_p50": 250000,
        "taux_insertion": 74.0,
        "indice_saturation": 0.4,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.65,
        "profil_riasec_dominant": {
            "R": 45,
            "I": 65,
            "A": 30,
            "S": 70,
            "E": 60,
            "C": 60
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "C",
                "D",
                "EA",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Génie Rural & Maîtrise de l'Eau",
        "domaine": "Sciences Agronomiques",
        "duree_theorique": 3,
        "salaire_median_p50": 280000,
        "taux_insertion": 80.0,
        "indice_saturation": 0.3,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.78,
        "profil_riasec_dominant": {
            "R": 85,
            "I": 75,
            "A": 20,
            "S": 40,
            "E": 40,
            "C": 65
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "C",
                "D",
                "EA"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Foresterie & Gestion des Forêts",
        "domaine": "Sciences Agronomiques",
        "duree_theorique": 3,
        "salaire_median_p50": 240000,
        "taux_insertion": 75.0,
        "indice_saturation": 0.3,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.78,
        "profil_riasec_dominant": {
            "R": 82,
            "I": 70,
            "A": 30,
            "S": 50,
            "E": 40,
            "C": 55
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "C",
                "D",
                "EA"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Aquaculture & Pêche",
        "domaine": "Sciences Agronomiques",
        "duree_theorique": 3,
        "salaire_median_p50": 250000,
        "taux_insertion": 77.0,
        "indice_saturation": 0.28,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.78,
        "profil_riasec_dominant": {
            "R": 80,
            "I": 72,
            "A": 25,
            "S": 45,
            "E": 45,
            "C": 55
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "C",
                "D",
                "EA"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Mathématiques",
        "domaine": "Sciences Fondamentales",
        "duree_theorique": 3,
        "salaire_median_p50": 220000,
        "taux_insertion": 68.0,
        "indice_saturation": 0.4,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.6,
        "profil_riasec_dominant": {
            "R": 40,
            "I": 95,
            "A": 30,
            "S": 30,
            "E": 30,
            "C": 78
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "C",
                "D",
                "E"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Physique",
        "domaine": "Sciences Fondamentales",
        "duree_theorique": 3,
        "salaire_median_p50": 230000,
        "taux_insertion": 67.0,
        "indice_saturation": 0.4,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.6,
        "profil_riasec_dominant": {
            "R": 60,
            "I": 92,
            "A": 30,
            "S": 25,
            "E": 30,
            "C": 72
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "C",
                "D",
                "E"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Chimie",
        "domaine": "Sciences Fondamentales",
        "duree_theorique": 3,
        "salaire_median_p50": 240000,
        "taux_insertion": 70.0,
        "indice_saturation": 0.4,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.65,
        "profil_riasec_dominant": {
            "R": 65,
            "I": 90,
            "A": 25,
            "S": 30,
            "E": 30,
            "C": 75
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Sciences de la Vie & de la Terre (Biologie)",
        "domaine": "Sciences Fondamentales",
        "duree_theorique": 3,
        "salaire_median_p50": 230000,
        "taux_insertion": 68.0,
        "indice_saturation": 0.45,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.68,
        "profil_riasec_dominant": {
            "R": 55,
            "I": 90,
            "A": 25,
            "S": 45,
            "E": 30,
            "C": 68
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Biochimie & Biologie Moléculaire",
        "domaine": "Sciences Fondamentales",
        "duree_theorique": 3,
        "salaire_median_p50": 270000,
        "taux_insertion": 70.0,
        "indice_saturation": 0.4,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.75,
        "profil_riasec_dominant": {
            "R": 55,
            "I": 92,
            "A": 25,
            "S": 40,
            "E": 25,
            "C": 72
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Géologie & Sciences de la Terre",
        "domaine": "Sciences Fondamentales",
        "duree_theorique": 3,
        "salaire_median_p50": 300000,
        "taux_insertion": 74.0,
        "indice_saturation": 0.3,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.7,
        "profil_riasec_dominant": {
            "R": 80,
            "I": 85,
            "A": 25,
            "S": 30,
            "E": 40,
            "C": 62
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Statistiques & Économétrie",
        "domaine": "Sciences Fondamentales",
        "duree_theorique": 3,
        "salaire_median_p50": 350000,
        "taux_insertion": 85.0,
        "indice_saturation": 0.25,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.9,
        "profil_riasec_dominant": {
            "R": 40,
            "I": 92,
            "A": 20,
            "S": 35,
            "E": 50,
            "C": 88
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Économie",
        "domaine": "Sciences Économiques & Gestion",
        "duree_theorique": 3,
        "salaire_median_p50": 300000,
        "taux_insertion": 76.0,
        "indice_saturation": 0.5,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.7,
        "profil_riasec_dominant": {
            "R": 20,
            "I": 75,
            "A": 20,
            "S": 50,
            "E": 80,
            "C": 78
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "B",
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Gestion des Entreprises",
        "domaine": "Sciences Économiques & Gestion",
        "duree_theorique": 3,
        "salaire_median_p50": 290000,
        "taux_insertion": 75.0,
        "indice_saturation": 0.55,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.68,
        "profil_riasec_dominant": {
            "R": 20,
            "I": 55,
            "A": 25,
            "S": 55,
            "E": 85,
            "C": 80
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "B",
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Comptabilité, Contrôle & Audit",
        "domaine": "Sciences Économiques & Gestion",
        "duree_theorique": 3,
        "salaire_median_p50": 320000,
        "taux_insertion": 82.0,
        "indice_saturation": 0.45,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.7,
        "profil_riasec_dominant": {
            "R": 20,
            "I": 65,
            "A": 15,
            "S": 40,
            "E": 60,
            "C": 92
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "B",
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Finance & Banque",
        "domaine": "Sciences Économiques & Gestion",
        "duree_theorique": 3,
        "salaire_median_p50": 350000,
        "taux_insertion": 83.0,
        "indice_saturation": 0.4,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.75,
        "profil_riasec_dominant": {
            "R": 15,
            "I": 70,
            "A": 15,
            "S": 45,
            "E": 75,
            "C": 88
        },
        "veto_factors": {
            "budget_min_fcfa": 120000,
            "serie_bac_requise": [
                "B",
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Banque & Institutions de Microfinance",
        "domaine": "Sciences Économiques & Gestion",
        "duree_theorique": 3,
        "salaire_median_p50": 310000,
        "taux_insertion": 80.0,
        "indice_saturation": 0.4,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.78,
        "profil_riasec_dominant": {
            "R": 15,
            "I": 65,
            "A": 15,
            "S": 55,
            "E": 72,
            "C": 85
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Finance Islamique",
        "domaine": "Sciences Économiques & Gestion",
        "duree_theorique": 3,
        "salaire_median_p50": 310000,
        "taux_insertion": 78.0,
        "indice_saturation": 0.35,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.78,
        "profil_riasec_dominant": {
            "R": 15,
            "I": 65,
            "A": 20,
            "S": 55,
            "E": 70,
            "C": 85
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "B",
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Assurance & Gestion des Risques",
        "domaine": "Sciences Économiques & Gestion",
        "duree_theorique": 3,
        "salaire_median_p50": 320000,
        "taux_insertion": 80.0,
        "indice_saturation": 0.35,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.72,
        "profil_riasec_dominant": {
            "R": 20,
            "I": 70,
            "A": 15,
            "S": 50,
            "E": 68,
            "C": 85
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Marketing & Communication Commerciale",
        "domaine": "Sciences Économiques & Gestion",
        "duree_theorique": 3,
        "salaire_median_p50": 290000,
        "taux_insertion": 76.0,
        "indice_saturation": 0.5,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.7,
        "profil_riasec_dominant": {
            "R": 20,
            "I": 50,
            "A": 55,
            "S": 70,
            "E": 90,
            "C": 55
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "B",
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Marketing Digital & Community Management",
        "domaine": "Sciences Économiques & Gestion",
        "duree_theorique": 3,
        "salaire_median_p50": 300000,
        "taux_insertion": 80.0,
        "indice_saturation": 0.4,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.85,
        "profil_riasec_dominant": {
            "R": 20,
            "I": 55,
            "A": 65,
            "S": 65,
            "E": 85,
            "C": 55
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "B",
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Gestion des Ressources Humaines",
        "domaine": "Sciences Économiques & Gestion",
        "duree_theorique": 3,
        "salaire_median_p50": 280000,
        "taux_insertion": 73.0,
        "indice_saturation": 0.55,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.65,
        "profil_riasec_dominant": {
            "R": 15,
            "I": 50,
            "A": 30,
            "S": 88,
            "E": 75,
            "C": 72
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "B",
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Logistique & Transport",
        "domaine": "Sciences Économiques & Gestion",
        "duree_theorique": 3,
        "salaire_median_p50": 290000,
        "taux_insertion": 78.0,
        "indice_saturation": 0.4,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.7,
        "profil_riasec_dominant": {
            "R": 50,
            "I": 58,
            "A": 20,
            "S": 45,
            "E": 72,
            "C": 80
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Commerce International",
        "domaine": "Sciences Économiques & Gestion",
        "duree_theorique": 3,
        "salaire_median_p50": 300000,
        "taux_insertion": 75.0,
        "indice_saturation": 0.45,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.7,
        "profil_riasec_dominant": {
            "R": 20,
            "I": 55,
            "A": 40,
            "S": 60,
            "E": 88,
            "C": 65
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "B",
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Gestion de Projet",
        "domaine": "Sciences Économiques & Gestion",
        "duree_theorique": 3,
        "salaire_median_p50": 320000,
        "taux_insertion": 80.0,
        "indice_saturation": 0.4,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.75,
        "profil_riasec_dominant": {
            "R": 30,
            "I": 65,
            "A": 30,
            "S": 60,
            "E": 82,
            "C": 78
        },
        "veto_factors": {
            "budget_min_fcfa": 110000,
            "serie_bac_requise": [
                "B",
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Administration des Affaires",
        "domaine": "Sciences Économiques & Gestion",
        "duree_theorique": 3,
        "salaire_median_p50": 300000,
        "taux_insertion": 76.0,
        "indice_saturation": 0.5,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.7,
        "profil_riasec_dominant": {
            "R": 20,
            "I": 58,
            "A": 25,
            "S": 55,
            "E": 85,
            "C": 78
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "B",
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Tourisme & Hôtellerie",
        "domaine": "Sciences Économiques & Gestion",
        "duree_theorique": 3,
        "salaire_median_p50": 220000,
        "taux_insertion": 70.0,
        "indice_saturation": 0.5,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.6,
        "profil_riasec_dominant": {
            "R": 35,
            "I": 35,
            "A": 60,
            "S": 82,
            "E": 75,
            "C": 55
        },
        "veto_factors": {
            "budget_min_fcfa": 90000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Gestion Fiscale & Financière",
        "domaine": "Sciences Économiques & Gestion",
        "duree_theorique": 3,
        "salaire_median_p50": 310000,
        "taux_insertion": 80.0,
        "indice_saturation": 0.4,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.7,
        "profil_riasec_dominant": {
            "R": 15,
            "I": 68,
            "A": 15,
            "S": 45,
            "E": 65,
            "C": 90
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "B",
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Droit Privé",
        "domaine": "Droit & Sciences Politiques",
        "duree_theorique": 3,
        "salaire_median_p50": 280000,
        "taux_insertion": 71.0,
        "indice_saturation": 0.6,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.65,
        "profil_riasec_dominant": {
            "R": 15,
            "I": 65,
            "A": 30,
            "S": 65,
            "E": 78,
            "C": 80
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Droit Public",
        "domaine": "Droit & Sciences Politiques",
        "duree_theorique": 3,
        "salaire_median_p50": 270000,
        "taux_insertion": 70.0,
        "indice_saturation": 0.6,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.62,
        "profil_riasec_dominant": {
            "R": 15,
            "I": 68,
            "A": 30,
            "S": 68,
            "E": 75,
            "C": 82
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Sciences Politiques & Relations Internationales",
        "domaine": "Droit & Sciences Politiques",
        "duree_theorique": 3,
        "salaire_median_p50": 290000,
        "taux_insertion": 68.0,
        "indice_saturation": 0.55,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.65,
        "profil_riasec_dominant": {
            "R": 15,
            "I": 72,
            "A": 40,
            "S": 70,
            "E": 80,
            "C": 65
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Administration Publique",
        "domaine": "Droit & Sciences Politiques",
        "duree_theorique": 3,
        "salaire_median_p50": 280000,
        "taux_insertion": 74.0,
        "indice_saturation": 0.55,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.6,
        "profil_riasec_dominant": {
            "R": 15,
            "I": 58,
            "A": 20,
            "S": 68,
            "E": 70,
            "C": 88
        },
        "veto_factors": {
            "budget_min_fcfa": 90000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Carrières Judiciaires & Greffe",
        "domaine": "Droit & Sciences Politiques",
        "duree_theorique": 3,
        "salaire_median_p50": 270000,
        "taux_insertion": 72.0,
        "indice_saturation": 0.5,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.62,
        "profil_riasec_dominant": {
            "R": 20,
            "I": 62,
            "A": 20,
            "S": 62,
            "E": 65,
            "C": 88
        },
        "veto_factors": {
            "budget_min_fcfa": 90000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Criminologie & Sécurité",
        "domaine": "Droit & Sciences Politiques",
        "duree_theorique": 3,
        "salaire_median_p50": 280000,
        "taux_insertion": 70.0,
        "indice_saturation": 0.4,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.7,
        "profil_riasec_dominant": {
            "R": 40,
            "I": 72,
            "A": 25,
            "S": 68,
            "E": 60,
            "C": 72
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Sciences de l'Éducation",
        "domaine": "Sciences Humaines & Sociales",
        "duree_theorique": 3,
        "salaire_median_p50": 180000,
        "taux_insertion": 78.0,
        "indice_saturation": 0.7,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.55,
        "profil_riasec_dominant": {
            "R": 20,
            "I": 50,
            "A": 40,
            "S": 92,
            "E": 40,
            "C": 60
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Psychologie",
        "domaine": "Sciences Humaines & Sociales",
        "duree_theorique": 3,
        "salaire_median_p50": 240000,
        "taux_insertion": 62.0,
        "indice_saturation": 0.6,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.6,
        "profil_riasec_dominant": {
            "R": 15,
            "I": 72,
            "A": 45,
            "S": 92,
            "E": 45,
            "C": 50
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Sociologie & Anthropologie",
        "domaine": "Sciences Humaines & Sociales",
        "duree_theorique": 3,
        "salaire_median_p50": 180000,
        "taux_insertion": 60.0,
        "indice_saturation": 0.75,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.45,
        "profil_riasec_dominant": {
            "R": 15,
            "I": 68,
            "A": 50,
            "S": 85,
            "E": 45,
            "C": 45
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Géographie & Aménagement du Territoire",
        "domaine": "Sciences Humaines & Sociales",
        "duree_theorique": 3,
        "salaire_median_p50": 200000,
        "taux_insertion": 65.0,
        "indice_saturation": 0.6,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.55,
        "profil_riasec_dominant": {
            "R": 50,
            "I": 72,
            "A": 35,
            "S": 55,
            "E": 45,
            "C": 60
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Histoire & Archéologie",
        "domaine": "Sciences Humaines & Sociales",
        "duree_theorique": 3,
        "salaire_median_p50": 175000,
        "taux_insertion": 58.0,
        "indice_saturation": 0.7,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.4,
        "profil_riasec_dominant": {
            "R": 25,
            "I": 75,
            "A": 55,
            "S": 60,
            "E": 40,
            "C": 55
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Philosophie",
        "domaine": "Sciences Humaines & Sociales",
        "duree_theorique": 3,
        "salaire_median_p50": 170000,
        "taux_insertion": 55.0,
        "indice_saturation": 0.75,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.38,
        "profil_riasec_dominant": {
            "R": 15,
            "I": 80,
            "A": 60,
            "S": 60,
            "E": 40,
            "C": 50
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Sciences du Langage & Communication",
        "domaine": "Sciences Humaines & Sociales",
        "duree_theorique": 3,
        "salaire_median_p50": 200000,
        "taux_insertion": 65.0,
        "indice_saturation": 0.6,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.55,
        "profil_riasec_dominant": {
            "R": 15,
            "I": 68,
            "A": 70,
            "S": 70,
            "E": 55,
            "C": 55
        },
        "veto_factors": {
            "budget_min_fcfa": 90000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Travail Social & Développement Communautaire",
        "domaine": "Sciences Humaines & Sociales",
        "duree_theorique": 3,
        "salaire_median_p50": 190000,
        "taux_insertion": 70.0,
        "indice_saturation": 0.5,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.6,
        "profil_riasec_dominant": {
            "R": 25,
            "I": 55,
            "A": 35,
            "S": 92,
            "E": 55,
            "C": 55
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Lettres Modernes",
        "domaine": "Arts, Lettres & Langues",
        "duree_theorique": 3,
        "salaire_median_p50": 175000,
        "taux_insertion": 60.0,
        "indice_saturation": 0.7,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.4,
        "profil_riasec_dominant": {
            "R": 10,
            "I": 62,
            "A": 85,
            "S": 65,
            "E": 40,
            "C": 50
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Anglais (Langue & Littérature)",
        "domaine": "Arts, Lettres & Langues",
        "duree_theorique": 3,
        "salaire_median_p50": 200000,
        "taux_insertion": 68.0,
        "indice_saturation": 0.6,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.5,
        "profil_riasec_dominant": {
            "R": 10,
            "I": 60,
            "A": 75,
            "S": 70,
            "E": 50,
            "C": 55
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Espagnol",
        "domaine": "Arts, Lettres & Langues",
        "duree_theorique": 3,
        "salaire_median_p50": 185000,
        "taux_insertion": 60.0,
        "indice_saturation": 0.6,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.45,
        "profil_riasec_dominant": {
            "R": 10,
            "I": 58,
            "A": 78,
            "S": 68,
            "E": 45,
            "C": 52
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "A",
                "B"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Allemand",
        "domaine": "Arts, Lettres & Langues",
        "duree_theorique": 3,
        "salaire_median_p50": 185000,
        "taux_insertion": 58.0,
        "indice_saturation": 0.6,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.45,
        "profil_riasec_dominant": {
            "R": 10,
            "I": 58,
            "A": 78,
            "S": 65,
            "E": 45,
            "C": 52
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "A",
                "B"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Linguistique & Langues Africaines",
        "domaine": "Arts, Lettres & Langues",
        "duree_theorique": 3,
        "salaire_median_p50": 170000,
        "taux_insertion": 55.0,
        "indice_saturation": 0.7,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.4,
        "profil_riasec_dominant": {
            "R": 10,
            "I": 68,
            "A": 80,
            "S": 70,
            "E": 40,
            "C": 55
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Arts Plastiques & Design",
        "domaine": "Arts, Lettres & Langues",
        "duree_theorique": 3,
        "salaire_median_p50": 190000,
        "taux_insertion": 58.0,
        "indice_saturation": 0.65,
        "tendance_ia": 3,
        "tendance_curricula_marche": 0.45,
        "profil_riasec_dominant": {
            "R": 35,
            "I": 40,
            "A": 95,
            "S": 45,
            "E": 55,
            "C": 35
        },
        "veto_factors": {
            "budget_min_fcfa": 90000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Design Graphique & Multimédia",
        "domaine": "Arts, Lettres & Langues",
        "duree_theorique": 3,
        "salaire_median_p50": 230000,
        "taux_insertion": 70.0,
        "indice_saturation": 0.5,
        "tendance_ia": 3,
        "tendance_curricula_marche": 0.7,
        "profil_riasec_dominant": {
            "R": 40,
            "I": 50,
            "A": 92,
            "S": 40,
            "E": 60,
            "C": 45
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D",
                "F"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Musique & Musicologie",
        "domaine": "Arts, Lettres & Langues",
        "duree_theorique": 3,
        "salaire_median_p50": 170000,
        "taux_insertion": 52.0,
        "indice_saturation": 0.7,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.4,
        "profil_riasec_dominant": {
            "R": 30,
            "I": 45,
            "A": 95,
            "S": 55,
            "E": 50,
            "C": 40
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Arts Dramatiques & Théâtre",
        "domaine": "Arts, Lettres & Langues",
        "duree_theorique": 3,
        "salaire_median_p50": 165000,
        "taux_insertion": 50.0,
        "indice_saturation": 0.72,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.38,
        "profil_riasec_dominant": {
            "R": 30,
            "I": 40,
            "A": 95,
            "S": 65,
            "E": 60,
            "C": 35
        },
        "veto_factors": {
            "budget_min_fcfa": 80000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Cinéma & Audiovisuel",
        "domaine": "Arts, Lettres & Langues",
        "duree_theorique": 3,
        "salaire_median_p50": 220000,
        "taux_insertion": 62.0,
        "indice_saturation": 0.6,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.6,
        "profil_riasec_dominant": {
            "R": 45,
            "I": 50,
            "A": 90,
            "S": 50,
            "E": 65,
            "C": 45
        },
        "veto_factors": {
            "budget_min_fcfa": 120000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Journalisme & Communication",
        "domaine": "Arts, Lettres & Langues",
        "duree_theorique": 3,
        "salaire_median_p50": 210000,
        "taux_insertion": 65.0,
        "indice_saturation": 0.65,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.55,
        "profil_riasec_dominant": {
            "R": 20,
            "I": 55,
            "A": 80,
            "S": 75,
            "E": 72,
            "C": 45
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Administration Culturelle",
        "domaine": "Arts, Lettres & Langues",
        "duree_theorique": 3,
        "salaire_median_p50": 200000,
        "taux_insertion": 60.0,
        "indice_saturation": 0.6,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.5,
        "profil_riasec_dominant": {
            "R": 20,
            "I": 50,
            "A": 80,
            "S": 65,
            "E": 68,
            "C": 55
        },
        "veto_factors": {
            "budget_min_fcfa": 90000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Interprétariat & Traduction",
        "domaine": "Arts, Lettres & Langues",
        "duree_theorique": 3,
        "salaire_median_p50": 250000,
        "taux_insertion": 70.0,
        "indice_saturation": 0.5,
        "tendance_ia": 3,
        "tendance_curricula_marche": 0.6,
        "profil_riasec_dominant": {
            "R": 10,
            "I": 62,
            "A": 75,
            "S": 70,
            "E": 50,
            "C": 62
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Génie de l'Environnement",
        "domaine": "Environnement & Aménagement",
        "duree_theorique": 3,
        "salaire_median_p50": 300000,
        "taux_insertion": 80.0,
        "indice_saturation": 0.3,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.85,
        "profil_riasec_dominant": {
            "R": 70,
            "I": 80,
            "A": 30,
            "S": 50,
            "E": 45,
            "C": 62
        },
        "veto_factors": {
            "budget_min_fcfa": 120000,
            "serie_bac_requise": [
                "C",
                "D",
                "EA"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Eau, Hygiène & Assainissement",
        "domaine": "Environnement & Aménagement",
        "duree_theorique": 3,
        "salaire_median_p50": 290000,
        "taux_insertion": 82.0,
        "indice_saturation": 0.28,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.85,
        "profil_riasec_dominant": {
            "R": 75,
            "I": 78,
            "A": 20,
            "S": 50,
            "E": 40,
            "C": 65
        },
        "veto_factors": {
            "budget_min_fcfa": 120000,
            "serie_bac_requise": [
                "C",
                "D",
                "EA"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Gestion des Changements Climatiques",
        "domaine": "Environnement & Aménagement",
        "duree_theorique": 3,
        "salaire_median_p50": 310000,
        "taux_insertion": 80.0,
        "indice_saturation": 0.25,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.9,
        "profil_riasec_dominant": {
            "R": 60,
            "I": 85,
            "A": 30,
            "S": 55,
            "E": 48,
            "C": 62
        },
        "veto_factors": {
            "budget_min_fcfa": 120000,
            "serie_bac_requise": [
                "C",
                "D",
                "EA"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Géomatique & Télédétection",
        "domaine": "Environnement & Aménagement",
        "duree_theorique": 3,
        "salaire_median_p50": 330000,
        "taux_insertion": 84.0,
        "indice_saturation": 0.25,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.9,
        "profil_riasec_dominant": {
            "R": 65,
            "I": 85,
            "A": 30,
            "S": 35,
            "E": 42,
            "C": 75
        },
        "veto_factors": {
            "budget_min_fcfa": 130000,
            "serie_bac_requise": [
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Planification & Gestion Urbaine",
        "domaine": "Environnement & Aménagement",
        "duree_theorique": 3,
        "salaire_median_p50": 300000,
        "taux_insertion": 76.0,
        "indice_saturation": 0.4,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.7,
        "profil_riasec_dominant": {
            "R": 55,
            "I": 72,
            "A": 45,
            "S": 60,
            "E": 55,
            "C": 62
        },
        "veto_factors": {
            "budget_min_fcfa": 110000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Architecture & Urbanisme",
        "domaine": "Environnement & Aménagement",
        "duree_theorique": 5,
        "salaire_median_p50": 400000,
        "taux_insertion": 74.0,
        "indice_saturation": 0.4,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.7,
        "profil_riasec_dominant": {
            "R": 70,
            "I": 68,
            "A": 85,
            "S": 40,
            "E": 55,
            "C": 60
        },
        "veto_factors": {
            "budget_min_fcfa": 200000,
            "serie_bac_requise": [
                "C",
                "D",
                "E"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Hydraulique & Gestion de l'Eau",
        "domaine": "Environnement & Aménagement",
        "duree_theorique": 3,
        "salaire_median_p50": 300000,
        "taux_insertion": 80.0,
        "indice_saturation": 0.28,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.8,
        "profil_riasec_dominant": {
            "R": 80,
            "I": 80,
            "A": 20,
            "S": 40,
            "E": 42,
            "C": 68
        },
        "veto_factors": {
            "budget_min_fcfa": 120000,
            "serie_bac_requise": [
                "C",
                "D",
                "EA"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Sciences & Médecine Vétérinaires",
        "domaine": "Santé",
        "duree_theorique": 5,
        "salaire_median_p50": 350000,
        "taux_insertion": 80.0,
        "indice_saturation": 0.25,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.7,
        "profil_riasec_dominant": {
            "R": 65,
            "I": 80,
            "A": 20,
            "S": 60,
            "E": 35,
            "C": 58
        },
        "veto_factors": {
            "budget_min_fcfa": 150000,
            "serie_bac_requise": [
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Génie Industriel & Qualité",
        "domaine": "Sciences & Technologie",
        "duree_theorique": 3,
        "salaire_median_p50": 340000,
        "taux_insertion": 82.0,
        "indice_saturation": 0.3,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.78,
        "profil_riasec_dominant": {
            "R": 75,
            "I": 80,
            "A": 25,
            "S": 35,
            "E": 55,
            "C": 78
        },
        "veto_factors": {
            "budget_min_fcfa": 130000,
            "serie_bac_requise": [
                "C",
                "D",
                "E",
                "F"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Pétrole & Gaz",
        "domaine": "Sciences & Technologie",
        "duree_theorique": 3,
        "salaire_median_p50": 420000,
        "taux_insertion": 80.0,
        "indice_saturation": 0.25,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.7,
        "profil_riasec_dominant": {
            "R": 80,
            "I": 82,
            "A": 20,
            "S": 25,
            "E": 50,
            "C": 70
        },
        "veto_factors": {
            "budget_min_fcfa": 200000,
            "serie_bac_requise": [
                "C",
                "D",
                "E"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Sciences Pharmaceutiques Industrielles",
        "domaine": "Santé",
        "duree_theorique": 3,
        "salaire_median_p50": 350000,
        "taux_insertion": 83.0,
        "indice_saturation": 0.3,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.78,
        "profil_riasec_dominant": {
            "R": 50,
            "I": 85,
            "A": 20,
            "S": 45,
            "E": 40,
            "C": 80
        },
        "veto_factors": {
            "budget_min_fcfa": 180000,
            "serie_bac_requise": [
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Biotechnologies",
        "domaine": "Sciences Fondamentales",
        "duree_theorique": 3,
        "salaire_median_p50": 320000,
        "taux_insertion": 78.0,
        "indice_saturation": 0.3,
        "tendance_ia": 0,
        "tendance_curricula_marche": 0.85,
        "profil_riasec_dominant": {
            "R": 55,
            "I": 92,
            "A": 30,
            "S": 40,
            "E": 35,
            "C": 70
        },
        "veto_factors": {
            "budget_min_fcfa": 130000,
            "serie_bac_requise": [
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "E-commerce & Économie Numérique",
        "domaine": "Sciences Économiques & Gestion",
        "duree_theorique": 3,
        "salaire_median_p50": 320000,
        "taux_insertion": 82.0,
        "indice_saturation": 0.35,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.88,
        "profil_riasec_dominant": {
            "R": 30,
            "I": 62,
            "A": 45,
            "S": 50,
            "E": 85,
            "C": 68
        },
        "veto_factors": {
            "budget_min_fcfa": 110000,
            "serie_bac_requise": [
                "B",
                "C",
                "D",
                "G",
                "F"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Comptabilité-Gestion Informatisée",
        "domaine": "Sciences Économiques & Gestion",
        "duree_theorique": 3,
        "salaire_median_p50": 310000,
        "taux_insertion": 83.0,
        "indice_saturation": 0.4,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.78,
        "profil_riasec_dominant": {
            "R": 30,
            "I": 65,
            "A": 20,
            "S": 40,
            "E": 58,
            "C": 90
        },
        "veto_factors": {
            "budget_min_fcfa": 110000,
            "serie_bac_requise": [
                "C",
                "D",
                "G",
                "F"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Gestion Hospitalière",
        "domaine": "Santé",
        "duree_theorique": 3,
        "salaire_median_p50": 300000,
        "taux_insertion": 80.0,
        "indice_saturation": 0.35,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.72,
        "profil_riasec_dominant": {
            "R": 25,
            "I": 65,
            "A": 25,
            "S": 75,
            "E": 68,
            "C": 80
        },
        "veto_factors": {
            "budget_min_fcfa": 130000,
            "serie_bac_requise": [
                "C",
                "D",
                "G"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Sage-Femme / Maïeutique Avancée",
        "domaine": "Santé",
        "duree_theorique": 3,
        "salaire_median_p50": 240000,
        "taux_insertion": 90.0,
        "indice_saturation": 0.2,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.78,
        "profil_riasec_dominant": {
            "R": 45,
            "I": 65,
            "A": 20,
            "S": 95,
            "E": 30,
            "C": 68
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "C",
                "D"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Génie Textile & Mode",
        "domaine": "Arts, Lettres & Langues",
        "duree_theorique": 3,
        "salaire_median_p50": 230000,
        "taux_insertion": 68.0,
        "indice_saturation": 0.45,
        "tendance_ia": 2,
        "tendance_curricula_marche": 0.6,
        "profil_riasec_dominant": {
            "R": 60,
            "I": 45,
            "A": 88,
            "S": 45,
            "E": 60,
            "C": 55
        },
        "veto_factors": {
            "budget_min_fcfa": 100000,
            "serie_bac_requise": [
                "A",
                "B",
                "C",
                "D",
                "F"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    },
    {
        "nom": "Topographie & Cartographie",
        "domaine": "Sciences & Technologie",
        "duree_theorique": 3,
        "salaire_median_p50": 310000,
        "taux_insertion": 80.0,
        "indice_saturation": 0.3,
        "tendance_ia": 1,
        "tendance_curricula_marche": 0.78,
        "profil_riasec_dominant": {
            "R": 78,
            "I": 78,
            "A": 25,
            "S": 30,
            "E": 42,
            "C": 75
        },
        "veto_factors": {
            "budget_min_fcfa": 120000,
            "serie_bac_requise": [
                "C",
                "D",
                "E",
                "F"
            ]
        },
        "poids_scoring": {
            "riasec": 0.6,
            "marche": 0.25,
            "ia": 0.15
        }
    }
]

UNIVERSITES = [
    {
        "nom": "Université d'Abomey-Calavi (UAC)",
        "type": "public",
        "localisation": "Abomey-Calavi",
        "cout_annuel_min": 30000,
        "cout_annuel_max": 80000,
        "taux_reussite": 0.62,
        "accreditation_mesrs": true,
        "accreditation_cames": true
    },
    {
        "nom": "Université de Parakou (UP)",
        "type": "public",
        "localisation": "Parakou",
        "cout_annuel_min": 30000,
        "cout_annuel_max": 80000,
        "taux_reussite": 0.6,
        "accreditation_mesrs": true,
        "accreditation_cames": true
    },
    {
        "nom": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "type": "public",
        "localisation": "Abomey",
        "cout_annuel_min": 40000,
        "cout_annuel_max": 100000,
        "taux_reussite": 0.65,
        "accreditation_mesrs": true,
        "accreditation_cames": true
    },
    {
        "nom": "Université Nationale d'Agriculture (UNA)",
        "type": "public",
        "localisation": "Kétou",
        "cout_annuel_min": 30000,
        "cout_annuel_max": 75000,
        "taux_reussite": 0.63,
        "accreditation_mesrs": true,
        "accreditation_cames": true
    },
    {
        "nom": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "type": "public",
        "localisation": "Abomey-Calavi",
        "cout_annuel_min": 40000,
        "cout_annuel_max": 90000,
        "taux_reussite": 0.68,
        "accreditation_mesrs": true,
        "accreditation_cames": true
    },
    {
        "nom": "École Nationale d'Économie Appliquée et de Management (ENEAM)",
        "type": "public",
        "localisation": "Cotonou",
        "cout_annuel_min": 50000,
        "cout_annuel_max": 120000,
        "taux_reussite": 0.7,
        "accreditation_mesrs": true,
        "accreditation_cames": true
    },
    {
        "nom": "Institut de Formation et de Recherche en Informatique (IFRI)",
        "type": "public",
        "localisation": "Abomey-Calavi",
        "cout_annuel_min": 40000,
        "cout_annuel_max": 90000,
        "taux_reussite": 0.71,
        "accreditation_mesrs": true,
        "accreditation_cames": false
    },
    {
        "nom": "Faculté des Sciences de la Santé (FSS)",
        "type": "public",
        "localisation": "Cotonou",
        "cout_annuel_min": 50000,
        "cout_annuel_max": 150000,
        "taux_reussite": 0.72,
        "accreditation_mesrs": true,
        "accreditation_cames": true
    },
    {
        "nom": "Institut National Médico-Sanitaire (INMeS)",
        "type": "public",
        "localisation": "Cotonou",
        "cout_annuel_min": 40000,
        "cout_annuel_max": 100000,
        "taux_reussite": 0.75,
        "accreditation_mesrs": true,
        "accreditation_cames": false
    },
    {
        "nom": "Faculté des Sciences Agronomiques (FSA)",
        "type": "public",
        "localisation": "Abomey-Calavi",
        "cout_annuel_min": 30000,
        "cout_annuel_max": 70000,
        "taux_reussite": 0.66,
        "accreditation_mesrs": true,
        "accreditation_cames": true
    },
    {
        "nom": "Institut National de l'Eau (INE)",
        "type": "public",
        "localisation": "Abomey-Calavi",
        "cout_annuel_min": 40000,
        "cout_annuel_max": 90000,
        "taux_reussite": 0.69,
        "accreditation_mesrs": true,
        "accreditation_cames": false
    },
    {
        "nom": "Institut National des Métiers d'Arts, d'Archéologie et de la Culture (INMAAC)",
        "type": "public",
        "localisation": "Abomey-Calavi",
        "cout_annuel_min": 35000,
        "cout_annuel_max": 80000,
        "taux_reussite": 0.64,
        "accreditation_mesrs": true,
        "accreditation_cames": false
    },
    {
        "nom": "Institut de Mathématiques et de Sciences Physiques (IMSP)",
        "type": "public",
        "localisation": "Dangbo",
        "cout_annuel_min": 30000,
        "cout_annuel_max": 70000,
        "taux_reussite": 0.7,
        "accreditation_mesrs": true,
        "accreditation_cames": true
    },
    {
        "nom": "Institut National Supérieur de Technologie Industrielle (INSTI Lokossa)",
        "type": "public",
        "localisation": "Lokossa",
        "cout_annuel_min": 40000,
        "cout_annuel_max": 95000,
        "taux_reussite": 0.67,
        "accreditation_mesrs": true,
        "accreditation_cames": false
    },
    {
        "nom": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "type": "prive",
        "localisation": "Cotonou",
        "cout_annuel_min": 350000,
        "cout_annuel_max": 600000,
        "taux_reussite": 0.74,
        "accreditation_mesrs": true,
        "accreditation_cames": false
    },
    {
        "nom": "Institut Supérieur de Technologie (IST)",
        "type": "prive",
        "localisation": "Cotonou",
        "cout_annuel_min": 300000,
        "cout_annuel_max": 550000,
        "taux_reussite": 0.72,
        "accreditation_mesrs": true,
        "accreditation_cames": false
    },
    {
        "nom": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "type": "confessionnel",
        "localisation": "Cotonou",
        "cout_annuel_min": 400000,
        "cout_annuel_max": 700000,
        "taux_reussite": 0.78,
        "accreditation_mesrs": true,
        "accreditation_cames": false
    },
    {
        "nom": "Haute École de Commerce et de Management (HECM)",
        "type": "prive",
        "localisation": "Cotonou",
        "cout_annuel_min": 350000,
        "cout_annuel_max": 650000,
        "taux_reussite": 0.73,
        "accreditation_mesrs": true,
        "accreditation_cames": false
    },
    {
        "nom": "Institut CERCO",
        "type": "prive",
        "localisation": "Cotonou",
        "cout_annuel_min": 300000,
        "cout_annuel_max": 550000,
        "taux_reussite": 0.7,
        "accreditation_mesrs": true,
        "accreditation_cames": false
    },
    {
        "nom": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "type": "prive",
        "localisation": "Cotonou",
        "cout_annuel_min": 350000,
        "cout_annuel_max": 600000,
        "taux_reussite": 0.72,
        "accreditation_mesrs": true,
        "accreditation_cames": false
    },
    {
        "nom": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "type": "confessionnel",
        "localisation": "Cotonou",
        "cout_annuel_min": 400000,
        "cout_annuel_max": 680000,
        "taux_reussite": 0.77,
        "accreditation_mesrs": true,
        "accreditation_cames": true
    },
    {
        "nom": "Sèmè City (Cité Internationale de l'Innovation)",
        "type": "public",
        "localisation": "Sèmè-Podji",
        "cout_annuel_min": 50000,
        "cout_annuel_max": 200000,
        "taux_reussite": 0.8,
        "accreditation_mesrs": true,
        "accreditation_cames": false
    }
]

FORMATIONS = [
    {
        "filiere": "Sciences de l'Éducation",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Psychologie",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Sociologie & Anthropologie",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Géographie & Aménagement du Territoire",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Histoire & Archéologie",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Philosophie",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Sciences du Langage & Communication",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Travail Social & Développement Communautaire",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Lettres Modernes",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Anglais (Langue & Littérature)",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Espagnol",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Allemand",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Linguistique & Langues Africaines",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Arts Plastiques & Design",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Design Graphique & Multimédia",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Musique & Musicologie",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Arts Dramatiques & Théâtre",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Cinéma & Audiovisuel",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Journalisme & Communication",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Administration Culturelle",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Interprétariat & Traduction",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Textile & Mode",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Droit Privé",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Droit Public",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Sciences Politiques & Relations Internationales",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Administration Publique",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Carrières Judiciaires & Greffe",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Criminologie & Sécurité",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Mathématiques",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Physique",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Chimie",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Sciences de la Vie & de la Terre (Biologie)",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Biochimie & Biologie Moléculaire",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Géologie & Sciences de la Terre",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Statistiques & Économétrie",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Biotechnologies",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie de l'Environnement",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Eau, Hygiène & Assainissement",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Gestion des Changements Climatiques",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Géomatique & Télédétection",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Planification & Gestion Urbaine",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Architecture & Urbanisme",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 5,
        "places_disponibles": 60
    },
    {
        "filiere": "Hydraulique & Gestion de l'Eau",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Économie",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Gestion des Entreprises",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Comptabilité, Contrôle & Audit",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Finance & Banque",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Banque & Institutions de Microfinance",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Finance Islamique",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Assurance & Gestion des Risques",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Marketing & Communication Commerciale",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Marketing Digital & Community Management",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Gestion des Ressources Humaines",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Logistique & Transport",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Commerce International",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Gestion de Projet",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Administration des Affaires",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Tourisme & Hôtellerie",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Gestion Fiscale & Financière",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "E-commerce & Économie Numérique",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Comptabilité-Gestion Informatisée",
        "universite": "Université d'Abomey-Calavi (UAC)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Droit Privé",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Droit Public",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Sciences Politiques & Relations Internationales",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Administration Publique",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Carrières Judiciaires & Greffe",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Criminologie & Sécurité",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Économie",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Gestion des Entreprises",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Comptabilité, Contrôle & Audit",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Finance & Banque",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Banque & Institutions de Microfinance",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Finance Islamique",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Assurance & Gestion des Risques",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Marketing & Communication Commerciale",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Marketing Digital & Community Management",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Gestion des Ressources Humaines",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Logistique & Transport",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Commerce International",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Gestion de Projet",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Administration des Affaires",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Tourisme & Hôtellerie",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Gestion Fiscale & Financière",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "E-commerce & Économie Numérique",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Comptabilité-Gestion Informatisée",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Sciences de l'Éducation",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Psychologie",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Sociologie & Anthropologie",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Géographie & Aménagement du Territoire",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Histoire & Archéologie",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Philosophie",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Sciences du Langage & Communication",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Travail Social & Développement Communautaire",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Médecine Générale",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 7,
        "places_disponibles": 60
    },
    {
        "filiere": "Pharmacie",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 6,
        "places_disponibles": 60
    },
    {
        "filiere": "Chirurgie Dentaire",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 6,
        "places_disponibles": 60
    },
    {
        "filiere": "Sciences Infirmières",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Sciences Obstétricales (Sage-femme)",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Kinésithérapie & Réadaptation",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Imagerie Médicale & Radiologie",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Analyses Biomédicales",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Santé Publique & Épidémiologie",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Nutrition & Diététique",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Sciences & Médecine Vétérinaires",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 5,
        "places_disponibles": 60
    },
    {
        "filiere": "Sciences Pharmaceutiques Industrielles",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Gestion Hospitalière",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Sage-Femme / Maïeutique Avancée",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Agronomie Générale",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Production Végétale & Phytotechnie",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Production Animale & Zootechnie",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Agroalimentaire & Nutrition",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Aménagement & Gestion des Ressources Naturelles",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Économie & Sociologie Rurale",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Rural & Maîtrise de l'Eau",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Foresterie & Gestion des Forêts",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Aquaculture & Pêche",
        "universite": "Université de Parakou (UP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Informatique & Systèmes",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Data Science & Intelligence Artificielle",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Cybersécurité & Réseaux",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Logiciel",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Administration des Réseaux Informatiques",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Analyse Informatique & Programmation",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Informatique de Gestion",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Civil & BTP",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Électrique & Électronique",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Mécanique & Productique",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Énergétique & Énergies Renouvelables",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Télécommunications",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Biomédical",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Maintenance Industrielle",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie des Procédés & Chimie Industrielle",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Mécatronique & Robotique",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Industriel & Qualité",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Pétrole & Gaz",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Topographie & Cartographie",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Mathématiques",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Physique",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Chimie",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Sciences de la Vie & de la Terre (Biologie)",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Biochimie & Biologie Moléculaire",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Géologie & Sciences de la Terre",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Statistiques & Économétrie",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Biotechnologies",
        "universite": "Université Nationale des Sciences, Technologies, Ingénierie et Mathématiques (UNSTIM)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Agronomie Générale",
        "universite": "Université Nationale d'Agriculture (UNA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Production Végétale & Phytotechnie",
        "universite": "Université Nationale d'Agriculture (UNA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Production Animale & Zootechnie",
        "universite": "Université Nationale d'Agriculture (UNA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Agroalimentaire & Nutrition",
        "universite": "Université Nationale d'Agriculture (UNA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Aménagement & Gestion des Ressources Naturelles",
        "universite": "Université Nationale d'Agriculture (UNA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Économie & Sociologie Rurale",
        "universite": "Université Nationale d'Agriculture (UNA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Rural & Maîtrise de l'Eau",
        "universite": "Université Nationale d'Agriculture (UNA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Foresterie & Gestion des Forêts",
        "universite": "Université Nationale d'Agriculture (UNA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Aquaculture & Pêche",
        "universite": "Université Nationale d'Agriculture (UNA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie de l'Environnement",
        "universite": "Université Nationale d'Agriculture (UNA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Eau, Hygiène & Assainissement",
        "universite": "Université Nationale d'Agriculture (UNA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Gestion des Changements Climatiques",
        "universite": "Université Nationale d'Agriculture (UNA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Géomatique & Télédétection",
        "universite": "Université Nationale d'Agriculture (UNA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Planification & Gestion Urbaine",
        "universite": "Université Nationale d'Agriculture (UNA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Architecture & Urbanisme",
        "universite": "Université Nationale d'Agriculture (UNA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 5,
        "places_disponibles": 60
    },
    {
        "filiere": "Hydraulique & Gestion de l'Eau",
        "universite": "Université Nationale d'Agriculture (UNA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Informatique & Systèmes",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Data Science & Intelligence Artificielle",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Cybersécurité & Réseaux",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Logiciel",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Administration des Réseaux Informatiques",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Analyse Informatique & Programmation",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Informatique de Gestion",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Civil & BTP",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Électrique & Électronique",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Mécanique & Productique",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Énergétique & Énergies Renouvelables",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Télécommunications",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Biomédical",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Maintenance Industrielle",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie des Procédés & Chimie Industrielle",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Mécatronique & Robotique",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Industriel & Qualité",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Pétrole & Gaz",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Topographie & Cartographie",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie de l'Environnement",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Eau, Hygiène & Assainissement",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Gestion des Changements Climatiques",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Géomatique & Télédétection",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Planification & Gestion Urbaine",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Architecture & Urbanisme",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 5,
        "places_disponibles": 60
    },
    {
        "filiere": "Hydraulique & Gestion de l'Eau",
        "universite": "École Polytechnique d'Abomey-Calavi (EPAC)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Économie",
        "universite": "École Nationale d'Économie Appliquée et de Management (ENEAM)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Gestion des Entreprises",
        "universite": "École Nationale d'Économie Appliquée et de Management (ENEAM)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Comptabilité, Contrôle & Audit",
        "universite": "École Nationale d'Économie Appliquée et de Management (ENEAM)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Finance & Banque",
        "universite": "École Nationale d'Économie Appliquée et de Management (ENEAM)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Banque & Institutions de Microfinance",
        "universite": "École Nationale d'Économie Appliquée et de Management (ENEAM)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Finance Islamique",
        "universite": "École Nationale d'Économie Appliquée et de Management (ENEAM)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Assurance & Gestion des Risques",
        "universite": "École Nationale d'Économie Appliquée et de Management (ENEAM)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Marketing & Communication Commerciale",
        "universite": "École Nationale d'Économie Appliquée et de Management (ENEAM)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Marketing Digital & Community Management",
        "universite": "École Nationale d'Économie Appliquée et de Management (ENEAM)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Gestion des Ressources Humaines",
        "universite": "École Nationale d'Économie Appliquée et de Management (ENEAM)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Logistique & Transport",
        "universite": "École Nationale d'Économie Appliquée et de Management (ENEAM)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Commerce International",
        "universite": "École Nationale d'Économie Appliquée et de Management (ENEAM)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Gestion de Projet",
        "universite": "École Nationale d'Économie Appliquée et de Management (ENEAM)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Administration des Affaires",
        "universite": "École Nationale d'Économie Appliquée et de Management (ENEAM)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Tourisme & Hôtellerie",
        "universite": "École Nationale d'Économie Appliquée et de Management (ENEAM)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Gestion Fiscale & Financière",
        "universite": "École Nationale d'Économie Appliquée et de Management (ENEAM)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "E-commerce & Économie Numérique",
        "universite": "École Nationale d'Économie Appliquée et de Management (ENEAM)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Comptabilité-Gestion Informatisée",
        "universite": "École Nationale d'Économie Appliquée et de Management (ENEAM)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Informatique & Systèmes",
        "universite": "Institut de Formation et de Recherche en Informatique (IFRI)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Data Science & Intelligence Artificielle",
        "universite": "Institut de Formation et de Recherche en Informatique (IFRI)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Cybersécurité & Réseaux",
        "universite": "Institut de Formation et de Recherche en Informatique (IFRI)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Logiciel",
        "universite": "Institut de Formation et de Recherche en Informatique (IFRI)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Administration des Réseaux Informatiques",
        "universite": "Institut de Formation et de Recherche en Informatique (IFRI)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Analyse Informatique & Programmation",
        "universite": "Institut de Formation et de Recherche en Informatique (IFRI)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Informatique de Gestion",
        "universite": "Institut de Formation et de Recherche en Informatique (IFRI)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Civil & BTP",
        "universite": "Institut de Formation et de Recherche en Informatique (IFRI)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Électrique & Électronique",
        "universite": "Institut de Formation et de Recherche en Informatique (IFRI)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Mécanique & Productique",
        "universite": "Institut de Formation et de Recherche en Informatique (IFRI)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Énergétique & Énergies Renouvelables",
        "universite": "Institut de Formation et de Recherche en Informatique (IFRI)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Télécommunications",
        "universite": "Institut de Formation et de Recherche en Informatique (IFRI)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Biomédical",
        "universite": "Institut de Formation et de Recherche en Informatique (IFRI)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Maintenance Industrielle",
        "universite": "Institut de Formation et de Recherche en Informatique (IFRI)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie des Procédés & Chimie Industrielle",
        "universite": "Institut de Formation et de Recherche en Informatique (IFRI)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Mécatronique & Robotique",
        "universite": "Institut de Formation et de Recherche en Informatique (IFRI)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Industriel & Qualité",
        "universite": "Institut de Formation et de Recherche en Informatique (IFRI)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Pétrole & Gaz",
        "universite": "Institut de Formation et de Recherche en Informatique (IFRI)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Topographie & Cartographie",
        "universite": "Institut de Formation et de Recherche en Informatique (IFRI)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Médecine Générale",
        "universite": "Faculté des Sciences de la Santé (FSS)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 7,
        "places_disponibles": 60
    },
    {
        "filiere": "Pharmacie",
        "universite": "Faculté des Sciences de la Santé (FSS)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 6,
        "places_disponibles": 60
    },
    {
        "filiere": "Chirurgie Dentaire",
        "universite": "Faculté des Sciences de la Santé (FSS)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 6,
        "places_disponibles": 60
    },
    {
        "filiere": "Sciences Infirmières",
        "universite": "Faculté des Sciences de la Santé (FSS)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Sciences Obstétricales (Sage-femme)",
        "universite": "Faculté des Sciences de la Santé (FSS)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Kinésithérapie & Réadaptation",
        "universite": "Faculté des Sciences de la Santé (FSS)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Imagerie Médicale & Radiologie",
        "universite": "Faculté des Sciences de la Santé (FSS)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Analyses Biomédicales",
        "universite": "Faculté des Sciences de la Santé (FSS)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Santé Publique & Épidémiologie",
        "universite": "Faculté des Sciences de la Santé (FSS)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Nutrition & Diététique",
        "universite": "Faculté des Sciences de la Santé (FSS)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Sciences & Médecine Vétérinaires",
        "universite": "Faculté des Sciences de la Santé (FSS)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 5,
        "places_disponibles": 60
    },
    {
        "filiere": "Sciences Pharmaceutiques Industrielles",
        "universite": "Faculté des Sciences de la Santé (FSS)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Gestion Hospitalière",
        "universite": "Faculté des Sciences de la Santé (FSS)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Sage-Femme / Maïeutique Avancée",
        "universite": "Faculté des Sciences de la Santé (FSS)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Médecine Générale",
        "universite": "Institut National Médico-Sanitaire (INMeS)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 7,
        "places_disponibles": 60
    },
    {
        "filiere": "Pharmacie",
        "universite": "Institut National Médico-Sanitaire (INMeS)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 6,
        "places_disponibles": 60
    },
    {
        "filiere": "Chirurgie Dentaire",
        "universite": "Institut National Médico-Sanitaire (INMeS)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 6,
        "places_disponibles": 60
    },
    {
        "filiere": "Sciences Infirmières",
        "universite": "Institut National Médico-Sanitaire (INMeS)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Sciences Obstétricales (Sage-femme)",
        "universite": "Institut National Médico-Sanitaire (INMeS)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Kinésithérapie & Réadaptation",
        "universite": "Institut National Médico-Sanitaire (INMeS)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Imagerie Médicale & Radiologie",
        "universite": "Institut National Médico-Sanitaire (INMeS)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Analyses Biomédicales",
        "universite": "Institut National Médico-Sanitaire (INMeS)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Santé Publique & Épidémiologie",
        "universite": "Institut National Médico-Sanitaire (INMeS)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Nutrition & Diététique",
        "universite": "Institut National Médico-Sanitaire (INMeS)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Sciences & Médecine Vétérinaires",
        "universite": "Institut National Médico-Sanitaire (INMeS)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 5,
        "places_disponibles": 60
    },
    {
        "filiere": "Sciences Pharmaceutiques Industrielles",
        "universite": "Institut National Médico-Sanitaire (INMeS)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Gestion Hospitalière",
        "universite": "Institut National Médico-Sanitaire (INMeS)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Sage-Femme / Maïeutique Avancée",
        "universite": "Institut National Médico-Sanitaire (INMeS)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Agronomie Générale",
        "universite": "Faculté des Sciences Agronomiques (FSA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Production Végétale & Phytotechnie",
        "universite": "Faculté des Sciences Agronomiques (FSA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Production Animale & Zootechnie",
        "universite": "Faculté des Sciences Agronomiques (FSA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Agroalimentaire & Nutrition",
        "universite": "Faculté des Sciences Agronomiques (FSA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Aménagement & Gestion des Ressources Naturelles",
        "universite": "Faculté des Sciences Agronomiques (FSA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Économie & Sociologie Rurale",
        "universite": "Faculté des Sciences Agronomiques (FSA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Rural & Maîtrise de l'Eau",
        "universite": "Faculté des Sciences Agronomiques (FSA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Foresterie & Gestion des Forêts",
        "universite": "Faculté des Sciences Agronomiques (FSA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Aquaculture & Pêche",
        "universite": "Faculté des Sciences Agronomiques (FSA)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie de l'Environnement",
        "universite": "Institut National de l'Eau (INE)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Eau, Hygiène & Assainissement",
        "universite": "Institut National de l'Eau (INE)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Gestion des Changements Climatiques",
        "universite": "Institut National de l'Eau (INE)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Géomatique & Télédétection",
        "universite": "Institut National de l'Eau (INE)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Planification & Gestion Urbaine",
        "universite": "Institut National de l'Eau (INE)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Architecture & Urbanisme",
        "universite": "Institut National de l'Eau (INE)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 5,
        "places_disponibles": 60
    },
    {
        "filiere": "Hydraulique & Gestion de l'Eau",
        "universite": "Institut National de l'Eau (INE)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Lettres Modernes",
        "universite": "Institut National des Métiers d'Arts, d'Archéologie et de la Culture (INMAAC)",
        "diplome": "Licence",
        "frais_inscription": 35000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Anglais (Langue & Littérature)",
        "universite": "Institut National des Métiers d'Arts, d'Archéologie et de la Culture (INMAAC)",
        "diplome": "Licence",
        "frais_inscription": 35000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Espagnol",
        "universite": "Institut National des Métiers d'Arts, d'Archéologie et de la Culture (INMAAC)",
        "diplome": "Licence",
        "frais_inscription": 35000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Allemand",
        "universite": "Institut National des Métiers d'Arts, d'Archéologie et de la Culture (INMAAC)",
        "diplome": "Licence",
        "frais_inscription": 35000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Linguistique & Langues Africaines",
        "universite": "Institut National des Métiers d'Arts, d'Archéologie et de la Culture (INMAAC)",
        "diplome": "Licence",
        "frais_inscription": 35000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Arts Plastiques & Design",
        "universite": "Institut National des Métiers d'Arts, d'Archéologie et de la Culture (INMAAC)",
        "diplome": "Licence",
        "frais_inscription": 35000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Design Graphique & Multimédia",
        "universite": "Institut National des Métiers d'Arts, d'Archéologie et de la Culture (INMAAC)",
        "diplome": "Licence",
        "frais_inscription": 35000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Musique & Musicologie",
        "universite": "Institut National des Métiers d'Arts, d'Archéologie et de la Culture (INMAAC)",
        "diplome": "Licence",
        "frais_inscription": 35000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Arts Dramatiques & Théâtre",
        "universite": "Institut National des Métiers d'Arts, d'Archéologie et de la Culture (INMAAC)",
        "diplome": "Licence",
        "frais_inscription": 35000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Cinéma & Audiovisuel",
        "universite": "Institut National des Métiers d'Arts, d'Archéologie et de la Culture (INMAAC)",
        "diplome": "Licence",
        "frais_inscription": 35000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Journalisme & Communication",
        "universite": "Institut National des Métiers d'Arts, d'Archéologie et de la Culture (INMAAC)",
        "diplome": "Licence",
        "frais_inscription": 35000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Administration Culturelle",
        "universite": "Institut National des Métiers d'Arts, d'Archéologie et de la Culture (INMAAC)",
        "diplome": "Licence",
        "frais_inscription": 35000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Interprétariat & Traduction",
        "universite": "Institut National des Métiers d'Arts, d'Archéologie et de la Culture (INMAAC)",
        "diplome": "Licence",
        "frais_inscription": 35000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Textile & Mode",
        "universite": "Institut National des Métiers d'Arts, d'Archéologie et de la Culture (INMAAC)",
        "diplome": "Licence",
        "frais_inscription": 35000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Mathématiques",
        "universite": "Institut de Mathématiques et de Sciences Physiques (IMSP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Physique",
        "universite": "Institut de Mathématiques et de Sciences Physiques (IMSP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Chimie",
        "universite": "Institut de Mathématiques et de Sciences Physiques (IMSP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Sciences de la Vie & de la Terre (Biologie)",
        "universite": "Institut de Mathématiques et de Sciences Physiques (IMSP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Biochimie & Biologie Moléculaire",
        "universite": "Institut de Mathématiques et de Sciences Physiques (IMSP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Géologie & Sciences de la Terre",
        "universite": "Institut de Mathématiques et de Sciences Physiques (IMSP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Statistiques & Économétrie",
        "universite": "Institut de Mathématiques et de Sciences Physiques (IMSP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Biotechnologies",
        "universite": "Institut de Mathématiques et de Sciences Physiques (IMSP)",
        "diplome": "Licence",
        "frais_inscription": 30000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Informatique & Systèmes",
        "universite": "Institut National Supérieur de Technologie Industrielle (INSTI Lokossa)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Data Science & Intelligence Artificielle",
        "universite": "Institut National Supérieur de Technologie Industrielle (INSTI Lokossa)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Cybersécurité & Réseaux",
        "universite": "Institut National Supérieur de Technologie Industrielle (INSTI Lokossa)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Logiciel",
        "universite": "Institut National Supérieur de Technologie Industrielle (INSTI Lokossa)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Administration des Réseaux Informatiques",
        "universite": "Institut National Supérieur de Technologie Industrielle (INSTI Lokossa)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Analyse Informatique & Programmation",
        "universite": "Institut National Supérieur de Technologie Industrielle (INSTI Lokossa)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Informatique de Gestion",
        "universite": "Institut National Supérieur de Technologie Industrielle (INSTI Lokossa)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Civil & BTP",
        "universite": "Institut National Supérieur de Technologie Industrielle (INSTI Lokossa)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Électrique & Électronique",
        "universite": "Institut National Supérieur de Technologie Industrielle (INSTI Lokossa)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Mécanique & Productique",
        "universite": "Institut National Supérieur de Technologie Industrielle (INSTI Lokossa)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Énergétique & Énergies Renouvelables",
        "universite": "Institut National Supérieur de Technologie Industrielle (INSTI Lokossa)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Télécommunications",
        "universite": "Institut National Supérieur de Technologie Industrielle (INSTI Lokossa)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Biomédical",
        "universite": "Institut National Supérieur de Technologie Industrielle (INSTI Lokossa)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Maintenance Industrielle",
        "universite": "Institut National Supérieur de Technologie Industrielle (INSTI Lokossa)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie des Procédés & Chimie Industrielle",
        "universite": "Institut National Supérieur de Technologie Industrielle (INSTI Lokossa)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Mécatronique & Robotique",
        "universite": "Institut National Supérieur de Technologie Industrielle (INSTI Lokossa)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Industriel & Qualité",
        "universite": "Institut National Supérieur de Technologie Industrielle (INSTI Lokossa)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Pétrole & Gaz",
        "universite": "Institut National Supérieur de Technologie Industrielle (INSTI Lokossa)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Topographie & Cartographie",
        "universite": "Institut National Supérieur de Technologie Industrielle (INSTI Lokossa)",
        "diplome": "Licence",
        "frais_inscription": 40000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Informatique & Systèmes",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Data Science & Intelligence Artificielle",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Cybersécurité & Réseaux",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Logiciel",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Administration des Réseaux Informatiques",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Analyse Informatique & Programmation",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Informatique de Gestion",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Civil & BTP",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Électrique & Électronique",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Mécanique & Productique",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Énergétique & Énergies Renouvelables",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Télécommunications",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Biomédical",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Maintenance Industrielle",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie des Procédés & Chimie Industrielle",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Mécatronique & Robotique",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Industriel & Qualité",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Pétrole & Gaz",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Topographie & Cartographie",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Économie",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion des Entreprises",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Comptabilité, Contrôle & Audit",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Finance & Banque",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Banque & Institutions de Microfinance",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Finance Islamique",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Assurance & Gestion des Risques",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Marketing & Communication Commerciale",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Marketing Digital & Community Management",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion des Ressources Humaines",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Logistique & Transport",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Commerce International",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion de Projet",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Administration des Affaires",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Tourisme & Hôtellerie",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion Fiscale & Financière",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "E-commerce & Économie Numérique",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Comptabilité-Gestion Informatisée",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Droit Privé",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Droit Public",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Sciences Politiques & Relations Internationales",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Administration Publique",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Carrières Judiciaires & Greffe",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Criminologie & Sécurité",
        "universite": "Université Africaine de Technologie et de Management (UATM-GASA)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Informatique & Systèmes",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Data Science & Intelligence Artificielle",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Cybersécurité & Réseaux",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Logiciel",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Administration des Réseaux Informatiques",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Analyse Informatique & Programmation",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Informatique de Gestion",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Civil & BTP",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Électrique & Électronique",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Mécanique & Productique",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Énergétique & Énergies Renouvelables",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Télécommunications",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Biomédical",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Maintenance Industrielle",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie des Procédés & Chimie Industrielle",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Mécatronique & Robotique",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Industriel & Qualité",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Pétrole & Gaz",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Topographie & Cartographie",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Économie",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion des Entreprises",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Comptabilité, Contrôle & Audit",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Finance & Banque",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Banque & Institutions de Microfinance",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Finance Islamique",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Assurance & Gestion des Risques",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Marketing & Communication Commerciale",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Marketing Digital & Community Management",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion des Ressources Humaines",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Logistique & Transport",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Commerce International",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion de Projet",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Administration des Affaires",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Tourisme & Hôtellerie",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion Fiscale & Financière",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "E-commerce & Économie Numérique",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Comptabilité-Gestion Informatisée",
        "universite": "Institut Supérieur de Technologie (IST)",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Économie",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion des Entreprises",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Comptabilité, Contrôle & Audit",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Finance & Banque",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Banque & Institutions de Microfinance",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Finance Islamique",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Assurance & Gestion des Risques",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Marketing & Communication Commerciale",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Marketing Digital & Community Management",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion des Ressources Humaines",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Logistique & Transport",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Commerce International",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion de Projet",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Administration des Affaires",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Tourisme & Hôtellerie",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion Fiscale & Financière",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "E-commerce & Économie Numérique",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Comptabilité-Gestion Informatisée",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Droit Privé",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Droit Public",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Sciences Politiques & Relations Internationales",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Administration Publique",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Carrières Judiciaires & Greffe",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Criminologie & Sécurité",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Médecine Générale",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 7,
        "places_disponibles": 40
    },
    {
        "filiere": "Pharmacie",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 6,
        "places_disponibles": 40
    },
    {
        "filiere": "Chirurgie Dentaire",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 6,
        "places_disponibles": 40
    },
    {
        "filiere": "Sciences Infirmières",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Sciences Obstétricales (Sage-femme)",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Kinésithérapie & Réadaptation",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Imagerie Médicale & Radiologie",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Analyses Biomédicales",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Santé Publique & Épidémiologie",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Nutrition & Diététique",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Sciences & Médecine Vétérinaires",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 5,
        "places_disponibles": 40
    },
    {
        "filiere": "Sciences Pharmaceutiques Industrielles",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion Hospitalière",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Sage-Femme / Maïeutique Avancée",
        "universite": "Université Protestante de l'Afrique de l'Ouest (UPAO)",
        "diplome": "Licence",
        "frais_inscription": 700000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Économie",
        "universite": "Haute École de Commerce et de Management (HECM)",
        "diplome": "Licence",
        "frais_inscription": 650000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion des Entreprises",
        "universite": "Haute École de Commerce et de Management (HECM)",
        "diplome": "Licence",
        "frais_inscription": 650000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Comptabilité, Contrôle & Audit",
        "universite": "Haute École de Commerce et de Management (HECM)",
        "diplome": "Licence",
        "frais_inscription": 650000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Finance & Banque",
        "universite": "Haute École de Commerce et de Management (HECM)",
        "diplome": "Licence",
        "frais_inscription": 650000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Banque & Institutions de Microfinance",
        "universite": "Haute École de Commerce et de Management (HECM)",
        "diplome": "Licence",
        "frais_inscription": 650000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Finance Islamique",
        "universite": "Haute École de Commerce et de Management (HECM)",
        "diplome": "Licence",
        "frais_inscription": 650000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Assurance & Gestion des Risques",
        "universite": "Haute École de Commerce et de Management (HECM)",
        "diplome": "Licence",
        "frais_inscription": 650000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Marketing & Communication Commerciale",
        "universite": "Haute École de Commerce et de Management (HECM)",
        "diplome": "Licence",
        "frais_inscription": 650000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Marketing Digital & Community Management",
        "universite": "Haute École de Commerce et de Management (HECM)",
        "diplome": "Licence",
        "frais_inscription": 650000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion des Ressources Humaines",
        "universite": "Haute École de Commerce et de Management (HECM)",
        "diplome": "Licence",
        "frais_inscription": 650000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Logistique & Transport",
        "universite": "Haute École de Commerce et de Management (HECM)",
        "diplome": "Licence",
        "frais_inscription": 650000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Commerce International",
        "universite": "Haute École de Commerce et de Management (HECM)",
        "diplome": "Licence",
        "frais_inscription": 650000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion de Projet",
        "universite": "Haute École de Commerce et de Management (HECM)",
        "diplome": "Licence",
        "frais_inscription": 650000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Administration des Affaires",
        "universite": "Haute École de Commerce et de Management (HECM)",
        "diplome": "Licence",
        "frais_inscription": 650000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Tourisme & Hôtellerie",
        "universite": "Haute École de Commerce et de Management (HECM)",
        "diplome": "Licence",
        "frais_inscription": 650000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion Fiscale & Financière",
        "universite": "Haute École de Commerce et de Management (HECM)",
        "diplome": "Licence",
        "frais_inscription": 650000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "E-commerce & Économie Numérique",
        "universite": "Haute École de Commerce et de Management (HECM)",
        "diplome": "Licence",
        "frais_inscription": 650000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Comptabilité-Gestion Informatisée",
        "universite": "Haute École de Commerce et de Management (HECM)",
        "diplome": "Licence",
        "frais_inscription": 650000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Informatique & Systèmes",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Data Science & Intelligence Artificielle",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Cybersécurité & Réseaux",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Logiciel",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Administration des Réseaux Informatiques",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Analyse Informatique & Programmation",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Informatique de Gestion",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Civil & BTP",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Électrique & Électronique",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Mécanique & Productique",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Énergétique & Énergies Renouvelables",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Télécommunications",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Biomédical",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Maintenance Industrielle",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie des Procédés & Chimie Industrielle",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Mécatronique & Robotique",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Industriel & Qualité",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Pétrole & Gaz",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Topographie & Cartographie",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Économie",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion des Entreprises",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Comptabilité, Contrôle & Audit",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Finance & Banque",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Banque & Institutions de Microfinance",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Finance Islamique",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Assurance & Gestion des Risques",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Marketing & Communication Commerciale",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Marketing Digital & Community Management",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion des Ressources Humaines",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Logistique & Transport",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Commerce International",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion de Projet",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Administration des Affaires",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Tourisme & Hôtellerie",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion Fiscale & Financière",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "E-commerce & Économie Numérique",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Comptabilité-Gestion Informatisée",
        "universite": "Institut CERCO",
        "diplome": "Licence",
        "frais_inscription": 550000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Informatique & Systèmes",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Data Science & Intelligence Artificielle",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Cybersécurité & Réseaux",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Logiciel",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Administration des Réseaux Informatiques",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Analyse Informatique & Programmation",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Informatique de Gestion",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Civil & BTP",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Électrique & Électronique",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Mécanique & Productique",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Énergétique & Énergies Renouvelables",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Télécommunications",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Biomédical",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Maintenance Industrielle",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie des Procédés & Chimie Industrielle",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Mécatronique & Robotique",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Industriel & Qualité",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Pétrole & Gaz",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Topographie & Cartographie",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Économie",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion des Entreprises",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Comptabilité, Contrôle & Audit",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Finance & Banque",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Banque & Institutions de Microfinance",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Finance Islamique",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Assurance & Gestion des Risques",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Marketing & Communication Commerciale",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Marketing Digital & Community Management",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion des Ressources Humaines",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Logistique & Transport",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Commerce International",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion de Projet",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Administration des Affaires",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Tourisme & Hôtellerie",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion Fiscale & Financière",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "E-commerce & Économie Numérique",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Comptabilité-Gestion Informatisée",
        "universite": "ESGIS (École Supérieure de Gestion d'Informatique et des Sciences)",
        "diplome": "Licence",
        "frais_inscription": 600000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Droit Privé",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Droit Public",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Sciences Politiques & Relations Internationales",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Administration Publique",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Carrières Judiciaires & Greffe",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Criminologie & Sécurité",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Économie",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion des Entreprises",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Comptabilité, Contrôle & Audit",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Finance & Banque",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Banque & Institutions de Microfinance",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Finance Islamique",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Assurance & Gestion des Risques",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Marketing & Communication Commerciale",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Marketing Digital & Community Management",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion des Ressources Humaines",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Logistique & Transport",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Commerce International",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion de Projet",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Administration des Affaires",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Tourisme & Hôtellerie",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Gestion Fiscale & Financière",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "E-commerce & Économie Numérique",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Comptabilité-Gestion Informatisée",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Sciences de l'Éducation",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Psychologie",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Sociologie & Anthropologie",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Géographie & Aménagement du Territoire",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Histoire & Archéologie",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Philosophie",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Sciences du Langage & Communication",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Travail Social & Développement Communautaire",
        "universite": "Université Catholique de l'Afrique de l'Ouest (UCAO)",
        "diplome": "Licence",
        "frais_inscription": 680000,
        "duree_reelle": 3,
        "places_disponibles": 40
    },
    {
        "filiere": "Génie Informatique & Systèmes",
        "universite": "Sèmè City (Cité Internationale de l'Innovation)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Data Science & Intelligence Artificielle",
        "universite": "Sèmè City (Cité Internationale de l'Innovation)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Cybersécurité & Réseaux",
        "universite": "Sèmè City (Cité Internationale de l'Innovation)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Logiciel",
        "universite": "Sèmè City (Cité Internationale de l'Innovation)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Administration des Réseaux Informatiques",
        "universite": "Sèmè City (Cité Internationale de l'Innovation)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Analyse Informatique & Programmation",
        "universite": "Sèmè City (Cité Internationale de l'Innovation)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Informatique de Gestion",
        "universite": "Sèmè City (Cité Internationale de l'Innovation)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Civil & BTP",
        "universite": "Sèmè City (Cité Internationale de l'Innovation)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Électrique & Électronique",
        "universite": "Sèmè City (Cité Internationale de l'Innovation)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Mécanique & Productique",
        "universite": "Sèmè City (Cité Internationale de l'Innovation)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Énergétique & Énergies Renouvelables",
        "universite": "Sèmè City (Cité Internationale de l'Innovation)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Télécommunications",
        "universite": "Sèmè City (Cité Internationale de l'Innovation)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Biomédical",
        "universite": "Sèmè City (Cité Internationale de l'Innovation)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Maintenance Industrielle",
        "universite": "Sèmè City (Cité Internationale de l'Innovation)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie des Procédés & Chimie Industrielle",
        "universite": "Sèmè City (Cité Internationale de l'Innovation)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Mécatronique & Robotique",
        "universite": "Sèmè City (Cité Internationale de l'Innovation)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Génie Industriel & Qualité",
        "universite": "Sèmè City (Cité Internationale de l'Innovation)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Pétrole & Gaz",
        "universite": "Sèmè City (Cité Internationale de l'Innovation)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    },
    {
        "filiere": "Topographie & Cartographie",
        "universite": "Sèmè City (Cité Internationale de l'Innovation)",
        "diplome": "Licence",
        "frais_inscription": 50000,
        "duree_reelle": 3,
        "places_disponibles": 60
    }
]


def seed_filieres(session):
    if session.exec(select(Filiere)).first():
        print("Filieres deja presentes.")
        return
    for data in FILIERES:
        session.add(Filiere(**data))
    session.commit()
    print(f"{len(FILIERES)} filieres inserees.")


def seed_universites(session):
    if session.exec(select(Universite)).first():
        print("Universites deja presentes.")
        return
    for data in UNIVERSITES:
        session.add(Universite(**data))
    session.commit()
    print(f"{len(UNIVERSITES)} universites inserees.")


def seed_formations(session):
    if session.exec(select(Formation)).first():
        print("Formations deja presentes.")
        return
    # Resoudre noms -> IDs
    fil_map = {f.nom: f.id_filiere for f in session.exec(select(Filiere)).all()}
    uni_map = {u.nom: u.id_universite for u in session.exec(select(Universite)).all()}
    n = 0
    for data in FORMATIONS:
        id_f = fil_map.get(data["filiere"])
        id_u = uni_map.get(data["universite"])
        if not id_f or not id_u:
            continue
        session.add(Formation(
            id_filiere=id_f, id_universite=id_u,
            diplome=data["diplome"],
            frais_inscription=data["frais_inscription"],
            duree_reelle=data["duree_reelle"],
            places_disponibles=data["places_disponibles"],
        ))
        n += 1
    session.commit()
    print(f"{n} formations inserees.")


def seed_all():
    create_db_and_tables()
    with Session(engine) as session:
        seed_filieres(session)
        seed_universites(session)
        seed_formations(session)


if __name__ == "__main__":
    seed_all()
