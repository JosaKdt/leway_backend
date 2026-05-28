# ORIAB — Backend API

**Outil de Recommandation et d'Information pour l'Avenir des Bacheliers**

> En juillet 2025, 57 349 bacheliers ont obtenu leur diplôme au Bénin. Chacun a dû choisir sa filière en quelques jours, sans aucun outil objectif. 51 % des jeunes béninois restent sans emploi stable après leurs études. 58,54 % déclarent que leur formation ne correspond pas à leur emploi. ORIAB est la réponse à ce problème structurel.

ORIAB est une plateforme web et mobile d'aide à l'orientation post-baccalauréat. Elle croise trois dimensions qu'aucun outil existant au Bénin ne combine : le profil psychologique du bachelier (RIASEC), les réalités du marché du travail béninois, et l'impact de l'intelligence artificielle sur les métiers visés.

Ce dépôt contient le **backend FastAPI** — le cerveau de la plateforme.

---

## Ce que fait ce backend

Un bachelier arrive sur ORIAB. Il répond à 28 questions. Quelques secondes plus tard, il reçoit un rapport personnalisé : ses 3 filières les plus compatibles avec qui il est, ce que le marché béninois paye réellement, et ce que l'IA va changer dans ces métiers d'ici 2030. Le tout expliqué en français accessible, pas en jargon académique.

Ce backend orchestre tout ça.

---

## Stack technique

| Couche | Technologie | Rôle |
|---|---|---|
| API | FastAPI 0.111 | Framework principal, validation Pydantic, routing |
| ORM | SQLModel 0.0.18 | Interface Python ↔ PostgreSQL |
| Base de données | PostgreSQL 15 | Persistance (9 tables) |
| Cache | Redis | Mise en cache des rapports générés |
| Auth | JWT (python-jose) + bcrypt | Authentification sécurisée |
| LLM local | Ollama + Mistral 7B Instruct | Mode offline — fonctionne sans internet |
| LLM cloud | Claude Haiku 4.5 (Anthropic) | Mode connecté — rapport plus riche |
| Frontend web | React.js (dépôt séparé) | Interface bachelier web |
| Frontend mobile | Flutter (dépôt séparé) | Application Android/iOS |
| Infrastructure | AWS EC2 + RDS + S3 | Déploiement production |

---

## Architecture du moteur de recommandation

Le cœur d'ORIAB. Voici comment une recommandation est générée, de la réponse au questionnaire jusqu'au rapport final.

```
Bachelier répond aux 28 questions (Likert 1-5)
          │
          ▼
POST /api/profil/
  ├── Sections A, B, C, E → calcul des 6 scores RIASEC (0-100)
  └── Section D (Q18–Q22) → Veto Factors SEULEMENT
       (budget, mobilité, horizon temporel — jamais dans les scores RIASEC)
          │
          ▼
POST /api/recommandations/generer
  │
  ├── 1. Similarité cosinus : profil bachelier ↔ profil idéal de chaque filière
  │
  ├── 2. Weighted Score pour chaque filière :
  │      WS = 60% × cosinus_RIASEC
  │         + 25% × score_marché  (taux_insertion × 0.6 + (1−saturation) × 0.4)
  │         + 15% × score_IA      (0→1.0 | 1→0.75 | 2→0.40 | 3→0.10)
  │      → Top 5 filières triées
  │
  ├── 3. Veto Factors (filtres éliminatoires)
  │      Veto 1 : durée filière > horizon souhaité
  │      Veto 2 : filière longue (≥ 6 ans) + budget insuffisant
  │      Veto 3 : mobilité internationale requise + bachelier non mobile
  │
  ├── 4. Rapport LLM — profil 100% anonymisé (RD16 : zéro PII transmis)
  │      LLM_MODE=local  → Mistral 7B via Ollama (localhost:11434)
  │      LLM_MODE=cloud  → Claude Haiku 4.5 (API Anthropic)
  │      Fallback offline automatique si Ollama non disponible
  │
  └── 5. Persistance + réponse
         → Table recommandation (1 ligne)
         → Table score_compatibilite (Top 5 avec décomposition 60/25/15)
```

**Règle absolue (RD16 + RD18)** : les données personnelles identifiables (nom, email, téléphone) sont supprimées avant tout appel au LLM. La Section D du questionnaire n'entre jamais dans les scores RIASEC — elle alimente uniquement les Veto Factors.

---

## Installation locale

### Prérequis

- Python 3.12+
- PostgreSQL 15+
- Redis
- Ollama (mode LLM local) : [ollama.ai](https://ollama.ai)

### Démarrage

```bash
# 1. Cloner
git clone https://github.com/JosaKdt/leway_backend.git
cd leway_backend

# 2. Environnement virtuel
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate       # Windows

# 3. Dépendances
pip install -r requirements.txt

# 4. Base de données
psql -U postgres -c "CREATE DATABASE leway_db;"

# 5. Variables d'environnement
cp .env.example .env
# Éditez .env avec vos valeurs

# 6. Lancer
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
```

> `--host 0.0.0.0` est nécessaire pour que l'émulateur Android puisse joindre le serveur depuis Flutter.

### LLM local — Mistral via Ollama

```bash
# Installer Ollama : https://ollama.ai
ollama serve            # démarrer le serveur
ollama pull mistral     # télécharger Mistral 7B (~4 Go, une seule fois)
```

Une fois Mistral installé, le backend fonctionne entièrement hors-ligne, sans aucune clé API.

### Variables d'environnement (.env)

```env
# Base de données
DATABASE_URL=postgresql://postgres:votre_mdp@localhost:5432/leway_db
REDIS_URL=redis://localhost:6379/0

# Auth
SECRET_KEY=changez_cette_cle_en_production_minimum_32_caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES_BACHELIER=1440
ACCESS_TOKEN_EXPIRE_MINUTES_ADMIN=480

# LLM local (défaut — Mistral via Ollama)
LLM_MODE=local
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# LLM cloud (activer quand ANTHROPIC_API_KEY disponible)
# LLM_MODE=cloud
# ANTHROPIC_API_KEY=sk-ant-votre-cle-ici
CLAUDE_MODEL=claude-haiku-4-5-20251001

APP_ENV=development
APP_VERSION=1.0.0
```

---

## API — Référence complète

### Documentation interactive

```
http://localhost:8000/docs    ← Swagger UI
http://localhost:8000/redoc   ← ReDoc
```

Pour tester les routes protégées dans Swagger : **Authorize** → coller le JWT obtenu au login.

---

### Auth — `/api/auth`

| Méthode | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/register` | Créer un compte bachelier | Non |
| POST | `/login` | Se connecter, obtenir le JWT | Non |
| GET | `/me` | Infos du compte connecté | JWT |

```json
POST /api/auth/register
{ "nom": "Mensah", "prenom": "Kofi", "email": "kofi@gmail.com",
  "mot_de_passe": "monmotdepasse", "serie_bac": "C" }

POST /api/auth/login
{ "email": "kofi@gmail.com", "mot_de_passe": "monmotdepasse" }
→ { "access_token": "eyJ...", "token_type": "bearer" }
```

---

### Profil psychométrique — `/api/profil`

| Méthode | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/items` | Les 28 questions du questionnaire | Non |
| POST | `/` | Soumettre ses réponses → calcul RIASEC | JWT |
| GET | `/moi` | Consulter ses scores RIASEC | JWT |
| PATCH | `/moi` | Recalculer avec de nouvelles réponses | JWT |

```json
POST /api/profil/
{
  "reponses": {
    "Q01":5,"Q02":4,"Q03":2,"Q04":3,"Q05":2,"Q06":2,"Q07":5,"Q08":2,
    "Q09":3,"Q10":2,"Q11":3,"Q12":3,"Q13":2,"Q14":2,"Q15":2,"Q16":5,
    "Q17":2,"Q18":3,"Q19":1,"Q20":1,"Q21":2,"Q22":1,
    "Q23":5,"Q24":1,"Q25":5,"Q26":3,"Q27":2,"Q28":4
  },
  "ressources_financieres": 2,
  "mobilite_geo": false,
  "horizon_temporel": "moyen"
}
→ { "score_r": 38.5, "score_i": 87.4, "score_a": 42.0,
    "score_s": 61.2, "score_e": 55.8, "score_c": 48.3,
    "dimension_dominante": "I" }
```

**Sections du questionnaire :**

| Section | Items | Contenu | Rôle |
|---|---|---|---|
| A | Q01–Q04 | Profil académique | Scores RIASEC |
| B | Q05–Q12 | Personnalité & Valeurs | Scores RIASEC |
| C | Q13–Q17 | Ambitions & Objectifs | Scores RIASEC |
| D | Q18–Q22 | Contexte socioéconomique | **Veto Factors uniquement** |
| E | Q23–Q28 | Capacités personnelles | Scores RIASEC |

---

### Recommandations — `/api/recommandations`

| Méthode | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/generer` | Pipeline complet → Top 5 + Veto + rapport LLM | JWT |
| GET | `/moi` | Historique de mes recommandations | JWT |
| GET | `/{id}` | Détail d'une recommandation | JWT |

```
POST /api/recommandations/generer
Authorization: Bearer eyJ...
(aucun body — le profil est déjà en DB)
```

---

### Filières — `/api/filieres`

| Méthode | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/` | Toutes les filières (filtre domaine) | Non |
| GET | `/search?q=...` | Recherche par mot-clé | Non |
| GET | `/{id}` | Détail d'une filière | Non |
| POST | `/comparer` | Comparaison côte à côte (2 ou 3 filières) | Non |

**Valeurs `tendance_ia` :**

| Valeur | Signification | Score IA |
|---|---|---|
| 0 | Secteur en forte croissance grâce à l'IA | 1.00 |
| 1 | Secteur stable | 0.75 |
| 2 | Secteur en transformation | 0.40 |
| 3 | Secteur fortement automatisable | 0.10 |

---

### Universités — `/api/universites` | Formations — `/api/formations`

Gestion des établissements et de la liaison Filière × Université. Endpoints publics pour la consultation, routes admin pour la modification.

---

### Favoris — `/api/favoris` | Bacheliers — `/api/bacheliers`

Gestion personnelle (JWT requis). Favoris : GET / POST / DELETE. Bacheliers : GET /me, PATCH /me.

---

### Administration — `/api/admin`

Réservé aux admins ORIAB (JWT admin requis).

| Endpoint | Description |
|---|---|
| GET `/metriques` | Dashboard — statistiques d'usage et perf algo |
| CRUD `/filieres` | Gestion complète de la base de connaissances |
| PATCH `/universites/{id}/accreditation` | Validation accréditation MESRS/CAMES |
| GET `/rapports/filieres-populaires` | Top 10 filières les plus recommandées |

---

## Structure du projet

```
leway_backend/
├── app/
│   ├── api/               ← 9 modules d'endpoints
│   ├── scoring/           ← Moteur psychométrique
│   │   ├── riasec.py      ← Calcul 6 scores RIASEC (0-100)
│   │   ├── cosinus.py     ← Similarité cosinus + Weighted Score
│   │   ├── veto.py        ← 3 Veto Factors éliminatoires
│   │   └── prompt_builder.py  ← Prompts LLM (sans PII)
│   ├── providers/         ← LLM Strategy Pattern
│   │   ├── ollama.py      ← Mistral 7B local + fallback offline
│   │   └── claude_haiku.py ← Claude Haiku 4.5 cloud
│   ├── models/            ← 9 tables PostgreSQL (SQLModel)
│   ├── core/              ← Config, DB, sécurité, dépendances
│   ├── data/
│   │   └── items.json     ← 28 items du questionnaire
│   ├── seed.py            ← Données initiales filières
│   └── main.py            ← Point d'entrée FastAPI
├── insert_filieres.sql    ← Import SQL filières
├── .env.example
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## Base de données — 9 tables

| Table | Description |
|---|---|
| `bachelier` | Comptes — email, série bac, mot de passe haché |
| `administrateur` | Comptes admin |
| `profil_psychometrique` | 6 scores RIASEC + Veto Factors |
| `recommandation` | Rapport généré — version algo, statut |
| `score_compatibilite` | Top 5 détaillé — décomposition 60/25/15 + justif LLM |
| `filiere` | Formations béninoises + données marché |
| `universite` | Établissements + accréditations MESRS/CAMES |
| `formation` | Liaison Filière × Université |
| `favoris` | Sauvegardes personnelles |

```bash
# Réimporter les filières après un reset DB
psql -U postgres -d leway_db -f insert_filieres.sql
```

---

## Règles de gestion (mémoire — non-négociables)

- **RD1** — Un utilisateur est soit bachelier, soit administrateur. Jamais les deux.
- **RD2/RD3** — Un bachelier a exactement un profil psychométrique.
- **RD16** — Les PII (nom, email, téléphone) sont supprimées avant tout appel LLM.
- **RD17** — Les 6 scores RIASEC sont obligatoirement normalisés entre 0 et 100.
- **RD18** — Les Veto Factors sont appliqués avant transmission au LLM.
- **RD19** — Le LLM fonctionne soit cloud, soit offline — jamais les deux pour une même recommandation.

---

## Roadmap v1.1

- [ ] Validation OTP par SMS (Orange API Bénin)
- [ ] Mise en cache Redis des rapports (CU03)
- [ ] Suivi longitudinal — collecte à 6 et 12 mois post-orientation
- [ ] Simulation financière — coût total études vs salaire projeté à 3 ans
- [ ] Tests end-to-end avec DB isolée (pytest-asyncio)
- [ ] Déploiement AWS EC2 + RDS (Fig. 12 du mémoire)
- [ ] Calibration empirique paramètres IRT (n ≥ 200 bacheliers béninois)

---

## Équipe

Mémoire de fin de formation — Licence Professionnelle, Génie Électrique option SIL, UATM GASA FORMATION, Bénin.

| Nom | Rôle |
|---|---|
| **Folawè Milarépa AGLI** | Moteur scoring RIASEC, providers LLM, intégration backend |
| **Marie Josaphat KOUDHOROT** | Infrastructure FastAPI, modèles DB, filières, universités, Flutter |

**Encadrant :** M. OGUNDE Zhoulikoufouli — Responsable IT, RIDCODE SYSTEMS / Enseignant UATM

**Année académique :** 2025–2026

---

*ORIAB — UATM GASA FORMATION — Bénin 2026*
