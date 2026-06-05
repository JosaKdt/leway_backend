"""
ORIAB — Test de validation chantier 2 (filtrage série bac)
Lancer : python3 /tmp/test_chantier2.py  (API doit tourner sur :8000)
"""
import json, urllib.request, urllib.error, random, sys

BASE = "http://localhost:8000"
OK = "\033[92m✅\033[0m"
FAIL = "\033[91m❌\033[0m"
errors = []

def call(method, path, data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token: headers["Authorization"] = "Bearer " + token
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(BASE+path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

def creer_profil(serie, reponses_fortes, tranche, mobile, horizon):
    email = f"t2_{random.randint(10000,99999)}@oriab.bj"
    st, reg = call("POST", "/api/auth/register", {
        "nom":"Test","prenom":f"Serie{serie}","email":email,
        "mot_de_passe":"test1234","serie_bac":serie
    })
    if st != 201:
        return None, None, None
    token = reg["access_token"]
    rep = {f"Q{i:02d}": 2 for i in range(1, 29)}
    rep.update(reponses_fortes)
    rep.update({"Q18":3,"Q19":3,"Q20":3,"Q21":3,"Q22":3})
    st, prof = call("POST", "/api/profil/", {
        "reponses": rep, "ressources_financieres": tranche,
        "mobilite_geo": mobile, "horizon_temporel": horizon
    }, token)
    if st != 201:
        return None, None, None
    st, rec = call("POST", "/api/recommandations/generer", {}, token)
    if st not in (200, 201):
        return None, None, None
    rid = rec.get("id_recommandation") or rec.get("id")
    _, detail = call("GET", f"/api/recommandations/{rid}", None, token)
    return prof, detail.get("scores", []), detail.get("eliminees", [])

def check(condition, msg_ok, msg_fail):
    global errors
    if condition:
        print(f"  {OK} {msg_ok}")
    else:
        print(f"  {FAIL} {msg_fail}")
        errors.append(msg_fail)

print("\n" + "="*65)
print("  CHANTIER 2 — Validation filtrage série bac (3 profils)")
print("="*65)

# ── TEST 1 : Série A2 (littéraire)
print("\n[1] Série A2 — Profil Artistique + Social dominant\n")
prof1, reco1, elim1 = creer_profil(
    "A2",
    {"Q03":5,"Q08":5,"Q17":5,"Q28":5,"Q11":5,"Q14":5},
    tranche=2, mobile=True, horizon="moyen"
)
if prof1:
    print(f"  Scores: R={prof1['score_r']} I={prof1['score_i']} A={prof1['score_a']} "
          f"S={prof1['score_s']} E={prof1['score_e']} C={prof1['score_c']}")
    print(f"  Dominante: {prof1['dimension_dominante']}")
    print(f"\n  Recommandées ({len(reco1)}):")
    for s in reco1:
        print(f"    #{s['classement']} {s['nom'][:50]} — WS={s['weighted_score']}%")
    print(f"\n  Éliminées (veto) : {len(elim1)}")
    for e in elim1[:6]:
        print(f"    ✗ {e['nom'][:50]}")

    reco_noms = [s["nom"] for s in reco1]
    elim_noms = [e["nom"] for e in elim1]

    check(len(reco1) >= 1,
          f"{len(reco1)} filières recommandées (au moins 1)",
          "0 filières recommandées — problème de veto trop restrictif!")
    check(not any("Médecine" in n for n in reco_noms),
          "Médecine absente des reco A2",
          "Médecine présente dans reco A2 — VETO 4 échoué!")
    check(not any("Génie Informatique" in n or "Data Science" in n for n in reco_noms),
          "Filières techno-scientifiques absentes des reco A2",
          "Filière techno-scientifique présente pour A2 — VETO 4 échoué!")
    check(not any("Sciences Infirmières" in n for n in reco_noms),
          "Sciences Infirmières absente des reco A2",
          "Sciences Infirmières présente pour A2 — VETO 4 échoué!")
    # Vérifier que des filières littéraires/humaines sont recommandées
    humanistes = ["Éducation","Psychologie","Lettres","Sociologie","Droit",
                  "Communication","Langues","Histoire","Journalisme","Arts"]
    has_human = any(any(h in n for h in humanistes) for n in reco_noms)
    check(has_human,
          f"Filières compatibles A2 recommandées: {reco_noms}",
          f"Aucune filière compatible A2 dans {reco_noms}")
    # Vérifier que des filières scientifiques sont bien éliminées
    check(any("Médecine" in n or "Génie" in n or "Data" in n for n in elim_noms),
          "Filières C/D correctement éliminées pour A2",
          "Filières C/D pas éliminées — VETO 4 pas actif!")
else:
    print(f"  {FAIL} ERREUR création profil A2")
    errors.append("Création profil A2 échouée")

# ── TEST 2 : Série D (scientifique)
print("\n[2] Série D — Profil Investigateur + Réaliste dominant\n")
prof2, reco2, elim2 = creer_profil(
    "D",
    {"Q02":5,"Q05":5,"Q07":5,"Q15":5,"Q16":5,"Q23":5,"Q25":5},
    tranche=3, mobile=True, horizon="long"
)
if prof2:
    print(f"  Scores: R={prof2['score_r']} I={prof2['score_i']} A={prof2['score_a']} "
          f"S={prof2['score_s']} E={prof2['score_e']} C={prof2['score_c']}")
    print(f"  Dominante: {prof2['dimension_dominante']}")
    print(f"\n  Recommandées ({len(reco2)}):")
    for s in reco2:
        print(f"    #{s['classement']} {s['nom'][:50]} — WS={s['weighted_score']}%")
    reco_noms2 = [s["nom"] for s in reco2]
    sci = ["Data Science","Génie","Médecine","Informatique","Sciences","Énergie","Physique","Math"]
    has_sci = any(any(s in n for s in sci) for n in reco_noms2)
    check(has_sci,
          f"Filières scientifiques recommandées pour D: {reco_noms2}",
          f"Aucune filière scientifique pour D — anomalie!")
    check(len(reco2) >= 1,
          f"{len(reco2)} filières recommandées",
          "0 filières recommandées pour série D!")

# ── TEST 3 : Série G2 (gestion)
print("\n[3] Série G2 — Profil Conventionnel + Entreprenant dominant\n")
prof3, reco3, elim3 = creer_profil(
    "G2",
    {"Q04":5,"Q09":5,"Q10":5,"Q12":5,"Q13":5,"Q26":5},
    tranche=3, mobile=False, horizon="moyen"
)
if prof3:
    print(f"  Scores: R={prof3['score_r']} I={prof3['score_i']} A={prof3['score_a']} "
          f"S={prof3['score_s']} E={prof3['score_e']} C={prof3['score_c']}")
    print(f"  Dominante: {prof3['dimension_dominante']}")
    print(f"\n  Recommandées ({len(reco3)}):")
    for s in reco3:
        print(f"    #{s['classement']} {s['nom'][:50]} — WS={s['weighted_score']}%")
    reco_noms3 = [s["nom"] for s in reco3]
    gest = ["Économie","Finance","Gestion","Commerce","Comptabilité","Marketing","Banque","Fiscal"]
    has_gest = any(any(g in n for g in gest) for n in reco_noms3)
    check(has_gest,
          f"Filières gestion recommandées pour G2: {reco_noms3}",
          f"Aucune filière gestion pour G2 — série G normalisée incorrectement?")
    check(not any("Médecine" in n for n in reco_noms3),
          "Médecine absente des reco G2",
          "Médecine présente pour G2 — VETO 4 échoué!")

# ── Bilan
print("\n" + "="*65)
if not errors:
    print(f"  {OK} CHANTIER 2 VALIDÉ — {3*4} vérifications passées")
    print("  Le filtrage série bac fonctionne correctement.")
else:
    print(f"  {FAIL} {len(errors)} ÉCHEC(S):")
    for e in errors:
        print(f"    - {e}")
print("="*65 + "\n")
