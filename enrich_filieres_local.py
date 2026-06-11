# -*- coding: utf-8 -*-
"""
enrich_filieres_local.py — Enrichissement des filières sans API externe
Toutes les données sont hardcodées, réalistes pour le Bénin 2025.
Usage: python enrich_filieres_local.py
"""
from sqlmodel import Session, select
from app.core.database import engine
from app.models.filiere import Filiere

DATA = {
    # ── ADMINISTRATION PUBLIQUE ──────────────────────────────────────────────
    "Administration Générale": {
        "description": "Formation aux métiers de la fonction publique et de la gestion administrative. Les étudiants apprennent la gestion des ressources humaines, le droit administratif et les politiques publiques au Bénin.",
        "debouches": ["Administrateur civil", "Chef de service administratif", "Secrétaire général de mairie", "Gestionnaire RH public", "Attaché d'administration"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 150000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.72,
    },
    "Administration Financière": {
        "description": "Spécialisation dans la gestion des finances publiques, la comptabilité de l'État et le contrôle budgétaire. Les étudiants maîtrisent les procédures de gestion financière dans les administrations béninoises.",
        "debouches": ["Comptable public", "Contrôleur financier", "Trésorier municipal", "Agent des finances", "Gestionnaire budgétaire"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 150000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.70,
    },
    "Administration du Travail et Sécurité Sociale": {
        "description": "Formation aux droits du travail, à l'inspection du travail et à la gestion de la sécurité sociale au Bénin. Prépare aux métiers de régulation et de protection sociale.",
        "debouches": ["Inspecteur du travail", "Contrôleur CNSS", "Responsable RH", "Conseiller en droit social", "Agent de la CNSS"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 150000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.75,
    },
    "Planification et Développement Local": {
        "description": "Filière axée sur la planification territoriale, le développement communal et la gestion de projets de développement au Bénin. Les étudiants apprennent à concevoir et suivre des politiques locales.",
        "debouches": ["Planificateur local", "Chef de projet développement", "Responsable communal", "Consultant en développement", "Agent de coopération"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 150000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.68,
    },
    "Diplomatie et Relations Internationales": {
        "description": "Formation aux relations entre États, au droit international et à la diplomatie. Prépare aux métiers des affaires étrangères et des organisations internationales actives au Bénin et en Afrique de l'Ouest.",
        "debouches": ["Diplomate", "Attaché d'ambassade", "Fonctionnaire international", "Conseiller politique", "Analyste géopolitique"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 200000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.65,
    },

    # ── AGRICULTURE ──────────────────────────────────────────────────────────
    "Agronomie Générale": {
        "description": "Formation de base en sciences agronomiques couvrant la production végétale, animale et la gestion des exploitations agricoles béninoises. Prépare à l'encadrement du monde rural.",
        "debouches": ["Ingénieur agronome", "Conseiller agricole", "Chef de projet agricole", "Agent de développement rural", "Technicien agricole"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 200000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.68,
    },
    "Production Végétale et Semencière": {
        "description": "Spécialisation dans la culture des plantes, la sélection variétale et la production de semences certifiées. Répond aux besoins de sécurité alimentaire du Bénin.",
        "debouches": ["Ingénieur en production végétale", "Sélectionneur de semences", "Chef de ferme", "Agent phytosanitaire", "Technicien semencier"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 180000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.65,
    },
    "Production et Santé Animales": {
        "description": "Formation à l'élevage, à la zootechnie et à la santé animale dans le contexte béninois. Couvre les filières bovine, avicole et porcine dominantes au Bénin.",
        "debouches": ["Zootechnicien", "Vétérinaire para-clinique", "Éleveur professionnel", "Agent de santé animale", "Inspecteur vétérinaire"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 200000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.66,
    },
    "Nutrition Humaine et Agroalimentaire": {
        "description": "Filière croisant nutrition, transformation des aliments et sécurité alimentaire. Forme des experts capables d'améliorer la chaîne alimentaire au Bénin et en Afrique de l'Ouest.",
        "debouches": ["Nutritionniste", "Technologue alimentaire", "Contrôleur qualité agroalimentaire", "Responsable sécurité alimentaire", "Consultant nutrition"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 250000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.70,
    },
    "Conseil Agricole et Gestion des Exploitations": {
        "description": "Formation orientée vers l'accompagnement des agriculteurs et la gestion économique des exploitations. Prépare à l'encadrement et au conseil des producteurs béninois.",
        "debouches": ["Conseiller agricole", "Gestionnaire d'exploitation", "Animateur rural", "Chef de projet agricole", "Agent de vulgarisation"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 180000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.65,
    },
    "Agroéconomie et Développement Rural": {
        "description": "Analyse économique des systèmes agricoles et des politiques de développement rural au Bénin. Forme des experts capables d'évaluer et concevoir des projets agricoles.",
        "debouches": ["Agroéconomiste", "Chargé de projets FAO/ONUDI", "Analyste filière agricole", "Consultant développement rural", "Économiste agricole"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 200000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.64,
    },
    "Génie Rural et Eaux-Forêts": {
        "description": "Formation en aménagement des espaces ruraux, gestion des eaux et des ressources forestières. Prépare aux métiers de l'environnement agricole et de la gestion durable des ressources.",
        "debouches": ["Ingénieur des eaux et forêts", "Hydrologue", "Technicien rural", "Agent forestier", "Gestionnaire de bassins versants"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 200000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.72,
    },
    "Horticulture et Aménagement des Espaces Verts": {
        "description": "Spécialisation dans la culture des fruits, légumes et plantes ornementales, ainsi que l'aménagement paysager. Répond au développement urbain croissant des villes béninoises.",
        "debouches": ["Horticulteur", "Paysagiste", "Gestionnaire d'espaces verts", "Maraîcher professionnel", "Consultant en urbanisme végétal"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 200000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.62,
    },
    "Machinisme Agricole et Mécanique": {
        "description": "Formation à la maintenance, à l'utilisation et à la gestion des équipements agricoles mécanisés. Répond à la mécanisation croissante de l'agriculture béninoise.",
        "debouches": ["Technicien en machinisme agricole", "Mécanicien d'équipements ruraux", "Chef atelier agricole", "Gestionnaire de parc machines", "Agent de mécanisation"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 200000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.70,
    },
    "Pêche et Aquaculture": {
        "description": "Formation à la gestion des ressources halieutiques, à l'aquaculture et à la pêche durable dans le contexte côtier et lagunaire du Bénin. Couvre les aspects techniques et économiques.",
        "debouches": ["Aquaculteur", "Technicien des pêches", "Gestionnaire de ressources halieutiques", "Inspecteur sanitaire poisson", "Consultant aquaculture"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 200000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.62,
    },

    # ── ARTS ET CULTURE ──────────────────────────────────────────────────────
    "Arts et Management Culturel": {
        "description": "Croisement entre pratiques artistiques et gestion de projets culturels. Forme des professionnels capables de gérer des structures culturelles, des événements et des politiques culturelles au Bénin.",
        "debouches": ["Manager culturel", "Directeur artistique", "Organisateur d'événements", "Chargé de communication culturelle", "Gestionnaire de musée"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 600000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.60,
    },
    "Réalisation Audiovisuelle": {
        "description": "Formation aux métiers du cinéma, de la télévision et de la production audiovisuelle. Prépare à la réalisation, au montage et à la production de contenus audiovisuels dans le secteur médiatique béninois.",
        "debouches": ["Réalisateur", "Monteur vidéo", "Caméraman", "Producteur audiovisuel", "Journaliste reporter d'images"],
        "niveau_admission": "Bac", "cout_annuel_min": 400000, "cout_annuel_max": 800000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.58,
    },

    # ── COMMERCE ET MARKETING ────────────────────────────────────────────────
    "Marketing et Action Commerciale": {
        "description": "Formation aux techniques de vente, de marketing et de gestion commerciale. Prépare à concevoir et mettre en œuvre des stratégies commerciales adaptées au marché béninois et ouest-africain.",
        "debouches": ["Commercial", "Chef de produit", "Responsable marketing", "Chargé de clientèle", "Directeur commercial"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.65,
    },
    "Commerce International": {
        "description": "Formation aux échanges commerciaux internationaux, au droit du commerce international et à la logistique douanière. Prépare aux métiers du commerce extérieur dans la zone CEDEAO.",
        "debouches": ["Responsable import-export", "Agent douanier", "Logisticien international", "Chargé d'affaires internationales", "Analyste commercial"],
        "niveau_admission": "Bac", "cout_annuel_min": 200000, "cout_annuel_max": 500000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.68,
    },
    "Négociation et Communication Multimédia": {
        "description": "Formation à la négociation commerciale et à la communication digitale. Prépare aux métiers de la vente, du marketing digital et de la gestion de la relation client à l'ère numérique.",
        "debouches": ["Négociateur commercial", "Community manager", "Responsable communication digitale", "Chargé de relation client", "Consultant en marketing digital"],
        "niveau_admission": "Bac", "cout_annuel_min": 350000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.62,
    },
    "Hôtellerie Restauration et Tourisme": {
        "description": "Formation aux métiers de l'accueil, de la restauration et du tourisme. Prépare à gérer des établissements hôteliers et à développer le secteur touristique béninois en pleine croissance.",
        "debouches": ["Hôtelier", "Responsable restauration", "Guide touristique", "Gestionnaire d'agence de voyage", "Chef cuisinier"],
        "niveau_admission": "Bac", "cout_annuel_min": 350000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.60,
    },

    # ── COMMUNICATION ET MÉDIAS ───────────────────────────────────────────────
    "Journalisme et Communication": {
        "description": "Formation aux techniques journalistiques, à la rédaction et à la communication médiatique. Prépare aux métiers de l'information dans la presse écrite, la radio et la télévision au Bénin.",
        "debouches": ["Journaliste", "Rédacteur en chef", "Présentateur TV/radio", "Attaché de presse", "Community manager"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.60,
    },
    "Communication d'Entreprise": {
        "description": "Spécialisation dans la communication interne et externe des organisations. Prépare à gérer l'image de marque, les relations publiques et la communication institutionnelle des entreprises béninoises.",
        "debouches": ["Responsable communication", "Attaché de presse", "Chargé de communication interne", "Community manager", "Directeur de communication"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.62,
    },
    "Communication et Relations Publiques": {
        "description": "Formation à la gestion de l'image institutionnelle et aux relations avec les médias et le public. Prépare aux métiers de la communication externe et des relations presse au Bénin.",
        "debouches": ["Chargé des relations publiques", "Responsable communication", "Attaché de presse", "Consultant en communication", "Directeur communication"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.60,
    },
    "Communication et Action Publicitaire": {
        "description": "Formation à la création et à la gestion de campagnes publicitaires. Prépare aux métiers des agences de publicité, du marketing et de la communication commerciale au Bénin.",
        "debouches": ["Créatif publicitaire", "Chef de publicité", "Directeur artistique", "Planneur stratégique", "Responsable marketing"],
        "niveau_admission": "Bac", "cout_annuel_min": 350000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.58,
    },
    "Sciences et Techniques de l'Information": {
        "description": "Formation à la collecte, au traitement et à la diffusion de l'information dans les médias et les organisations. Couvre le journalisme, la documentation et la veille informationnelle.",
        "debouches": ["Documentaliste", "Archiviste", "Journaliste", "Veilleur informationnel", "Bibliothécaire"],
        "niveau_admission": "Bac", "cout_annuel_min": 200000, "cout_annuel_max": 500000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.62,
    },
    "Communication Politique et Stratégique": {
        "description": "Formation avancée à la communication en contexte politique et institutionnel. Prépare à conseiller des élus, des partis politiques et des organisations dans leur stratégie de communication au Bénin.",
        "debouches": ["Conseiller en communication politique", "Spin doctor", "Chargé de communication institutionnelle", "Analyste politique", "Consultant stratégique"],
        "niveau_admission": "Bac+3", "cout_annuel_min": 500000, "cout_annuel_max": 1000000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.58,
    },

    # ── DROIT ─────────────────────────────────────────────────────────────────
    "Droit Privé": {
        "description": "Étude du droit civil, commercial et des personnes dans le système juridique béninois inspiré du droit français. Prépare aux professions juridiques et au conseil aux particuliers et entreprises.",
        "debouches": ["Avocat", "Notaire", "Juriste d'entreprise", "Huissier", "Magistrat"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 250000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.65,
    },
    "Droit Public": {
        "description": "Étude du droit administratif, constitutionnel et des institutions publiques béninoises. Prépare aux carrières dans la fonction publique et aux métiers du droit de l'État.",
        "debouches": ["Magistrat administratif", "Fonctionnaire juridique", "Conseiller juridique public", "Analyste politique", "Juriste d'État"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 250000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.65,
    },
    "Droit des Affaires": {
        "description": "Spécialisation dans le droit commercial, des sociétés et des contrats dans le cadre de l'OHADA. Prépare à conseiller les entreprises dans leurs opérations juridiques en Afrique de l'Ouest.",
        "debouches": ["Juriste d'affaires", "Avocat d'affaires", "Notaire", "Conseiller juridique entreprise", "Directeur juridique"],
        "niveau_admission": "Bac", "cout_annuel_min": 350000, "cout_annuel_max": 800000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.65,
    },
    "Sciences Juridiques": {
        "description": "Formation généraliste en droit couvrant les principales branches du droit béninois et international. Offre une base solide pour les métiers juridiques et l'accès aux études de droit supérieures.",
        "debouches": ["Juriste", "Conseiller juridique", "Greffier", "Assistant juridique", "Chargé de conformité"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 600000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.62,
    },
    "Fiscalité et Droit des Affaires": {
        "description": "Formation spécialisée croisant le droit fiscal et le droit des affaires OHADA. Prépare à conseiller les entreprises sur leur conformité fiscale et juridique au Bénin.",
        "debouches": ["Fiscaliste", "Conseiller fiscal", "Expert-comptable", "Directeur administratif et financier", "Juriste fiscal"],
        "niveau_admission": "Bac+3", "cout_annuel_min": 450000, "cout_annuel_max": 900000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.68,
    },

    # ── ÉCONOMIE ──────────────────────────────────────────────────────────────
    "Sciences Économiques": {
        "description": "Étude des mécanismes économiques, des marchés et des politiques macroéconomiques appliqués au contexte béninois et africain. Base solide pour l'analyse économique et les institutions.",
        "debouches": ["Économiste", "Analyste financier", "Chargé d'études", "Conseiller économique", "Statisticien"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 500000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.65,
    },
    "Statistique et Planification": {
        "description": "Formation aux méthodes statistiques, à la collecte et à l'analyse des données pour la planification nationale. Filière très recherchée dans les administrations et organisations internationales au Bénin.",
        "debouches": ["Statisticien", "Planificateur national", "Analyste données", "Chargé d'études INSAE", "Consultant en développement"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 200000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.75,
    },
    "Économie Publique et Statistique": {
        "description": "Formation avancée à l'économie publique, aux politiques fiscales et aux méthodes quantitatives de l'African School of Economics. Niveau master orienté recherche et institutions internationales.",
        "debouches": ["Économiste senior", "Chercheur en économie", "Analyste Banque mondiale", "Conseiller FMI/BAfD", "Directeur études économiques"],
        "niveau_admission": "Bac+3", "cout_annuel_min": 800000, "cout_annuel_max": 1500000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.78,
    },
    "Modélisation Aléatoire, Statistique et Finances": {
        "description": "Formation de pointe en mathématiques financières, en actuariat et en modélisation statistique. Prépare aux métiers quantitatifs des banques, assurances et institutions financières en Afrique.",
        "debouches": ["Actuaire", "Quant analyste", "Gestionnaire des risques", "Analyste financier quantitatif", "Data scientist finance"],
        "niveau_admission": "Bac+3", "cout_annuel_min": 80000, "cout_annuel_max": 300000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.80,
    },

    # ── ÉDUCATION ET PÉDAGOGIE ────────────────────────────────────────────────
    "CAPES Lettres Modernes": {
        "description": "Certification professionnelle préparant à l'enseignement du français et de la littérature dans les lycées béninois. Formation pédagogique et disciplinaire de haut niveau.",
        "debouches": ["Professeur de français lycée", "Enseignant lettres collège", "Directeur établissement scolaire", "Inspecteur pédagogique", "Formateur d'enseignants"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.82,
    },
    "CAPES Anglais": {
        "description": "Certification préparant à l'enseignement de l'anglais dans le secondaire béninois. Couvre la linguistique anglaise, la didactique des langues et la pédagogie.",
        "debouches": ["Professeur d'anglais lycée", "Enseignant anglais collège", "Formateur en langues", "Traducteur pédagogique", "Directeur centre de langues"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 300000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.84,
    },
    "CAPES Histoire-Géographie": {
        "description": "Certification pour l'enseignement de l'histoire et de la géographie dans les établissements secondaires du Bénin. Inclut l'histoire africaine et la géographie du Bénin.",
        "debouches": ["Professeur histoire-géo lycée", "Enseignant collège", "Archiviste", "Guide touristique culturel", "Chercheur en histoire"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.80,
    },
    "CAPES Philosophie": {
        "description": "Certification préparant à l'enseignement de la philosophie dans les terminales béninoises. Formation approfondie en histoire de la philosophie et en didactique.",
        "debouches": ["Professeur de philosophie", "Enseignant en lycée", "Conseiller en éthique", "Formateur", "Chercheur en philosophie"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.78,
    },
    "CAPES Sciences de Vie et de la Terre": {
        "description": "Certification pour l'enseignement des SVT dans le secondaire béninois. Couvre la biologie, la géologie et les sciences environnementales.",
        "debouches": ["Professeur SVT lycée", "Enseignant biologie collège", "Technicien de laboratoire", "Inspecteur pédagogique", "Animateur environnement"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.83,
    },
    "BAPES / CAPES Mathématiques-Informatique": {
        "description": "Double certification pour l'enseignement des mathématiques et de l'informatique dans les établissements secondaires béninois. Filière très demandée face à la pénurie d'enseignants en sciences.",
        "debouches": ["Professeur maths-info lycée", "Enseignant mathématiques", "Formateur informatique", "Inspecteur maths", "Directeur établissement"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.88,
    },
    "BAPES Physique-Chimie et Technologie": {
        "description": "Certification préparant à l'enseignement de la physique, chimie et technologie dans les lycées béninois. Associe la maîtrise scientifique et les compétences pédagogiques.",
        "debouches": ["Professeur physique-chimie", "Enseignant technologie", "Technicien de laboratoire", "Formateur sciences", "Inspecteur pédagogique"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.85,
    },
    "BAPES Sciences et Vie de la Terre": {
        "description": "Certification axée sur l'enseignement des sciences naturelles et de la vie dans le secondaire béninois. Couvre la biologie, l'écologie et les sciences de la Terre.",
        "debouches": ["Professeur SVT", "Enseignant biologie", "Animateur environnemental", "Technicien laboratoire", "Inspecteur SVT"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.84,
    },
    "BAPES Éducation Physique et Sportive": {
        "description": "Certification pour l'enseignement de l'EPS dans les établissements scolaires béninois. Associe la pédagogie sportive, la physiologie et la gestion des activités physiques.",
        "debouches": ["Professeur d'EPS", "Entraîneur sportif", "Animateur sportif", "Éducateur sportif communautaire", "Inspecteur EPS"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.80,
    },
    "Sciences de l'Éducation": {
        "description": "Étude des théories et pratiques éducatives, de la psychologie de l'apprentissage et des politiques éducatives au Bénin. Prépare à la formation des enseignants et à l'ingénierie pédagogique.",
        "debouches": ["Formateur d'enseignants", "Inspecteur pédagogique", "Conseiller pédagogique", "Directeur d'école", "Chercheur en éducation"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 300000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.68,
    },
    "Éducation et Pédagogie": {
        "description": "Formation générale aux sciences de l'éducation et aux pratiques pédagogiques. Prépare à l'enseignement, à la formation et à l'encadrement pédagogique dans les systèmes éducatifs béninois.",
        "debouches": ["Enseignant", "Formateur professionnel", "Conseiller pédagogique", "Directeur d'établissement", "Animateur éducatif"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 600000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.70,
    },

    # ── ENVIRONNEMENT ─────────────────────────────────────────────────────────
    "Gestion de l'Environnement et Aménagement": {
        "description": "Formation à la gestion durable des ressources naturelles et à l'aménagement du territoire au Bénin. Prépare aux défis environnementaux liés au changement climatique en Afrique de l'Ouest.",
        "debouches": ["Gestionnaire de l'environnement", "Chargé de mission environnement", "Expert en évaluation d'impact", "Consultant développement durable", "Agent ANPE"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 600000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.65,
    },
    "Génie de l'Environnement": {
        "description": "Formation technique à la maîtrise des pollutions, au traitement des déchets et aux études d'impact environnemental. Prépare aux métiers de l'ingénierie environnementale en développement au Bénin.",
        "debouches": ["Ingénieur environnement", "Responsable HSE", "Expert en traitement des eaux", "Consultant EIES", "Chef de projet environnemental"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 300000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.68,
    },
    "Hygiène Nutrition Santé et Environnement": {
        "description": "Formation transversale croisant hygiène alimentaire, nutrition communautaire et santé environnementale. Prépare aux métiers de la santé publique et de la prévention sanitaire au Bénin.",
        "debouches": ["Hygiéniste", "Agent de santé communautaire", "Inspecteur sanitaire", "Nutritionniste communautaire", "Responsable sécurité alimentaire"],
        "niveau_admission": "Bac", "cout_annuel_min": 350000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.65,
    },

    # ── FINANCE ET COMPTABILITÉ ───────────────────────────────────────────────
    "Banque Finance et Assurance": {
        "description": "Formation aux métiers de la banque, de la gestion financière et de l'assurance. Prépare aux carrières dans les établissements financiers de la zone UEMOA opérant au Bénin.",
        "debouches": ["Chargé de clientèle bancaire", "Analyste crédit", "Agent d'assurance", "Gestionnaire de portefeuille", "Conseiller financier"],
        "niveau_admission": "Bac", "cout_annuel_min": 350000, "cout_annuel_max": 800000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.68,
    },
    "Comptabilité Contrôle et Audit": {
        "description": "Formation aux techniques comptables, au contrôle interne et à l'audit financier selon les normes SYSCOHADA. Prépare aux métiers du chiffre dans les entreprises et cabinets béninois.",
        "debouches": ["Comptable", "Auditeur", "Contrôleur de gestion", "Expert-comptable", "Directeur financier"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.68,
    },
    "Finance et Contrôle de Gestion": {
        "description": "Formation avancée en analyse financière, gestion budgétaire et contrôle de gestion. Prépare aux postes de direction financière dans les grandes entreprises et institutions béninoises.",
        "debouches": ["Contrôleur de gestion", "Directeur financier", "Analyste financier", "Responsable budget", "Trésorier d'entreprise"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.70,
    },
    "Gestion Financière et Comptable": {
        "description": "Formation pratique à la gestion des finances et à la tenue de comptabilité selon le SYSCOHADA. Prépare aux postes opérationnels dans les PME et administrations béninoises.",
        "debouches": ["Comptable d'entreprise", "Gestionnaire financier", "Assistant DAF", "Chargé de recouvrement", "Responsable paie"],
        "niveau_admission": "Bac", "cout_annuel_min": 200000, "cout_annuel_max": 500000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.68,
    },
    "Techniques Comptables et Financières": {
        "description": "Formation de base aux techniques de comptabilité, de fiscalité et de gestion financière. Prépare aux postes d'assistant comptable et de technicien financier dans les entreprises béninoises.",
        "debouches": ["Assistant comptable", "Aide-comptable", "Technicien financier", "Agent de facturation", "Gestionnaire de caisse"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 600000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.65,
    },

    # ── GESTION ET MANAGEMENT ─────────────────────────────────────────────────
    "Gestion des Ressources Humaines": {
        "description": "Formation à la gestion du capital humain, au recrutement, à la formation et aux relations sociales en entreprise. Prépare aux postes RH dans les organisations béninoises et multinationales.",
        "debouches": ["Responsable RH", "Chargé de recrutement", "Gestionnaire de paie", "Directeur des ressources humaines", "Consultant RH"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.68,
    },
    "Management des Entreprises": {
        "description": "Formation générale au management des organisations, à la stratégie d'entreprise et au leadership. Prépare aux postes d'encadrement dans les entreprises béninoises de toutes tailles.",
        "debouches": ["Manager", "Chef de projet", "Responsable d'unité", "Directeur général PME", "Consultant en management"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.65,
    },
    "Administration et Gestion des Entreprises": {
        "description": "Formation polyvalente couvrant l'administration, la gestion et le management des entreprises. Prépare à des postes de direction généraliste dans les PME béninoises.",
        "debouches": ["Directeur administratif", "Gestionnaire PME", "Responsable administratif", "Chef d'entreprise", "Consultant en gestion"],
        "niveau_admission": "Bac", "cout_annuel_min": 350000, "cout_annuel_max": 750000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.65,
    },
    "Entrepreneuriat et Gestion des PME": {
        "description": "Formation à la création et à la gestion d'entreprises dans le contexte béninois. Couvre le business plan, le financement, le marketing et la gestion opérationnelle des PME.",
        "debouches": ["Entrepreneur", "Créateur d'entreprise", "Gestionnaire PME", "Chef de projet", "Consultant en création d'entreprise"],
        "niveau_admission": "Bac", "cout_annuel_min": 350000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.62,
    },
    "Gestion de Projets": {
        "description": "Formation aux méthodologies de gestion de projets (PMI, PRINCE2) appliquées aux contextes béninois et africain. Prépare à planifier, exécuter et contrôler des projets de développement.",
        "debouches": ["Chef de projet", "Coordinateur de projets ONG", "Gestionnaire de programmes", "Consultant en gestion de projets", "Responsable planification"],
        "niveau_admission": "Bac", "cout_annuel_min": 350000, "cout_annuel_max": 750000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.68,
    },
    "Management International": {
        "description": "Formation au management dans un contexte international, couvrant les échanges commerciaux, la gestion interculturelle et les stratégies d'internationalisation des entreprises africaines.",
        "debouches": ["Directeur international", "Responsable développement Afrique", "Chef de projet international", "Consultant en commerce extérieur", "Manager expatrié"],
        "niveau_admission": "Bac", "cout_annuel_min": 400000, "cout_annuel_max": 800000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.62,
    },
    "Sciences de Gestion": {
        "description": "Approche académique et théorique des sciences de l'organisation et du management. Offre une solide formation de base pour les études supérieures en gestion et les carrières dans les organisations béninoises.",
        "debouches": ["Manager", "Consultant", "Analyste organisationnel", "Chercheur en gestion", "Responsable de département"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.65,
    },
    "Intelligence Économique et Stratégie": {
        "description": "Formation avancée à la veille stratégique, à l'analyse concurrentielle et à l'intelligence économique. Prépare à conseiller les entreprises et institutions béninoises dans leur positionnement stratégique.",
        "debouches": ["Analyste en intelligence économique", "Consultant stratégique", "Responsable veille", "Directeur stratégie", "Conseiller en développement des affaires"],
        "niveau_admission": "Bac+3", "cout_annuel_min": 500000, "cout_annuel_max": 1000000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.65,
    },
    "Gestion des Marchés Publics": {
        "description": "Spécialisation dans les procédures de passation et d'exécution des marchés publics au Bénin selon les règles de l'UEMOA. Prépare aux métiers de la commande publique dans les administrations.",
        "debouches": ["Responsable marchés publics", "Juriste commande publique", "Contrôleur financier PRMP", "Auditeur marchés publics", "Consultant en procurement"],
        "niveau_admission": "Bac+3", "cout_annuel_min": 450000, "cout_annuel_max": 900000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.72,
    },

    # ── INFORMATIQUE ET NUMÉRIQUE ─────────────────────────────────────────────
    "Génie Informatique et Télécommunications": {
        "description": "Formation d'ingénieur en informatique couvrant le développement logiciel, les réseaux et les systèmes embarqués. Prépare aux métiers techniques du numérique en forte croissance au Bénin.",
        "debouches": ["Ingénieur logiciel", "Développeur full-stack", "Architecte système", "Ingénieur réseaux", "Chef de projet IT"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.82,
    },
    "Intelligence Artificielle et Data Science": {
        "description": "Formation de pointe en apprentissage automatique, traitement des données et intelligence artificielle. Prépare aux métiers du futur les plus demandés dans les entreprises et startups tech béninoises.",
        "debouches": ["Data scientist", "Ingénieur IA", "Analyste données", "Machine learning engineer", "Consultant Big Data"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.88,
    },
    "Informatique de Gestion": {
        "description": "Croisement entre informatique et gestion d'entreprise. Prépare à déployer et gérer les systèmes d'information dans les organisations béninoises, PME et administrations.",
        "debouches": ["Administrateur système", "Analyste-programmeur", "Responsable informatique PME", "Gestionnaire ERP", "Technicien support IT"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 600000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.75,
    },
    "Informatique Réseaux et Télécommunications": {
        "description": "Formation aux infrastructures réseaux, à la sécurité informatique et aux télécommunications. Prépare aux métiers de l'administration réseau et de la cybersécurité dans les entreprises béninoises.",
        "debouches": ["Administrateur réseaux", "Ingénieur télécom", "Expert cybersécurité", "Technicien infrastructure IT", "Responsable sécurité informatique"],
        "niveau_admission": "Bac", "cout_annuel_min": 350000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.80,
    },
    "Génie Télécoms et TIC": {
        "description": "Formation aux technologies des télécommunications, aux réseaux mobiles et aux systèmes de communication. Prépare aux métiers des opérateurs télécom et des entreprises TIC au Bénin.",
        "debouches": ["Ingénieur télécom", "Technicien réseau mobile", "Responsable infrastructure TIC", "Consultant réseaux", "Ingénieur systèmes embarqués"],
        "niveau_admission": "Bac", "cout_annuel_min": 350000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.78,
    },
    "Réseaux et Génie Logiciel": {
        "description": "Formation duale couvrant le développement logiciel et l'administration des réseaux informatiques. Prépare à des profils polyvalents très recherchés dans les entreprises numériques béninoises.",
        "debouches": ["Développeur logiciel", "Administrateur réseau", "Ingénieur DevOps", "Technicien infrastructure", "Chef de projet IT"],
        "niveau_admission": "Bac", "cout_annuel_min": 350000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.80,
    },
    "Modélisation et Simulation Numérique": {
        "description": "Formation de haut niveau en simulation informatique, calcul scientifique et modélisation mathématique. Prépare à des postes de recherche et d'ingénierie avancée dans les institutions béninoises.",
        "debouches": ["Ingénieur en simulation", "Chercheur en calcul scientifique", "Data scientist avancé", "Ingénieur R&D", "Consultant en modélisation"],
        "niveau_admission": "Bac+3", "cout_annuel_min": 80000, "cout_annuel_max": 300000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.85,
    },

    # ── INGÉNIERIE ET TECHNOLOGIE ─────────────────────────────────────────────
    "Génie Civil et BTP": {
        "description": "Formation en conception et construction d'ouvrages civils, routes, bâtiments et infrastructures hydrauliques. Prépare aux chantiers de construction en forte croissance au Bénin.",
        "debouches": ["Ingénieur civil", "Conducteur de travaux", "Chef de chantier BTP", "Projeteur", "Responsable infrastructure"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 500000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.75,
    },
    "Architecture et Urbanisme": {
        "description": "Formation à la conception architecturale et à l'aménagement urbain dans le contexte béninois. Prépare à concevoir des bâtiments et espaces urbains adaptés aux réalités climatiques et culturelles d'Afrique de l'Ouest.",
        "debouches": ["Architecte", "Urbaniste", "Designer d'intérieur", "Chef de projet urbain", "Maître d'œuvre"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 500000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.72,
    },
    "Génie Électrique et Automatisme": {
        "description": "Formation aux systèmes électriques, à l'automatisation industrielle et aux installations électriques. Prépare aux métiers de l'électricité industrielle et des systèmes automatisés au Bénin.",
        "debouches": ["Ingénieur électricien", "Technicien en automatisme", "Responsable maintenance électrique", "Chef d'équipe électrique", "Ingénieur installation"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.78,
    },
    "Génie Électronique et Télécommunications": {
        "description": "Formation aux composants électroniques, aux circuits intégrés et aux systèmes de communication. Prépare aux métiers de l'électronique industrielle et des télécom au Bénin.",
        "debouches": ["Ingénieur électronicien", "Technicien télécom", "Développeur systèmes embarqués", "Responsable maintenance électronique", "Ingénieur R&D"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.75,
    },
    "Génie Mécanique et Énergétique": {
        "description": "Formation à la conception mécanique, à la thermodynamique et aux systèmes énergétiques. Prépare aux industries manufacturières et aux projets énergétiques en développement au Bénin.",
        "debouches": ["Ingénieur mécanicien", "Technicien en énergie", "Chef de maintenance industrielle", "Ingénieur de production", "Consultant en efficacité énergétique"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.75,
    },
    "Génie Énergétique et Énergies Renouvelables": {
        "description": "Formation aux systèmes d'énergie solaire, éolienne et hydraulique adaptés aux réalités béninoises. Prépare aux métiers de la transition énergétique en Afrique de l'Ouest.",
        "debouches": ["Ingénieur en énergie solaire", "Technicien énergies renouvelables", "Chef de projet énergie verte", "Consultant en efficacité énergétique", "Responsable centrale solaire"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 500000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.78,
    },
    "Génie Frigorifique et Climatisation": {
        "description": "Formation aux systèmes de réfrigération, de climatisation et aux énergies renouvelables associées. Prépare aux métiers de la chaîne du froid et du confort thermique très demandés au Bénin.",
        "debouches": ["Technicien en froid", "Frigoriste", "Installateur climatisation", "Responsable chaîne du froid", "Technicien maintenance CVC"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.78,
    },
    "Génie de l'Eau et Hydraulique": {
        "description": "Formation à la gestion des ressources en eau, à l'hydraulique et aux systèmes d'assainissement. Répond aux enjeux d'accès à l'eau potable et d'assainissement au Bénin.",
        "debouches": ["Ingénieur hydraulicien", "Technicien en eau et assainissement", "Hydrologue", "Chef de projet eau", "Expert WASH"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.78,
    },
    "Génie de la Maintenance Industrielle": {
        "description": "Formation à la maintenance préventive et corrective des équipements industriels. Prépare aux métiers de la maintenance dans les usines, ports et infrastructures industrielles du Bénin.",
        "debouches": ["Technicien de maintenance", "Responsable maintenance", "Ingénieur fiabilité", "Chef atelier industriel", "Agent de maintenance portuaire"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.78,
    },
    "Génie des Procédés Industriels": {
        "description": "Formation aux procédés de fabrication industrielle, à la chimie appliquée et à l'optimisation des processus de production. Prépare aux industries de transformation au Bénin.",
        "debouches": ["Ingénieur procédés", "Technicien de production", "Responsable qualité industrielle", "Chef de ligne de production", "Consultant industriel"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.75,
    },
    "Système Industriel et Automatisation": {
        "description": "Formation aux systèmes automatisés, à la robotique et à la programmation des automates industriels. Prépare à l'industrie 4.0 en développement progressif au Bénin.",
        "debouches": ["Automaticien", "Ingénieur en systèmes industriels", "Technicien robotique", "Programmeur automates", "Responsable automatisation"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.75,
    },
    "Géomètre Topographe": {
        "description": "Formation aux mesures topographiques, à la cartographie et au bornage foncier. Métier clé pour le développement immobilier et l'aménagement du territoire au Bénin.",
        "debouches": ["Géomètre expert", "Topographe", "Cadastreur", "Chef de mission topographique", "Expert foncier"],
        "niveau_admission": "Bac", "cout_annuel_min": 350000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.78,
    },
    "Génie Biomédical": {
        "description": "Formation à la conception, maintenance et gestion des équipements médicaux. Prépare à soutenir l'amélioration des plateaux techniques hospitaliers béninois en plein développement.",
        "debouches": ["Ingénieur biomédical", "Technicien équipements médicaux", "Responsable maintenance hospitalière", "Chargé des équipements de santé", "Consultant biomédical"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.78,
    },
    "Contrôle Qualité et Génie Agroalimentaire": {
        "description": "Formation au contrôle de la qualité des aliments et aux procédés de transformation agroalimentaire. Répond aux besoins de l'industrie alimentaire béninoise et des exportations agricoles.",
        "debouches": ["Ingénieur agroalimentaire", "Contrôleur qualité", "Responsable production alimentaire", "Technicien laboratoire alimentaire", "Auditeur qualité"],
        "niveau_admission": "Bac", "cout_annuel_min": 350000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.72,
    },
    "Génie des Expertises et Analyses": {
        "description": "Formation aux techniques d'analyse chimique, microbiologique et physique appliquées aux contrôles industriels et environnementaux au Bénin.",
        "debouches": ["Analyste de laboratoire", "Expert en analyses", "Technicien contrôle qualité", "Responsable laboratoire", "Consultant en analyses techniques"],
        "niveau_admission": "Bac", "cout_annuel_min": 350000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.72,
    },
    "Transport et Territoire": {
        "description": "Formation à l'ingénierie des transports, à la planification des infrastructures routières et à l'aménagement territorial. Prépare aux grands projets d'infrastructure au Bénin.",
        "debouches": ["Ingénieur en infrastructures de transport", "Planificateur urbain", "Chef de projet routes", "Expert mobilité", "Consultant infrastructure"],
        "niveau_admission": "Bac+3", "cout_annuel_min": 80000, "cout_annuel_max": 300000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.72,
    },

    # ── LANGUES ET LETTRES ────────────────────────────────────────────────────
    "Lettres Modernes": {
        "description": "Étude de la littérature française et africaine, de la linguistique et des sciences du langage. Prépare à l'enseignement, à l'édition et aux métiers de la culture au Bénin.",
        "debouches": ["Professeur de lettres", "Journaliste", "Rédacteur", "Auteur", "Traducteur"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 250000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.62,
    },
    "Philosophie": {
        "description": "Étude des grands courants philosophiques, de la logique et de l'éthique. Prépare à l'enseignement de la philosophie et développe la capacité d'analyse critique utile dans de nombreuses carrières.",
        "debouches": ["Professeur de philosophie", "Consultant éthique", "Journaliste d'opinion", "Chercheur", "Conseiller en gouvernance"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 300000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.60,
    },
    "Sciences du Langage et de la Communication": {
        "description": "Étude scientifique des langues, de la communication et du discours. Croise linguistique, sémiotique et sciences de l'information pour préparer aux métiers de la communication au Bénin.",
        "debouches": ["Linguiste appliqué", "Chargé de communication", "Traducteur", "Enseignant en langues", "Analyste du discours"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 250000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.62,
    },
    "Étude des Langues (Français, Anglais, Yoruba)": {
        "description": "Formation multilingue couvrant le français, l'anglais et le yoruba, langue parlée par une importante communauté au Bénin. Prépare à la médiation interculturelle et à l'enseignement des langues.",
        "debouches": ["Interprète", "Traducteur", "Professeur de langues", "Médiateur interculturel", "Guide touristique multilingue"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 600000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.62,
    },
    "Traduction et Interprétation": {
        "description": "Formation professionnelle à la traduction écrite et à l'interprétation orale entre le français, l'anglais et d'autres langues. Prépare aux métiers de la médiation linguistique dans les organisations internationales actives au Bénin.",
        "debouches": ["Traducteur professionnel", "Interprète de conférence", "Traducteur technique", "Médiateur linguistique", "Chargé de localisation"],
        "niveau_admission": "Bac+3", "cout_annuel_min": 400000, "cout_annuel_max": 800000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.62,
    },

    # ── SANTÉ ─────────────────────────────────────────────────────────────────
    "Médecine Humaine": {
        "description": "Formation médicale complète de 7 ans préparant au diagnostic, au traitement et à la prévention des maladies. La filière la plus exigeante et la mieux rémunérée du système de santé béninois.",
        "debouches": ["Médecin généraliste", "Médecin spécialiste", "Chirurgien", "Médecin de santé publique", "Chercheur médical"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 500000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.90,
    },
    "Pharmacie": {
        "description": "Formation de 6 ans en sciences pharmaceutiques couvrant la chimie, la biologie et la dispensation des médicaments. Prépare aux métiers de la pharmacie officinale, hospitalière et industrielle au Bénin.",
        "debouches": ["Pharmacien officinal", "Pharmacien hospitalier", "Inspecteur des médicaments", "Chercheur pharmaceutique", "Responsable laboratoire"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.88,
    },
    "Odontostomatologie": {
        "description": "Formation en chirurgie dentaire et en soins bucco-dentaires. Prépare aux métiers de la santé dentaire dans un contexte béninois où la demande dépasse largement l'offre de soins.",
        "debouches": ["Chirurgien-dentiste", "Orthodontiste", "Médecin stomatologiste", "Chercheur en santé bucco-dentaire", "Responsable santé dentaire"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.88,
    },
    "Kinésithérapie": {
        "description": "Formation aux techniques de rééducation fonctionnelle et de physiothérapie. Prépare aux métiers de la rééducation dans les hôpitaux et cliniques béninois en plein développement.",
        "debouches": ["Kinésithérapeute", "Physiothérapeute", "Rééducateur sportif", "Responsable unité de kinésithérapie", "Consultant en réhabilitation"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.82,
    },
    "Nutrition et Diététique": {
        "description": "Formation à la nutrition clinique, à la diététique thérapeutique et à la nutrition communautaire. Prépare aux métiers de la santé nutritionnelle dans les hôpitaux et les programmes de santé publique au Bénin.",
        "debouches": ["Diététicien", "Nutritionniste clinique", "Conseiller en nutrition", "Responsable programme nutritionnel ONG", "Chercheur en nutrition"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.72,
    },
    "Sciences Infirmières et Obstétriques": {
        "description": "Formation aux soins infirmiers, à la maternité et à la santé de la mère et de l'enfant. Pilier du système de santé béninois, cette filière prépare aux soins de premier recours dans les centres de santé.",
        "debouches": ["Infirmier(ère)", "Sage-femme", "Infirmier spécialisé", "Coordinateur soins infirmiers", "Agent de santé communautaire"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 300000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.85,
    },
    "Santé Publique": {
        "description": "Formation à la prévention des maladies, à l'épidémiologie et à la gestion des systèmes de santé. Prépare à concevoir et piloter des politiques et programmes de santé au Bénin.",
        "debouches": ["Épidémiologiste", "Responsable programme santé", "Gestionnaire système de santé", "Chargé de santé OMS/UNICEF", "Directeur département santé"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 300000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.75,
    },
    "Analyses Biomédicales": {
        "description": "Formation aux techniques d'analyse biologique, microbiologique et hématologique dans les laboratoires médicaux. Prépare aux métiers du diagnostic biologique en forte demande au Bénin.",
        "debouches": ["Biologiste médical", "Technicien de laboratoire", "Responsable laboratoire d'analyses", "Bioanalyste", "Technicien en anatomopathologie"],
        "niveau_admission": "Bac", "cout_annuel_min": 350000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.78,
    },
    "Travail Social et Action Communautaire": {
        "description": "Formation au travail social, à l'animation communautaire et à l'accompagnement des populations vulnérables. Prépare aux métiers de l'action sociale dans les ONG et administrations béninoises.",
        "debouches": ["Travailleur social", "Animateur communautaire", "Agent de protection sociale", "Coordinateur ONG", "Responsable programme social"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 250000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.65,
    },

    # ── SCIENCES FONDAMENTALES ────────────────────────────────────────────────
    "Mathématiques": {
        "description": "Formation fondamentale en mathématiques pures et appliquées. Base indispensable pour les études supérieures en sciences, ingénierie et économie. Prépare à l'enseignement et à la recherche au Bénin.",
        "debouches": ["Professeur de mathématiques", "Analyste quantitatif", "Actuaire", "Statisticien", "Chercheur en mathématiques"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 200000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.62,
    },
    "Physique": {
        "description": "Étude des lois fondamentales de la matière et de l'énergie. Prépare à l'enseignement, à la recherche et aux applications industrielles de la physique dans le contexte béninois.",
        "debouches": ["Professeur de physique", "Ingénieur de recherche", "Technicien en métrologie", "Analyste en physique appliquée", "Chercheur"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 200000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.60,
    },
    "Chimie": {
        "description": "Étude des substances chimiques, de leurs propriétés et réactions. Prépare aux industries chimiques, pharmaceutiques et agroalimentaires au Bénin.",
        "debouches": ["Chimiste", "Analyste chimique", "Professeur de chimie", "Technicien de laboratoire", "Responsable qualité chimique"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 200000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.60,
    },
    "Biologie": {
        "description": "Étude du vivant, des organismes et de leurs interactions avec l'environnement. Base pour les études en médecine, pharmacie, agronomie et environnement au Bénin.",
        "debouches": ["Biologiste", "Professeur de biologie", "Technicien en analyses biologiques", "Agent de conservation de la nature", "Chercheur en biologie"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 200000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.60,
    },
    "Géologie": {
        "description": "Étude des roches, des sols et des ressources minérales du sous-sol. Prépare aux métiers des mines, du pétrole et de la gestion des ressources géologiques en Afrique de l'Ouest.",
        "debouches": ["Géologue", "Ingénieur mines", "Hydrogéologue", "Expert en ressources minérales", "Consultant en géologie pétrolière"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 200000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.65,
    },
    "Biotechnologie": {
        "description": "Application des sciences biologiques et de la biologie moléculaire au développement de produits et procédés innovants. Filière d'avenir pour le Bénin dans les domaines de la santé et de l'agriculture.",
        "debouches": ["Biotechnologiste", "Chercheur en biotechnologie", "Technicien de laboratoire biotech", "Responsable R&D", "Consultant en biotechnologies"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.68,
    },
    "Mathématiques Appliquées": {
        "description": "Application des mathématiques à la résolution de problèmes concrets en finance, informatique et physique. Prépare aux métiers quantitatifs dans les entreprises et institutions béninoises.",
        "debouches": ["Mathématicien appliqué", "Analyste financier", "Data scientist", "Ingénieur en modélisation", "Chercheur en mathématiques appliquées"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 300000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.70,
    },
    "Physique-Chimie": {
        "description": "Formation combinant physique et chimie, préparant à l'enseignement et aux applications industrielles. Prépare aux postes de technicien scientifique dans les laboratoires et industries béninoises.",
        "debouches": ["Professeur physique-chimie", "Technicien de laboratoire", "Analyste physicochimiste", "Agent de contrôle qualité", "Chercheur sciences physiques"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 200000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.60,
    },
    "Sciences et Techniques des Eaux": {
        "description": "Formation à la gestion et au traitement des eaux, à l'hydrologie et à l'assainissement. Répond directement aux enjeux d'accès à l'eau et de gestion environnementale au Bénin.",
        "debouches": ["Ingénieur en eau et assainissement", "Hydrologue", "Technicien traitement des eaux", "Responsable station d'épuration", "Expert WASH ONG"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 300000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.68,
    },

    # ── SCIENCES SOCIALES ET HUMAINES ─────────────────────────────────────────
    "Sociologie et Anthropologie": {
        "description": "Étude des sociétés, des cultures et des organisations sociales dans le contexte africain. Prépare à l'analyse sociale, à la recherche et au développement communautaire au Bénin.",
        "debouches": ["Sociologue", "Anthropologue", "Chargé d'études sociales", "Consultant en développement", "Chercheur en sciences sociales"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 250000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.62,
    },
    "Histoire": {
        "description": "Étude critique du passé des sociétés humaines, avec un accent sur l'histoire africaine et béninoise. Prépare à l'enseignement, à la recherche historique et aux métiers des archives.",
        "debouches": ["Professeur d'histoire", "Archiviste", "Chercheur", "Guide touristique culturel", "Consultant en patrimoine"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 200000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.60,
    },
    "Géographie et Aménagement du Territoire": {
        "description": "Étude de l'espace géographique, de l'aménagement territorial et des dynamiques urbaines au Bénin. Prépare aux métiers de la planification spatiale et de la gestion des territoires.",
        "debouches": ["Géographe", "Urbaniste", "Planificateur territorial", "Cartographe", "Expert en SIG"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 250000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.65,
    },
    "Psychologie et Sciences de l'Éducation": {
        "description": "Étude des comportements humains, des processus cognitifs et des pratiques éducatives. Prépare aux métiers de l'accompagnement psychologique et de la formation au Bénin.",
        "debouches": ["Psychologue", "Conseiller d'orientation", "Thérapeute", "Formateur", "Responsable ressources humaines"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 600000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.65,
    },
    "Science Politique et Relations Internationales": {
        "description": "Analyse des systèmes politiques, des institutions et des relations entre États. Prépare aux carrières dans la diplomatie, les ONG internationales et l'administration publique béninoise.",
        "debouches": ["Analyste politique", "Diplomat", "Fonctionnaire international", "Consultant en gouvernance", "Chercheur en sciences politiques"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 400000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.62,
    },
    "Sciences du Mariage et de la Famille": {
        "description": "Formation spécialisée dans les sciences humaines appliquées à la famille, au mariage et aux relations interpersonnelles dans le contexte africain et chrétien au Bénin.",
        "debouches": ["Conseiller conjugal", "Animateur familial", "Médiateur familial", "Aumônier", "Responsable programmes familiaux ONG"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 500000,
        "langue_enseignement": "Français", "accreditation_mesrs": False, "accreditation_cames": False, "taux_reussite": 0.72,
    },
    "Théologie": {
        "description": "Formation académique aux sciences religieuses, à la théologie chrétienne et à l'éthique. Prépare aux ministères religieux et aux métiers de l'accompagnement spirituel au Bénin.",
        "debouches": ["Prêtre/Pasteur", "Aumônier", "Professeur de religion", "Chercheur en théologie", "Animateur pastoral"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 500000,
        "langue_enseignement": "Français", "accreditation_mesrs": False, "accreditation_cames": False, "taux_reussite": 0.75,
    },

    # ── SPORT ET ÉDUCATION PHYSIQUE ───────────────────────────────────────────
    "Sciences et Techniques des Activités Physiques et Sportives": {
        "description": "Formation aux sciences du sport, à l'entraînement sportif et à la gestion des activités physiques. Prépare aux métiers de l'enseignement EPS, de l'entraînement et du management sportif au Bénin.",
        "debouches": ["Professeur d'EPS", "Entraîneur sportif", "Manager sportif", "Animateur sportif", "Responsable infrastructure sportive"],
        "niveau_admission": "Bac", "cout_annuel_min": 80000, "cout_annuel_max": 250000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": True, "taux_reussite": 0.72,
    },
    "Management du Sport": {
        "description": "Formation à la gestion des organisations sportives, des événements et des équipements sportifs. Prépare aux postes d'administration dans les fédérations, clubs et institutions sportives béninoises.",
        "debouches": ["Manager de club sportif", "Directeur d'équipements sportifs", "Organisateur d'événements sportifs", "Agent sportif", "Chargé de marketing sportif"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 600000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.62,
    },

    # ── TRANSPORT ET LOGISTIQUE ───────────────────────────────────────────────
    "Gestion des Transports et Logistique": {
        "description": "Formation à la gestion des flux de marchandises, à la logistique portuaire et au transport multimodal. Prépare aux métiers du transport au Port de Cotonou et dans les entreprises logistiques béninoises.",
        "debouches": ["Responsable logistique", "Transitaire", "Gestionnaire de flotte", "Agent portuaire", "Supply chain manager"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.70,
    },
    "Transport et Logistique Maritime": {
        "description": "Spécialisation dans le transport maritime, la gestion portuaire et le commerce maritime. Prépare aux métiers du Port Autonome de Cotonou, hub commercial majeur de l'Afrique de l'Ouest.",
        "debouches": ["Agent maritime", "Transitaire maritime", "Responsable opérations portuaires", "Courtier maritime", "Gestionnaire terminal conteneurs"],
        "niveau_admission": "Bac", "cout_annuel_min": 350000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.72,
    },
    "Métiers Portuaires et Douanes": {
        "description": "Formation aux procédures douanières, à la gestion des opérations portuaires et au commerce international. Prépare aux métiers du Port de Cotonou et des administrations douanières béninoises.",
        "debouches": ["Douanier", "Agent de transit", "Déclarant en douane", "Responsable dédouanement", "Inspecteur douanier"],
        "niveau_admission": "Bac", "cout_annuel_min": 350000, "cout_annuel_max": 700000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.75,
    },
    "Secrétariat de Direction": {
        "description": "Formation aux fonctions d'assistant(e) de direction, à la gestion administrative et à la communication professionnelle. Prépare aux postes d'assistant(e) dans les entreprises et administrations béninoises.",
        "debouches": ["Assistant(e) de direction", "Secrétaire de direction", "Office manager", "Chargé d'accueil", "Assistant administratif"],
        "niveau_admission": "Bac", "cout_annuel_min": 300000, "cout_annuel_max": 600000,
        "langue_enseignement": "Français", "accreditation_mesrs": True, "accreditation_cames": False, "taux_reussite": 0.68,
    },
}

def enrich():
    with Session(engine) as session:
        filieres = session.exec(select(Filiere)).all()
        to_enrich = [f for f in filieres if not f.description]

        print(f"\n{'='*55}")
        print(f"  {len(to_enrich)} filières à enrichir sur {len(filieres)} total")
        print(f"{'='*55}\n")

        success = 0
        not_found = []

        for filiere in to_enrich:
            data = DATA.get(filiere.nom)
            if not data:
                not_found.append(filiere.nom)
                continue

            filiere.description         = data["description"]
            filiere.debouches           = {"liste": data["debouches"]}
            filiere.niveau_admission    = data["niveau_admission"]
            filiere.cout_annuel_min     = data["cout_annuel_min"]
            filiere.cout_annuel_max     = data["cout_annuel_max"]
            filiere.langue_enseignement = data["langue_enseignement"]
            filiere.accreditation_mesrs = data["accreditation_mesrs"]
            filiere.accreditation_cames = data["accreditation_cames"]
            filiere.taux_reussite       = data["taux_reussite"]

            session.add(filiere)
            success += 1
            print(f"  ✅ {filiere.nom}")

        session.commit()

        print(f"\n{'='*55}")
        print(f"  ✅ {success} filières enrichies")
        if not_found:
            print(f"\n  ⚠️  {len(not_found)} filières non trouvées dans le dictionnaire :")
            for n in not_found:
                print(f"    - {n}")
        print(f"{'='*55}\n")

if __name__ == "__main__":
    enrich()
