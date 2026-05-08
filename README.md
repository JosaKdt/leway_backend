# LÉWAY — Backend API

> **Plateforme d'orientation post-baccalauréat au Bénin**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)
[![Status](https://img.shields.io/badge/Status-En%20développement-orange.svg)]()

---

## Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Configuration](#configuration)
- [Lancer le serveur](#lancer-le-serveur)
- [API Reference](#api-reference)
- [Endpoints à implémenter](#endpoints-à-implémenter)
- [Tests](#tests)
- [Équipe](#équipe)

---

## Vue d'ensemble

LÉWAY est une **plateforme d'aide à l'orientation post-baccalauréat** conçue pour les bacheliers béninois. Elle croise trois sources de données pour recommander les filières les plus adaptées à chaque profil :

| Source | Description |
|---|---|
| **Profil psychométrique RIASEC** | Questionnaire 28 items — 6 dimensions (Réaliste, Investigateur, Artistique, Social, Entrepreneur, Conventionnel) |
| **Données marché béninois** | Salaires médians, taux d'insertion, durée réelle des études, 35 filières |
| **Impact IA sur les métiers** | Score tendance IA (0=Croissance → 3=Fortement affecté) |

### Modèle d'intégration

```
LÉWAY Backend (ce repo — FastAPI)
        ↕ HTTP + JWT
App Mobile Flutter (Android)      ←── Marie (KOUDHOROT)
        +
Web React.js (Bolt)               ←── Les deux applis partagent le même backend
        ↕
Moteur de scoring RIASEC          ←── Chéri (à intégrer sur port 8000)
        ↕
LLM Claude Haiku / Ollama         ←── Génération justifications Top 5
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    LÉWAY BACKEND (FastAPI)                    │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  ENDPOINTS DISPONIBLES (Marie)                          │ │
│  │                                                         │ │
│  │  POST /api/auth/register  ── Inscription bachelier      │ │
│  │  POST /api/auth/login     ── Connexion JWT              │ │
│  │  GET  /api/auth/me        ── Profil connecté            │ │
│  │  GET  /api/filieres       ── Liste 35 filières          │ │
│  │  GET  /api/filieres/{id}  ── Détail filière             │ │
│  │  GET  /api/favoris        ── Mes favoris                │ │
│  │  POST /api/favoris        ── Ajouter favori             │ │
│  │  DELETE /api/favoris/{id} ── Supprimer favori           │ │
│  │  GET  /api/bacheliers/me  ── Mon profil                 │ │
│  │  PATCH /api/bacheliers/me ── Mettre à jour profil       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  ENDPOINTS À IMPLÉMENTER (Chéri)                        │ │
│  │                                                         │ │
│  │  POST /api/questionnaire/submit  ── Soumettre réponses  │ │
│  │  GET  /api/recommandations/{id}  ── Top 5 filières      │ │
│  │  GET  /api/profil-riasec/{id}    ── Scores RIASEC       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────┬───────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
     ┌────────▼────────┐      ┌─────────▼────────┐
     │   PostgreSQL 15  │      │    Redis 7.2      │
     │   9 tables       │      │    Cache scoring  │
     └─────────────────┘      └──────────────────┘
```

---

## Structure du projet

```
leway_backend/
│
├── app/
│   ├── __init__.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py          ← POST register / login / GET me
│   │   ├── filieres.py      ← GET liste + détail filières
│   │   ├── favoris.py       ← GET / POST / DELETE favoris
│   │   ├── bacheliers.py    ← GET / PATCH profil bachelier
│   │   │
│   │   │   ── À créer (Chéri) ──
│   │   ├── questionnaire.py ← POST submit réponses RIASEC
│   │   └── recommandations.py ← GET Top 5 + scores RIASEC
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        ← Settings, variables d'environnement
│   │   ├── database.py      ← Connexion PostgreSQL (SQLModel)
│   │   ├── security.py      ← Hash bcrypt + JWT jose
│   │   └── dependencies.py  ← get_current_bachelier (JWT guard)
│   │
│   ├── models/              ← Tables PostgreSQL (SQLModel)
│   │   ├── __init__.py
│   │   ├── bachelier.py
│   │   ├── administrateur.py
│   │   ├── filiere.py
│   │   ├── universite.py
│   │   ├── formation.py
│   │   ├── profil_psychometrique.py
│   │   ├── recommandation.py
│   │   ├── score_compatibilite.py
│   │   └── favoris.py
│   │
│   ├── main.py              ← Point d'entrée FastAPI
│   └── seed.py              ← Seed 35 filières béninoises
│
├── .env.example             ← Variables d'environnement (template)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Installation

### Prérequis

- Python 3.12+
- PostgreSQL 15+
- pip

### Installation locale

```bash
# 1. Cloner le repo
git clone https://github.com/JosaKdt/leway-backend.git
cd leway-backend

# 2. Créer l'environnement virtuel
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Créer la base de données PostgreSQL
psql -U postgres -c "CREATE DATABASE leway_db;"

# 5. Configurer les variables d'environnement
copy .env.example .env
# Éditer .env avec tes valeurs

# 6. Lancer le serveur (les tables se créent automatiquement)
uvicorn app.main:app --reload --port 8000

# 7. Peupler les 35 filières béninoises
python -m app.seed
```

---

## Configuration

Copier `.env.example` en `.env` et renseigner :

```env
# Base de données
POSTGRES_USER=postgres
POSTGRES_PASSWORD=ton_mot_de_passe
POSTGRES_DB=leway_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql://postgres:ton_mot_de_passe@localhost:5432/leway_db

# Redis (optionnel en dev)
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=leway_secret_key_minimum_32_caracteres_ok
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES_BACHELIER=1440
ACCESS_TOKEN_EXPIRE_MINUTES_ADMIN=480

# LLM
LLM_MODE=cloud           # cloud = Claude Haiku | local = Ollama
ANTHROPIC_API_KEY=       # Clé Claude pour LLM_MODE=cloud
OLLAMA_BASE_URL=http://localhost:11434

# App
APP_ENV=development
APP_VERSION=1.0.0
```

---

## Lancer le serveur

```bash
# Développement (rechargement automatique)
uvicorn app.main:app --reload --port 8000

# Documentation interactive
# http://localhost:8000/docs      ← Swagger UI
# http://localhost:8000/redoc     ← ReDoc
```

---

## API Reference

### Auth

#### `POST /api/auth/register`
Inscription d'un nouveau bachelier. Retourne un JWT directement.

```json
{
  "nom": "Mensah",
  "prenom": "Kofi",
  "email": "kofi@email.com",
  "telephone": "+22997000000",
  "mot_de_passe": "password123",
  "serie_bac": "C",
  "notes_bac": null
}
```

**Response 201 :**
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

#### `POST /api/auth/login`
Connexion bachelier.

```json
{
  "email": "kofi@email.com",
  "mot_de_passe": "password123"
}
```

#### `GET /api/auth/me`
Profil du bachelier connecté. Nécessite `Authorization: Bearer {token}`.

---

### Filières

#### `GET /api/filieres`
Liste les 35 filières béninoises. Paramètres optionnels : `domaine`, `search`.

```
GET /api/filieres?domaine=Santé
GET /api/filieres?search=informatique
```

#### `GET /api/filieres/{id_filiere}`
Détail complet d'une filière.

---

### Favoris (nécessite JWT)

#### `GET /api/favoris`
Mes filières sauvegardées.

#### `POST /api/favoris`
```json
{ "id_filiere": "uuid-filiere" }
```

#### `DELETE /api/favoris/{id_favori}`
Supprimer un favori.

---

### Bachelier (nécessite JWT)

#### `GET /api/bacheliers/me`
Mon profil complet.

#### `PATCH /api/bacheliers/me`
```json
{
  "nom": "Mensah",
  "telephone": "+22997111111"
}
```

---

## Endpoints à implémenter (Chéri)

> Ces endpoints sont attendus par l'app Flutter. Marie a déjà préparé les appels dans `api_service.dart`.

### `POST /api/questionnaire/submit`

Soumet les réponses au questionnaire RIASEC et déclenche le calcul des scores.

**Request :**
```json
{
  "reponses": [
    { "question_index": 0, "score": 5 },
    { "question_index": 1, "score": 3 },
    ...
  ]
}
```

**Response attendue :**
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

---

### `GET /api/recommandations/{id_bachelier}`

Retourne le Top 5 des filières recommandées avec justification LLM.

**Response attendue :**
```json
{
  "top_5": [
    {
      "id_filiere": "uuid",
      "nom": "Génie Informatique & Systèmes",
      "score_global": 91,
      "score_riasec": 88,
      "score_marche": 95,
      "score_ia": 92,
      "tendance_ia": "croissance",
      "justification": "Votre profil Investigateur dominant (I) correspond parfaitement..."
    }
  ]
}
```

> **Note :** La décomposition du score suit la formule :
> `score_global = (score_riasec × 0.60) + (score_marche × 0.25) + (score_ia × 0.15)`

---

### `GET /api/profil-riasec/{id_bachelier}`

Retourne le profil RIASEC calculé du bachelier.

---

## Tests

```bash
# Tous les tests
pytest

# Avec coverage
pytest --cov=app --cov-report=term-missing

# Un module spécifique
pytest tests/test_auth.py -v
```

---

## Convention Git

```
main          → code stable uniquement
develop       → branche de travail commune
feature/xxx   → nouvelle fonctionnalité (ex: feature/questionnaire-endpoint)
fix/xxx       → correction de bug
```

**Workflow :**
1. Créer une branche depuis `develop`
2. Coder + commiter
3. Pull request vers `develop`
4. Review → merge

---

## Équipe

| Rôle | Nom | Périmètre |
|---|---|---|
| Frontend Flutter + Backend base | KOUDHOROT Marie Josaphat | Auth, Filières, Favoris, Bacheliers, Seed |
| Moteur RIASEC + LLM + Intégration | AGLI Folawè | Questionnaire, Recommandations, Scoring |

**Encadrement :** Arnaud Rama AGLI

**Institution :** UATM — Filière Génie Électrique, Option Système Informatique et Logiciel

**Année académique :** 2025–2026

---

*LÉWAY Backend — UATM × BFT Group — 2026*
