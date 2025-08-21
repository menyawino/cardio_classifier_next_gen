import React from 'react';

interface RuleBadgeProps { code: string; strength: string; }

const strengthColor: Record<string,string> = {
  VeryStrong: 'bg-red-700',
  Strong: 'bg-red-600',
  Moderate: 'bg-orange-500',
  Supporting: 'bg-yellow-400 text-black',
  StandAloneBenign: 'bg-green-700',
  StrongBenign: 'bg-green-600',
  SupportingBenign: 'bg-green-300 text-black'
};

export const RuleBadges: React.FC<{ rules: {code:string; strength:string}[] }> = ({ rules }) => {
  return (
    <div className="flex flex-wrap gap-2">
      {rules.map(r => (
        <span key={r.code+Math.random()} className={`px-2 py-1 rounded text-xs font-medium ${strengthColor[r.strength] || 'bg-slate-500'}`}>
          {r.code}
        </span>
      ))}
    </div>
  );
};
