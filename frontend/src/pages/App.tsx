import React, { useState, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { classifyVariant, setAuthToken, api } from '../lib/api';
import { RuleBadges } from '../components/RuleBadges';
import { AuthPanel } from '../components/AuthPanel';
import { listVariants, getVariantHistory, ClassificationEvent, StoredVariant } from '../lib/variants';
// axios instance provided via api import

export default function App() {
  const [token, setToken] = useState<string | null>(null);
  const [hgvs, setHgvs] = useState('NM_000000.0:c.123A>T');
  const [variants, setVariants] = useState<StoredVariant[]>([]);
  const [selectedVariant, setSelectedVariant] = useState<StoredVariant | null>(null);
  const [history, setHistory] = useState<ClassificationEvent[]>([]);
  const [batchText, setBatchText] = useState('NM_000000.0:c.123A>T\nNM_000001.1:c.456G>C');
  const [batchResult, setBatchResult] = useState<any[] | null>(null);

  useEffect(()=>{
    if(token){
      setAuthToken(token);
      refreshVariants();
    }
  },[token]);

  async function refreshVariants(){
    try { setVariants(await listVariants()); } catch(e){ /* ignore */ }
  }

  const mutation = useMutation({
    mutationFn: () => classifyVariant(hgvs),
    onSuccess: ()=> refreshVariants()
  });

  async function loadHistory(v: StoredVariant){
    setSelectedVariant(v);
    try { setHistory(await getVariantHistory(v.id)); } catch(e){ setHistory([]); }
  }

  async function submitBatch(){
  const lines = batchText.split(/\r?\n/).map((l: string)=>l.trim()).filter(Boolean);
    if(!lines.length) return;
    try {
  const res = await api.post('/variants/batch', { variants: lines.map((h: string)=>({ hgvs: h }))});
      setBatchResult(res.data);
      refreshVariants();
    } catch(e){ setBatchResult([{ error: 'Batch failed'}]); }
  }

  if(!token){
    return <div className="max-w-md mx-auto py-10 px-6"><h1 className="text-3xl font-bold mb-6">Cardio Classifier</h1><AuthPanel onAuth={setToken} /></div>;
  }

  return (
    <div className="max-w-6xl mx-auto py-8 px-6 space-y-8">
      <header className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Cardio Classifier</h1>
  <button onClick={()=>{setToken(null); setAuthToken(null);}} className="text-sm text-red-600">Logout</button>
      </header>

      <section className="grid md:grid-cols-2 gap-8">
        <div className="space-y-4">
          <h2 className="font-semibold text-lg">Single Classification</h2>
          <div className="flex gap-2">
            <input className="border rounded px-3 py-2 flex-1" value={hgvs} onChange={e=>setHgvs(e.target.value)} />
            <button onClick={()=>mutation.mutate()} className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50" disabled={mutation.isLoading}>Classify</button>
          </div>
          {mutation.isPending && <p>Classifying...</p>}
          {mutation.isError && <p className="text-red-600">Error</p>}
          {mutation.data && (
            <div className="space-y-2 border rounded p-3">
              <p className="font-semibold">Classification: {mutation.data.classification}</p>
              <RuleBadges rules={mutation.data.applied_rules.map((r:any)=>({code:r.code,strength:r.strength}))} />
              <pre className="bg-slate-100 p-2 rounded text-xs overflow-auto max-h-40">{JSON.stringify(mutation.data.applied_rules, null, 2)}</pre>
            </div>
          )}
        </div>
        <div className="space-y-4">
          <h2 className="font-semibold text-lg">Batch Classification</h2>
            <textarea className="border rounded w-full h-40 p-2 text-sm font-mono" value={batchText} onChange={e=>setBatchText(e.target.value)} />
            <button onClick={submitBatch} className="bg-indigo-600 text-white px-4 py-2 rounded">Run Batch</button>
            {batchResult && <pre className="bg-slate-100 p-2 rounded text-xs max-h-40 overflow-auto">{JSON.stringify(batchResult,null,2)}</pre>}
        </div>
      </section>

      <section className="grid md:grid-cols-2 gap-8">
        <div>
          <h2 className="font-semibold mb-2">Recent Variants</h2>
          <div className="space-y-2 max-h-80 overflow-auto border rounded p-2 text-sm">
            {variants.map(v=> (
              <button key={v.id} onClick={()=>loadHistory(v)} className={`block w-full text-left px-2 py-1 rounded hover:bg-slate-100 ${selectedVariant?.id===v.id?'bg-slate-200':''}`}>{v.hgvs} <span className="text-xs text-slate-500">{v.classification}</span></button>
            ))}
          </div>
        </div>
        <div>
          <h2 className="font-semibold mb-2">History {selectedVariant && <span className="text-slate-500">({selectedVariant.hgvs})</span>}</h2>
          <div className="space-y-2 max-h-80 overflow-auto border rounded p-2 text-xs">
            {history.length===0 && <p className="text-slate-500">Select a variant.</p>}
            {history.map(h => (
              <div key={h.id} className="border rounded p-2 bg-white">
                <p className="font-semibold">{h.classification} <span className="text-slate-400">{new Date(h.created_at).toLocaleString()}</span></p>
                <pre className="bg-slate-50 p-2 rounded overflow-auto max-h-32">{JSON.stringify(h.evidence, null, 2)}</pre>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
