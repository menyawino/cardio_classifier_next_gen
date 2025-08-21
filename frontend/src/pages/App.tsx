import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { classifyVariant } from '../lib/api';
import { RuleBadges } from '../components/RuleBadges';

export default function App() {
  const [hgvs, setHgvs] = useState('NM_000000.0:c.123A>T');
  const mutation = useMutation({
    mutationFn: () => classifyVariant(hgvs)
  });

  return (
    <div className="max-w-3xl mx-auto py-10 px-6">
      <h1 className="text-3xl font-bold mb-4">Cardio Classifier</h1>
      <div className="flex gap-2 mb-4">
        <input className="border rounded px-3 py-2 flex-1" value={hgvs} onChange={e=>setHgvs(e.target.value)} />
        <button onClick={()=>mutation.mutate()} className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50" disabled={mutation.isLoading}>Classify</button>
      </div>
      {mutation.isPending && <p>Classifying...</p>}
      {mutation.isError && <p className="text-red-600">Error</p>}
      {mutation.data && (
        <div className="space-y-4">
          <div>
            <p className="font-semibold text-lg">Classification: {mutation.data.classification}</p>
            <RuleBadges rules={mutation.data.applied_rules.map((r:any)=>({code:r.code,strength:r.strength}))} />
          </div>
          <div>
            <h2 className="font-semibold">Evidence JSON</h2>
            <pre className="bg-slate-100 p-3 rounded text-xs overflow-auto max-h-64">{JSON.stringify(mutation.data.applied_rules, null, 2)}</pre>
          </div>
          <p className="text-xs text-slate-500">{mutation.data.rationale}</p>
        </div>
      )}
    </div>
  );
}
