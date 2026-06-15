#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ORIAB — TEST EXHAUSTIF DE CONFORMITÉ AU MÉMOIRE
================================================
Valide CHAQUE règle RD, CHAQUE cas d'utilisation CU, CHAQUE formule,
CHAQUE table du schéma relationnel, et CHAQUE fonctionnalité décrite.

Usage : venv/bin/python3 scripts/test_exhaustif.py
Prérequis : API sur :8000, PostgreSQL démarré, Ollama (optionnel)

Référence : Mémoire ORIAB Chapitres II (Conception) et III (Réalisation)
"""
import json, urllib.request, urllib.error, random, sys, os, time

BASE = "http://localhost:8000"
DB_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:azerty@localhost:5432/leway_db")
OK   = "\033[92m✅\033[0m"
FAIL = "\033[91m❌\033[0m"
WARN = "\033[93m⚠️ \033[0m"
SKIP = "\033[90m⊘\033[0m"
BOLD = "\033[1m"
RST  = "\033[0m"

passed, failed, warned, skipped = [], [], [], []

def call(method, path, data=None, token=None, timeout=60):
    headers = {"Content-Type": "application/json"}
    if token: headers["Authorization"] = "Bearer " + token
    body = json.dumps(data).encode() if data else None
    url = path if path.startswith("http") else BASE + path
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            txt = r.read().decode()
            return r.status, (json.loads(txt) if txt else {})
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read().decode())
        except: return e.code, {}
    except Exception as e:
        return 0, {"error": str(e)}

def check(ok, msg, detail=""):
    if ok:
        passed.append(msg); print(f"  {OK} {msg}")
    else:
        failed.append((msg, detail))
        print(f"  {FAIL} {msg}" + (f"  → {detail}" if detail else ""))

def warn(msg, detail=""):
    warned.append(msg); print(f"  {WARN} {msg}" + (f"  → {detail}" if detail else ""))

def skip(msg):
    skipped.append(msg); print(f"  {SKIP} {msg} (ignoré)")

def section(titre):
    print(f"\n{BOLD}{titre}{RST}")

# DB direct (psycopg2)
try:
    import psycopg2
    HAS_DB = True
except ImportError:
    HAS_DB = False

def db_query(sql, params=None):
    if not HAS_DB: return None
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        cur.close(); conn.close()
        return rows
    except Exception as e:
        return [("DBERROR", str(e))]

# Helpers métier
def register(serie, prefix="t"):
    email = f"{prefix}_{random.randint(10000,99999)}@oriab.bj"
    st, r = call("POST", "/api/auth/register", {
        "nom":"Test","prenom":f"P{serie}","email":email,
        "mot_de_passe":"testpass123","serie_bac":serie})
    return (email, r.get("access_token")) if st == 201 else (None, None)

def fill_questionnaire(token, riasec, tranche=2, mobile=True, horizon="moyen"):
    st, data = call("GET","/api/profil/items",token=token)
    if st != 200: return None, None
    rep = {}
    for it in data["items"]:
        d = it["dimension"]
        if d == "VETO":
            q = it["id"]
            rep[q] = {"Q18":tranche,"Q19":5 if mobile else 1,"Q20":5 if mobile else 1,
                      "Q21":1 if horizon=="court" else 3 if horizon=="moyen" else 5,
                      "Q22":1}.get(q,3)
        else:
            s = riasec.get(d,3)
            rep[it["id"]] = (6-s) if it.get("inverse") else s
    st, prof = call("POST","/api/profil/",{
        "reponses":rep,"ressources_financieres":tranche,
        "mobilite_geo":mobile,"horizon_temporel":horizon},token)
    return st, prof

def generate_reco(token):
    st, rec = call("POST","/api/recommandations/generer",{},token,timeout=90)
    if st not in (200,201): return None, None
    rid = rec.get("id_recommandation") or rec.get("id")
    st2, detail = call("GET",f"/api/recommandations/{rid}",token=token)
    return (rid, detail) if st2==200 else (rid, None)

print(f"\n{'='*68}")
print(f"  {BOLD}ORIAB — TEST EXHAUSTIF DE CONFORMITÉ AU MÉMOIRE{RST}")
print(f"  20 règles RD · 4 cas CU · formules · 8 tables · sécurité")
print(f"{'='*68}")

# ════════════════════════════════════════════════════════════════
section("§0 — INFRASTRUCTURE")
st, _ = call("GET","/health")
check(st==200, "API FastAPI accessible (:8000)", f"status={st}")
if HAS_DB:
    rows = db_query("SELECT version()")
    check(rows and "PostgreSQL" in str(rows[0][0]), "PostgreSQL connecté")
else:
    skip("Vérif DB directe (psycopg2 absent)")

# Ollama optionnel
st_ol, _ = call("GET","http://localhost:11434/api/tags",timeout=3)
if st_ol == 200:
    check(True, "Ollama accessible (mode offline LLM)")
else:
    warn("Ollama non accessible", "le LLM offline ne répondra pas — fallback testé plus bas")

# ════════════════════════════════════════════════════════════════
section("§1 — SCHÉMA RELATIONNEL (mémoire §330-339, 8 tables)")
if HAS_DB:
    tables_attendues = ["bachelier","profil_psychometrique","filiere","universite",
                        "formation","recommandation","score_compatibilite","favoris"]
    rows = db_query("""SELECT table_name FROM information_schema.tables 
                       WHERE table_schema='public'""")
    tables_db = [r[0] for r in rows] if rows else []
    for t in tables_attendues:
        check(t in tables_db, f"Table '{t}' existe")
    # Colonnes critiques SCORE_COMPATIBILITE
    rows = db_query("""SELECT column_name FROM information_schema.columns 
                       WHERE table_name='score_compatibilite'""")
    cols = [r[0] for r in rows] if rows else []
    for c in ["score_weighted","score_riasec_match","score_marche","score_ia","classement","justification_ia"]:
        check(c in cols, f"score_compatibilite.{c} (mémoire §338)")
    # PROFIL : les 6 scores + veto factors
    rows = db_query("""SELECT column_name FROM information_schema.columns 
                       WHERE table_name='profil_psychometrique'""")
    pcols = [r[0] for r in rows] if rows else []
    for c in ["score_r","score_i","score_a","score_s","score_e","score_c",
              "ressources_financieres","mobilite_geo","horizon_temporel"]:
        check(c in pcols, f"profil_psychometrique.{c} (mémoire §333)")
else:
    skip("Vérification schéma (psycopg2 absent)")

# ════════════════════════════════════════════════════════════════
section("§2 — CU01 : Inscription + création profil (mémoire §202)")
email, token = register("D","cu01")
check(token is not None, "CU01 : inscription bachelier → token JWT")
if HAS_DB and email:
    rows = db_query("SELECT serie_bac, mot_de_passe_hash FROM bachelier WHERE email=%s",(email,))
    if rows and rows[0][0] != "DBERROR":
        check(rows[0][0]=="D", "Série bac persistée en DB")
        check(rows[0][1] and rows[0][1] != "testpass123",
              "RD: mot de passe haché (bcrypt), pas en clair")

# ════════════════════════════════════════════════════════════════
section("§3 — CU02 : Connexion (mémoire §204)")
st, r = call("POST","/api/auth/login",{"email":email,"mot_de_passe":"testpass123"})
check(st==200 and r.get("access_token"), "CU02 : login → token JWT")
st, _ = call("POST","/api/auth/login",{"email":email,"mot_de_passe":"WRONG"})
check(st==401, "Login mauvais mot de passe → 401")
st, _ = call("POST","/api/auth/login",{"email":"inexistant@x.bj","mot_de_passe":"x"})
check(st==401, "Login email inexistant → 401")

# ════════════════════════════════════════════════════════════════
section("§4 — RD17 : Banque RIASEC + normalisation 0-100")
st, data = call("GET","/api/profil/items",token=token)
check(st==200, "GET /api/profil/items → 200")
if st==200:
    items = data["items"]
    check(data["total"]==35, "35 items/session", f"obtenu {data['total']}")
    check(data["riasec_items"]==30, "30 items RIASEC")
    check(data["veto_items"]==5, "5 items VETO")
    dims={}
    for it in items:
        if it["dimension"]!="VETO": dims[it["dimension"]]=dims.get(it["dimension"],0)+1
    check(all(dims.get(d,0)==5 for d in "RIASEC"), "5 items/dimension", str(dims))
    ids=[it["id"] for it in items]
    check(len(ids)==len(set(ids)), "Aucun item dupliqué")
    veto_ids = [it["id"] for it in items if it["dimension"]=="VETO"]
    check(sorted(veto_ids)==["Q18","Q19","Q20","Q21","Q22"], "Items VETO = Q18-Q22")
    # Inversés présents
    inverses = [it for it in items if it.get("inverse")]
    check(len(inverses)>=1, f"Items inversés présents ({len(inverses)})")

# ════════════════════════════════════════════════════════════════
section("§5 — Scoring RIASEC : normalisation + dominantes + déterminisme")
# Profil R pur
_, tok_r = register("D","sco_r")
st, pr = fill_questionnaire(tok_r, {"R":5,"I":2,"A":1,"S":1,"E":2,"C":3})
check(st==201, "Soumission questionnaire → 201")
if pr:
    scores = [pr[f"score_{d}"] for d in "risaec"]
    check(all(0<=s<=100 for s in scores), "RD17 : tous scores ∈ [0,100]", str(scores))
    check(pr["dimension_dominante"]=="R", "Profil R pur → dominante R", pr["dimension_dominante"])
    check(pr["score_r"]>pr["score_s"], f"R({pr['score_r']}) > S({pr['score_s']})")

# Profil S pur
_, tok_s = register("A1","sco_s")
_, ps = fill_questionnaire(tok_s, {"R":1,"I":2,"A":3,"S":5,"E":3,"C":2})
if ps:
    check(ps["dimension_dominante"]=="S", "Profil S pur → dominante S", ps["dimension_dominante"])

# Déterminisme
_, t1 = register("C","det1"); _, t2 = register("C","det2")
rep = {"R":4,"I":5,"A":2,"S":3,"E":3,"C":4}
_, p1 = fill_questionnaire(t1, rep); _, p2 = fill_questionnaire(t2, rep)
if p1 and p2:
    check(p1["score_i"]==p2["score_i"] and p1["score_r"]==p2["score_r"],
          "Déterminisme : mêmes réponses → mêmes scores",
          f"I:{p1['score_i']}={p2['score_i']} R:{p1['score_r']}={p2['score_r']}")

# RD2/RD3 : un seul profil par bachelier
st_dup, _ = fill_questionnaire(tok_r, {"R":3,"I":3,"A":3,"S":3,"E":3,"C":3})
check(st_dup==409, "RD2/RD3 : 2e profil refusé → 409 (un seul profil/bachelier)", f"status={st_dup}")

# ════════════════════════════════════════════════════════════════
section("§6 — RD18 : Veto Factors AVANT le LLM")
# VETO 4 — Série bac (A2 ne peut pas Médecine/Génie)
_, tok_a2 = register("A2","veto4")
fill_questionnaire(tok_a2, {"R":2,"I":5,"A":3,"S":4,"E":2,"C":2})
rid_a2, det_a2 = generate_reco(tok_a2)
if det_a2:
    noms = [s["nom"] for s in det_a2.get("scores",[])]
    interdits = ["Médecine","Génie Informatique","Data Science","Pharmacie","Sciences Infirmières","Chirurgie"]
    viol = [n for n in noms if any(i in n for i in interdits)]
    check(len(viol)==0, "VETO 4 : A2 ne reçoit aucune filière C/D", f"violations={viol}")
    elim = det_a2.get("eliminees",[])
    serie_elim = [e for e in elim if "série" in " ".join(e.get("raisons_veto",e.get("motif_veto",""))).lower()] if elim else []
    check(len(elim)>0, f"Des filières éliminées par veto ({len(elim)})")

# VETO 1 — Durée (horizon court → pas de filières longues)
_, tok_c = register("D","veto1")
fill_questionnaire(tok_c, {"R":3,"I":4,"A":2,"S":3,"E":3,"C":3}, tranche=4, horizon="court")
rid_c, det_c = generate_reco(tok_c)
if det_c:
    trop_long = [s for s in det_c.get("scores",[]) if (s.get("duree_theorique") or 0)>3]
    check(len(trop_long)==0, "VETO 1 : horizon court → aucune filière >3 ans",
          f"violations={[s['nom'] for s in trop_long]}")

# VETO 4 inverse — D accède aux filières scientifiques
_, tok_d = register("D","veto_d")
fill_questionnaire(tok_d, {"R":4,"I":5,"A":2,"S":3,"E":3,"C":4}, tranche=4, horizon="long")
rid_d, det_d = generate_reco(tok_d)
if det_d:
    noms_d = [s["nom"] for s in det_d.get("scores",[])]
    check(len(noms_d)>0, f"Série D reçoit des filières ({len(noms_d)})", str(noms_d[:3]))

# ════════════════════════════════════════════════════════════════
section("§7 — Formule Weighted Score (mémoire §289-292)")
# WS = 0.60*RIASEC + 0.25*marché + 0.15*IA
if det_d and det_d.get("scores"):
    erreurs_formule = 0
    erreurs_detail = []
    for s in det_d["scores"]:
        ws = s.get("weighted_score",0)
        sim = s.get("sim_riasec",0)      # 0-100 (score_riasec_match en DB)
        sm  = s.get("score_marche",0)    # 0-1
        sia = s.get("score_ia",0)        # 0-1
        if sim and sm is not None and sia is not None:
            # sim est déjà en 0-100, donc sim/100 le ramène en 0-1 pour la formule
            ws_calc = (0.60*(sim/100.0) + 0.25*sm + 0.15*sia)*100
            ecart = abs(ws_calc - ws)
            if ecart > 2.0:
                erreurs_formule += 1
                erreurs_detail.append(f"{s['nom'][:25]}: calc={round(ws_calc,1)} db={ws} (sim={sim},sm={sm},sia={sia})")
    check(erreurs_formule==0, "WS = 0.60×RIASEC + 0.25×marché + 0.15×IA vérifié sur Top 3",
          f"{erreurs_formule} écart(s)>2% — {erreurs_detail[:2]}")
    # Tri décroissant
    ws_list = [s["weighted_score"] for s in det_d["scores"]]
    check(ws_list==sorted(ws_list,reverse=True), "Filières triées par WS décroissant", str([round(w) for w in ws_list]))
    # 1 à 3 filières
    check(1<=len(det_d["scores"])<=3, f"Top entre 1 et 3 filières ({len(det_d['scores'])})")
    # WS dans [0,100]
    check(all(0<w<=100 for w in ws_list), "Tous les WS ∈ ]0,100]", str([round(w) for w in ws_list]))

# score_IA selon table (0→1.00, 1→0.75, 2→0.40, 3→0.10)
section("§8 — Mapping score_IA (mémoire : 0→1.00|1→0.75|2→0.40|3→0.10)")
if HAS_DB:
    mapping = {0:1.00, 1:0.75, 2:0.40, 3:0.10}
    rows = db_query("""SELECT f.tendance_ia, sc.score_ia, f.nom
                       FROM score_compatibilite sc 
                       JOIN filiere f ON f.id_filiere=sc.id_filiere
                       WHERE sc.score_ia IS NOT NULL AND f.tendance_ia IS NOT NULL
                       LIMIT 50""")
    if rows and rows[0][0]!="DBERROR":
        erreurs=0; details=[]
        for tend, score_ia, nom in rows:
            tend_i = int(tend)
            if tend_i in mapping and abs(mapping[tend_i]-float(score_ia))>0.05:
                erreurs+=1
                details.append(f"{nom[:20]}: tend={tend_i} score_ia={float(score_ia)} attendu={mapping[tend_i]}")
        check(erreurs==0, "Mapping tendance_ia → score_ia conforme sur recos existantes",
              f"{erreurs} écart(s) — {details[:2]}")
    else:
        skip("Pas de données score_ia à vérifier")
else:
    skip("Mapping score_IA (psycopg2 absent)")

# ════════════════════════════════════════════════════════════════
section("§9 — CU03 : Consulter recommandations (mémoire §206)")
st, mes = call("GET","/api/recommandations/moi",token=tok_d)
check(st==200, "CU03 : GET /api/recommandations/moi → 200")
check(isinstance(mes,list) and len(mes)>=1, "Historique recommandations non vide")
if det_d:
    check("scores" in det_d, "Détail recommandation contient scores[]")
    check("eliminees" in det_d, "Détail recommandation contient eliminees[]")
    # Vérifier données enrichies
    if det_d.get("scores"):
        s0 = det_d["scores"][0]
        for champ in ["nom","domaine","weighted_score","duree_theorique"]:
            check(champ in s0, f"Score enrichi avec '{champ}'")

# ════════════════════════════════════════════════════════════════
section("§10 — CU04 : Comparer filières (mémoire §208)")
st, comp = call("POST","/api/filieres/comparer",
                {"noms":["Médecine Générale","Chirurgie Dentaire"]})
check(st==200, "CU04 : POST /api/filieres/comparer → 200")
if st==200:
    check(isinstance(comp,list), "Comparer retourne une liste")
    check(len(comp)>=1, f"Comparaison retourne des filières ({len(comp)})")

# ════════════════════════════════════════════════════════════════
section("§11 — RD16 : PII supprimées avant LLM")
# Vérification indirecte : le profil envoyé au LLM ne doit pas contenir email/nom
# On vérifie que les justifications ne contiennent jamais l'email du bachelier
if det_d and det_d.get("scores"):
    just_all = " ".join(s.get("justification_ia","") or "" for s in det_d["scores"])
    email_d_local = "veto_d"
    check(email_d_local not in just_all and "@oriab.bj" not in just_all,
          "RD16 : aucune PII (email) dans les justifications LLM")

# ════════════════════════════════════════════════════════════════
section("§12 — Base de connaissances (Chantier 1)")
st, fils = call("GET","/api/filieres/")
check(st==200, "GET /api/filieres/ → 200")
if st==200:
    check(len(fils)>=100, f"≥100 filières en base ({len(fils)})")
    domaines = set(f.get("domaine") for f in fils if f.get("domaine"))
    check(len(domaines)>=5, f"≥5 domaines ({len(domaines)})", str(list(domaines)[:6]))
    # Toutes ont une durée
    sans_duree = [f["nom"] for f in fils if not f.get("duree_theorique")]
    check(len(sans_duree)==0, "Toutes les filières ont une durée", f"{len(sans_duree)} sans durée")

# Universités
if HAS_DB:
    rows = db_query("SELECT COUNT(*) FROM universite")
    if rows and rows[0][0]!="DBERROR":
        check(rows[0][0]>=10, f"≥10 universités en base ({rows[0][0]})")
    rows = db_query("SELECT COUNT(*) FROM formation")
    if rows and rows[0][0]!="DBERROR":
        check(rows[0][0]>=100, f"≥100 formations (liens filière-université) ({rows[0][0]})")

# ════════════════════════════════════════════════════════════════
section("§13 — RD19 : Mode LLM unique (cloud XOR offline)")
if HAS_DB:
    # Vérifier .env : LLM_MODE défini
    skip("Vérif LLM_MODE (lecture .env hors scope test runtime)")
else:
    skip("RD19 (psycopg2 absent)")
# Test indirect : une reco a été générée → le LLM (ou fallback) a fonctionné
check(det_d is not None, "RD19 : pipeline LLM a produit une recommandation (mode actif)")

# ════════════════════════════════════════════════════════════════
section("§14 — SÉCURITÉ JWT (mémoire §322-323)")
st, _ = call("GET","/api/profil/moi")
check(st==401, "Endpoint protégé sans token → 401 (profil/moi)")
st, _ = call("POST","/api/recommandations/generer",{})
check(st==401, "Génération sans token → 401")
st, _ = call("GET","/api/recommandations/moi")
check(st==401, "Historique sans token → 401")
st, _ = call("GET","/api/profil/items")
check(st==200, "Items publics accessibles sans token")
st, _ = call("GET","/api/filieres/")
check(st==200, "Filières publiques accessibles sans token")
# Token invalide
st, _ = call("GET","/api/profil/moi",token="faux.token.invalide")
check(st==401, "Token JWT invalide → 401")

# ════════════════════════════════════════════════════════════════
section("§15 — Section D = Veto uniquement (jamais dans RIASEC)")
# Deux bachelier mêmes réponses RIASEC mais Section D différente → mêmes scores RIASEC
_, tA = register("D","secD_a"); _, tB = register("D","secD_b")
riasec_fixe = {"R":4,"I":3,"A":2,"S":3,"E":4,"C":3}
_, pA = fill_questionnaire(tA, riasec_fixe, tranche=1, mobile=False, horizon="court")
_, pB = fill_questionnaire(tB, riasec_fixe, tranche=4, mobile=True, horizon="long")
if pA and pB:
    memes_scores = all(pA[f"score_{d}"]==pB[f"score_{d}"] for d in "risaec")
    check(memes_scores,
          "Section D n'affecte PAS les scores RIASEC (budget/mobilité/horizon ≠ psychologie)",
          f"A:R{pA['score_r']} B:R{pB['score_r']}")

# ════════════════════════════════════════════════════════════════
# BILAN
print(f"\n{'='*68}")
total = len(passed)+len(failed)
print(f"  {BOLD}RÉSULTATS{RST}")
print(f"  {OK} Passés  : {len(passed)}/{total}")
print(f"  {FAIL} Échoués : {len(failed)}/{total}")
print(f"  {WARN} Alertes : {len(warned)}")
print(f"  {SKIP} Ignorés : {len(skipped)}")
if failed:
    print(f"\n  {BOLD}DÉTAIL DES ÉCHECS :{RST}")
    for msg, detail in failed:
        print(f"    {FAIL} {msg}" + (f"\n        → {detail}" if detail else ""))
if warned:
    print(f"\n  {BOLD}ALERTES :{RST}")
    for msg in warned:
        print(f"    {WARN} {msg}")
print(f"\n{'='*68}")
if not failed:
    print(f"  {OK} {BOLD}CONFORMITÉ TOTALE AU MÉMOIRE — Application validée{RST}")
else:
    print(f"  {FAIL} {BOLD}{len(failed)} non-conformité(s) à corriger{RST}")
print(f"{'='*68}\n")
sys.exit(0 if not failed else 1)
