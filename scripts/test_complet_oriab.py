#!/usr/bin/env python3
"""
ORIAB — Script de validation complète (conformité mémoire)
Usage: venv/bin/python3 /tmp/test_complet_oriab.py
API doit tourner sur http://localhost:8000
Teste tous les cas décrits dans le mémoire (Chapitres II et III)
"""
import json, urllib.request, urllib.error, random, sys, time
from dataclasses import dataclass

BASE = "http://localhost:8000"
OK   = "\033[92m✅\033[0m"
FAIL = "\033[91m❌\033[0m"
WARN = "\033[93m⚠️\033[0m"
SEP  = "─" * 65

passed, failed = [], []

def call(method, path, data=None, token=None, timeout=30):
    headers = {"Content-Type": "application/json"}
    if token: headers["Authorization"] = "Bearer " + token
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(BASE+path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read().decode())
        except: return e.code, {}

def check(ok, msg, detail=""):
    if ok:
        passed.append(msg)
        print(f"  {OK} {msg}")
    else:
        failed.append(msg)
        print(f"  {FAIL} {msg}" + (f" — {detail}" if detail else ""))

def creer_bachelier(serie, email_prefix):
    email = f"{email_prefix}_{random.randint(1000,9999)}@oriab.bj"
    st, r = call("POST", "/api/auth/register", {
        "nom": "Test", "prenom": f"Profil{serie}",
        "email": email, "mot_de_passe": "testpass123",
        "serie_bac": serie
    })
    if st != 201:
        return None, None, None
    token = r.get("access_token")
    return email, "testpass123", token

def soumettre_questionnaire(token, reponses_riasec, tranche=2, mobile=True, horizon="moyen"):
    """reponses_riasec = dict {dim: score_1_5} ex: {'R':5,'I':2,'A':2,'S':2,'E':2,'C':2}"""
    # Récupérer les items de la banque
    st, items_data = call("GET", "/api/profil/items", token=token)
    if st != 200:
        return None, None
    items = items_data["items"]
    
    reponses = {}
    for item in items:
        dim = item["dimension"]
        if dim == "VETO":
            qid = item["id"]
            if qid == "Q18": reponses[qid] = tranche
            elif qid == "Q19": reponses[qid] = 5 if mobile else 1
            elif qid == "Q20": reponses[qid] = 5 if mobile else 1
            elif qid == "Q21":
                reponses[qid] = 1 if horizon=="court" else (3 if horizon=="moyen" else 5)
            elif qid == "Q22": reponses[qid] = 1
        else:
            score = reponses_riasec.get(dim, 3)
            if item.get("inverse"): score = 6 - score
            reponses[item["id"]] = score
    
    st, profil = call("POST", "/api/profil/", {
        "reponses": reponses,
        "ressources_financieres": tranche,
        "mobilite_geo": mobile,
        "horizon_temporel": horizon
    }, token)
    return st, profil

# ══════════════════════════════════════════════════════════════════
print(f"\n{'='*65}")
print("  ORIAB — VALIDATION COMPLÈTE (conformité mémoire §§ II-III)")
print(f"{'='*65}\n")

# ── 0. HEALTH CHECK
print(f"[0] HEALTH CHECK")
st, health = call("GET", "/health")
check(st == 200, "API accessible sur localhost:8000", f"status={st}")
print()

# ── 1. AUTH
print(f"[1] AUTHENTIFICATION")
email_test = f"test_auth_{random.randint(1000,9999)}@oriab.bj"
st, r = call("POST", "/api/auth/register", {
    "nom":"Test","prenom":"Auth","email":email_test,
    "mot_de_passe":"testpass123","serie_bac":"D"
})
check(st == 201, "POST /api/auth/register → 201")
token_test = r.get("access_token","")
check(bool(token_test), "Token JWT reçu à l'inscription")

st, r2 = call("POST", "/api/auth/login",
    {"email": email_test, "mot_de_passe": "testpass123"})
check(st == 200, "POST /api/auth/login → 200")
check(bool(r2.get("access_token")), "Token JWT reçu au login")

st, _ = call("POST", "/api/auth/login",
    {"email": email_test, "mot_de_passe": "mauvais_mdp"})
check(st == 401, "Login avec mauvais mot de passe → 401")
print()

# ── 2. BANQUE D'ITEMS
print(f"[2] BANQUE DE QUESTIONS RIASEC (Chantier 3)")
st, items_data = call("GET", "/api/profil/items", token=token_test)
check(st == 200, "GET /api/profil/items → 200")
if st == 200:
    items = items_data["items"]
    total = items_data["total"]
    riasec_count = items_data["riasec_items"]
    veto_count = items_data["veto_items"]
    check(total == 35, f"Session = 35 items (obtenu: {total})", f"attendu 35")
    check(riasec_count == 30, f"30 items RIASEC (obtenu: {riasec_count})")
    check(veto_count == 5, f"5 items VETO (obtenu: {veto_count})")
    dims = {}
    for item in items:
        d = item["dimension"]
        if d != "VETO": dims[d] = dims.get(d,0) + 1
    check(all(dims.get(d,0)==5 for d in "RIASEC"),
          "5 items par dimension RIASEC",
          f"distribution: {dims}")
    ids = [i["id"] for i in items]
    check(len(ids) == len(set(ids)), "Aucun item dupliqué dans la session")
    check(all("Q18","Q19","Q20","Q21","Q22") and
          all(q in ids for q in ["Q18","Q19","Q20","Q21","Q22"]),
          "Items VETO Q18-Q22 présents")
print()

# ── 3. SCORING RIASEC — profils contrastés
print(f"[3] SCORING RIASEC (déterminisme + normalisation)")

# Profil Réaliste dominant
_, tok_r = creer_bachelier("D", "profil_r")[1:] or (None, None)
email_r, _, tok_r = creer_bachelier("D", "profil_r")
if tok_r:
    st, profil_r = soumettre_questionnaire(tok_r,
        {"R":5,"I":2,"A":1,"S":2,"E":2,"C":3})
    check(st == 201, "POST /api/profil/ → 201 (profil Réaliste)")
    if st == 201:
        check(profil_r["score_r"] > profil_r["score_s"],
              f"R domine S (R={profil_r['score_r']}, S={profil_r['score_s']})")
        check(profil_r["dimension_dominante"] == "R",
              f"Dimension dominante = R (obtenu: {profil_r['dimension_dominante']})")
        check(all(0 <= profil_r[f"score_{d.lower()}"] <= 100 for d in "RIASEC"),
              "Tous les scores normalisés 0-100")

# Profil Social dominant
email_s, _, tok_s = creer_bachelier("A1", "profil_s")
if tok_s:
    st, profil_s = soumettre_questionnaire(tok_s,
        {"R":1,"I":2,"A":3,"S":5,"E":3,"C":2})
    if st == 201:
        check(profil_s["score_s"] > profil_s["score_r"],
              f"S domine R (S={profil_s['score_s']}, R={profil_s['score_r']})")
        check(profil_s["dimension_dominante"] == "S",
              f"Dimension dominante = S (obtenu: {profil_s['dimension_dominante']})")

# Déterminisme : même réponses → mêmes scores
email_d1, _, tok_d1 = creer_bachelier("C", "determ1")
email_d2, _, tok_d2 = creer_bachelier("C", "determ2")
reponses_test = {"R":4,"I":5,"A":2,"S":3,"E":3,"C":4}
if tok_d1 and tok_d2:
    _, p1 = soumettre_questionnaire(tok_d1, reponses_test)
    _, p2 = soumettre_questionnaire(tok_d2, reponses_test)
    if p1 and p2:
        check(p1.get("score_i") == p2.get("score_i"),
              f"Déterminisme : mêmes réponses → mêmes scores (I={p1.get('score_i')})",
              f"p1={p1.get('score_i')} p2={p2.get('score_i')}")
print()

# ── 4. VETO FACTORS (Chantier 2)
print(f"[4] VETO FACTORS — filtrage éliminatoire (§§ RD18 du mémoire)")

def generer_reco(token):
    st_r, rec = call("POST", "/api/recommandations/generer", {}, token, timeout=60)
    if st_r not in (200,201): return None
    rid = rec.get("id_recommandation") or rec.get("id")
    st_d, detail = call("GET", f"/api/recommandations/{rid}", token=token)
    return detail if st_d == 200 else None

# VETO 4 : série bac — A2 ne doit pas avoir Médecine/Génie
email_a2, _, tok_a2 = creer_bachelier("A2", "veto_serie")
if tok_a2:
    # Profil Investigateur fort (devrait vouloir Médecine) mais série A2
    soumettre_questionnaire(tok_a2, {"R":2,"I":5,"A":3,"S":4,"E":2,"C":2})
    detail_a2 = generer_reco(tok_a2)
    if detail_a2:
        scores_a2 = detail_a2.get("scores", [])
        noms_a2 = [s["nom"] for s in scores_a2]
        # Médecine, Génie Info, Data Science exigent C ou D — pas A2
        interdits = ["Médecine", "Génie Informatique", "Data Science", 
                     "Pharmacie", "Sciences Infirmières"]
        violation = [n for n in noms_a2 if any(i in n for i in interdits)]
        check(len(violation)==0,
              f"VETO 4 série bac : A2 ne reçoit pas les filières C/D (reco: {noms_a2[:3]})",
              f"violations: {violation}")
        check(len(scores_a2) > 0,
              f"A2 reçoit quand même des filières compatibles ({len(scores_a2)} filière(s))")

# VETO 1 : durée — horizon court ne doit pas avoir filières >3 ans
email_court, _, tok_court = creer_bachelier("D", "veto_duree")
if tok_court:
    soumettre_questionnaire(tok_court, {"R":3,"I":4,"A":2,"S":3,"E":3,"C":3},
                           tranche=3, mobile=True, horizon="court")
    detail_court = generer_reco(tok_court)
    if detail_court:
        scores_court = detail_court.get("scores", [])
        trop_long = [s for s in scores_court if s.get("duree_theorique",0) > 3]
        check(len(trop_long)==0,
              f"VETO 1 durée : horizon court → pas de filières >3 ans",
              f"violations: {[s['nom'] for s in trop_long]}")
        eliminees = detail_court.get("eliminees", [])
        check(len(eliminees) > 0, f"Des filières ont été éliminées par veto ({len(eliminees)} éliminées)")
print()

# ── 5. RECOMMANDATIONS — qualité et cohérence
print(f"[5] RECOMMANDATIONS — qualité (§§ 289-292 mémoire)")

email_d, _, tok_d = creer_bachelier("D", "reco_d")
if tok_d:
    soumettre_questionnaire(tok_d, {"R":5,"I":5,"A":2,"S":3,"E":3,"C":4},
                           tranche=4, mobile=True, horizon="long")
    detail_d = generer_reco(tok_d)
    if detail_d:
        scores_d = detail_d.get("scores", [])
        check(1 <= len(scores_d) <= 3,
              f"Top entre 1 et 3 filières (obtenu: {len(scores_d)})")
        if len(scores_d) >= 2:
            ws_values = [s.get("weighted_score",0) for s in scores_d]
            check(ws_values == sorted(ws_values, reverse=True),
                  f"Filières triées par WS décroissant: {[round(w) for w in ws_values]}")
            check(all(0 < w <= 100 for w in ws_values),
                  f"WS entre 0 et 100: {ws_values}")
        # Vérifier la formule WS = 0.60*RIASEC + 0.25*marché + 0.15*IA
        for s in scores_d[:1]:
            ws = s.get("weighted_score",0)
            sim = s.get("sim_riasec",0)   # 0-100
            sm  = s.get("score_marche",0) # 0-1
            sia = s.get("score_ia",0)     # 0-1
            if sim and sm and sia:
                ws_calc = 0.60*(sim/100) + 0.25*sm + 0.15*sia
                ecart = abs(ws_calc*100 - ws)
                check(ecart < 2.0,
                      f"Formule WS validée : calc={round(ws_calc*100,1)}% vs DB={ws}% (écart={round(ecart,2)}%)")
print()

# ── 6. BASE DE CONNAISSANCES
print(f"[6] BASE DE CONNAISSANCES (Chantier 1)")
st, filieres_list = call("GET", "/api/filieres/")
check(st == 200, "GET /api/filieres/ → 200")
if st == 200:
    n = len(filieres_list)
    check(n >= 100, f"Au moins 100 filières en base (obtenu: {n})")
    domaines = set(f["domaine"] for f in filieres_list if f.get("domaine"))
    check(len(domaines) >= 5, f"Au moins 5 domaines distincts ({len(domaines)}: {list(domaines)[:5]})")

# Test endpoint comparer
st_c, comp = call("POST", "/api/filieres/comparer",
    {"noms": ["Médecine Générale", "Chirurgie Dentaire"]})
check(st_c == 200, "POST /api/filieres/comparer → 200")
if st_c == 200:
    check(len(comp) == 2,
          f"Comparer retourne 2 filières (obtenu: {len(comp)})",
          f"noms retournés: {[f['nom'] for f in comp]}")
print()

# ── 7. PIPELINE LLM
print(f"[7] PIPELINE LLM DUAL (mode hors-ligne Ollama)")
st_ol, ollama = call("GET", "http://localhost:11434/api/tags".replace(BASE,""),
    timeout=3) if False else (None, None)
# Test indirect : vérifier que la recommandation a une synthèse
if tok_d and detail_d:
    st_rec, rec_full = call("GET", f"/api/recommandations/{detail_d.get('id_recommandation','')}",
        token=tok_d)
    if st_rec == 200:
        synth = rec_full.get("rapport_synthese","") or ""
        just  = next((s.get("justification_ia","") for s in scores_d if s.get("justification_ia")), "")
        check(len(synth) > 20 or len(just) > 20,
              f"LLM a généré une justification ({len(just)} chars)",
              "LLM peut ne pas avoir répondu — vérifier Ollama")
print()

# ── 8. SÉCURITÉ — règles RD
print(f"[8] SÉCURITÉ (règles RD du mémoire)")
# RD01 : endpoint protégé sans token → 401
st_p, _ = call("GET", "/api/profil/moi")
check(st_p == 401, "RD01 : profil/moi sans token → 401")
st_p2, _ = call("POST", "/api/recommandations/generer", {})
check(st_p2 == 401, "RD01 : recommandations/generer sans token → 401")
# Items non protégés (données publiques)
st_i, _ = call("GET", "/api/profil/items")
check(st_i == 200, "Items questionnaire accessibles sans token (données publiques)")
print()

# ── BILAN
print(f"{'='*65}")
print(f"  RÉSULTATS : {len(passed)} tests passés / {len(passed)+len(failed)} total")
if failed:
    print(f"\n  {FAIL} ÉCHECS ({len(failed)}) :")
    for f in failed:
        print(f"    - {f}")
else:
    print(f"\n  {OK} TOUS LES TESTS PASSENT — Application conforme au mémoire")
print(f"{'='*65}\n")
sys.exit(0 if not failed else 1)
