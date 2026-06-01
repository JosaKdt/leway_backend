#!/usr/bin/env bash
set -e
SRC="/mnt/c/Users/folaw/ProjetReact/src"
ROOT="/mnt/c/Users/folaw/ProjetReact"

echo "╔══════════════════════════════════════════════════╗"
echo "║  ORIAB — Connexion React ↔ FastAPI (suite)      ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ── .env (VITE_API_URL) ──────────────────────────────────────────────────────
cat > "$ROOT/.env.local" << 'ENV'
VITE_API_URL=http://localhost:8000
ENV
echo "✅ .env.local"

# ── hooks/useAuth.ts — branché sur authAPI réel ──────────────────────────────
cat > "$SRC/hooks/useAuth.ts" << 'TS'
// hooks/useAuth.ts — branché sur FastAPI
import { useState } from 'react';
import { authAPI } from '../services/api';

export function useAuthState() {
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('oriab_token')
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const login = async (email: string, password: string) => {
    setLoading(true); setError('');
    try {
      const res = await authAPI.login(email, password);
      const t = res.data.access_token;
      localStorage.setItem('oriab_token', t);
      setToken(t);
      window.dispatchEvent(new Event('oriab_auth_change'));
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })
        ?.response?.data?.detail || 'Erreur de connexion';
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('oriab_token');
    localStorage.removeItem('oriab_admin_token');
    setToken(null);
    window.dispatchEvent(new Event('oriab_auth_change'));
  };

  return { isAuthenticated: !!token, token, login, logout, loading, error };
}
TS
echo "✅ hooks/useAuth.ts"

# ── services/apiExtra.ts — nettoyé, redirige vers api.ts ────────────────────
cat > "$SRC/services/apiExtra.ts" << 'TS'
// Redirige vers api.ts — ce fichier est conservé pour la compatibilité
export { filieresAPI as filiereAPI, adminAPI, api as default } from './api';
TS
echo "✅ services/apiExtra.ts"


# ── QuestionnairePage.tsx — branché FastAPI ──────────────────────────────────
cat > "$SRC/pages/questionnaire/QuestionnairePage.tsx" << 'TSX'
// pages/questionnaire/QuestionnairePage.tsx — branché FastAPI
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight, ChevronLeft, Save, Loader2 } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { QUESTIONS, SECTIONS } from './questionsData';
import { profilAPI, recommandationsAPI } from '../../services/api';
import { markQuestionnaireCompleted } from '../../lib/auth';
import { extractVetoFactors } from '../../lib/scoring';

type Section = 'A'|'B'|'C'|'D'|'E';
const SECTION_ORDER: Section[] = ['A','B','C','D','E'];
const STORAGE_KEY = 'oriab_questionnaire_progress';
const LIKERT = [
  {val:1,label:'Pas du tout'},{val:2,label:'Peu'},
  {val:3,label:'Moyennement'},{val:4,label:'Beaucoup'},{val:5,label:'Tout à fait'},
];

export function QuestionnairePage() {
  const navigate = useNavigate();
  const [sectionIdx, setSectionIdx] = useState(0);
  const [reponses, setReponses] = useState<Record<string,number>>(() => {
    const s = localStorage.getItem(STORAGE_KEY);
    return s ? JSON.parse(s) : {};
  });
  const [submitting, setSubmitting] = useState(false);
  const [submitStep, setSubmitStep] = useState('');
  const [saved, setSaved]   = useState(false);
  const [apiError, setApiError] = useState('');

  const currentSection  = SECTION_ORDER[sectionIdx];
  const sectionQuestions = QUESTIONS.filter(q => q.section === currentSection);
  const sectionAnswered  = sectionQuestions.every(q => reponses[q.id] !== undefined);
  const totalAnswered    = QUESTIONS.filter(q => reponses[q.id] !== undefined).length;

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(reponses));
  }, [reponses]);

  const setReponse = (id: string, val: number) =>
    setReponses(p => ({...p, [id]: val}));

  const submitToBackend = async (patch = false) => {
    const veto    = extractVetoFactors(reponses);
    const rf      = veto.ressources_financieres;
    const tranche = rf < 100000 ? 1 : rf < 200000 ? 2 : rf < 400000 ? 3 : 4;
    const payload = {
      reponses,
      ressources_financieres: tranche,
      mobilite_geo:           veto.mobilite_geo,
      horizon_temporel:       veto.horizon_temporel,
    };
    setSubmitStep(patch ? 'Mise à jour du profil...' : 'Calcul du profil RIASEC...');
    if (patch) {
      await profilAPI.recalculer(payload);
    } else {
      await profilAPI.submit(payload);
    }
    setSubmitStep('Génération des recommandations...');
    const rec = await recommandationsAPI.generer();
    const data = rec.data as Record<string,string>;
    return data.id_recommandation || data.id;
  };

  const handleSubmit = async () => {
    setSubmitting(true); setApiError('');
    try {
      const id = await submitToBackend(false);
      markQuestionnaireCompleted();
      localStorage.removeItem(STORAGE_KEY);
      navigate(`/rapport?id=${id}`);
    } catch (err: unknown) {
      const detail = (err as {response?:{data?:{detail?:string}}})?.response?.data?.detail;
      if (detail?.includes('déjà existant')) {
        try {
          const id = await submitToBackend(true);
          markQuestionnaireCompleted();
          localStorage.removeItem(STORAGE_KEY);
          navigate(`/rapport?id=${id}`);
          return;
        } catch { /* afficher erreur */ }
      }
      setApiError(detail || 'Erreur serveur. Vérifie que le backend tourne sur localhost:8000');
    } finally {
      setSubmitting(false); setSubmitStep('');
    }
  };

  const isLast = sectionIdx === SECTION_ORDER.length - 1;

  return (
    <div className="min-h-screen bg-[#F8FAFB] pt-20 pb-16">
      {/* Barre progression */}
      <div className="fixed top-16 left-0 right-0 z-40 bg-white border-b border-gray-100">
        <div className="max-w-2xl mx-auto px-4 py-3 flex items-center gap-4">
          <div className="flex gap-1.5">
            {SECTION_ORDER.map((s,i) => (
              <button key={s} onClick={() => setSectionIdx(i)}
                className={`h-1.5 rounded-full transition-all
                  ${i<=sectionIdx?'bg-[#00853F]':'bg-gray-200'}
                  ${i===sectionIdx?'w-8':'w-3'}`}/>
            ))}
          </div>
          <span className="text-xs text-gray-500 font-medium ml-auto">
            {totalAnswered}/{QUESTIONS.length} réponses
          </span>
          <button onClick={() => {setSaved(true); setTimeout(()=>setSaved(false),2000);}}
            className={`flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-lg
              ${saved?'text-[#00853F] bg-green-50':'text-gray-400'}`}>
            <Save size={12}/> {saved?'Sauvegardé !':'Sauvegarder'}
          </button>
        </div>
        <div className="h-0.5 bg-gray-100">
          <div className="h-0.5 bg-[#00853F] transition-all duration-500"
            style={{width:`${(totalAnswered/QUESTIONS.length)*100}%`}}/>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 pt-8">
        {/* En-tête section */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-xs font-bold text-[#00853F] bg-green-50 px-3 py-1 rounded-full">
              Section {currentSection} · {sectionIdx+1}/{SECTION_ORDER.length}
            </span>
            {currentSection==='D' && (
              <span className="text-xs text-amber-600 bg-amber-50 px-3 py-1 rounded-full font-medium">
                ℹ️ Contexte uniquement
              </span>
            )}
          </div>
          <h1 className="text-2xl font-black text-[#0D1B2A]">{SECTIONS[currentSection]}</h1>
          {currentSection==='D' && (
            <p className="text-sm text-gray-500 mt-2 bg-amber-50 border border-amber-100 rounded-xl p-3">
              Ces informations définissent tes contraintes pratiques. Elles ne rentrent{' '}
              <strong>pas</strong> dans le calcul de ton profil psychologique — uniquement
              dans le filtrage des filières.
            </p>
          )}
        </div>

        {/* Erreur API */}
        {apiError && (
          <div className="mb-6 p-4 bg-red-50 border border-red-100 rounded-xl text-sm text-[#E8112D]">
            <p className="font-semibold mb-1">⚠️ Erreur</p>
            <p>{apiError}</p>
            <p className="mt-2 text-xs text-red-400">
              Backend FastAPI requis sur <code>http://localhost:8000</code>
            </p>
          </div>
        )}

        {/* Questions */}
        <div className="flex flex-col gap-5">
          {sectionQuestions.map((q,qi) => (
            <div key={q.id} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
              <div className="flex items-start gap-3 mb-5">
                <span className="shrink-0 w-6 h-6 rounded-full bg-gray-100 text-gray-500
                  text-xs font-bold flex items-center justify-center">{qi+1}</span>
                <p className="text-[#0D1B2A] font-medium text-sm leading-relaxed">{q.texte}</p>
              </div>
              <div className="flex justify-between gap-1">
                {LIKERT.map(l => {
                  const sel = reponses[q.id]===l.val;
                  return (
                    <button key={l.val} onClick={() => setReponse(q.id,l.val)}
                      className={`flex flex-col items-center gap-1.5 flex-1 py-3 rounded-xl
                        border-2 transition-all text-center
                        ${sel
                          ?'border-[#00853F] bg-green-50 text-[#00853F]'
                          :'border-gray-100 hover:border-gray-300 text-gray-400'}`}>
                      <span className={`text-xl font-black
                        ${sel?'text-[#00853F]':'text-gray-300'}`}>{l.val}</span>
                      <span className="text-[9px] font-medium leading-tight">{l.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between mt-8 pb-4">
          <Button variant="ghost" onClick={() => setSectionIdx(s=>s-1)}
            disabled={sectionIdx===0}>
            <ChevronLeft size={16}/> Précédent
          </Button>
          {isLast ? (
            <Button onClick={handleSubmit} loading={submitting}
              disabled={totalAnswered < QUESTIONS.length} className="px-8">
              {submitting
                ? <span className="flex items-center gap-2">
                    <Loader2 size={14} className="animate-spin"/>
                    {submitStep||'Traitement...'}
                  </span>
                : `Voir mon rapport (${totalAnswered}/${QUESTIONS.length})`}
            </Button>
          ) : (
            <Button onClick={() => setSectionIdx(s=>s+1)} disabled={!sectionAnswered}>
              Section suivante <ChevronRight size={16}/>
            </Button>
          )}
        </div>
        {!sectionAnswered && !isLast && (
          <p className="text-center text-xs text-gray-400 mt-2">
            Réponds à toutes les questions pour continuer
          </p>
        )}
      </div>
    </div>
  );
}
TSX
echo "✅ pages/questionnaire/QuestionnairePage.tsx"

# ── RapportPage.tsx — branché FastAPI ────────────────────────────────────────
cat > "$SRC/pages/rapport/RapportPage.tsx" << 'TSX'
// pages/rapport/RapportPage.tsx — branché FastAPI
import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  RadarChart, PolarGrid, PolarAngleAxis,
  Radar, ResponsiveContainer, Tooltip
} from 'recharts';
import {
  ArrowRight, Star, TrendingUp, Clock,
  Users, Zap, BarChart3, BookOpen, Loader2
} from 'lucide-react';
import { Card, CardBody } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { recommandationsAPI, profilAPI } from '../../services/api';
import { IA_TENDANCE_LABELS, formatFCFA } from '../../lib/utils';

const RIASEC_LABELS: Record<string,string> = {
  R:'Réaliste', I:'Investigateur', A:'Artistique',
  S:'Social', E:'Entreprenant', C:'Conventionnel',
};

interface ProfilRiasec {
  score_r:number; score_i:number; score_a:number;
  score_s:number; score_e:number; score_c:number;
  dimension_dominante:string;
}

interface FiliereScoree {
  nom:string; domaine:string;
  weighted_score:number; sim_riasec:number;
  score_marche:number; score_ia:number;
  duree_theorique:number; salaire_median_p50?:number;
  taux_insertion?:number; indice_saturation?:number;
  tendance_ia?:number; justification_ia?:string;
}

export function RapportPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const id = searchParams.get('id');

  const [profil, setProfil]   = useState<ProfilRiasec|null>(null);
  const [top3, setTop3]       = useState<FiliereScoree[]>([]);
  const [genDate, setGenDate] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState('');
  const [compareList, setCompareList] = useState<string[]>([]);

  useEffect(() => {
    (async () => {
      try {
        // 1. Profil RIASEC
        const pr = await profilAPI.getMon();
        setProfil(pr.data as ProfilRiasec);

        // 2. Recommandation (par id ou la plus récente)
        let recId = id;
        if (!recId) {
          const list = await recommandationsAPI.getMes();
          const recs = list.data as Record<string,string>[];
          if (recs.length === 0) throw new Error('Aucune recommandation trouvée.');
          recId = recs[0].id_recommandation || recs[0].id;
        }
        const detail = await recommandationsAPI.getById(recId!);
        const d = detail.data as Record<string,unknown>;
        setGenDate((d.date_generation as string) || '');

        // 3. Scores de compatibilité
        const scores = (d.scores as FiliereScoree[]) || [];
        setTop3(scores.slice(0,3));
      } catch (e: unknown) {
        setError((e as {message?:string})?.message || 'Erreur de chargement.');
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  if (loading) return (
    <div className="min-h-screen bg-[#F8FAFB] flex items-center justify-center pt-20">
      <div className="flex flex-col items-center gap-3 text-gray-500">
        <Loader2 size={32} className="animate-spin text-[#00853F]"/>
        <p className="text-sm font-medium">Chargement de ton rapport...</p>
      </div>
    </div>
  );

  if (error || !profil) return (
    <div className="min-h-screen bg-[#F8FAFB] flex items-center justify-center pt-20 px-4">
      <div className="text-center max-w-md">
        <div className="w-20 h-20 mx-auto rounded-2xl bg-gray-100 flex items-center justify-center mb-4">
          <BarChart3 size={36} className="text-gray-300"/>
        </div>
        <h2 className="text-xl font-black text-[#0D1B2A] mb-2">Aucun rapport disponible</h2>
        <p className="text-gray-500 text-sm mb-2">{error || 'Complète le questionnaire pour recevoir tes recommandations.'}</p>
        {error && <p className="text-xs text-red-400 mb-4">Vérifie que le backend FastAPI tourne sur localhost:8000</p>}
        <Button onClick={() => navigate('/questionnaire')}>
          <BookOpen size={16}/> Passer le questionnaire
        </Button>
      </div>
    </div>
  );

  const scores = {
    R:profil.score_r, I:profil.score_i, A:profil.score_a,
    S:profil.score_s, E:profil.score_e, C:profil.score_c,
  };
  const radarData = Object.entries(scores).map(([k,v]) => ({
    subject: RIASEC_LABELS[k], score: v, fullMark: 100,
  }));
  const dominants = Object.entries(scores).sort(([,a],[,b]) => b-a).slice(0,3);

  const toggleCompare = (nom: string) =>
    setCompareList(p => p.includes(nom)
      ? p.filter(x=>x!==nom)
      : p.length < 3 ? [...p,nom] : p);

  return (
    <div className="min-h-screen bg-[#F8FAFB] pt-20 pb-16 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex items-start justify-between gap-4 flex-wrap">
          <div>
            <p className="text-xs font-bold text-[#00853F] uppercase tracking-widest mb-1">Rapport ORIAB</p>
            <h1 className="text-3xl font-black text-[#0D1B2A]">Tes recommandations personnalisées</h1>
            {genDate && (
              <p className="text-gray-500 text-sm mt-1">
                Généré le {new Date(genDate).toLocaleDateString('fr-FR',
                  {day:'numeric',month:'long',year:'numeric'})}
              </p>
            )}
          </div>
          {compareList.length >= 2 && (
            <Button onClick={() => navigate(`/filieres/comparer?ids=${compareList.join(',')}`)}>
              Comparer {compareList.length} filières <ArrowRight size={15}/>
            </Button>
          )}
        </div>

        {/* Radar + scores */}
        <div className="grid lg:grid-cols-5 gap-6 mb-8">
          <Card className="lg:col-span-3">
            <CardBody>
              <h2 className="font-black text-[#0D1B2A] mb-1">Ton profil psychométrique RIASEC</h2>
              <p className="text-xs text-gray-400 mb-4">6 dimensions · 28 questions · Calibré contexte béninois</p>
              <ResponsiveContainer width="100%" height={260}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#e5e7eb"/>
                  <PolarAngleAxis dataKey="subject"
                    tick={{fill:'#374151',fontSize:11,fontWeight:600}}/>
                  <Radar dataKey="score" stroke="#00853F" fill="#00853F"
                    fillOpacity={0.15} strokeWidth={2}/>
                  <Tooltip formatter={(v:number) => [`${v}/100`,'Score']}/>
                </RadarChart>
              </ResponsiveContainer>
            </CardBody>
          </Card>

          <div className="lg:col-span-2 flex flex-col gap-4">
            <Card><CardBody className="p-5">
              <h3 className="font-black text-[#0D1B2A] text-sm mb-4">Scores détaillés</h3>
              <div className="flex flex-col gap-2.5">
                {Object.entries(scores).sort(([,a],[,b])=>b-a).map(([k,v]) => (
                  <div key={k}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="font-semibold text-[#0D1B2A]">{k} — {RIASEC_LABELS[k]}</span>
                      <span className="font-bold text-[#00853F]">{v}/100</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-1.5">
                      <div className="bg-[#00853F] h-1.5 rounded-full" style={{width:`${v}%`}}/>
                    </div>
                  </div>
                ))}
              </div>
            </CardBody></Card>

            <Card className="bg-green-50/50 border-[#00853F]/20">
              <CardBody className="p-5">
                <h3 className="font-black text-[#0D1B2A] text-sm mb-3">🎯 Dimensions dominantes</h3>
                {dominants.map(([k,v],i) => (
                  <div key={k} className="flex items-center gap-2 mb-2">
                    <span className="w-5 h-5 rounded-full bg-[#00853F] text-white
                      text-xs font-black flex items-center justify-center">{i+1}</span>
                    <span className="font-semibold text-[#0D1B2A] text-sm">
                      {RIASEC_LABELS[k]}
                    </span>
                    <span className="text-gray-400 text-xs ml-auto">{v}/100</span>
                  </div>
                ))}
              </CardBody>
            </Card>
          </div>
        </div>

        {/* Top 3 */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-black text-[#0D1B2A]">Tes filières recommandées</h2>
            <p className="text-xs text-gray-400">Score = 60% RIASEC · 25% marché · 15% IA</p>
          </div>

          {top3.length === 0 ? (
            <div className="text-center py-12 text-gray-400 bg-white rounded-2xl border border-gray-100">
              <p className="font-medium">Aucune filière recommandée</p>
              <p className="text-xs mt-1">
                Toutes les filières ont été filtrées par les Veto Factors.<br/>
                Revois tes contraintes (budget, durée, mobilité).
              </p>
              <button onClick={() => navigate('/questionnaire')}
                className="mt-4 text-sm text-[#00853F] hover:underline font-medium">
                Refaire le questionnaire →
              </button>
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              {top3.map((f,i) => {
                const ia = IA_TENDANCE_LABELS[f.tendance_ia??1];
                const inComp = compareList.includes(f.nom);
                return (
                  <Card key={f.nom}
                    className={i===0?'border-[#00853F]/40 ring-1 ring-[#00853F]/20':''}>
                    <CardBody className="p-5">
                      <div className="flex items-start gap-4 flex-wrap">
                        <div className={`shrink-0 w-12 h-12 rounded-xl flex flex-col
                          items-center justify-center font-black text-sm
                          ${i===0
                            ?'bg-[#00853F] text-white shadow-lg shadow-green-200'
                            :'bg-gray-100 text-gray-600'}`}>
                          {i===0 && <Star size={12} className="mb-0.5"/>}
                          #{i+1}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-2 flex-wrap">
                            <div>
                              <h3 className="font-black text-[#0D1B2A]">{f.nom}</h3>
                              <p className="text-xs text-gray-400">{f.domaine}</p>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-2xl font-black text-[#00853F]">
                                {Math.round(f.weighted_score)}%
                              </span>
                              <span className="text-xs font-semibold px-2 py-1 rounded-full"
                                style={{backgroundColor:ia.color+'18',color:ia.color}}>
                                {ia.label}
                              </span>
                            </div>
                          </div>

                          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-3">
                            {[
                              {icon:<TrendingUp size={11}/>,label:'Salaire médian',
                                val:formatFCFA(f.salaire_median_p50??0)},
                              {icon:<Users size={11}/>,label:'Insertion',
                                val:`${f.taux_insertion??0}%`},
                              {icon:<Clock size={11}/>,label:'Durée',
                                val:`${f.duree_theorique} ans`},
                              {icon:<Zap size={11}/>,label:'Match RIASEC',
                                val:`${Math.round(f.sim_riasec*100)}%`},
                            ].map(m => (
                              <div key={m.label} className="bg-gray-50 rounded-xl p-2.5">
                                <div className="flex items-center gap-1 text-gray-400
                                  text-[10px] mb-1">{m.icon}{m.label}</div>
                                <p className="font-bold text-[#0D1B2A] text-sm">{m.val}</p>
                              </div>
                            ))}
                          </div>

                          {f.justification_ia && (
                            <p className="text-xs text-gray-500 leading-relaxed mt-3
                              border-t border-gray-100 pt-3">
                              {f.justification_ia}
                            </p>
                          )}

                          <div className="flex gap-2 mt-3">
                            <button
                              onClick={() => toggleCompare(f.nom)}
                              disabled={!inComp && compareList.length >= 3}
                              className={`text-xs font-semibold py-1.5 px-3 rounded-lg
                                border-2 transition-all
                                ${inComp
                                  ?'bg-[#00853F] border-[#00853F] text-white'
                                  :compareList.length>=3
                                    ?'border-gray-200 text-gray-300 cursor-not-allowed'
                                    :'border-gray-200 text-gray-600 hover:border-[#00853F] hover:text-[#00853F]'}`}>
                              {inComp ? '✓ Sélectionnée' : '+ Comparer'}
                            </button>
                          </div>
                        </div>
                      </div>
                    </CardBody>
                  </Card>
                );
              })}
            </div>
          )}
        </div>

        <div className="mt-8 text-center">
          <button onClick={() => navigate('/questionnaire')}
            className="text-sm text-gray-400 hover:text-[#00853F] font-medium
              hover:underline transition-colors">
            Refaire le questionnaire pour mettre à jour mon profil →
          </button>
        </div>
      </div>
    </div>
  );
}
TSX
echo "✅ pages/rapport/RapportPage.tsx"

# ── Vérification finale ───────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "  Fichiers écrits :"
for f in \
  ".env.local" \
  "src/hooks/useAuth.ts" \
  "src/services/apiExtra.ts" \
  "src/pages/questionnaire/QuestionnairePage.tsx" \
  "src/pages/rapport/RapportPage.tsx"; do
  if [ -f "$ROOT/$f" ]; then
    echo "  ✅ $f"
  else
    echo "  ❌ MANQUANT: $f"
  fi
done

echo ""
echo "  Fichiers déjà écrits (session précédente) :"
for f in \
  "src/services/api.ts" \
  "src/lib/auth.ts" \
  "src/pages/auth/LoginPage.tsx" \
  "src/pages/auth/InscriptionPage.tsx"; do
  if [ -f "$ROOT/$f" ]; then
    echo "  ✅ $f"
  else
    echo "  ❌ MANQUANT: $f"
  fi
done

echo ""
echo "═══════════════════════════════════════════════════"
echo "  ORIAB — Connexion React ↔ FastAPI COMPLÈTE ✅"
echo "═══════════════════════════════════════════════════"
echo ""
echo "  Démarrer le backend (WSL) :"
echo "    cd ~/leway_backend"
echo "    source venv/bin/activate"
echo "    uvicorn app.main:app --reload --port 8000 --host 0.0.0.0"
echo ""
echo "  Démarrer le frontend (PowerShell) :"
echo "    cd C:\Users\folaw\ProjetReact"
echo "    npm run dev"
echo ""
echo "  Ouvrir dans le navigateur : http://localhost:5173"
