# LÉWAY Backend — FastAPI

Plateforme d'aide à l'orientation post-baccalauréat pour les bacheliers béninois.

---

## État actuel du projet (Mai 2026)

### Ce qui est fait et fonctionnel

**Backend (Marie)**
- Auth complète : inscription, connexion, JWT Bearer
- 199 filières béninoises insérées en base PostgreSQL (20 domaines)
- CRUD filières avec filtres domaine et recherche
- CRUD favoris
- Profil bachelier (GET + PATCH)

**App Flutter (Marie)**
- Connexion réelle au backend (JWT)
- Navigation filières par domaine (grille 20 domaines → liste → comparaison)
- Recherche globale et par domaine
- Comparaison jusqu'à 3 filières
- Profil bachelier connecté à l'API
- Cache local des filières (6h) — fallback offline
- URL auto-détectée selon plateforme (Android : `10.0.2.2:8000`, Windows : `127.0.0.1:8000`)

### Ce qui reste à faire (Folawè)

| Endpoint | Description |
|---|---|
| `POST /api/questionnaire/submit` | Soumettre réponses RIASEC → déclencher scoring |
| `GET /api/recommandations/{id_bachelier}` | Top 5 filières recommandées + justification LLM |
| `GET /api/profil-riasec/{id_bachelier}` | Scores RIASEC calculés |

> Le Flutter a déjà les appels préparés dans `api_service.dart`. Dès que ces 3 endpoints existent, la connexion est immédiate.

---

## Architecture

```
LÉWAY Backend (FastAPI — port 8000)
        ↕ HTTP + JWT Bearer
App Mobile Flutter (Android/Windows)   ← Marie
        +
Moteur de scoring RIASEC               ← Folawè (à intégrer)
        ↕
LLM Claude Haiku / Ollama              ← Génération justifications Top 5
        ↕
PostgreSQL 15 (9 tables) + Redis 7.2
```

---

## Installation

### Prérequis

- Python 3.12+
- PostgreSQL 15+

### Démarrage local

```bash
# 1. Cloner le repo
git clone https://github.com/JosaKdt/leway-backend.git
cd leway-backend

# 2. Environnement virtuel
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

# 3. Dépendances
pip install -r requirements.txt

# 4. Base de données
psql -U postgres -c "CREATE DATABASE leway_db;"

# 5. Variables d'environnement
copy .env.example .env
# Éditer .env avec tes valeurs

# 6. Lancer le serveur
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
```

> **Important :** `--host 0.0.0.0` est obligatoire pour que l'émulateur Android puisse joindre le serveur.

### Variables d'environnement (.env)

```env
DATABASE_URL=postgresql://postgres:ton_mot_de_passe@localhost:5432/leway_db
REDIS_URL=redis://localhost:6379/0

SECRET_KEY=leway_secret_key_minimum_32_caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES_BACHELIER=1440
ACCESS_TOKEN_EXPIRE_MINUTES_ADMIN=480

LLM_MODE=cloud
ANTHROPIC_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434

APP_ENV=development
APP_VERSION=1.0.0
```

---

## Base de données

### Remettre les filières après un DROP

Si tu recrées la base, réexécuter le script SQL :

```bash
psql -U postgres -d leway_db -f insert_filieres.sql
```

Le fichier `insert_filieres.sql` (199 filières) est versionné dans ce repo.

### Nettoyer les doublons d'encodage (Windows)

Si tu constates des doublons (`Ingénierie` / `Ing├®nierie`) après import sur Windows :

```sql
UPDATE filiere SET domaine = 'Ingénierie'  WHERE domaine ILIKE 'Ing%nierie';
UPDATE filiere SET domaine = 'Santé'       WHERE domaine ILIKE 'Sant%';
UPDATE filiere SET domaine = 'Education'   WHERE domaine ILIKE '%ducation%';
UPDATE filiere SET domaine = 'Economie'    WHERE domaine ILIKE '%conomie%';
```

---

## API Reference

### Auth

| Méthode | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/auth/register` | Inscription bachelier — retourne JWT | Non |
| POST | `/api/auth/login` | Connexion — retourne JWT | Non |
| GET | `/api/auth/me` | Profil du bachelier connecté | JWT |

**Register — body :**
```json
{
  "nom": "Mensah",
  "prenom": "Kofi",
  "email": "kofi@email.com",
  "telephone": "+22997000000",
  "mot_de_passe": "password123",
  "serie_bac": "C"
}
```

**Login — body :**
```json
{
  "email": "kofi@email.com",
  "mot_de_passe": "password123"
}
```

**Réponse login/register :**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "bachelier": {
    "id_bachelier": "uuid",
    "nom": "Mensah",
    "prenom": "Kofi",
    "email": "kofi@email.com",
    "serie_bac": "C",
    "date_creation": "2026-05-06T10:00:00Z"
  }
}
```

---

### Filières

| Méthode | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/filieres` | Liste des 199 filières (filtres optionnels) | Non |
| GET | `/api/filieres/{id_filiere}` | Détail d'une filière | Non |
| POST | `/api/filieres` | Créer une filière (admin) | Non |

**Paramètres de filtre :**
```
GET /api/filieres?domaine=Informatique
GET /api/filieres?search=gestion
```

**Structure d'une filière :**
```json
{
  "id_filiere": "uuid",
  "nom": "Génie Logiciel",
  "domaine": "Informatique",
  "duree_theorique": 3,
  "salaire_median_p50": 250000,
  "taux_insertion": 0.85,
  "indice_saturation": 0.30,
  "tendance_ia": 0,
  "tendance_curricula_marche": 0.70,
  "profil_riasec_dominant": {"R": 0.4, "I": 0.9, "A": 0.3, "S": 0.4, "E": 0.6, "C": 0.7}
}
```

**Valeurs `tendance_ia` :**

| Valeur | Signification |
|---|---|
| 0 | En forte croissance |
| 1 | Stable |
| 2 | En transformation |
| 3 | Fortement affecté par l'IA |

---

### Bachelier

| Méthode | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/bacheliers/me` | Profil complet | JWT |
| PATCH | `/api/bacheliers/me` | Mettre à jour le profil | JWT |

**PATCH — body (tous les champs optionnels) :**
```json
{
  "nom": "Mensah",
  "telephone": "+22997111111",
  "serie_bac": "D"
}
```

---

### Favoris

| Méthode | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/favoris` | Mes favoris | JWT |
| POST | `/api/favoris` | Ajouter un favori | JWT |
| DELETE | `/api/favoris/{id_favori}` | Supprimer un favori | JWT |

**POST — body :**
```json
{ "id_filiere": "uuid-filiere" }
```

---

### Endpoints à implémenter — Folawè

> Ces 3 endpoints sont attendus par le Flutter. Les appels sont déjà préparés dans `api_service.dart`.

#### `POST /api/questionnaire/submit` — JWT requis

Soumet les 28 réponses RIASEC et déclenche le calcul.

**Body attendu :**
```json
{
  "reponses": [
    { "question_index": 0, "score": 5 },
    { "question_index": 1, "score": 3 }
  ]
}
```

**Réponse attendue :**
```json
{
  "profil_riasec": {
    "R": 70, "I": 88, "A": 55,
    "S": 65, "E": 72, "C": 80
  },
  "profil_dominant": "I",
  "score_global": 78
}
```

#### `GET /api/recommandations/{id_bachelier}` — JWT requis

Retourne le Top 5 filières recommandées avec justification LLM.

**Réponse attendue :**
```json
{
  "top_5": [
    {
      "id_filiere": "uuid",
      "nom": "Génie Informatique",
      "score_global": 91,
      "score_riasec": 88,
      "score_marche": 95,
      "score_ia": 92,
      "justification": "Votre profil Investigateur dominant (I) correspond parfaitement..."
    }
  ]
}
```

> Formule du score : `score_global = (score_riasec × 0.60) + (score_marche × 0.25) + (score_ia × 0.15)`

#### `GET /api/profil-riasec/{id_bachelier}` — JWT requis

Retourne les scores RIASEC calculés du bachelier.

---

## Structure du projet

```
leway_backend/
├── app/
│   ├── api/
│   │   ├── auth.py           ✅ POST register / login / GET me
│   │   ├── filieres.py       ✅ GET liste + détail + POST
│   │   ├── favoris.py        ✅ GET / POST / DELETE
│   │   ├── bacheliers.py     ✅ GET / PATCH profil
│   │   ├── questionnaire.py  ⏳ À créer — Folawè
│   │   └── recommandations.py ⏳ À créer — Folawè
│   ├── core/
│   │   ├── config.py         ✅ Settings pydantic-settings
│   │   ├── database.py       ✅ SQLModel + PostgreSQL
│   │   ├── security.py       ✅ bcrypt + JWT jose
│   │   └── dependencies.py   ✅ JWT guards bachelier + admin
│   ├── models/
│   │   ├── bachelier.py      ✅
│   │   ├── administrateur.py ✅
│   │   ├── filiere.py        ✅
│   │   ├── universite.py     ✅
│   │   ├── formation.py      ✅
│   │   ├── profil_psychometrique.py ✅
│   │   ├── recommandation.py ✅
│   │   ├── score_compatibilite.py   ✅
│   │   └── favoris.py        ✅
│   └── main.py               ✅ Point d'entrée FastAPI
├── insert_filieres.sql        ✅ 199 filières béninoises
├── .env.example
├── requirements.txt
└── README.md
```

---

## Convention Git

```
main        → code stable uniquement
develop     → branche de travail commune
feature/xxx → nouvelle fonctionnalité
fix/xxx     → correction de bug
```

**Workflow :**
1. Créer une branche depuis `develop`
2. Coder + commiter
3. Pull request vers `develop`
4. Review → merge

---

## Documentation interactive

Avec le serveur démarré :

```
http://localhost:8000/docs    ← Swagger UI (tester les endpoints)
http://localhost:8000/redoc   ← ReDoc
```

Pour tester les routes protégées dans `/docs` : cliquer **Authorize** → coller le token JWT obtenu au login.

---

## Équipe

| Rôle | Nom | Périmètre |
|---|---|---|
| Frontend Flutter + Backend base | KOUDHOROT Marie Josaphat | Auth, Filières, Favoris, Bacheliers |
| Moteur RIASEC + LLM + Intégration | AGLI Folawè Milarépa | Questionnaire, Recommandations, Scoring |

**Encadrement :** Arnaud Rama AGLI

**Institution :** UATM — Filière Génie Électrique, Option Système Informatique et Logiciel

**Année académique :** 2025–2026

---

*LÉWAY Backend — UATM × BFT Group — 2026*
